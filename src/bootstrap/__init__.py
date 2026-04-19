"""
bootstrap — Composition Root del bot.

Único lugar donde se ensamblan todas las dependencias del sistema.
El resto del código solo recibe lo que necesita, sin saber cómo se construye.
"""

from .factory import create_main_handler
from .tool_factory import create_tool_registry
from .service_factory import create_permission_service, create_memory_service
from .orchestrator_factory import create_agent_orchestrator

__all__ = [
    "create_main_handler",
    "create_tool_registry",
    "create_permission_service",
    "create_memory_service",
    "create_agent_orchestrator",
]
