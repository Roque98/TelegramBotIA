"""
AgentOrchestrator - Rutea consultas al agente correcto según el intent.

Flujo:
  1. Carga agentes activos desde BD vía AgentConfigService
  2. IntentClassifier (nano LLM) selecciona el agente por nombre
  3. AgentBuilder construye/recupera la instancia del agente
  4. Delega al agente seleccionado
  5. Marca en response.routed_agent el nombre del agente usado

La interfaz pública (.execute()) es idéntica a ReActAgent — MainHandler
no sabe cuántos agentes existen.
"""

import datetime
import logging
import time
from typing import Any, Awaitable, Callable, Optional

from src.agents.base.agent import AgentResponse
from src.agents.base.agent_events import AgentEvent
from src.agents.base.events import UserContext
from src.agents.factory.agent_builder import AgentBuilder
from src.domain.agent_config.agent_config_entity import AgentDefinition
from src.domain.agent_config.agent_config_service import AgentConfigService
from src.domain.cost.cost_tracker import CostTracker, reset_current_tracker, set_current_tracker

from .intent_classifier import IntentClassifier

logger = logging.getLogger(__name__)


class AgentConfigException(Exception):
    """Excepción cuando la configuración de agentes está en estado inválido."""
    pass


class AgentOrchestrator:
    """
    Orquestador N-way: selecciona el agente dinámicamente desde BD.

    Expone la misma interfaz que ReActAgent (.execute()) para ser transparente
    al resto del pipeline.

    Example:
        >>> orchestrator = AgentOrchestrator(
        ...     agent_config_service=service,
        ...     agent_builder=builder,
        ...     intent_classifier=IntentClassifier(nano_llm),
        ... )
        >>> response = await orchestrator.execute("¿cuántas ventas ayer?", context)
    """

    def __init__(
        self,
        agent_config_service: AgentConfigService,
        agent_builder: AgentBuilder,
        intent_classifier: IntentClassifier,
    ) -> None:
        self.agent_config_service = agent_config_service
        self.agent_builder = agent_builder
        self.intent_classifier = intent_classifier

    async def execute(
        self,
        query: str,
        context: UserContext,
        event_callback: Optional[Callable[[AgentEvent], Awaitable[None]]] = None,
        **kwargs: Any,
    ) -> AgentResponse:
        """
        Clasifica el intent, selecciona el agente y delega la ejecución.

        Args:
            query: Consulta del usuario
            context: Contexto del usuario
            event_callback: Callback para eventos del agente (StatusMessage)

        Returns:
            AgentResponse del agente seleccionado, con routed_agent indicando
            el nombre del agente que respondió.
        """
        t_config = time.perf_counter()
        t_config_dt = datetime.datetime.utcnow()
        try:
            definitions = self.agent_config_service.get_active_agents()
        except AgentConfigException as e:
            logger.error(f"AgentConfigException en orchestrator: {e}")
            return AgentResponse.error_response(
                agent_name="orchestrator",
                error="Servicio temporalmente no disponible. Por favor reintentá más tarde.",
            )
        config_ms = int((time.perf_counter() - t_config) * 1000)

        t0 = time.perf_counter()
        t0_dt = datetime.datetime.utcnow()
        classify_tracker = CostTracker()
        _classify_token = set_current_tracker(classify_tracker)
        try:
            classify_result = await self.intent_classifier.classify(query, definitions)
        finally:
            reset_current_tracker(_classify_token)
        classify_ms = int((time.perf_counter() - t0) * 1000)

        classify_turn = classify_tracker.turns[0] if classify_tracker.turns else None
        classify_tokens_in  = classify_turn.input_tokens  if classify_turn else None
        classify_tokens_out = classify_turn.output_tokens if classify_turn else None
        classify_cost_usd   = classify_turn.cost_usd      if classify_turn else None

        try:
            definition, used_fallback = self._resolve(classify_result.agent_name, definitions)
        except AgentConfigException as e:
            logger.error(f"AgentConfigException en orchestrator: {e}")
            return AgentResponse.error_response(
                agent_name="orchestrator",
                error="Servicio temporalmente no disponible. Por favor reintentá más tarde.",
            )

        logger.info(
            f"Orchestrator: '{query[:50]}' → '{definition.nombre}' "
            f"(classify={classify_ms}ms, confidence={classify_result.confidence}, "
            f"fallback={used_fallback})"
        )

        t_build = time.perf_counter()
        t_build_dt = datetime.datetime.utcnow()
        agent = self.agent_builder.build(definition)
        build_ms = int((time.perf_counter() - t_build) * 1000)

        response = await agent.execute(
            query=query,
            context=context,
            event_callback=event_callback,
            **kwargs,
        )

        response.routed_agent = definition.nombre
        response.classify_ms = classify_ms
        response.agent_confidence = classify_result.confidence
        response.used_fallback = used_fallback or classify_result.used_fallback

        if response.data is not None:
            config_step = {
                "tipo": "config_load",
                "nombre": "AgentConfigService",
                "entrada": None,
                "salida": f"{len(definitions)} agentes activos",
                "tokensIn": None,
                "tokensOut": None,
                "costoUSD": None,
                "duracionMs": config_ms,
                "fechaInicio": t_config_dt,
            }
            classifier_step = {
                "tipo": "llm_call",
                "nombre": getattr(self.intent_classifier.llm, "model", "classifier"),
                "entrada": query[:4000],
                "salida": classify_result.agent_name,
                "tokensIn": classify_tokens_in,
                "tokensOut": classify_tokens_out,
                "costoUSD": classify_cost_usd,
                "duracionMs": classify_ms,
                "fechaInicio": t0_dt,
            }
            build_step = {
                "tipo": "agent_build",
                "nombre": definition.nombre,
                "entrada": None,
                "salida": f"v{definition.version} cache={'hit' if build_ms < 5 else 'miss'}",
                "tokensIn": None,
                "tokensOut": None,
                "costoUSD": None,
                "duracionMs": build_ms,
                "fechaInicio": t_build_dt,
            }
            existing = response.data.get("step_traces") or []
            all_steps = [config_step, classifier_step, build_step] + existing
            for i, step in enumerate(all_steps):
                step["stepNum"] = i
            response.data["step_traces"] = all_steps

            cost_summary = response.data.get("cost")
            if cost_summary and classify_turn:
                cost_summary["input_tokens"]  = (cost_summary.get("input_tokens")  or 0) + classify_tokens_in
                cost_summary["output_tokens"] = (cost_summary.get("output_tokens") or 0) + classify_tokens_out
                cost_summary["cost_usd"]      = round(
                    (cost_summary.get("cost_usd") or 0.0) + classify_cost_usd, 6
                )
                cost_summary["llm_calls"]     = (cost_summary.get("llm_calls") or 0) + 1
                if cost_summary.get("model") and cost_summary["model"] != "mixed":
                    cost_summary["model"] = "mixed"

        return response

    def _resolve(
        self, agent_name: str, definitions: list[AgentDefinition]
    ) -> tuple[AgentDefinition, bool]:
        """
        Resuelve la definición del agente por nombre, con fallback al generalista.

        Returns:
            Tupla (AgentDefinition, used_fallback).

        Raises:
            AgentConfigException: Si no hay agente generalista activo en BD
        """
        for d in definitions:
            if d.nombre == agent_name:
                return d, False

        for d in definitions:
            if d.es_generalista:
                logger.info(
                    f"Orchestrator: agente '{agent_name}' no encontrado, "
                    f"usando generalista como fallback"
                )
                return d, True

        raise AgentConfigException(
            "No hay agente generalista activo en la configuración de BD. "
            "Verificar BotIAv2_AgenteDef (esGeneralista=1, activo=1)."
        )

    async def health_check(self) -> bool:
        """Verifica que hay al menos un agente activo (incluyendo el generalista)."""
        try:
            definitions = self.agent_config_service.get_active_agents()
            has_generalista = any(d.es_generalista for d in definitions)
            if not has_generalista:
                logger.warning("health_check: sin agente generalista activo")
            return len(definitions) > 0 and has_generalista
        except Exception as e:
            logger.error(f"health_check error: {e}")
            return False
