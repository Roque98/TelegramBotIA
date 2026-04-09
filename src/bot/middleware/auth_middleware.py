"""
Middleware de autenticación para el bot de Telegram.

Este middleware:
- Verifica que el usuario esté registrado y verificado
- Comprueba permisos de comando via PermissionService (nuevo SEC-01)
- Actualiza la última actividad del usuario
- Permite acceso a comandos públicos sin autenticación
"""

import logging
from typing import Callable, Optional, Any

from telegram import Update
from telegram.ext import Application, ContextTypes

from src.domain.auth.constants import AccountState
from src.domain.auth.user_query_repository import UserQueryRepository

logger = logging.getLogger(__name__)


class AuthMiddleware:
    """Middleware de autenticación con soporte async y PermissionService."""

    # Comandos que no requieren autenticación
    PUBLIC_COMMANDS = [
        '/start',
        '/help',
        '/register',
        '/verify',
        '/recargar_permisos',
    ]

    def __init__(self, db_manager: Any, permission_service: Optional[Any] = None):
        self.db_manager = db_manager
        self._permission_service = permission_service
        self._user_repo = UserQueryRepository(db_manager)

    async def check_auth(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
    ) -> bool:
        """
        Verifica autenticación y permisos del usuario.

        1. Permite acceso a PUBLIC_COMMANDS sin autenticación.
        2. Verifica que el usuario esté registrado, verificado y activo.
        3. Si hay PermissionService disponible, verifica el permiso de comando.
        """
        if not update.effective_user:
            return False

        chat_id = update.effective_user.id
        message_text = update.message.text if update.message else ""

        # Extraer el comando base (ej: "/ia" de "/ia consulta")
        command = None
        if message_text.startswith("/"):
            command = message_text.split()[0].split("@")[0].lower()

        # Comandos públicos: no requieren autenticación
        if command and command in self.PUBLIC_COMMANDS:
            return True

        try:
            user = await self._user_repo.get_by_chat_id(chat_id)

            if not user:
                await update.message.reply_text(
                    "No estás registrado en el sistema.\n\n"
                    "Por favor, usa /register para registrarte."
                )
                return False

            if not user.is_verified:
                await update.message.reply_text(
                    "Tu cuenta no está verificada.\n\n"
                    "Consulta tu código en el Portal de Consola de Monitoreo.\n"
                    "Luego usa: /verify <codigo>"
                )
                return False

            if not user.is_active:
                await update.message.reply_text(
                    "Tu cuenta está inactiva.\n\n"
                    "Por favor, contacta al administrador."
                )
                return False

            # Verificar permiso de comando via PermissionService (SEC-01)
            if command and self._permission_service:
                profile = await self._user_repo.get_profile_for_permissions(chat_id)
                if profile:
                    recurso = f"cmd:{command}"
                    allowed = await self._permission_service.can(
                        user_id=profile["user_id"],
                        recurso=recurso,
                        role_id=profile["role_id"],
                        gerencia_ids=profile["gerencia_ids"],
                        direccion_ids=profile["direccion_ids"],
                    )
                    if not allowed:
                        logger.warning(
                            f"Permiso denegado: user={profile['user_id']} cmd={command}"
                        )
                        await update.message.reply_text(
                            "No tienes permiso para ejecutar este comando."
                        )
                        return False

            # Guardar usuario y actualizar actividad
            context.user_data["telegram_user"] = user
            await self._user_repo.update_last_activity(chat_id)
            return True

        except Exception as e:
            logger.error(f"Error verificando autenticación para chat_id={chat_id}: {e}")
            await update.message.reply_text(
                "Error al verificar tu autenticación. Por favor, intenta más tarde."
            )
            return False


def setup_auth_middleware(application: Application, db_manager: Any) -> None:
    """Configura el middleware en la aplicación (referencia para uso futuro)."""
    logger.info("Middleware de autenticación configurado")


class StopPropagation(Exception):
    """Excepción para detener la propagación de updates."""
    pass


def require_auth(func: Callable) -> Callable:
    """
    Decorador para requerir autenticación en un handler.
    Usa async UserQueryRepository en lugar de sync UserService.
    """
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        if not update.effective_user:
            return

        chat_id = update.effective_user.id
        db_manager = context.bot_data.get("db_manager")
        if not db_manager:
            logger.error("db_manager no encontrado en bot_data")
            await update.message.reply_text("Error de configuración del sistema.")
            return

        try:
            repo = UserQueryRepository(db_manager)
            user = await repo.get_by_chat_id(chat_id)

            if not user:
                await update.message.reply_text(
                    "No estás registrado en el sistema.\n\nUsa /register para registrarte."
                )
                return

            if not user.is_verified:
                await update.message.reply_text(
                    "Tu cuenta no está verificada.\n\nUsa /verify <codigo>."
                )
                return

            if not user.is_active:
                await update.message.reply_text(
                    "Tu cuenta está inactiva. Contacta al administrador."
                )
                return

            context.user_data["telegram_user"] = user
            await repo.update_last_activity(chat_id)
            return await func(update, context, *args, **kwargs)

        except Exception as e:
            logger.error(f"Error en require_auth para chat_id={chat_id}: {e}")
            await update.message.reply_text("Error al verificar tu autenticación.")
            return

    return wrapper
