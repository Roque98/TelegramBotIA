"""
Main Handler - Orquesta el flujo de conversación.

Coordina:
- MessageGateway: Normalización de entrada
- MemoryService: Contexto del usuario
- ReActAgent: Procesamiento de consultas
"""

import asyncio
import logging
import time
from typing import Any, Awaitable, Callable, Optional, Protocol

from telegram import Update
from telegram.ext import ContextTypes

from src.agents.base.agent import AgentResponse
from src.agents.base.agent_events import AgentEvent
from src.agents.base.events import ConversationEvent, UserContext
from src.agents.react.agent import ReActAgent
from src.domain.cost.cost_entity import CostSession
from src.domain.cost.cost_repository import CostRepository
from src.domain.memory.memory_service import MemoryService
from src.gateway.message_gateway import MessageGateway
from src.infra.observability.sql_repository import ObservabilityRepository

try:
    from src.infra.observability import get_tracer
    _OBSERVABILITY_AVAILABLE = True
except ImportError:
    _OBSERVABILITY_AVAILABLE = False

logger = logging.getLogger(__name__)


class FallbackAgent(Protocol):
    """Protocolo para agente de fallback (LLMAgent existente)."""

    async def process_query(self, query: str) -> str:
        """Procesa una consulta y retorna respuesta."""
        ...


