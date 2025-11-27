"""
Handlers para comandos del bot de Telegram.

Maneja comandos básicos como /start, /help, /stats, etc.
"""
import logging
from telegram import Update
from telegram.ext import CommandHandler, ContextTypes, Application

logger = logging.getLogger(__name__)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Manejar el comando /start.

    Args:
        update: Objeto de actualización de Telegram
        context: Contexto de la conversación
    """
    user = update.effective_user
    logger.info(f"Usuario {user.id} ({user.username}) ejecutó /start")

    welcome_message = (
        f"¡Hola {user.first_name}! 👋\n\n"
        "Soy tu **asistente de base de datos inteligente**.\n\n"
        "Puedo ayudarte a:\n"
        "• Consultar datos en lenguaje natural\n"
        "• Traducir tus preguntas a SQL\n"
        "• Obtener información de la base de datos\n\n"
        "**Ejemplos de consultas:**\n"
        "- ¿Cuántos usuarios hay?\n"
        "- Muéstrame los últimos 5 pedidos\n"
        "- ¿Cuál es el producto más vendido?\n\n"
        "**Comandos disponibles:**\n"
        "/help - Ver ayuda detallada\n"
        "/stats - Ver estadísticas de uso\n\n"
        "¡Escribe tu pregunta y empecemos! 🚀"
    )

    await update.message.reply_text(
        welcome_message,
        parse_mode='Markdown'
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Manejar el comando /help.

    Args:
        update: Objeto de actualización de Telegram
        context: Contexto de la conversación
    """
    user_id = update.effective_user.id
    logger.info(f"Usuario {user_id} ejecutó /help")

    help_message = (
        "**📖 Guía de Uso**\n\n"
        "**Comandos Disponibles:**\n"
        "/start - Iniciar el bot y ver bienvenida\n"
        "/help - Mostrar esta ayuda\n"
        "/stats - Ver estadísticas de uso\n\n"
        "**Cómo hacer consultas:**\n\n"
        "1️⃣ **Consultas a la base de datos:**\n"
        "   Escribe preguntas en lenguaje natural sobre tus datos:\n"
        "   • ¿Cuántos registros hay en la tabla usuarios?\n"
        "   • Muéstrame las ventas del último mes\n"
        "   • Lista los productos más vendidos\n\n"
        "2️⃣ **Preguntas generales:**\n"
        "   También puedo responder preguntas generales:\n"
        "   • ¿Qué es SQL?\n"
        "   • ¿Cómo funciona una base de datos?\n"
        "   • Explícame qué es un índice\n\n"
        "**Consejos:**\n"
        "✅ Sé específico en tus preguntas\n"
        "✅ Menciona nombres de tablas si los conoces\n"
        "✅ Puedes pedir ejemplos de datos\n\n"
        "**Seguridad:**\n"
        "🔒 Solo se permiten consultas de lectura (SELECT)\n"
        "🔒 No se pueden modificar datos\n\n"
        "¿Necesitas más ayuda? Contáctanos en: soporte@ejemplo.com"
    )

    await update.message.reply_text(
        help_message,
        parse_mode='Markdown'
    )


async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Manejar el comando /stats.

    Muestra estadísticas de uso del bot (placeholder por ahora).

    Args:
        update: Objeto de actualización de Telegram
        context: Contexto de la conversación
    """
    user_id = update.effective_user.id
    logger.info(f"Usuario {user_id} ejecutó /stats")

    # TODO: Implementar estadísticas reales cuando se tenga el sistema de logging
    stats_message = (
        "**📊 Estadísticas de Uso**\n\n"
        "🔄 Consultas realizadas: N/A\n"
        "✅ Consultas exitosas: N/A\n"
        "❌ Consultas con error: N/A\n"
        "⏱️ Tiempo promedio: N/A\n\n"
        "_Sistema de estadísticas en desarrollo_"
    )

    await update.message.reply_text(
        stats_message,
        parse_mode='Markdown'
    )


async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Manejar el comando /cancel.

    Cancela la operación actual (útil para flujos conversacionales).

    Args:
        update: Objeto de actualización de Telegram
        context: Contexto de la conversación
    """
    user_id = update.effective_user.id
    logger.info(f"Usuario {user_id} ejecutó /cancel")

    await update.message.reply_text(
        "Operación cancelada. ¿En qué más puedo ayudarte?",
        parse_mode='Markdown'
    )


def register_command_handlers(application: Application) -> None:
    """
    Registrar todos los command handlers en la aplicación.

    Args:
        application: Aplicación de Telegram
    """
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("stats", stats_command))
    application.add_handler(CommandHandler("cancel", cancel_command))

    logger.info("Command handlers registrados exitosamente")
