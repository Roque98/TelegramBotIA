"""
orchestrator_factory — Construcción del AgentOrchestrator dinámico (ARQ-35).

Responsabilidad única: ensamblar AgentConfigService, AgentBuilder,
IntentClassifier y AgentOrchestrator con validación de startup.
"""

from __future__ import annotations

import logging
from typing import Any

from src.agents.providers.openai_provider import OpenAIProvider
from src.agents.tools.registry import ToolRegistry
from src.pipeline.agent_factory.agent_builder import AgentBuilder
from src.pipeline.orchestrator.orchestrator import AgentOrchestrator
from src.pipeline.orchestrator.intent_classifier import IntentClassifier
from src.domain.agent_config.agent_config_repository import AgentConfigRepository
from src.domain.agent_config.agent_config_service import AgentConfigService
from src.config.settings import settings

logger = logging.getLogger(__name__)


def create_agent_orchestrator(
    db_manager: Any,
    tool_registry: ToolRegistry,
    data_llm: Any,
) -> tuple[AgentOrchestrator, AgentConfigService]:
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

    agent_config_repo = AgentConfigRepository(db_manager=db_manager)
    agent_config_service = AgentConfigService(repository=agent_config_repo)

    # Builder sin service aún — dependencia circular
    agent_builder = AgentBuilder(
        tool_registry=tool_registry,
        openai_api_key=settings.openai_api_key,
    )

    # Inyección tardía para que invalidate_cache() pueda limpiar ambos caches
    agent_config_service.set_builder(agent_builder)

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

    # Fail-fast: mejor fallar en startup que descubrirlo en producción
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
