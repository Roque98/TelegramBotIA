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

from src.domain.auth.user_query_repository import UserQueryRepository
from src.utils.status_message import StatusMessage

if TYPE_CHECKING:
    from src.pipeline.handler import MainHandler

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
        telegram_user = context.user_data.get("telegram_user")

        if not telegram_user:
            db_manager = context.bot_data.get("db_manager")
            if not db_manager:
                await update.message.reply_text("❌ Error de configuración del sistema.")
                return

            repo = UserQueryRepository(db_manager)
            telegram_user = await repo.get_by_chat_id(chat_id)

            if not telegram_user:
                await update.message.reply_text(
                    "⚠️ No estás registrado en el sistema.\n\nUsa /register para registrarte."
                )
                return

            if not telegram_user.is_verified:
                await update.message.reply_text(
                    "⚠️ Tu cuenta no está verificada.\n\n"
                    "Consulta tu código en el Portal de Consola de Monitoreo.\n"
                    "Luego usa: /verify <codigo>"
                )
                return

            if not telegram_user.is_active:
                await update.message.reply_text(
                    "⚠️ Tu cuenta está inactiva. Contacta al administrador."
                )
                return

            context.user_data["telegram_user"] = telegram_user

        logger.info(
            f"Usuario {telegram_user.id_usuario} ({telegram_user.nombre_completo}): "
            f"{user_message[:50]}..."
        )

        db_manager = context.bot_data.get("db_manager")

        async with StatusMessage(update, initial_message="🔍 Amber analizando tu consulta...") as status:
            try:
                async def on_agent_event(event):
                    await status.set_phase(event.status_text)

                response = await self.main_handler.handle_telegram(
                    update, context, event_callback=on_agent_event
                )
                await status.complete(response)

                duration_ms = int((time.time() - start_time) * 1000)
                logger.info(
                    f"Respuesta enviada exitosamente a usuario {telegram_user.id_usuario} "
                    f"({duration_ms}ms)"
                )

            except Exception as e:
                duration_ms = int((time.time() - start_time) * 1000)
                logger.error(
                    f"Error procesando mensaje de usuario {telegram_user.id_usuario} "
                    f"({duration_ms}ms): {e}",
                    exc_info=True
                )

                error_msg = (
                    "Lo siento, ocurrió un error al procesar tu consulta. "
                    "Por favor, intenta de nuevo o reformula tu pregunta.\n\n"
                    "Si el problema persiste, usa /help para más información."
                )
                await status.error(error_msg)
                raise


    async def handle_document_message(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
    ):
        """
        Manejar documentos/archivos enviados por el usuario.

        Obtiene los metadatos del archivo desde Telegram, los inyecta como
        session_notes y delega al MainHandler igual que un mensaje de texto.
        """
        doc = update.message.document
        if not doc:
            return

        user = update.effective_user
        chat_id = user.id
        telegram_user = context.user_data.get("telegram_user")

        if not telegram_user:
            db_manager = context.bot_data.get("db_manager")
            if not db_manager:
                await update.message.reply_text("❌ Error de configuración del sistema.")
                return
            from src.domain.auth.user_query_repository import UserQueryRepository
            repo = UserQueryRepository(db_manager)
            telegram_user = await repo.get_by_chat_id(chat_id)
            if not telegram_user or not telegram_user.is_verified or not telegram_user.is_active:
                await update.message.reply_text(
                    "⚠️ No podés enviar archivos hasta tener la cuenta verificada y activa."
                )
                return
            context.user_data["telegram_user"] = telegram_user

        # Obtener metadatos del archivo desde Telegram
        try:
            tg_file = await context.bot.get_file(doc.file_id)
        except Exception as e:
            logger.error(f"Error obteniendo file info de Telegram: {e}")
            await update.message.reply_text("❌ No pude acceder al archivo. Por favor, intenta de nuevo.")
            return

        name = doc.file_name or "archivo"
        size_kb = (doc.file_size or 0) // 1024
        file_path = tg_file.file_path
        caption = update.message.caption or "Por favor analiza este archivo."

        # Nota de sesión para que ReadAttachmentTool lo encuentre
        session_notes = [
            f"[ATTACHMENT:{doc.file_id}] name={name} size={size_kb}KB path={file_path}"
        ]

        # Texto sintético que verá el agente
        update.message.text = (
            f"[Archivo adjunto: {name} ({size_kb}KB) — ID: {doc.file_id}]\n{caption}"
        )

        logger.info(
            f"Usuario {telegram_user.id_usuario}: archivo adjunto '{name}' ({size_kb}KB)"
        )

        async with StatusMessage(update, initial_message="📎 Procesando archivo adjunto...") as status:
            try:
                async def on_agent_event(event):
                    await status.set_phase(event.status_text)

                response = await self.main_handler.handle_telegram(
                    update, context,
                    event_callback=on_agent_event,
                    session_notes=session_notes,
                )
                await status.complete(response)
            except Exception as e:
                logger.error(f"Error procesando archivo de usuario {telegram_user.id_usuario}: {e}", exc_info=True)
                await status.error("Lo siento, ocurrió un error al procesar el archivo.")
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
    application.add_handler(
        MessageHandler(
            filters.Document.ALL,
            query_handler.handle_document_message
        )
    )

    logger.info("Query handlers registrados exitosamente (texto + documentos)")
