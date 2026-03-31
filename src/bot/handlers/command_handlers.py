"""
Handlers para comandos del bot de Telegram.

Maneja comandos básicos como /start, /help, /stats, etc.
"""
import logging
from typing import Any, List, Dict, Optional
from telegram import Update
from telegram.ext import CommandHandler, ContextTypes, Application
from src.domain.knowledge import KnowledgeRepository
from src.infra.database.connection import DatabaseManager

logger = logging.getLogger(__name__)


def _get_categories_from_db(id_rol: Optional[int] = None) -> List[Dict[str, Any]]:
    """
    Obtener categorías disponibles desde la base de datos, filtradas por rol.

    Args:
        id_rol: ID del rol del usuario para filtrar categorías (opcional)

    Returns:
        Lista de diccionarios con {name, display_name, icon, entry_count}
    """
    try:
        repository = KnowledgeRepository()
        return repository.get_categories_info(id_rol=id_rol)
    except Exception as e:
        logger.warning(f"No se pudieron cargar categorías desde BD: {e}")
        # Fallback básico
        return [
            {'name': 'PROCESOS', 'display_name': 'Procesos', 'icon': '⚙️', 'entry_count': 0},
            {'name': 'POLITICAS', 'display_name': 'Políticas', 'icon': '📋', 'entry_count': 0},
            {'name': 'FAQS', 'display_name': 'Preguntas Frecuentes', 'icon': '❓', 'entry_count': 0}
        ]


