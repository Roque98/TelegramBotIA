"""
Factory - Construcción de MainHandler con todas sus dependencias.

Proporciona funciones factory para crear el handler principal
con todas las dependencias configuradas.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, Optional

from src.agents.react.agent import ReActAgent
from src.agents.orchestrator import AgentOrchestrator, IntentClassifier
from src.agents.tools.registry import ToolRegistry
from src.agents.tools.database_tool import DatabaseTool
from src.agents.tools.knowledge_tool import KnowledgeTool
from src.agents.tools.calculate_tool import CalculateTool
from src.agents.tools.datetime_tool import DateTimeTool
from src.agents.tools.preference_tool import SavePreferenceTool
from src.agents.tools.save_memory_tool import SaveMemoryTool
from src.agents.tools.reload_permissions_tool import ReloadPermissionsTool
from src.agents.tools.read_attachment_tool import ReadAttachmentTool
from src.agents.providers.openai_provider import OpenAIProvider
from src.domain.knowledge import KnowledgeService
from src.config.settings import settings
from src.domain.auth.permission_repository import PermissionRepository
from src.domain.auth.permission_service import PermissionService
from src.domain.cost.cost_repository import CostRepository
from src.domain.memory.memory_service import MemoryService
from src.domain.memory.memory_repository import MemoryRepository
from src.infra.observability.sql_repository import ObservabilityRepository
from src.config.logging_config import get_sql_handler

from .handler import MainHandler

if TYPE_CHECKING:
    from src.infra.database.connection import DatabaseManager

logger = logging.getLogger(__name__)


def create_tool_registry(
    db_manager: Optional[Any] = None,
    knowledge_manager: Optional[Any] = None,
    memory_service: Optional[Any] = None,
    permission_service: Optional[Any] = None,
    bot_token: Optional[str] = None,
) -> ToolRegistry:
    """Crea y configura el registro de herramientas."""
    ToolRegistry.reset()
    registry = ToolRegistry()

    registry.register(DatabaseTool(db_manager=db_manager))
    if knowledge_manager is not None:
        registry.register(KnowledgeTool(knowledge_manager=knowledge_manager))
    else:
        logger.warning("KnowledgeTool not registered: no KnowledgeService available")
    registry.register(CalculateTool())
    registry.register(DateTimeTool())
    registry.register(SavePreferenceTool(db_manager=db_manager, memory_service=memory_service))
    registry.register(SaveMemoryTool(memory_service=memory_service))
    registry.register(ReloadPermissionsTool(permission_service=permission_service))
    token = bot_token or settings.telegram_bot_token
    if token:
        registry.register(ReadAttachmentTool(bot_token=token))

    logger.info(f"ToolRegistry created with {len(registry)} tools")
    return registry


def create_react_agent(
    llm_provider: Any,
    db_manager: Optional[Any] = None,
    knowledge_manager: Optional[Any] = None,
    memory_service: Optional[Any] = None,
    permission_service: Optional[Any] = None,
    bot_token: Optional[str] = None,
) -> ReActAgent:
    """Crea el agente ReAct con sus dependencias."""
    tool_registry = create_tool_registry(db_manager, knowledge_manager, memory_service, permission_service, bot_token)
    agent = ReActAgent(
        llm=llm_provider,
        tool_registry=tool_registry,
        max_iterations=10,
        temperature=0.1,
    )
    logger.info(f"ReActAgent created (model={llm_provider.model})")
    return agent


def create_orchestrator(
    db_manager: Optional[Any] = None,
    knowledge_manager: Optional[Any] = None,
    memory_service: Optional[Any] = None,
    permission_service: Optional[Any] = None,
) -> AgentOrchestrator:
    """
    Crea el orquestador con sus tres proveedores LLM.

    - IntentClassifier usa gpt-5.4-nano (barato, solo clasifica)
    - CasualAgent usa gpt-5.4-mini (conversación casual, preferencias)
    - DataAgent usa gpt-5.4 (queries SQL complejas, síntesis de datos)
    """
    if not settings.openai_api_key:
        raise ValueError("No se encontró OPENAI_API_KEY en la configuración")

    intent_llm = OpenAIProvider(api_key=settings.openai_api_key, model=settings.openai_intent_model)
    casual_llm = OpenAIProvider(api_key=settings.openai_api_key, model=settings.openai_casual_model)
    data_llm   = OpenAIProvider(api_key=settings.openai_api_key, model=settings.openai_data_model)

    intent_classifier = IntentClassifier(llm=intent_llm)
    casual_agent = create_react_agent(casual_llm, db_manager, knowledge_manager, memory_service, permission_service, settings.telegram_bot_token)
    data_agent   = create_react_agent(data_llm,   db_manager, knowledge_manager, memory_service, permission_service, settings.telegram_bot_token)

    orchestrator = AgentOrchestrator(
        casual_agent=casual_agent,
        data_agent=data_agent,
        intent_classifier=intent_classifier,
    )

    logger.info(
        f"AgentOrchestrator created: "
        f"intent={settings.openai_intent_model}, "
        f"casual={settings.openai_casual_model}, "
        f"data={settings.openai_data_model}"
    )
    return orchestrator


def create_permission_service(
    db_manager: Optional[Any] = None,
) -> PermissionService:
    """Crea el servicio de permisos SEC-01."""
    repository = PermissionRepository(db_manager=db_manager)
    service = PermissionService(repository=repository)
    logger.info("PermissionService created")
    return service


def create_memory_service(
    db_manager: Optional[Any] = None,
    permission_service: Optional[Any] = None,
) -> MemoryService:
    """Crea el servicio de memoria."""
    repository = MemoryRepository(db_manager=db_manager)
    service = MemoryService(
        repository=repository,
        permission_service=permission_service,
        cache_ttl_seconds=300,
        max_cache_size=1000,
        max_working_memory=10,
    )
    logger.info("MemoryService created")
    return service


def create_llm_provider() -> OpenAIProvider:
    """Crea el proveedor de LLM según la configuración (legacy — usar create_orchestrator)."""
    if not settings.openai_api_key:
        raise ValueError("No se encontró OPENAI_API_KEY en la configuración")
    return OpenAIProvider(api_key=settings.openai_api_key, model=settings.openai_model)


def create_main_handler(
    db_manager: Optional[Any] = None,
) -> MainHandler:
    """Crea el handler principal con todas sus dependencias."""
    from src.infra.database.connection import DatabaseManager
    db = db_manager or DatabaseManager()

    try:
        knowledge_manager = KnowledgeService(db_manager=db)
        logger.info(
            f"KnowledgeService created: {len(knowledge_manager.knowledge_base)} entries loaded"
        )
    except Exception as e:
        logger.warning(f"KnowledgeService creation failed, knowledge search disabled: {e}")
        knowledge_manager = None

    permission_service = create_permission_service(db_manager=db)
    memory_service = create_memory_service(db_manager=db, permission_service=permission_service)

    orchestrator = create_orchestrator(
        db_manager=db,
        knowledge_manager=knowledge_manager,
        memory_service=memory_service,
        permission_service=permission_service,
    )

    obs_repo = ObservabilityRepository(db_manager=db)
    cost_repo = CostRepository(db_manager=db)

    sql_handler = get_sql_handler()
    if sql_handler:
        sql_handler.set_repository(obs_repo)
        logger.info("SqlLogHandler wired to ObservabilityRepository")

    handler = MainHandler(
        react_agent=orchestrator,
        memory_service=memory_service,
        observability_repo=obs_repo,
        cost_repository=cost_repo,
    )

    logger.info("MainHandler created with AgentOrchestrator + ObservabilityRepository")
    return handler


class HandlerManager:
    """Gestor singleton para el MainHandler."""

    _instance: Optional["HandlerManager"] = None
    _handler: Optional[MainHandler] = None

    def __new__(cls) -> "HandlerManager":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def initialize(
        self,
        db_manager: Optional[Any] = None,
    ) -> MainHandler:
        if self._handler is None:
            self._handler = create_main_handler(db_manager)
            logger.info("HandlerManager initialized")
        return self._handler

    @property
    def handler(self) -> Optional[MainHandler]:
        return self._handler

    def is_initialized(self) -> bool:
        return self._handler is not None

    @classmethod
    def reset(cls) -> None:
        cls._instance = None
        cls._handler = None


def get_handler_manager() -> HandlerManager:
    """Obtiene la instancia del HandlerManager."""
    return HandlerManager()
