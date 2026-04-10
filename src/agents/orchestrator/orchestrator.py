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
        t0 = time.perf_counter()
        t0_dt = datetime.datetime.utcnow()

        try:
            # 1. Cargar agentes activos desde cache/BD
            definitions = self.agent_config_service.get_active_agents()

            # 2. Clasificar intent (retorna ClassifyResult con confianza y alternativas)
            classify_result = await self.intent_classifier.classify(query, definitions)
            classify_ms = int((time.perf_counter() - t0) * 1000)

            # 3. Resolver definición (con fallback a generalista)
            definition, used_fallback = self._resolve(classify_result.agent_name, definitions)

            logger.info(
                f"Orchestrator: '{query[:50]}' → '{definition.nombre}' "
                f"(classify={classify_ms}ms, confidence={classify_result.confidence}, "
                f"fallback={used_fallback})"
            )

            # 4. Construir / recuperar del cache la instancia del agente
            agent = self.agent_builder.build(definition)

        except AgentConfigException as e:
            logger.error(f"AgentConfigException en orchestrator: {e}")
            return AgentResponse.error_response(
                agent_name="orchestrator",
                error="Servicio temporalmente no disponible. Por favor reintentá más tarde.",
            )

        # 5. Ejecutar el agente seleccionado
        response = await agent.execute(
            query=query,
            context=context,
            event_callback=event_callback,
            **kwargs,
        )

        # 6. Registrar qué agente respondió y métricas de ruteo (para observabilidad)
        response.routed_agent = definition.nombre
        response.classify_ms = classify_ms
        response.agent_confidence = classify_result.confidence
        response.used_fallback = used_fallback or classify_result.used_fallback

        # 7. Inyectar el step del clasificador al inicio de step_traces para
        #    que el tiempo de clasificación quede reflejado en la medición total.
        if response.data is not None:
            classifier_step = {
                "stepNum": 0,
                "tipo": "llm_call",
                "nombre": getattr(self.intent_classifier.llm, "model", "classifier"),
                "entrada": query[:4000],
                "salida": classify_result.agent_name,
                "tokensIn": None,
                "tokensOut": None,
                "costoUSD": None,
                "duracionMs": classify_ms,
                "fechaInicio": t0_dt,
            }
            existing = response.data.get("step_traces") or []
            for step in existing:
                step["stepNum"] = step.get("stepNum", 0) + 1
            response.data["step_traces"] = [classifier_step] + existing

        return response

    def _resolve(
        self, agent_name: str, definitions: list[AgentDefinition]
    ) -> tuple[AgentDefinition, bool]:
        """
        Resuelve la definición del agente por nombre, con fallback al generalista.

        Args:
            agent_name: Nombre del agente seleccionado por el classifier
            definitions: Lista de agentes activos

        Returns:
            Tupla (AgentDefinition, used_fallback). used_fallback=True si se recurrió
            al generalista porque el agente clasificado no estaba en la lista activa.

        Raises:
            AgentConfigException: Si no hay agente generalista activo en BD
        """
        # Búsqueda directa por nombre
        for d in definitions:
            if d.nombre == agent_name:
                return d, False

        # Fallback al generalista
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
