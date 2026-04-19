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
    elif name in (
        "create_main_handler",
        "create_memory_service",
        "create_tool_registry",
        "HandlerManager",
        "get_handler_manager",
    ):
        from . import factory
        return getattr(factory, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    "MainHandler",
    "create_main_handler",
    "create_memory_service",
    "create_tool_registry",
    "HandlerManager",
    "get_handler_manager",
]
