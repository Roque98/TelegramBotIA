"""
tool_factory — Construcción del catálogo y registro de tools del bot.

Responsabilidad única: saber qué tools existen, cómo instanciarlas
y cuáles registrar según lo activo en BotIAv2_Recurso.
"""

from __future__ import annotations

import logging
from typing import Any, Optional

from src.agents.tools.registry import ToolRegistry
from src.agents.tools.database_tool import DatabaseTool
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
from src.infra.database.registry import DatabaseRegistry
from src.config.settings import settings

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
    token = bot_token

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
    db_manager: Any = None,
    knowledge_manager: Any = None,
    memory_service: Any = None,
    permission_service: Any = None,
    bot_token: Optional[str] = None,
    data_llm: Any = None,
    agent_config_service: Any = None,
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
