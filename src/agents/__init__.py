"""
Agents Package - ReAct Architecture

Arquitectura basada en un único ReAct Agent que razona y actúa.

Estructura:
- base/: Contratos base (BaseAgent, AgentResponse, UserContext)
- react/: ReAct Agent con loop Think-Act-Observe
- tools/: Herramientas (DatabaseTool, KnowledgeTool, etc.)
"""

from .base.agent import BaseAgent, AgentResponse
from .base.events import ConversationEvent, UserContext
from .base.exceptions import AgentException, ToolException, ValidationException

__all__ = [
    "BaseAgent",
    "AgentResponse",
    "ConversationEvent",
    "UserContext",
    "AgentException",
    "ToolException",
    "ValidationException",
]
