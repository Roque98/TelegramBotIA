"""
AgentOrchestrator - Rutea consultas al agente correcto según el intent.

Flujo:
  1. IntentClassifier (nano) determina si es casual o business_data
  2. Rutea a CasualAgent (mini) o DataAgent (gpt-5.4)
  3. Retorna AgentResponse con misma interfaz que ReActAgent

Esto permite que MainHandler no sepa nada del routing — simplemente
llama a orchestrator.execute() igual que antes.
"""

import logging
import time
from typing import Any, Awaitable, Callable, Optional

from src.agents.base.agent import AgentResponse
from src.agents.base.agent_events import AgentEvent
from src.agents.base.events import UserContext

from .intent_classifier import Intent, IntentClassifier

logger = logging.getLogger(__name__)


class AgentOrchestrator:
    """
    Orquestador que selecciona el agente óptimo por costo/calidad según el intent.

    Expone la misma interfaz que ReActAgent (.execute()) para ser transparente
    al resto del pipeline.

    Example:
        >>> orchestrator = AgentOrchestrator(
        ...     casual_agent=casual_react_agent,
        ...     data_agent=data_react_agent,
        ...     intent_classifier=IntentClassifier(nano_llm),
        ... )
        >>> response = await orchestrator.execute("hola!", user_context)
    """

    def __init__(
        self,
        casual_agent: Any,
        data_agent: Any,
        intent_classifier: IntentClassifier,
    ) -> None:
        self.casual_agent = casual_agent
        self.data_agent = data_agent
        self.intent_classifier = intent_classifier

    async def execute(
        self,
        query: str,
        context: UserContext,
        event_callback: Optional[Callable[[AgentEvent], Awaitable[None]]] = None,
        **kwargs: Any,
    ) -> AgentResponse:
        """
        Clasifica el intent y delega al agente correspondiente.

        Args:
            query: Consulta del usuario
            context: Contexto del usuario
            event_callback: Callback para eventos del agente (StatusMessage)

        Returns:
            AgentResponse del agente seleccionado
        """
        t0 = time.perf_counter()
        intent = await self.intent_classifier.classify(query)
        classify_ms = (time.perf_counter() - t0) * 1000

        if intent == Intent.BUSINESS_DATA:
            agent = self.data_agent
            agent_label = "data"
        else:
            agent = self.casual_agent
            agent_label = "casual"

        logger.info(
            f"Orchestrator: intent={intent.value} → {agent_label}_agent "
            f"(classify={classify_ms:.0f}ms)"
        )

        return await agent.execute(
            query=query,
            context=context,
            event_callback=event_callback,
            **kwargs,
        )

    async def health_check(self) -> bool:
        """Verifica que ambos agentes estén operativos."""
        casual_ok = await self.casual_agent.health_check()
        data_ok = await self.data_agent.health_check()
        return casual_ok and data_ok