class MainHandler:
    """
    Handler principal que orquesta el flujo de conversación.

    Flujo:
    1. Gateway normaliza el input
    2. MemoryService obtiene contexto del usuario
    3. ReActAgent procesa la consulta
    4. Se registra la interacción
    5. Se retorna la respuesta

    Example:
        ```python
        handler = MainHandler(
            react_agent=agent,
            memory_service=memory,
            fallback_agent=llm_agent,  # opcional
        )
        response = await handler.handle_telegram(update, context)
        ```
    """

    def __init__(
        self,
        react_agent: ReActAgent,
        memory_service: MemoryService,
        fallback_agent: Optional[FallbackAgent] = None,
        use_fallback_on_error: bool = True,
        observability_repo: Optional[ObservabilityRepository] = None,
        cost_repository: Optional[CostRepository] = None,
    ):
        """
        Inicializa el handler.

        Args:
            react_agent: Agente ReAct para procesamiento
            memory_service: Servicio de memoria
            fallback_agent: Agente de fallback (LLMAgent existente)
            use_fallback_on_error: Si usar fallback cuando ReAct falla
            observability_repo: Repositorio para persistir trazas en SQL
            cost_repository: Repositorio para persistir costos de sesión
        """
        self.react_agent = react_agent
        self.memory = memory_service
        self.fallback_agent = fallback_agent
        self.use_fallback_on_error = use_fallback_on_error
        self.observability_repo = observability_repo
        self.cost_repo = cost_repository
        self.gateway = MessageGateway()

        logger.info(
            f"MainHandler inicializado "
            f"(fallback={'enabled' if fallback_agent else 'disabled'})"
        )

    async def handle_telegram(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        event_callback: Optional[Callable[[AgentEvent], Awaitable[None]]] = None,
        session_notes: Optional[list[str]] = None,
    ) -> str:
        """
        Procesa un mensaje de Telegram.

        Args:
            update: Update de Telegram
            context: Contexto de Telegram

        Returns:
            Respuesta para enviar al usuario
        """
        start_time = time.perf_counter()

        try:
            # 1. Normalizar input
            event = self.gateway.from_telegram(update)

            # 2. Iniciar trace aquí para que abarque StatusMessage y todo el pipeline
            tracer = None
            if _OBSERVABILITY_AVAILABLE:
                try:
                    tracer = get_tracer()
                    tracer.start_trace(
                        user_id=event.user_id,
                        channel=event.channel,
                        correlation_id=event.correlation_id,
                    )
                except Exception:
                    tracer = None

            # 3. Procesar
            response = await self._process_event(
                event, event_callback=event_callback, session_notes=session_notes
            )

            elapsed = (time.perf_counter() - start_time) * 1000
            logger.info(
                f"Telegram message processed: user={event.user_id}, "
                f"success={response.success}, time={elapsed:.0f}ms"
            )

            return response.message if response.success else self._format_error(response)

        except Exception as e:
            elapsed = (time.perf_counter() - start_time) * 1000
            logger.error(
                f"Error handling Telegram message: {e} ({elapsed:.0f}ms)",
                exc_info=True,
            )
            return self._get_error_message()

        finally:
            if _OBSERVABILITY_AVAILABLE and tracer:
                try:
                    tracer.end_trace()
                except Exception:
                    pass

    async def handle_api(
        self,
        user_id: str,
        text: str,
        session_id: Optional[str] = None,
        metadata: Optional[dict[str, Any]] = None,
    ) -> AgentResponse:
        """
        Procesa una solicitud de API.

        Args:
            user_id: ID del usuario
            text: Texto del mensaje
            session_id: ID de sesión opcional
            metadata: Metadata adicional

        Returns:
            AgentResponse con el resultado
        """
        start_time = time.perf_counter()

        try:
            # Crear evento
            event = self.gateway.from_api(
                user_id=user_id,
                text=text,
                session_id=session_id,
                metadata=metadata,
            )

            # Procesar
            response = await self._process_event(event)

            elapsed = (time.perf_counter() - start_time) * 1000
            logger.info(
                f"API request processed: user={user_id}, "
                f"success={response.success}, time={elapsed:.0f}ms"
            )

            return response

        except Exception as e:
            elapsed = (time.perf_counter() - start_time) * 1000
            logger.error(
                f"Error handling API request: {e} ({elapsed:.0f}ms)",
                exc_info=True,
            )
            return AgentResponse.error_response(
                agent_name="main_handler",
                error=str(e),
                execution_time_ms=elapsed,
            )

    async def _process_event(
        self,
        event: ConversationEvent,
        event_callback: Optional[Callable[[AgentEvent], Awaitable[None]]] = None,
        session_notes: Optional[list[str]] = None,
    ) -> AgentResponse:
        """
        Procesa un evento normalizado midiendo cada etapa del pipeline.

        Args:
            event: Evento a procesar

        Returns:
            AgentResponse con el resultado
        """
        t_start = time.perf_counter()

        # 1. Obtener contexto del usuario
        user_context = await self.memory.get_context(event.user_id)
        if session_notes:
            user_context.session_notes.extend(session_notes)
        memory_ms = int((time.perf_counter() - t_start) * 1000)

        # 2. Ejecutar ReAct Agent
        t_react = time.perf_counter()
        try:
            response = await self.react_agent.execute(
                query=event.text,
                context=user_context,
                event_callback=event_callback,
            )
        except Exception as e:
            logger.error(f"ReActAgent error: {e}", exc_info=True)
            if self.use_fallback_on_error and self.fallback_agent:
                logger.info("Using fallback agent")
                response = await self._use_fallback(event.text, user_context)
            else:
                response = AgentResponse.error_response(
                    agent_name="main_handler",
                    error=str(e),
                    execution_time_ms=0,
                )
        react_ms = int((time.perf_counter() - t_react) * 1000)

        # 3. Registrar interacción (async, no bloqueante)
        t_save = time.perf_counter()
        asyncio.create_task(self._record_interaction(event, response))
        save_ms = int((time.perf_counter() - t_save) * 1000)

        total_ms = int((time.perf_counter() - t_start) * 1000)

        # 4. Transaction trace: log de consola + SQL en background
        self._log_transaction(event, response, memory_ms, react_ms, save_ms, total_ms)
        if self.observability_repo:
            asyncio.create_task(
                self._save_transaction_trace(event, response, memory_ms, react_ms, save_ms, total_ms)
            )

        return response

    def _log_transaction(
        self,
        event: ConversationEvent,
        response: AgentResponse,
        memory_ms: int,
        react_ms: int,
        save_ms: int,
        total_ms: int,
    ) -> None:
        """Una línea de log con el flujo completo del request."""
        status = "OK" if response.success else "ERROR"
        cid = (event.correlation_id or "")[:8]
        query_preview = repr((event.text or "")[:40])
        logger.info(
            f"[{cid}] user={event.user_id} | {query_preview} | "
            f"memory:{memory_ms}ms react:{react_ms}ms save:{save_ms}ms | "
            f"{status} {total_ms}ms"
        )

    async def _save_transaction_trace(
        self,
        event: ConversationEvent,
        response: AgentResponse,
        memory_ms: int,
        react_ms: int,
        save_ms: int,
        total_ms: int,
    ) -> None:
        """Persiste la traza de transacción en SQL en background."""
        try:
            tools_used = None
            if response.data and "scratchpad" in response.data:
                steps = response.data["scratchpad"].get("steps", [])
                tools_used = list({
                    s.get("action") for s in steps
                    if s.get("action") not in (None, "finish")
                })

            await self.observability_repo.save_transaction(
                correlation_id=event.correlation_id or "",
                user_id=event.user_id,
                username=event.metadata.get("username"),
                query=event.text,
                channel=event.channel,
                memory_ms=memory_ms,
                react_ms=react_ms,
                save_ms=save_ms,
                total_ms=total_ms,
                success=response.success,
                error_message=response.error if not response.success else None,
                tools_used=tools_used,
                steps_count=response.steps_taken,
            )
        except Exception as e:
            logger.error(f"Error saving transaction trace: {e}")

    async def _use_fallback(
        self,
        query: str,
        context: UserContext,
    ) -> AgentResponse:
        """
        Usa el agente de fallback.

        Args:
            query: Consulta del usuario
            context: Contexto del usuario

        Returns:
            AgentResponse del fallback
        """
        start_time = time.perf_counter()

        try:
            message = await self.fallback_agent.process_query(query)
            elapsed = (time.perf_counter() - start_time) * 1000

            return AgentResponse.success_response(
                agent_name="fallback",
                message=message,
                execution_time_ms=elapsed,
                metadata={"used_fallback": True},
            )
        except Exception as e:
            elapsed = (time.perf_counter() - start_time) * 1000
            logger.error(f"Fallback agent error: {e}", exc_info=True)

            return AgentResponse.error_response(
                agent_name="fallback",
                error=str(e),
                execution_time_ms=elapsed,
            )

    async def _record_cost(
        self,
        user_id: str,
        cost: dict,
        steps_taken: int,
    ) -> None:
        """Persiste el costo de la sesión en CostSesiones."""
        if not self.cost_repo:
            return
        try:
            session = CostSession.from_summary(user_id, cost, steps_taken)
            await self.cost_repo.save_session(session)
        except Exception as e:
            logger.error(f"Error guardando costo de sesión: {e}")

    async def _record_interaction(
        self,
        event: ConversationEvent,
        response: AgentResponse,
    ) -> None:
        """
        Registra la interacción en memoria.

        Args:
            event: Evento original
            response: Respuesta del agente
        """
        try:
            cost = (response.data or {}).get("cost") if response.data else None
            await self.memory.record_interaction(
                user_id=event.user_id,
                query=event.text,
                response=response.message or "",
                error=response.error if not response.success else None,
                metadata={
                    "channel": event.channel,
                    "agent": response.agent_name,
                    "steps_taken": response.steps_taken,
                    "execution_time_ms": response.execution_time_ms,
                    "correlation_id": event.correlation_id,
                    "username": event.metadata.get("username"),
                },
            )
            if cost:
                asyncio.create_task(self._record_cost(event.user_id, cost, response.steps_taken))
        except Exception as e:
            logger.error(f"Error recording interaction: {e}")

    def _format_error(self, response: AgentResponse) -> str:
        """
        Formatea un error para mostrar al usuario.

        Args:
            response: Respuesta con error

        Returns:
            Mensaje formateado
        """
        return (
            "Lo siento, no pude procesar tu consulta correctamente. "
            "Por favor, intenta de nuevo o reformula tu pregunta."
        )

    def _get_error_message(self) -> str:
        """
        Retorna mensaje de error genérico.

        Returns:
            Mensaje de error
        """
        return (
            "Lo siento, ocurrió un error inesperado. "
            "Por favor, intenta de nuevo más tarde."
        )

    async def health_check(self) -> dict[str, Any]:
        """
        Verifica el estado de todos los componentes.

        Returns:
            Dict con estado de cada componente
        """
        results = {
            "gateway": True,  # Siempre disponible
            "memory": False,
            "react_agent": False,
            "fallback_agent": None,
        }

        # Verificar memoria
        try:
            results["memory"] = await self.memory.health_check()
        except Exception as e:
            logger.error(f"Memory health check failed: {e}")

        # Verificar ReAct Agent
        try:
            results["react_agent"] = await self.react_agent.health_check()
        except Exception as e:
            logger.error(f"ReAct Agent health check failed: {e}")

        # Verificar fallback si existe
        if self.fallback_agent:
            results["fallback_agent"] = True  # Asumimos que funciona

        results["healthy"] = results["memory"] and results["react_agent"]

        return results
