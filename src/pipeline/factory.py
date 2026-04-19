"""
Factory - Construcción de MainHandler con todas sus dependencias.

Proporciona funciones factory para crear el handler principal
con todas las dependencias configuradas.
"""

from __future__ import annotations

import asyncio
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
from src.agents.tools.get_active_alerts_tool import GetActiveAlertsTool
from src.agents.tools.get_historical_tickets_tool import GetHistoricalTicketsTool
from src.agents.tools.get_escalation_matrix_tool import GetEscalationMatrixTool
from src.agents.tools.get_alert_detail_tool import GetAlertDetailTool
from src.agents.tools.get_template_by_id_tool import GetTemplateByIdTool
from src.agents.tools.get_contacto_gerencia_tool import GetContactoGerenciaTool
from src.agents.tools.get_inventory_by_ip_tool import GetInventoryByIpTool
from src.agents.tools.alert_analysis_tool import AlertAnalysisTool
from src.domain.alerts.alert_repository import AlertRepository
from src.agents.providers.openai_provider import OpenAIProvider
from src.pipeline.agent_factory.agent_builder import AgentBuilder
from src.pipeline.orchestrator.orchestrator import AgentOrchestrator
from src.pipeline.orchestrator.intent_classifier import IntentClassifier
from src.domain.agent_config.agent_config_repository import AgentConfigRepository
from src.domain.agent_config.agent_config_service import AgentConfigService
from src.domain.knowledge import KnowledgeService
from src.config.settings import settings
from src.domain.auth.permission_repository import PermissionRepository
from src.domain.auth.permission_service import PermissionService
from src.domain.cost.cost_repository import CostRepository
from src.domain.memory.memory_service import MemoryService
from src.domain.memory.memory_repository import MemoryRepository
from src.domain.interaction.interaction_repository import InteractionRepository
from src.infra.observability.logging_config import get_sql_handler
from src.infra.notifications.admin_notifier import fire_admin_notify
from src.domain.auth.user_query_repository import UserQueryRepository

from .handler import MainHandler

if TYPE_CHECKING:
    from src.infra.database.connection import DatabaseManager

logger = logging.getLogger(__name__)


def _build_tool_catalog(
    db_manager: Any,
    knowledge_manager: Any,
    memory_service: Any,
    permission_service: Any,
    agent_config_service: Any,
    data_llm: Any,
    db_registry: Any,
    bot_token: Optional[str],
) -> dict[str, Any]:
    """
    Catálogo completo de tools disponibles en el codebase.

    La clave coincide exactamente con el sufijo del campo `recurso` en
    BotIAv2_Recurso (formato 'tool:<clave>'). Solo se instancian las tools
    cuya clave aparezca en BotIAv2_Recurso con activo=1 — el resto se ignora.

    Para agregar una tool nueva a un proyecto:
      1. Crear la clase en src/agents/tools/
      2. Añadir una entrada aquí
      3. INSERT en BotIAv2_Recurso del proyecto con activo=1
    """
    db_source = db_registry if db_registry is not None else db_manager
    token = bot_token  # None → se omite; el caller decide si pasar settings.telegram_bot_token

    def _monitoreo_repo() -> Optional[AlertRepository]:
        if db_registry is not None and db_registry.is_configured("monitoreo"):
            return AlertRepository(db_registry.get("monitoreo"))
        return None

    return {
        "database_query":    lambda: DatabaseTool(db_manager=db_source, llm_provider=data_llm) if (db_source and data_llm) else None,
        "knowledge_search":  lambda: KnowledgeTool(knowledge_manager=knowledge_manager) if knowledge_manager else None,
        "calculate":         lambda: CalculateTool(),
        "datetime":          lambda: DateTimeTool(),
        "save_preference":   lambda: SavePreferenceTool(db_manager=db_manager, memory_service=memory_service),
        "save_memory":       lambda: SaveMemoryTool(memory_service=memory_service),
        "reload_permissions":    lambda: ReloadPermissionsTool(permission_service=permission_service),
        "reload_agent_config":   lambda: ReloadAgentConfigTool(agent_config_service=agent_config_service),
        "read_attachment":        lambda: ReadAttachmentTool(bot_token=token) if token else None,
        "get_active_alerts":      lambda: GetActiveAlertsTool(repo=r) if (r := _monitoreo_repo()) else None,
        "get_historical_tickets": lambda: GetHistoricalTicketsTool(repo=r) if (r := _monitoreo_repo()) else None,
        "get_escalation_matrix":  lambda: GetEscalationMatrixTool(repo=r) if (r := _monitoreo_repo()) else None,
        "get_alert_detail":       lambda: GetAlertDetailTool(repo=r) if (r := _monitoreo_repo()) else None,
        "get_template_by_id":     lambda: GetTemplateByIdTool(repo=r) if (r := _monitoreo_repo()) else None,
        "get_contacto_gerencia":  lambda: GetContactoGerenciaTool(repo=r) if (r := _monitoreo_repo()) else None,
        "get_inventory_by_ip":    lambda: GetInventoryByIpTool(repo=r) if (r := _monitoreo_repo()) else None,
        "alert_analysis":         lambda: AlertAnalysisTool(repo=r, llm=data_llm) if ((r := _monitoreo_repo()) and data_llm) else None,
    }


