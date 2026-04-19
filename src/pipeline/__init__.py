"""
Pipeline Package.

Orquestación del flujo de conversación y construcción de dependencias:
- MainHandler: Coordina MessageGateway → Memory → ReActAgent
- Factory functions: Construcción e inicialización de componentes
"""


def __getattr__(name: str):
    """Lazy imports para evitar dependencias pesadas en tiempo de importación."""
    if name == "MainHandler":
        from .handler import MainHandler
        return MainHandler
    elif name == "create_main_handler":
        from .factory import create_main_handler
        return create_main_handler
    elif name == "create_tool_registry":
        from .tool_factory import create_tool_registry
        return create_tool_registry
    elif name == "create_memory_service":
        from .service_factory import create_memory_service
        return create_memory_service
    elif name in ("HandlerManager", "get_handler_manager"):
        from . import handler_manager
        return getattr(handler_manager, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    "MainHandler",
    "create_main_handler",
    "create_memory_service",
    "create_tool_registry",
    "HandlerManager",
    "get_handler_manager",
]
