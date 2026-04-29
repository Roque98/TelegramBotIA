"""
factory — Ensamblador principal del bot.

Responsabilidad única: orquestar la construcción del MainHandler
coordinando los módulos especializados de factory.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any, Optional

from src.infra.database.registry import DatabaseRegistry
from src.domain.knowledge import KnowledgeService
from src.domain.auth.permission_repository import PermissionRepository
from src.domain.interaction.interaction_repository import InteractionRepository
from src.domain.cost.cost_repository import CostRepository
from src.domain.auth.user_query_repository import UserQueryRepository
from src.agents.providers.openai_provider import OpenAIProvider
from src.infra.observability.logging_config import get_sql_handler
from src.infra.notifications.admin_notifier import fire_admin_notify
from src.config.settings import settings

from src.pipeline.handler import MainHandler
from .service_factory import create_permission_service, create_memory_service
from .tool_factory import create_tool_registry
from .orchestrator_factory import create_agent_orchestrator

logger = logging.getLogger(__name__)


def create_main_handler(
    db_manager: Any = None,
) -> tuple[MainHandler, Any, DatabaseRegistry]:
    """Ensambla el MainHandler con todas sus dependencias."""
    from src.infra.database.connection import DatabaseManager
    db = db_manager or DatabaseManager()

    db_registry = DatabaseRegistry.from_settings()

    try:
        knowledge_manager = KnowledgeService(db_manager=db)
        logger.info(f"KnowledgeService created: {len(knowledge_manager.knowledge_base)} entries loaded")
    except Exception as e:
        logger.warning(f"KnowledgeService creation failed, knowledge search disabled: {e}")
        knowledge_manager = None

    permission_service = create_permission_service(db_manager=db)
    memory_service = create_memory_service(db_manager=db, permission_service=permission_service)

    if not settings.openai_api_key:
        raise ValueError("No se encontró OPENAI_API_KEY en la configuración")

    data_llm = OpenAIProvider(api_key=settings.openai_api_key, model=settings.openai_data_model)

    active_tool_names: Optional[list[str]] = None
    try:
        perm_repo = PermissionRepository(db_manager=db)
        active_tool_names = asyncio.run(perm_repo.get_active_tool_names())
        logger.info(f"Tools activas en BD: {active_tool_names}")
    except Exception as e:
        logger.warning(f"No se pudieron obtener tools activas de BD, usando fallback completo: {e}")

    tool_registry = create_tool_registry(
        db_manager=db,
        knowledge_manager=knowledge_manager,
        memory_service=memory_service,
        permission_service=permission_service,
        bot_token=settings.telegram_bot_token,
        data_llm=data_llm,
        agent_config_service=None,
        db_registry=db_registry,
        active_tool_names=active_tool_names,
    )

    orchestrator, agent_config_service = create_agent_orchestrator(
        db_manager=db,
        tool_registry=tool_registry,
        data_llm=data_llm,
    )

    reload_tool = tool_registry.get("reload_agent_config")
    if reload_tool is not None:
        reload_tool.set_agent_config_service(agent_config_service)
        logger.info("ReloadAgentConfigTool: agent_config_service inyectado")

    obs_repo = InteractionRepository(db_manager=db)
    cost_repo = CostRepository(db_manager=db)

    sql_handler = get_sql_handler()
    if sql_handler:
        sql_handler.set_repository(obs_repo)
        logger.info("SqlLogHandler wired to InteractionRepository")

    _user_query_repo = UserQueryRepository(db_manager=db)

    async def _get_admin_ids() -> list[int]:
        return await _user_query_repo.get_admin_chat_ids()

    def admin_notify(bot: Any, *, level: str = "ERROR", error: Optional[BaseException] = None, message: str = "", user_info: str = "desconocido") -> None:
        fire_admin_notify(bot, _get_admin_ids, level=level, error=error, user_info=user_info, message=message)

    handler = MainHandler(
        react_agent=orchestrator,
        memory_service=memory_service,
        observability_repo=obs_repo,
        cost_repository=cost_repo,
        admin_notifier=admin_notify,
        user_query_repo=_user_query_repo,
    )

    logger.info("MainHandler created with AgentOrchestrator (ARQ-35 dynamic N-way)")
    return handler, admin_notify, db_registry
