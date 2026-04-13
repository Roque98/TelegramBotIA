"""
Handlers para comandos /ia y /query.

Delegan el procesamiento al MainHandler (ReActAgent).
"""
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

from src.utils.status_message import StatusMessage

logger = logging.getLogger(__name__)


async def handle_ia_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Manejar comando /ia usando MainHandler (ReAct).

    Args:
        update: Update de Telegram
        context: Context de Telegram
    """
    message_text = update.message.text

    # Extraer la query (todo después de /ia)
    query_text = message_text.replace('/ia', '', 1).strip()

    if not query_text:
        await update.message.reply_text(
            "❓ Por favor, proporciona una consulta después de /ia\n\n"
            "*Ejemplos:*\n"
            "• `/ia ¿Cuántos usuarios hay registrados?`\n"
            "• `/ia ¿Qué es Python?`\n"
            "• `/ia Dame un resumen del sistema`",
            parse_mode='MarkdownV2'
        )
        return

    main_handler = context.bot_data.get('main_handler')
    if not main_handler:
        await update.message.reply_text(
            "❌ Error de configuración del sistema.\n\n"
            "Por favor, contacta al administrador."
        )
        logger.error("main_handler no encontrado en bot_data")
        return

    # Reemplazar el texto para que el gateway reciba solo la query (sin /ia)
    update.message.text = query_text

    async with StatusMessage(update, initial_message="🔍 Analizando tu consulta...") as status:
        async def on_agent_event(event):
            await status.set_phase(event.status_text)

        response = await main_handler.handle_telegram(update, context, event_callback=on_agent_event)
        await status.complete(response)


async def handle_query_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Manejar comando /query (alias de /ia).

    Args:
        update: Update de Telegram
        context: Context de Telegram
    """
    update.message.text = update.message.text.replace('/query', '/ia', 1)
    await handle_ia_command(update, context)


def register_tools_handlers(application: Application) -> None:
    """
    Registrar handlers del sistema de Tools.

    Args:
        application: Aplicación de Telegram
    """
    application.add_handler(CommandHandler('ia', handle_ia_command))
    application.add_handler(CommandHandler('query', handle_query_command))

    logger.info("Tools handlers registrados exitosamente (comandos: /ia, /query)")
