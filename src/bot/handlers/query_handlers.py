"""
Handlers para consultas en lenguaje natural.

Maneja mensajes de texto que no son comandos y los procesa con MainHandler (ReAct).
Requiere autenticación y validación de permisos.
"""
import logging
import time
from typing import TYPE_CHECKING

from telegram import Update
from telegram.ext import MessageHandler, filters, ContextTypes, Application

from src.auth import UserService
from src.utils.status_message import StatusMessage

if TYPE_CHECKING:
    from src.gateway.handler import MainHandler

logger = logging.getLogger(__name__)


class QueryHandler:
    """Handler para procesar consultas en lenguaje natural."""

    def __init__(self, main_handler: "MainHandler"):
        self.main_handler = main_handler
        logger.info("QueryHandler inicializado con MainHandler (ReAct)")

    async def handle_text_message(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
    ):
        """
        Manejar mensajes de texto del usuario.

        Valida autenticación y permisos antes de procesar la consulta.
        """
        user_message = update.message.text
        user = update.effective_user
        chat_id = user.id
        start_time = time.time()

        # Obtener usuario autenticado del context (lo pone el middleware de auth)
        telegram_user = context.user_data.get('telegram_user')

        if not telegram_user:
            db_manager = context.bot_data.get('db_manager')

            if not db_manager:
                await update.message.reply_text(
                    "❌ Error de configuración del sistema."
                )
                return

            with db_manager.get_session() as session:
                user_service = UserService(session)
                telegram_user = user_service.get_user_by_chat_id(chat_id)

                if not telegram_user:
                    await update.message.reply_text(
                        "⚠️ No estás registrado en el sistema.\n\n"
                        "Por favor, usa /register para registrarte."
                    )
                    return

                if not telegram_user.is_verified:
                    await update.message.reply_text(
                        "⚠️ Tu cuenta no está verificada.\n\n"
                        "Consulta tu código de verificación en el Portal de Consola de Monitoreo.\n"
                        "Luego usa: /verify <codigo>"
                    )
                    return

                if not telegram_user.is_active:
                    await update.message.reply_text(
                        "⚠️ Tu cuenta está inactiva.\n\n"
                        "Por favor, contacta al administrador."
                    )
                    return

                context.user_data['telegram_user'] = telegram_user

        logger.info(
            f"Usuario {telegram_user.id_usuario} ({telegram_user.nombre_completo}): "
            f"{user_message[:50]}..."
        )

        db_manager = context.bot_data.get('db_manager')

        # Verificar permiso para consultas con IA
        with db_manager.get_session() as session:
            user_service = UserService(session)
            permission = user_service.check_permission(
                telegram_user.id_usuario,
                '/ia'
            )

            if not permission.is_allowed:
                user_service.log_operation(
                    user_id=telegram_user.id_usuario,
                    comando='/ia',
                    telegram_chat_id=chat_id,
                    telegram_username=user.username,
                    parametros={'query': user_message[:100]},
                    resultado='DENEGADO',
                    mensaje_error=permission.mensaje
                )

                await update.message.reply_text(
                    f"🚫 *Acceso Denegado*\n\n"
                    f"No tienes permiso para realizar consultas con IA.\n\n"
                    f"_{permission.mensaje}_",
                    parse_mode='Markdown'
                )
                return

        async with StatusMessage(update, initial_message="🔍 Amber analizando tu consulta...") as status:
            try:
                response = await self.main_handler.handle_telegram(update, context)
                await status.complete(response)

                duration_ms = int((time.time() - start_time) * 1000)

                with db_manager.get_session() as session:
                    user_service = UserService(session)
                    user_service.log_operation(
                        user_id=telegram_user.id_usuario,
                        comando='/ia',
                        telegram_chat_id=chat_id,
                        telegram_username=user.username,
                        parametros={'query': user_message[:200]},
                        resultado='EXITOSO',
                        duracion_ms=duration_ms
                    )

                logger.info(
                    f"Respuesta enviada exitosamente a usuario {telegram_user.id_usuario} "
                    f"({duration_ms}ms)"
                )

            except Exception as e:
                logger.error(
                    f"Error procesando mensaje de usuario {telegram_user.id_usuario}: {e}",
                    exc_info=True
                )

                duration_ms = int((time.time() - start_time) * 1000)
                with db_manager.get_session() as session:
                    user_service = UserService(session)
                    user_service.log_operation(
                        user_id=telegram_user.id_usuario,
                        comando='/ia',
                        telegram_chat_id=chat_id,
                        telegram_username=user.username,
                        parametros={'query': user_message[:200]},
                        resultado='ERROR',
                        mensaje_error=str(e),
                        duracion_ms=duration_ms
                    )

                error_msg = (
                    "Lo siento, ocurrió un error al procesar tu consulta. "
                    "Por favor, intenta de nuevo o reformula tu pregunta.\n\n"
                    "Si el problema persiste, usa /help para más información."
                )
                await status.error(error_msg)
                raise


def register_query_handlers(application: Application, main_handler: "MainHandler") -> None:
    """
    Registrar handler de queries en la aplicación.

    Args:
        application: Aplicación de Telegram
        main_handler: MainHandler configurado con ReActAgent
    """
    query_handler = QueryHandler(main_handler)

    application.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            query_handler.handle_text_message
        )
    )

    logger.info("Query handlers registrados exitosamente")
