"""
DashboardHandler — despacha callbacks dash:* al renderizado correcto.

Flujo por callback:
  1. query.answer() inmediato (evita spinner infinito)
  2. Auth guard: verifica admin (cacheado en user_data)
  3. Construye DashboardService con las deps de bot_data
  4. Renderiza la vista y edita el mensaje
"""
import logging

from telegram import Update
from telegram.error import BadRequest
from telegram.ext import Application, CallbackQueryHandler, ContextTypes

from src.domain.auth.user_query_repository import UserQueryRepository
from .dashboard_service import DashboardService
from .views import (
    render_agents,
    render_alerts,
    render_knowledge,
    render_logs,
    render_menu,
    render_overview,
    render_users,
)

logger = logging.getLogger(__name__)


class DashboardHandler:

    async def handle(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        query = update.callback_query

        # 1. Responder siempre primero — evita spinner infinito en el botón
        await query.answer()

        data = query.data or ""
        if data == "dash:noop":
            return

        # 2. Auth guard (cacheado en user_data para no hacer query en cada pulsación)
        chat_id = update.effective_user.id
        is_admin = context.user_data.get("is_admin")
        if is_admin is None:
            db_manager = context.bot_data.get("db_manager")
            repo = UserQueryRepository(db_manager)
            try:
                admin_ids = await repo.get_admin_chat_ids()
                is_admin = chat_id in admin_ids
            except Exception as e:
                logger.error(f"DashboardHandler: error verificando admin: {e}")
                is_admin = False
            context.user_data["is_admin"] = is_admin

        if not is_admin:
            await _edit(query, "⛔ Solo administradores pueden usar el dashboard.")
            return

        # 3. Dispatch
        parts = data.split(":")  # ["dash", "overview", "hoy"]
        section = parts[1] if len(parts) > 1 else ""

        db_manager = context.bot_data.get("db_manager")
        db_registry = context.bot_data.get("db_registry")
        service = DashboardService(db_manager, db_registry)

        try:
            text, keyboard = await _dispatch(section, parts, service)
        except Exception as e:
            logger.error(f"DashboardHandler [{data}]: {e}", exc_info=True)
            await _edit(query, "❌ Error al cargar datos. Intenta de nuevo.")
            return

        context.user_data["dash_current_view"] = data
        await _edit(query, text, keyboard, parse_mode="HTML")


async def _dispatch(section: str, parts: list[str], service: DashboardService):
    if section == "menu":
        return render_menu()

    if section == "overview":
        periodo = parts[2] if len(parts) > 2 else "hoy"
        data = await service.get_overview(periodo)
        return render_overview(data, periodo)

    if section == "alerts":
        data = await service.get_alerts()
        return render_alerts(data)

    if section == "logs":
        page = int(parts[2]) if len(parts) > 2 and parts[2].isdigit() else 1
        data = await service.get_logs(page)
        return render_logs(data)

    if section == "agents":
        data = await service.get_agents()
        return render_agents(data)

    if section == "users":
        data = await service.get_users()
        return render_users(data)

    if section == "knowledge":
        data = await service.get_knowledge()
        return render_knowledge(data)

    return render_menu()


async def _edit(query, text: str, keyboard=None, parse_mode: str | None = None) -> None:
    try:
        await query.edit_message_text(text, reply_markup=keyboard, parse_mode=parse_mode)
    except BadRequest as e:
        if "Message is not modified" not in str(e):
            logger.warning(f"DashboardHandler edit_message_text: {e}")


def register_dashboard_handlers(application: Application) -> None:
    handler = DashboardHandler()
    application.add_handler(
        CallbackQueryHandler(handler.handle, pattern=r"^dash:")
    )
    logger.info("Dashboard handler registrado (patrón: ^dash:)")
