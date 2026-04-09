"""
Factory - Construcción de MainHandler con todas sus dependencias.

Proporciona funciones factory para crear el handler principal
con todas las dependencias configuradas.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, Optional

from src.agents.react.agent import ReActAgent
from src.agents.tools.registry import ToolRegistry
from src.agents.tools.database_tool import DatabaseTool
from src.infra.database.registry import DatabaseRegistry
from src.agents.tools.knowledge_tool import KnowledgeTool
from src.agents.tools.calculate_tool import CalculateTool
from src.agents.tools.datetime_tool import DateTimeTool
from src.agents.tools.preference_tool import SavePreferenceTool
from src.agents.tools.save_memory_tool import SaveMemoryTool
from src.agents.tools.reload_permissions_tool import ReloadPermissionsTool
from src.agents.tools.reload_agent_config_tool import ReloadAgentConfigTool
from src.agents.tools.read_attachment_tool import ReadAttachmentTool
from src.agents.providers.openai_provider import OpenAIProvider
from src.agents.factory.agent_builder import AgentBuilder
from src.agents.orchestrator.orchestrator import AgentOrchestrator
from src.agents.orchestrator.intent_classifier import IntentClassifier
from src.domain.agent_config.agent_config_repository import AgentConfigRepository
from src.domain.agent_config.agent_config_service import AgentConfigService
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
    data_llm: Optional[Any] = None,
    agent_config_service: Optional[Any] = None,
    db_registry: Optional[DatabaseRegistry] = None,
) -> ToolRegistry:
    """Crea y configura el registro de herramientas."""
    ToolRegistry.reset()
    registry = ToolRegistry()

    # Preferir DatabaseRegistry (multi-DB) sobre db_manager legacy
    db_source = db_registry if db_registry is not None else db_manager
    registry.register(DatabaseTool(db_manager=db_source, llm_provider=data_llm))
    if knowledge_manager is not None:
        registry.register(KnowledgeTool(knowledge_manager=knowledge_manager))
    else:
        logger.warning("KnowledgeTool not registered: no KnowledgeService available")
    registry.register(CalculateTool())
    registry.register(DateTimeTool())
    registry.register(SavePreferenceTool(db_manager=db_manager, memory_service=memory_service))
    registry.register(SaveMemoryTool(memory_service=memory_service))
    registry.register(ReloadPermissionsTool(permission_service=permission_service))
    registry.register(ReloadAgentConfigTool(agent_config_service=agent_config_service))
    token = bot_token or settings.telegram_bot_token
    if token:
        registry.register(ReadAttachmentTool(bot_token=token))

    logger.info(f"ToolRegistry created with {len(registry)} tools")
    return registry


def create_react_agent(
    db_manager: Optional[Any] = None,
    knowledge_manager: Optional[Any] = None,
    memory_service: Optional[Any] = None,
    permission_service: Optional[Any] = None,
    bot_token: Optional[str] = None,
) -> ReActAgent:
    """
    Crea el agente ReAct con sus dependencias (sin orquestador dinámico).

    - loop_llm (gpt-5.4-mini): reasoning + selección de tools
    - data_llm (gpt-5.4): generación de SQL dentro de DatabaseTool
    """
    if not settings.openai_api_key:
        raise ValueError("No se encontró OPENAI_API_KEY en la configuración")

    loop_llm = OpenAIProvider(api_key=settings.openai_api_key, model=settings.openai_loop_model)
    data_llm  = OpenAIProvider(api_key=settings.openai_api_key, model=settings.openai_data_model)

    tool_registry = create_tool_registry(
        db_manager, knowledge_manager, memory_service, permission_service,
        bot_token or settings.telegram_bot_token,
        data_llm=data_llm,
    )
    agent = ReActAgent(
        llm=loop_llm,
        tool_registry=tool_registry,
        max_iterations=10,
        temperature=0.1,
    )
    logger.info(f"ReActAgent created (loop={settings.openai_loop_model}, data={settings.openai_data_model})")
    return agent


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


def create_agent_orchestrator(
    db_manager: Any,
    tool_registry: ToolRegistry,
    data_llm: Any,
) -> AgentOrchestrator:
    """
    Crea el orquestador dinámico N-way (ARQ-35).

    Wiring:
        AgentConfigRepository → AgentConfigService
        AgentBuilder (tool_registry, api_key)
        IntentClassifier (nano_llm)
        AgentOrchestrator (service, builder, classifier)

    Inyección tardía: agent_config_service.set_builder(agent_builder)
    para evitar dependencia circular en el constructor del service.

    Raises:
        RuntimeError: Si no hay agentes activos o falta el generalista al startup.
    """
    if not settings.openai_api_key:
        raise ValueError("No se encontró OPENAI_API_KEY en la configuración")

    # Dominio
    agent_config_repo = AgentConfigRepository(db_manager=db_manager)
    agent_config_service = AgentConfigService(repository=agent_config_repo)

    # Builder (sin service aún — dependencia circular)
    agent_builder = AgentBuilder(
        tool_registry=tool_registry,
        openai_api_key=settings.openai_api_key,
    )

    # Inyección tardía para que invalidate_cache() pueda limpiar ambos caches
    agent_config_service.set_builder(agent_builder)

    # Classifier usa el modelo más barato disponible
    nano_llm = OpenAIProvider(
        api_key=settings.openai_api_key,
        model=settings.openai_loop_model,
    )
    intent_classifier = IntentClassifier(llm=nano_llm)

    orchestrator = AgentOrchestrator(
        agent_config_service=agent_config_service,
        agent_builder=agent_builder,
        intent_classifier=intent_classifier,
    )

    # ── Validación de startup ──────────────────────────────────────────────
    # Verificar que hay al menos un agente activo con generalista.
    # Mejor fallar rápido en startup que descubrirlo en producción.
    agents = agent_config_service.get_active_agents()
    if not agents:
        raise RuntimeError(
            "No hay agentes activos en BotIAv2_AgenteDef. "
            "Ejecutar la migración ARQ-35 y verificar que activo=1 en los agentes."
        )
    if not any(a.es_generalista for a in agents):
        raise RuntimeError(
            "No hay agente generalista activo en BotIAv2_AgenteDef. "
            "Verificar que esGeneralista=1 y activo=1 para el agente 'generalista'."
        )

    logger.info(
        f"AgentOrchestrator creado con {len(agents)} agentes activos: "
        f"{[a.nombre for a in agents]}"
    )
    return orchestrator, agent_config_service


def create_main_handler(
    db_manager: Optional[Any] = None,
) -> MainHandler:
    """Crea el handler principal con todas sus dependencias."""
    from src.infra.database.connection import DatabaseManager
    db = db_manager or DatabaseManager()

    # DB-37: DatabaseRegistry para multi-conexión
    db_registry = DatabaseRegistry.from_settings()

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

    if not settings.openai_api_key:
        raise ValueError("No se encontró OPENAI_API_KEY en la configuración")

    data_llm = OpenAIProvider(api_key=settings.openai_api_key, model=settings.openai_data_model)

    # Crear ToolRegistry sin agent_config_service primero
    # (se actualizará tras crear el orchestrator)
    tool_registry = create_tool_registry(
        db_manager=db,
        knowledge_manager=knowledge_manager,
        memory_service=memory_service,
        permission_service=permission_service,
        bot_token=settings.telegram_bot_token,
        data_llm=data_llm,
        agent_config_service=None,  # Se inyecta abajo
        db_registry=db_registry,    # DB-37: multi-database registry
    )

    # Crear orquestador dinámico
    orchestrator, agent_config_service = create_agent_orchestrator(
        db_manager=db,
        tool_registry=tool_registry,
        data_llm=data_llm,
    )

    # Actualizar la tool de recarga con el service ya construido
    reload_tool = tool_registry.get("reload_agent_config")
    if reload_tool is not None:
        reload_tool._agent_config_service = agent_config_service
        logger.info("ReloadAgentConfigTool: agent_config_service inyectado")

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

    logger.info("MainHandler created with AgentOrchestrator (ARQ-35 dynamic N-way)")
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
