"""
Pipeline Package.

Coordina el flujo de conversación:
  mensaje → Gateway → Memory → AgentOrchestrator → respuesta

La construcción de dependencias vive en src/bootstrap/.
"""


def __getattr__(name: str):
    """Lazy imports para evitar dependencias pesadas en tiempo de importación."""
    if name == "MainHandler":
        from .handler import MainHandler
        return MainHandler
    elif name in ("HandlerManager", "get_handler_manager"):
        from . import handler_manager
        return getattr(handler_manager, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    "MainHandler",
    "HandlerManager",
    "get_handler_manager",
]