def create_tool_registry(
    db_manager: Optional[Any] = None,
    knowledge_manager: Optional[Any] = None,
    memory_service: Optional[Any] = None,
    permission_service: Optional[Any] = None,
    bot_token: Optional[str] = None,
    data_llm: Optional[Any] = None,
    agent_config_service: Optional[Any] = None,
    db_registry: Optional[DatabaseRegistry] = None,
    active_tool_names: Optional[list[str]] = None,
) -> ToolRegistry:
    """
    Crea y configura el registro de herramientas según lo activo en BotIAv2_Recurso.

    Si `active_tool_names` es None (no se pudo consultar la BD), registra
    todas las tools disponibles como fallback para no romper el arranque.
    """
    ToolRegistry.reset()
    registry = ToolRegistry()

    # Resolver token: argumento explícito tiene prioridad, luego settings
    resolved_token = bot_token or settings.telegram_bot_token

    catalog = _build_tool_catalog(
        db_manager=db_manager,
        knowledge_manager=knowledge_manager,
        memory_service=memory_service,
        permission_service=permission_service,
        agent_config_service=agent_config_service,
        data_llm=data_llm,
        db_registry=db_registry,
        bot_token=resolved_token,
    )

    if active_tool_names is None:
        # Fallback: registrar todo el catálogo (BD no disponible en startup)
        logger.warning("ToolRegistry: no se pudo consultar BD — registrando todas las tools del catálogo")
        names_to_register = list(catalog.keys())
    else:
        names_to_register = active_tool_names

    for name in names_to_register:
        factory_fn = catalog.get(name)
        if factory_fn is None:
            logger.warning(f"ToolRegistry: '{name}' está activo en BD pero no existe en el catálogo — ignorado")
            continue
        tool = factory_fn()
        if tool is None:
            logger.warning(f"ToolRegistry: '{name}' no pudo instanciarse (dependencia faltante) — ignorado")
            continue
        registry.register(tool)

    logger.info(f"ToolRegistry creado con {len(registry)} tools: {list(registry._tools.keys())}")
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
) -> tuple[MainHandler, Any]:
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

    # Consultar BD para saber qué tools están activas en este proyecto
    active_tool_names: Optional[list[str]] = None
    try:
        perm_repo = PermissionRepository(db_manager=db)
        active_tool_names = asyncio.run(
            perm_repo.get_active_tool_names()
        )
        logger.info(f"Tools activas en BD: {active_tool_names}")
    except Exception as e:
        logger.warning(f"No se pudieron obtener tools activas de BD, usando fallback completo: {e}")

    # Crear ToolRegistry basado en lo activo en BotIAv2_Recurso
    tool_registry = create_tool_registry(
        db_manager=db,
        knowledge_manager=knowledge_manager,
        memory_service=memory_service,
        permission_service=permission_service,
        bot_token=settings.telegram_bot_token,
        data_llm=data_llm,
        agent_config_service=None,  # Se inyecta abajo
        db_registry=db_registry,    # DB-37: multi-database registry
        active_tool_names=active_tool_names,
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

    obs_repo = InteractionRepository(db_manager=db)
    cost_repo = CostRepository(db_manager=db)

    sql_handler = get_sql_handler()
    if sql_handler:
        sql_handler.set_repository(obs_repo)
        logger.info("SqlLogHandler wired to InteractionRepository")

    # AdminNotifier: get_admin_ids se resuelve en factory para que fire_admin_notify
    # no dependa de domain — la función queda capturada por closure.
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
    )

    logger.info("MainHandler created with AgentOrchestrator (ARQ-35 dynamic N-way)")
    return handler, admin_notify, db_registry


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
            self._handler, _, __ = create_main_handler(db_manager)
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
