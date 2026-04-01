"""
Agent Events - Eventos tipados del ciclo de vida del agente ReAct.

Permite a los callers recibir feedback en tiempo real sobre qué está
haciendo el agente: inicio, razonamiento, tool calls, respuesta final.

Uso típico:
    async def on_event(event: AgentEvent) -> None:
        await status_message.set_phase(event.status_text)

    response = await agent.execute(query, context, event_callback=on_event)
"""

from datetime import UTC, datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


class AgentEventType(str, Enum):
    SESSION_STARTED = "session_started"
    THOUGHT_GENERATED = "thought_generated"
    TOOL_CALLED = "tool_called"
    OBSERVATION_RECEIVED = "observation_received"
    FINAL_ANSWER = "final_answer"
    AGENT_ERROR = "agent_error"


class AgentEvent(BaseModel):
    """Evento emitido por el agente durante su ejecución."""

    event_type: AgentEventType
    session_id: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    metadata: dict[str, Any] = Field(default_factory=dict)

    # Texto corto listo para mostrar al usuario (ej. en StatusMessage)
    status_text: str = ""

    model_config = {"frozen": True}


def session_started_event(session_id: str, user_id: str, tool_count: int) -> AgentEvent:
    return AgentEvent(
        event_type=AgentEventType.SESSION_STARTED,
        session_id=session_id,
        status_text="⚙️ Procesando tu solicitud...",
        metadata={"user_id": user_id, "tool_count": tool_count},
    )


def thought_generated_event(session_id: str, thought: str) -> AgentEvent:
    return AgentEvent(
        event_type=AgentEventType.THOUGHT_GENERATED,
        session_id=session_id,
        status_text="🧠 Razonando...",
        metadata={"thought_preview": thought[:100]},
    )


def tool_called_event(session_id: str, tool_name: str, step: int) -> AgentEvent:
    _tool_labels = {
        "database_query": "🗄️ Consultando base de datos...",
        "knowledge_search": "📚 Buscando en el conocimiento...",
        "calculate": "🔢 Calculando...",
        "datetime": "📅 Consultando fecha/hora...",
        "get_preferences": "👤 Revisando preferencias...",
        "save_preferences": "💾 Guardando preferencias...",
    }
    status = _tool_labels.get(tool_name, f"🔧 Usando herramienta: {tool_name}...")
    return AgentEvent(
        event_type=AgentEventType.TOOL_CALLED,
        session_id=session_id,
        status_text=status,
        metadata={"tool_name": tool_name, "step": step},
    )


def observation_received_event(session_id: str, tool_name: str, success: bool) -> AgentEvent:
    status = "✅ Datos obtenidos, procesando..." if success else "⚠️ Revisando resultado..."
    return AgentEvent(
        event_type=AgentEventType.OBSERVATION_RECEIVED,
        session_id=session_id,
        status_text=status,
        metadata={"tool_name": tool_name, "success": success},
    )


def final_answer_event(session_id: str, steps_taken: int) -> AgentEvent:
    return AgentEvent(
        event_type=AgentEventType.FINAL_ANSWER,
        session_id=session_id,
        status_text="✍️ Redactando respuesta...",
        metadata={"steps_taken": steps_taken},
    )


def agent_error_event(session_id: str, error: str) -> AgentEvent:
    return AgentEvent(
        event_type=AgentEventType.AGENT_ERROR,
        session_id=session_id,
        status_text="❌ Error procesando solicitud",
        metadata={"error": error[:200]},
    )
