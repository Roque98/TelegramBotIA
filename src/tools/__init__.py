"""
Sistema de orquestación de Tools.

Proporciona una arquitectura extensible para agregar nuevas funcionalidades
al bot de manera modular y desacoplada.
"""
from .tool_base import (
    BaseTool,
    ToolMetadata,
    ToolParameter,
    ToolResult,
    ToolCategory,
    ParameterType
)
from .tool_registry import ToolRegistry, get_registry
from .execution_context import ExecutionContext, ExecutionContextBuilder
from .tool_orchestrator import ToolOrchestrator

__all__ = [
    # Clases base
    "BaseTool",
    "ToolMetadata",
    "ToolParameter",
    "ToolResult",
    "ToolCategory",
    "ParameterType",
    # Registry
    "ToolRegistry",
    "get_registry",
    # Contexto de ejecución
    "ExecutionContext",
    "ExecutionContextBuilder",
    # Orquestador
    "ToolOrchestrator"
]

__version__ = "0.1.0"
