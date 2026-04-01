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

    Muestra estadísticas históricas del usuario desde LogOperaciones.

    Args:
        update: Objeto de actualización de Telegram
        context: Contexto de la conversación
    """
    user_id = str(update.effective_user.id)
    logger.info(f"Usuario {user_id} ejecutó /stats")

    try:
        from src.domain.memory.memory_repository import MemoryRepository

        db = context.bot_data.get("db_manager")
        repo = MemoryRepository(db_manager=db)
        s = await repo.get_user_stats(user_id)

        if not s or not s.get("total"):
            stats_message = "Aún no tenés interacciones registradas. ¡Empezá chateando conmigo! 😊"
        else:
            total = s.get("total") or 0
            exitosos = s.get("exitosos") or 0
            errores = s.get("errores") or 0
            avg_ms = s.get("avg_ms") or 0
            max_ms = s.get("max_ms") or 0
            tasa = (exitosos / total * 100) if total else 0

            primera = s.get("primera")
            ultima = s.get("ultima")
            primera_str = primera.strftime("%d/%m/%Y") if primera else "—"
            ultima_str = ultima.strftime("%d/%m/%Y %H:%M") if ultima else "—"

            stats_message = (
                "*Tus estadísticas* 📊\n\n"
                f"*Consultas totales:* {total}\n"
                f"*Exitosas:* {exitosos} ({tasa:.0f}%)\n"
                f"*Errores:* {errores}\n\n"
                f"*Tiempo de respuesta:*\n"
                f"  Promedio: {avg_ms:.0f}ms\n"
                f"  Máximo: {max_ms}ms\n\n"
                f"*Primera consulta:* {primera_str}\n"
                f"*Última consulta:* {ultima_str}"
            )

    except Exception as e:
        logger.error(f"Error obteniendo estadísticas del usuario {user_id}: {e}")
        stats_message = "Error obteniendo estadísticas. Intenta de nuevo."

    try:
        await update.message.reply_text(stats_message, parse_mode='Markdown')
    except Exception:
        await update.message.reply_text(stats_message)


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


async def costo_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Manejar el comando /costo — solo para admins.

    Muestra tokens y costo USD acumulado del día/mes por usuario,
    extraído del campo parametros JSON de LogOperaciones.
    """
    from src.config.settings import settings

    chat_id = update.effective_user.id
    if settings.admin_chat_ids and chat_id not in settings.admin_chat_ids:
        await update.message.reply_text("⛔ No tienes permiso para usar este comando.")
        return

    db_manager = context.bot_data.get("db_manager")
    if not db_manager:
        await update.message.reply_text("❌ Base de datos no disponible.")
        return

    try:
        query = """
            SELECT
                cs.telegramChatId                                       AS chat_id,
                COALESCE(u.Nombre, ut.telegramUsername, 'Desconocido') AS nombre,
                COUNT(*)                                                AS sesiones,
                SUM(cs.llamadasLLM)                                    AS llamadas,
                SUM(cs.inputTokens)                                    AS input_tokens,
                SUM(cs.outputTokens)                                   AS output_tokens,
                SUM(cs.costoUSD)                                       AS costo_usd
            FROM abcmasplus..CostSesiones cs
            LEFT JOIN abcmasplus..UsuariosTelegram ut ON cs.telegramChatId = ut.telegramChatId
            LEFT JOIN abcmasplus..Usuarios u ON ut.idUsuario = u.idUsuario
            WHERE cs.fechaSesion >= CAST(GETDATE() AS DATE)
            GROUP BY cs.telegramChatId, u.Nombre, ut.telegramUsername
            ORDER BY costo_usd DESC
        """
        rows = await db_manager.execute_query_async(query)

        if not rows:
            await update.message.reply_text("_Sin datos de costo para hoy._", parse_mode="Markdown")
            return

        lines = ["*Costo del día por usuario* 💸\n"]
        total_usd = 0.0
        for row in rows:
            nombre = row.get("nombre", "?")
            sesiones = row.get("sesiones", 0)
            llamadas = row.get("llamadas") or 0
            inp = row.get("input_tokens") or 0
            out = row.get("output_tokens") or 0
            usd = row.get("costo_usd") or 0.0
            total_usd += usd
            lines.append(
                f"• *{nombre}*: {sesiones} sesiones | {llamadas} llamadas LLM | "
                f"{inp+out:,} tokens | `${usd:.4f}`"
            )

        lines.append(f"\n*Total: ${total_usd:.4f}*")
        await update.message.reply_text("\n".join(lines), parse_mode="Markdown")

    except Exception as e:
        logger.error(f"Error en /costo: {e}")
        await update.message.reply_text("❌ Error consultando datos de costo.")


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
    application.add_handler(CommandHandler("costo", costo_command))

    logger.info("Command handlers registrados exitosamente")
