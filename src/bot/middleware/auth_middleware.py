"""
Middleware de autenticación para el bot de Telegram.

Este middleware:
- Verifica que el usuario esté registrado
- Valida que la cuenta esté verificada
- Actualiza la última actividad del usuario
- Permite acceso a comandos de registro sin autenticación
"""

import logging
from typing import Callable, Awaitable
from telegram import Update
from telegram.ext import Application, ContextTypes
from src.database.connection import DatabaseManager
from src.auth import UserManager

logger = logging.getLogger(__name__)


class AuthMiddleware:
    """Middleware de autenticación."""

    # Comandos que no requieren autenticación
    PUBLIC_COMMANDS = [
        '/start',
        '/help',
        '/register',
        '/verify'
    ]

    def __init__(self, db_manager: DatabaseManager):
        """
        Inicializar middleware.

        Args:
            db_manager: Gestor de base de datos
        """
        self.db_manager = db_manager

    async def check_auth(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
    ) -> bool:
        """
        Verificar autenticación del usuario.

        Args:
            update: Update de Telegram
            context: Contexto del bot

        Returns:
            True si está autenticado, False en caso contrario
        """
        # Obtener chat_id del usuario
        if not update.effective_user:
            return False

        chat_id = update.effective_user.id

        # Verificar si el comando es público
        message_text = update.message.text if update.message else ""
        if any(cmd in message_text for cmd in self.PUBLIC_COMMANDS):
            return True

        # Verificar autenticación en base de datos
        try:
            with self.db_manager.get_session() as session:
                user_manager = UserManager(session)

                # Buscar usuario
                user = user_manager.get_user_by_chat_id(chat_id)

                if not user:
                    # Usuario no registrado
                    await update.message.reply_text(
                        "No estás registrado en el sistema.\n\n"
                        "Por favor, usa /register para registrarte."
                    )
                    return False

                if not user.is_verified:
                    # Usuario no verificado
                    await update.message.reply_text(
                        "Tu cuenta no está verificada.\n\n"
                        "Por favor, usa /verify <codigo> para verificar tu cuenta."
                    )
                    return False

                if not user.is_active:
                    # Usuario inactivo
                    await update.message.reply_text(
                        "Tu cuenta está inactiva.\n\n"
                        "Por favor, contacta al administrador."
                    )
                    return False

                # Guardar usuario en context para uso posterior
                context.user_data['telegram_user'] = user

                # Actualizar última actividad
                user_manager.update_last_activity(chat_id)

                return True

        except Exception as e:
            logger.error(f"Error verificando autenticación: {e}")
            await update.message.reply_text(
                "Error al verificar tu autenticación. "
                "Por favor, intenta más tarde."
            )
            return False


def setup_auth_middleware(application: Application, db_manager: DatabaseManager):
    """
    Configurar middleware de autenticación en la aplicación.

    Args:
        application: Aplicación de Telegram
        db_manager: Gestor de base de datos
    """
    logger.info("Configurando middleware de autenticación...")

    auth_middleware = AuthMiddleware(db_manager)

    # Agregar el middleware como un handler de tipo "update"
    # Este se ejecutará antes de los handlers específicos
    async def auth_filter(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Filtro de autenticación."""
        if update.message:
            is_authenticated = await auth_middleware.check_auth(update, context)
            if not is_authenticated:
                # Detener el procesamiento si no está autenticado
                raise StopPropagation()

    # Nota: Para implementar esto correctamente con python-telegram-bot v20,
    # necesitamos usar un approach diferente. El middleware se implementará
    # directamente en los handlers o usando decoradores.

    logger.info("Middleware de autenticación configurado")


class StopPropagation(Exception):
    """Excepción para detener la propagación de updates."""
    pass


def require_auth(func: Callable) -> Callable:
    """
    Decorador para requerir autenticación en un handler.

    Args:
        func: Función handler a decorar

    Returns:
        Función decorada
    """
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        """Wrapper que verifica autenticación."""
        if not update.effective_user:
            return

        chat_id = update.effective_user.id

        # Obtener db_manager del context (debe ser inyectado previamente)
        db_manager = context.bot_data.get('db_manager')
        if not db_manager:
            logger.error("db_manager no encontrado en bot_data")
            await update.message.reply_text(
                "Error de configuración del sistema."
            )
            return

        # Verificar autenticación
        try:
            with db_manager.get_session() as session:
                user_manager = UserManager(session)
                user = user_manager.get_user_by_chat_id(chat_id)

                if not user:
                    await update.message.reply_text(
                        "No estás registrado en el sistema.\n\n"
                        "Por favor, usa /register para registrarte."
                    )
                    return

                if not user.is_verified:
                    await update.message.reply_text(
                        "Tu cuenta no está verificada.\n\n"
                        "Por favor, usa /verify <codigo> para verificar tu cuenta."
                    )
                    return

                if not user.is_active:
                    await update.message.reply_text(
                        "Tu cuenta está inactiva.\n\n"
                        "Por favor, contacta al administrador."
                    )
                    return

                # Guardar usuario en context
                context.user_data['telegram_user'] = user

                # Actualizar última actividad
                user_manager.update_last_activity(chat_id)

                # Ejecutar handler original
                return await func(update, context, *args, **kwargs)

        except Exception as e:
            logger.error(f"Error en decorador de autenticación: {e}")
            await update.message.reply_text(
                "Error al verificar tu autenticación."
            )
            return

    return wrapper


def require_permission(comando: str):
    """
    Decorador para requerir permiso específico.

    Args:
        comando: Comando que requiere permiso (ej: '/crear_ticket')

    Returns:
        Decorador
    """
    def decorator(func: Callable) -> Callable:
        async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
            """Wrapper que verifica permiso."""
            # Primero verificar autenticación
            user = context.user_data.get('telegram_user')
            if not user:
                await update.message.reply_text(
                    "Debes estar autenticado para ejecutar esta operación."
                )
                return

            # Obtener db_manager
            db_manager = context.bot_data.get('db_manager')
            if not db_manager:
                logger.error("db_manager no encontrado en bot_data")
                return

            # Verificar permiso
            try:
                from src.auth import PermissionChecker

                with db_manager.get_session() as session:
                    permission_checker = PermissionChecker(session)
                    result = permission_checker.check_permission(
                        user.id_usuario,
                        comando
                    )

                    if not result.is_allowed:
                        await update.message.reply_text(
                            f"No tienes permiso para ejecutar esta operación.\n\n"
                            f"{result.mensaje}"
                        )
                        return

                    # Guardar permiso en context
                    context.user_data['current_permission'] = result

                    # Ejecutar handler original
                    return await func(update, context, *args, **kwargs)

            except Exception as e:
                logger.error(f"Error verificando permiso: {e}")
                await update.message.reply_text(
                    "Error al verificar permisos."
                )
                return

        return wrapper
    return decorator
