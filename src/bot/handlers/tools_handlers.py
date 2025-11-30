"""
Handlers que integran el sistema de Tools con Telegram.

Conecta los comandos de Telegram con el ToolOrchestrator para ejecutar
tools de manera consistente y orquestada.
"""
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from src.tools import (
    get_registry,
    ToolOrchestrator,
    ExecutionContextBuilder
)
from src.utils.status_message import StatusMessage
from src.auth import PermissionChecker, UserManager

logger = logging.getLogger(__name__)


async def handle_ia_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Manejar comando /ia usando el sistema de Tools.

    Args:
        update: Update de Telegram
        context: Context de Telegram
    """
    user_id = update.effective_user.id
    message_text = update.message.text

    # Extraer la query (todo después de /ia)
    query_text = message_text.replace('/ia', '').strip()

    if not query_text:
        await update.message.reply_text(
            "❓ Por favor, proporciona una consulta después de /ia\n\n"
            "**Ejemplos:**\n"
            "• `/ia ¿Cuántos usuarios hay registrados?`\n"
            "• `/ia ¿Qué es Python?`\n"
            "• `/ia Dame un resumen del sistema`",
            parse_mode='Markdown'
        )
        return

    # Obtener componentes del bot_data
    db_manager = context.bot_data.get('db_manager')
    llm_agent = context.bot_data.get('agent')

    if not db_manager or not llm_agent:
        await update.message.reply_text(
            "❌ Error de configuración del sistema.\n"
            "Por favor, contacta al administrador."
        )
        logger.error("db_manager o agent no encontrados en bot_data")
        return

    # Crear mensaje de estado
    status_msg = StatusMessage(update, initial_message="🔍 Analizando tu consulta...")
    await status_msg.start()

    try:
        # Obtener registry y crear orquestador
        registry = get_registry()
        orchestrator = ToolOrchestrator(registry)

        # Construir contexto de ejecución con todos los componentes
        with db_manager.get_session() as session:
            user_manager = UserManager(session)
            permission_checker = PermissionChecker(session)

            exec_context = (
                ExecutionContextBuilder()
                .with_telegram(update, context)
                .with_db_manager(db_manager)
                .with_llm_agent(llm_agent)
                .with_user_manager(user_manager)
                .with_permission_checker(permission_checker)
                .build()
            )

            # Ejecutar comando a través del orquestador
            result = await orchestrator.execute_command(
                user_id=user_id,
                command="/ia",
                params={"query": query_text},
                context=exec_context
            )

            # Completar con resultado o error
            if result.success:
                await status_msg.complete(result.data)

                logger.info(
                    f"Comando /ia ejecutado exitosamente para usuario {user_id} "
                    f"en {result.execution_time_ms:.2f}ms"
                )
            else:
                error_msg = result.user_friendly_error or result.error
                await status_msg.error(error_msg)
                logger.warning(f"Comando /ia falló para usuario {user_id}: {result.error}")

    except Exception as e:
        logger.error(f"Error en handle_ia_command: {e}", exc_info=True)
        await status_msg.error(
            "Ocurrió un error al procesar tu consulta"
        )


async def handle_query_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Manejar comando /query (alias de /ia).

    Args:
        update: Update de Telegram
        context: Context de Telegram
    """
    # Reemplazar /query por /ia y delegar
    update.message.text = update.message.text.replace('/query', '/ia', 1)
    await handle_ia_command(update, context)


def register_tools_handlers(application: Application) -> None:
    """
    Registrar handlers del sistema de Tools.

    Args:
        application: Aplicación de Telegram
    """
    # Handler para comando /ia
    application.add_handler(
        CommandHandler('ia', handle_ia_command)
    )

    # Handler para comando /query (alias)
    application.add_handler(
        CommandHandler('query', handle_query_command)
    )

    logger.info(
        "Tools handlers registrados exitosamente "
        "(comandos: /ia, /query)"
    )
