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
        f"¡Hola {user.first_name}! 👋 Soy **Amber**\n\n"
        "Analista del Centro de Operaciones aquí ✨\n\n"
        "Estoy para ayudarte con:\n"
        "📊 Consultas de datos en lenguaje natural\n"
        "🔍 Información de la base de datos\n"
        "💡 Conocimiento sobre políticas y procesos\n\n"
        "**Ejemplos de lo que puedes preguntarme:**\n"
        "• ¿Cuántos usuarios hay registrados?\n"
        "• Muéstrame las ventas del último mes\n"
        "• ¿Cómo solicito vacaciones?\n"
        "• ¿Cuál es el horario de atención?\n\n"
        "**Comandos disponibles:**\n"
        "/help - Ver guía completa\n"
        "/stats - Estadísticas de uso\n\n"
        "¿En qué puedo ayudarte hoy? 🎯"
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
        "**📖 Guía de Uso - Amber te explica**\n\n"
        "Hola de nuevo! Aquí está todo lo que puedo hacer por ti ✨\n\n"
        "**Comandos Disponibles:**\n"
        "/start - Volver a la bienvenida\n"
        "/help - Mostrar esta guía\n"
        "/stats - Ver estadísticas de uso\n"
        "/ia [pregunta] - Hacer una consulta directa\n\n"
        "**Cómo hacer consultas:**\n\n"
        "1️⃣ **Consultas de datos:**\n"
        "   Pregúntame en lenguaje natural sobre datos:\n"
        "   • ¿Cuántos usuarios hay registrados?\n"
        "   • Muéstrame las ventas de este mes\n"
        "   • Lista los productos más vendidos\n\n"
        "2️⃣ **Información empresarial:**\n"
        "   Pregúntame sobre políticas y procesos:\n"
        "   • ¿Cómo solicito vacaciones?\n"
        "   • ¿Cuál es el horario de trabajo?\n"
        "   • ¿Dónde encuentro el manual de usuario?\n\n"
        "3️⃣ **Preguntas generales:**\n"
        "   También puedo ayudarte con conceptos:\n"
        "   • ¿Qué es una base de datos?\n"
        "   • Explícame qué significa SQL\n\n"
        "**Consejos de Amber:**\n"
        "✅ Sé específico, me ayuda a ayudarte mejor\n"
        "✅ Puedo trabajar con lenguaje natural, no necesitas saber SQL\n"
        "✅ Si algo no está claro, pregúntame de nuevo\n\n"
        "**Seguridad:**\n"
        "🔒 Solo consulto datos (no los modifico)\n"
        "🔒 Tus consultas son seguras y validadas\n\n"
        "¿Algo más en lo que pueda ayudarte? 💡"
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
        "Aquí van tus métricas ✨\n\n"
        "🔄 Consultas realizadas: N/A\n"
        "✅ Consultas exitosas: N/A\n"
        "❌ Consultas con error: N/A\n"
        "⏱️ Tiempo promedio: N/A\n\n"
        "🚧 _Estoy trabajando en el sistema de estadísticas completo_\n"
        "_Pronto tendrás métricas detalladas!_ 💪"
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
        "✅ Operación cancelada.\n\n¿En qué más puedo ayudarte? 💡",
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
