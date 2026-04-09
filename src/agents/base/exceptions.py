"""
Exceptions - Excepciones específicas del sistema de agentes.

Este módulo define excepciones personalizadas para manejar
errores de manera consistente en todo el sistema.
"""

from typing import Any, Optional


class AgentException(Exception):
    """
    Excepción base para errores del agente.

    Attributes:
        message: Mensaje de error
        agent_name: Nombre del agente que generó el error
        details: Detalles adicionales del error
    """

    def __init__(
        self,
        message: str,
        agent_name: Optional[str] = None,
        details: Optional[dict[str, Any]] = None,
    ):
        self.message = message
        self.agent_name = agent_name
        self.details = details or {}
        super().__init__(self.message)

    def __str__(self) -> str:
        if self.agent_name:
            return f"[{self.agent_name}] {self.message}"
        return self.message


class ToolException(AgentException):
    """
    Excepción para errores en la ejecución de herramientas.

    Attributes:
        tool_name: Nombre de la herramienta que falló
        action_input: Input que causó el error
    """

    def __init__(
        self,
        message: str,
        tool_name: str,
        action_input: Optional[dict[str, Any]] = None,
        details: Optional[dict[str, Any]] = None,
    ):
        self.tool_name = tool_name
        self.action_input = action_input
        super().__init__(
            message=message,
            agent_name=f"Tool:{tool_name}",
            details={
                **(details or {}),
                "tool_name": tool_name,
                "action_input": action_input,
            },
        )


class ValidationException(AgentException):
    """
    Excepción para errores de validación.

    Attributes:
        field: Campo que falló la validación
        value: Valor que causó el error
    """

    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        value: Optional[Any] = None,
        details: Optional[dict[str, Any]] = None,
    ):
        self.field = field
        self.value = value
        super().__init__(
            message=message,
            details={
                **(details or {}),
                "field": field,
                "value": value,
            },
        )


class MaxIterationsException(AgentException):
    """
    Excepción cuando el agente excede el máximo de iteraciones.

    Attributes:
        max_iterations: Límite de iteraciones configurado
        steps_taken: Pasos que se ejecutaron
    """

    def __init__(
        self,
        max_iterations: int,
        steps_taken: int,
        partial_result: Optional[str] = None,
    ):
        self.max_iterations = max_iterations
        self.steps_taken = steps_taken
        self.partial_result = partial_result
        super().__init__(
            message=f"Se excedió el máximo de {max_iterations} iteraciones",
            agent_name="ReActAgent",
            details={
                "max_iterations": max_iterations,
                "steps_taken": steps_taken,
                "partial_result": partial_result,
            },
        )


class LLMException(AgentException):
    """
    Excepción para errores del LLM.

    Attributes:
        provider: Proveedor del LLM (openai, anthropic, etc.)
        status_code: Código de estado HTTP si aplica
    """

    def __init__(
        self,
        message: str,
        provider: Optional[str] = None,
        status_code: Optional[int] = None,
        details: Optional[dict[str, Any]] = None,
    ):
        self.provider = provider
        self.status_code = status_code
        super().__init__(
            message=message,
            agent_name=f"LLM:{provider}" if provider else "LLM",
            details={
                **(details or {}),
                "provider": provider,
                "status_code": status_code,
            },
        )
