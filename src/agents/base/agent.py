"""
Base Agent - Contrato base para el agente ReAct.

Este módulo define:
- AgentResponse: Modelo Pydantic de respuesta estándar
- BaseAgent: Clase abstracta base
"""

from abc import ABC, abstractmethod
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any, Optional

from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from .events import UserContext


class AgentResponse(BaseModel):
    """
    Respuesta estándar del agente.

    Attributes:
        success: Si la operación fue exitosa
        message: Mensaje de respuesta para el usuario
        data: Datos adicionales (opcional)
        error: Mensaje de error si success=False
        agent_name: Nombre del agente que generó la respuesta
        execution_time_ms: Tiempo de ejecución en milisegundos
        steps_taken: Número de iteraciones del loop ReAct
        metadata: Datos adicionales de contexto
    """

    success: bool
    message: Optional[str] = None
    data: Optional[dict[str, Any]] = None
    error: Optional[str] = None
    agent_name: str
    execution_time_ms: float = 0
    steps_taken: int = 1
    metadata: dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    routed_agent: Optional[str] = None        # Nombre del agente seleccionado por el orquestador
    classify_ms: Optional[int] = None         # Latencia del IntentClassifier (ms)
    agent_confidence: Optional[float] = None  # Confianza del clasificador (0.0–1.0)
    used_fallback: bool = False               # True si se usó generalista como fallback
    llm_iteraciones: Optional[int] = None     # Iteraciones LLM dentro del loop ReAct

    model_config = {"frozen": False}

    @classmethod
    def success_response(
        cls,
        agent_name: str,
        message: str,
        data: Optional[dict[str, Any]] = None,
        execution_time_ms: float = 0,
        steps_taken: int = 1,
        metadata: Optional[dict[str, Any]] = None,
    ) -> "AgentResponse":
        """
        Factory method para crear respuesta exitosa.

        Args:
            agent_name: Nombre del agente
            message: Mensaje de respuesta
            data: Datos adicionales
            execution_time_ms: Tiempo de ejecución
            steps_taken: Pasos tomados
            metadata: Metadata adicional

        Returns:
            AgentResponse con success=True
        """
        return cls(
            success=True,
            message=message,
            agent_name=agent_name,
            data=data,
            execution_time_ms=execution_time_ms,
            steps_taken=steps_taken,
            metadata=metadata or {},
        )

    @classmethod
    def error_response(
        cls,
        agent_name: str,
        error: str,
        execution_time_ms: float = 0,
        steps_taken: int = 0,
        metadata: Optional[dict[str, Any]] = None,
    ) -> "AgentResponse":
        """
        Factory method para crear respuesta de error.

        Args:
            agent_name: Nombre del agente
            error: Mensaje de error
            execution_time_ms: Tiempo de ejecución
            steps_taken: Pasos tomados antes del error
            metadata: Metadata adicional

        Returns:
            AgentResponse con success=False
        """
        return cls(
            success=False,
            error=error,
            agent_name=agent_name,
            execution_time_ms=execution_time_ms,
            steps_taken=steps_taken,
            metadata=metadata or {},
        )


class BaseAgent(ABC):
    """
    Contrato base para el agente ReAct.

    Attributes:
        name: Nombre único del agente
    """

    name: str

    @abstractmethod
    async def execute(
        self,
        query: str,
        context: "UserContext",
        **kwargs: Any,
    ) -> AgentResponse:
        """
        Ejecuta la lógica del agente.

        Args:
            query: Consulta del usuario
            context: Contexto del usuario (memoria, roles, etc.)
            **kwargs: Argumentos adicionales

        Returns:
            AgentResponse con el resultado de la ejecución
        """
        pass

    async def health_check(self) -> bool:
        """
        Verifica que el agente esté funcionando correctamente.

        Returns:
            True si el agente está saludable
        """
        return True

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(name={self.name})>"