def _get_example_questions_from_db(limit: int = 4) -> List[str]:
    """
    Obtener preguntas de ejemplo desde la base de datos.

    Args:
        limit: Número de preguntas a retornar

    Returns:
        Lista de preguntas de ejemplo
    """
    try:
        repository = KnowledgeRepository()
        examples = repository.get_example_questions(limit)

        if not examples:
            # Fallback básico
            return [
                "¿Cómo solicito vacaciones?",
                "¿Cuál es el horario de trabajo?",
                "¿Cómo contacto al departamento de IT?"
            ]

        return examples
    except Exception as e:
        logger.warning(f"No se pudieron cargar ejemplos desde BD: {e}")
        # Fallback básico
        return [
            "¿Cómo solicito vacaciones?",
            "¿Cuál es el horario de trabajo?",
            "¿Cómo contacto al departamento de IT?"
        ]


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Manejar el comando /start.
    Genera el mensaje de bienvenida dinámicamente desde la BD.

    Args:
        update: Objeto de actualización de Telegram
        context: Contexto de la conversación
    """
    user = update.effective_user
    logger.info(f"Usuario {user.id} ({user.username}) ejecutó /start")

    # Obtener rol del usuario para filtrar categorías
    id_rol = None
    try:
        db_manager = context.bot_data.get('db_manager')
        if db_manager:
            from src.domain.auth import UserService
            with db_manager.get_session() as session:
                user_service = UserService(session)
                telegram_user = user_service.get_user_by_telegram_chat_id(user.id)
                if telegram_user and telegram_user.usuario:
                    id_rol = telegram_user.usuario.rol
                    logger.debug(f"Usuario tiene rol: {id_rol}")
    except Exception as e:
        logger.warning(f"No se pudo obtener rol del usuario: {e}")

    # Obtener categorías y ejemplos desde BD (filtradas por rol)
    categories = _get_categories_from_db(id_rol=id_rol)
    examples = _get_example_questions_from_db(4)

    # Construir lista de categorías
    categories_text = "\n".join([
        f"{cat['icon']} {cat['display_name']}"
        for cat in categories
        if cat.get('entry_count', 0) > 0
    ])

    # Construir ejemplos
    examples_text = "\n".join([f"• {q}" for q in examples])

    welcome_message = (
        f"¡Hola {user.first_name}! 👋 Soy **IRIS**\n\n"
        "Tu asistente del Centro de Operaciones aquí ✨\n\n"
        "Estoy para ayudarte con información sobre:\n"
        f"{categories_text}\n\n"
        "**Ejemplos de lo que puedes preguntarme:**\n"
        f"{examples_text}\n\n"
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
    Genera la guía dinámicamente desde la BD.

    Args:
        update: Objeto de actualización de Telegram
        context: Contexto de la conversación
    """
    user = update.effective_user
    logger.info(f"Usuario {user.id} ejecutó /help")

    # Obtener rol del usuario para filtrar categorías
    id_rol = None
    try:
        db_manager = context.bot_data.get('db_manager')
        if db_manager:
            from src.domain.auth import UserService
            with db_manager.get_session() as session:
                user_service = UserService(session)
                telegram_user = user_service.get_user_by_telegram_chat_id(user.id)
                if telegram_user and telegram_user.usuario:
                    id_rol = telegram_user.usuario.rol
                    logger.debug(f"Usuario tiene rol: {id_rol}")
    except Exception as e:
        logger.warning(f"No se pudo obtener rol del usuario: {e}")

    # Obtener categorías desde BD (filtradas por rol)
    categories = _get_categories_from_db(id_rol=id_rol)
    examples = _get_example_questions_from_db(6)  # Más ejemplos para /help

    # Construir sección de categorías con ejemplos
    categories_section = ""
    emoji_num = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣"]

    for idx, cat in enumerate(categories[:7]):  # Máximo 7 categorías
        if cat.get('entry_count', 0) > 0:
            categories_section += f"\n{emoji_num[idx]} **{cat['icon']} {cat['display_name']}:**\n"
            categories_section += f"   Tengo {cat['entry_count']} respuestas sobre este tema\n"

    # Construir ejemplos agrupados
    examples_text = "\n".join([f"   • {q}" for q in examples[:6]])

    help_message = (
        "**📖 Guía de Uso - IRIS te explica**\n\n"
        "Hola de nuevo! Aquí está todo lo que puedo hacer por ti ✨\n\n"
        "**Comandos Disponibles:**\n"
        "/start - Volver a la bienvenida\n"
        "/help - Mostrar esta guía\n"
        "/stats - Ver estadísticas de uso\n"
        "/ia [pregunta] - Hacer una consulta directa\n\n"
        "**Temas sobre los que puedo ayudarte:**"
        f"{categories_section}\n\n"
        "**Ejemplos de preguntas:**\n"
        f"{examples_text}\n\n"
        "**Consejos de IRIS:**\n"
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

    Muestra métricas de la sesión actual del bot (desde el último reinicio).

    Args:
        update: Objeto de actualización de Telegram
        context: Contexto de la conversación
    """
    user_id = update.effective_user.id
    logger.info(f"Usuario {user_id} ejecutó /stats")

    try:
        from src.infra.observability import get_metrics
        s = get_metrics().get_stats()

        req = s["requests"]
        lat = s["latency"].get("_total", {})
        uptime_min = int(s["uptime_seconds"] // 60)

        tools_section = ""
        if s["tools_usage"]:
            top = sorted(s["tools_usage"].items(), key=lambda x: -x[1])[:5]
            tools_section = "\n*Tools más usadas:*\n" + "\n".join(
                f"  {name}: {count}x" for name, count in top
            )

        errors_section = ""
        if s["errors_by_type"]:
            errors_section = "\n*Errores por tipo:*\n" + "\n".join(
                f"  {t}: {c}" for t, c in s["errors_by_type"].items()
            )

        stats_message = (
            "*Estadísticas — sesión actual*\n"
            f"_Uptime: {uptime_min} min_\n\n"
            f"*Requests:*\n"
            f"  Total: {req['total']}\n"
            f"  Exitosos: {req['success']} ({req['success_rate_percent']:.0f}%)\n"
            f"  Errores: {req['error']}\n"
            f"  Fallbacks: {req['fallbacks_used']}\n\n"
            f"*Latencia (total):*\n"
            f"  Promedio: {lat.get('avg_ms', 0):.0f}ms\n"
            f"  Máximo: {lat.get('max_ms', 0):.0f}ms\n"
            f"  Último: {lat.get('last_ms', 0):.0f}ms\n\n"
            f"*Pasos promedio por request:* {s['steps']['average']:.1f}\n"
            f"{tools_section}"
            f"{errors_section}"
        )
    except Exception as e:
        logger.error(f"Error obteniendo métricas: {e}")
        stats_message = "Error obteniendo estadísticas. Intenta de nuevo."

    await update.message.reply_text(stats_message, parse_mode='Markdown')


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
