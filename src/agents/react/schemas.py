"""
ReAct Schemas - Modelos de datos para el agente ReAct.

Este módulo define:
- ActionType: Enum de acciones disponibles
- ReActStep: Modelo de un paso del loop
- ReActResponse: Respuesta del LLM en cada iteración
"""

from datetime import UTC, datetime
from typing import Any, Optional

from pydantic import BaseModel, Field
from pydantic_core import core_schema


class ActionType:
    """
    Representa una acción del agente ReAct: un tool registrado o FINISH.

    Ya no es un Enum fijo — valida contra el set de tools activos que
    el agente pasa en cada llamada a from_string(), de modo que cualquier
    tool registrado en ToolRegistry es una acción válida sin tocar este archivo.
    """

    FINISH = "finish"

    # Aliases independientes del catálogo de tools
    _ALIASES: dict[str, str] = {
        "db": "database_query",
        "database": "database_query",
        "query": "database_query",
        "sql": "database_query",
        "knowledge": "knowledge_search",
        "kb": "knowledge_search",
        "search": "knowledge_search",
        "calc": "calculate",
        "math": "calculate",
        "date": "datetime",
        "time": "datetime",
        "preference": "save_preference",
        "save_pref": "save_preference",
        "set_preference": "save_preference",
        "memory": "save_memory",
        "save_mem": "save_memory",
        "remember": "save_memory",
        "done": "finish",
        "end": "finish",
        "answer": "finish",
        # Acciones de aclaración que el LLM puede inventar → redirigir a finish
        "ask": "finish",
        "ask_user": "finish",
        "clarify": "finish",
        "clarification": "finish",
        "pedir_detalle": "finish",
        "pedir_aclaracion": "finish",
        "solicitar_detalle": "finish",
        "preguntar": "finish",
        "responder": "finish",
        "respond": "finish",
        "reply": "finish",
        # OpenAI function-calling nativo — el LLM envuelve la llamada real en action_input.
        # Se manejan en _build_react_response para rescatar el tool real.
        "call_tool": "_call_tool_wrapper",
        "tool_call": "_call_tool_wrapper",
        "use_tool": "_call_tool_wrapper",
        "invoke": "_call_tool_wrapper",
        "invoke_tool": "_call_tool_wrapper",
        "function_call": "_call_tool_wrapper",
    }

    def __init__(self, value: str) -> None:
        self.value = value

    def is_final(self) -> bool:
        """Retorna True si la acción es FINISH."""
        return self.value == self.FINISH

    def is_tool(self) -> bool:
        """Retorna True si la acción es un tool (no FINISH)."""
        return not self.is_final()

    def __eq__(self, other: object) -> bool:
        if isinstance(other, ActionType):
            return self.value == other.value
        if isinstance(other, str):
            return self.value == other
        return NotImplemented

    def __hash__(self) -> int:
        return hash(self.value)

    def __str__(self) -> str:
        return self.value

    def __repr__(self) -> str:
        return f"ActionType({self.value!r})"

    @classmethod
    def from_string(
        cls,
        value: str,
        valid_tools: Optional[set[str]] = None,
    ) -> "ActionType":
        """
        Convierte un string a ActionType.

        Args:
            value: Nombre de la acción que devolvió el LLM
            valid_tools: Set de nombres de tools activos en el registry.
                Si se pasa, solo acepta esos nombres + "finish".
                Si es None, acepta cualquier string (backward compat / tests).

        Raises:
            ValueError: Si valid_tools está definido y la acción no es válida.
        """
        resolved = cls._ALIASES.get(value.lower().strip(), value.lower().strip())

        if resolved == cls.FINISH:
            return cls(cls.FINISH)

        if valid_tools is not None:
            if resolved in valid_tools:
                return cls(resolved)
            valid_list = sorted(valid_tools) + [cls.FINISH]
            raise ValueError(
                f"Unknown action: {value}. Valid actions: {valid_list}"
            )

        # Sin valid_tools: acepta cualquier string (tests y backward compat)
        return cls(resolved)

    # ── Pydantic v2 — permite usar ActionType como tipo de campo ──────────
    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: Any
    ) -> Any:
        return core_schema.no_info_plain_validator_function(
            lambda v: cls(v.lower().strip()) if isinstance(v, str) else v,
            serialization=core_schema.to_string_ser_schema(),
        )


class ReActStep(BaseModel):
    """
    Representa un paso completo del loop ReAct.

    Attributes:
        step_number: Número del paso (1-indexed)
        thought: Razonamiento del agente
        action: Acción a ejecutar
        action_input: Parámetros de la acción
        observation: Resultado de ejecutar la acción
        timestamp: Momento del paso
    """

    step_number: int
    thought: str
    action: ActionType
    action_input: dict[str, Any] = Field(default_factory=dict)
    observation: Optional[str] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))

    def to_prompt_format(self) -> str:
        """
        Genera formato para incluir en el prompt.

        Returns:
            String formateado del paso
        """
        lines = [
            f"Step {self.step_number}:",
            f"Thought: {self.thought}",
            f"Action: {self.action.value}",
            f"Action Input: {self.action_input}",
        ]

        if self.observation is not None:
            lines.append(f"Observation: {self.observation}")

        return "\n".join(lines)

    def to_dict(self) -> dict[str, Any]:
        """Convierte el paso a diccionario."""
        return {
            "step_number": self.step_number,
            "thought": self.thought,
            "action": self.action.value,
            "action_input": self.action_input,
            "observation": self.observation,
            "timestamp": self.timestamp.isoformat(),
        }


class ReActResponse(BaseModel):
    """
    Respuesta del LLM en cada iteración del loop.

    Este es el formato que esperamos del LLM cuando genera
    el siguiente paso de razonamiento.

    Attributes:
        thought: Razonamiento sobre qué hacer
        action: Acción a ejecutar
        action_input: Parámetros para la acción
        final_answer: Respuesta final (solo si action=FINISH)
    """

    thought: str = Field(
        description="Your reasoning about what to do next"
    )
    action: ActionType = Field(
        description="The action to take"
    )
    action_input: dict[str, Any] = Field(
        default_factory=dict,
        description="Parameters for the action"
    )
    final_answer: Optional[str] = Field(
        default=None,
        description="Your final answer to the user (only if action is 'finish')"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "thought": "The user is asking about sales. I need to query the database.",
                    "action": "database_query",
                    "action_input": {"query": "SELECT COUNT(*) FROM ventas"},
                    "final_answer": None,
                },
                {
                    "thought": "I have all the information I need to answer.",
                    "action": "finish",
                    "action_input": {},
                    "final_answer": "There were 150 sales yesterday.",
                },
            ]
        }
    }

    def is_final(self) -> bool:
        """Retorna True si esta es la respuesta final."""
        return self.action.is_final()

    @classmethod
    def finish(cls, thought: str, answer: str) -> "ReActResponse":
        """
        Factory para crear respuesta final.

        Args:
            thought: Razonamiento final
            answer: Respuesta al usuario

        Returns:
            ReActResponse con action=FINISH
        """
        return cls(
            thought=thought,
            action=ActionType.FINISH,
            action_input={},
            final_answer=answer,
        )

    @classmethod
    def tool_call(
        cls,
        thought: str,
        action: ActionType,
        action_input: dict[str, Any],
    ) -> "ReActResponse":
        """
        Factory para crear llamada a tool.

        Args:
            thought: Razonamiento
            action: Tool a ejecutar
            action_input: Parámetros del tool

        Returns:
            ReActResponse con la llamada al tool
        """
        if action.is_final():
            raise ValueError("Use ReActResponse.finish() for final responses")

        return cls(
            thought=thought,
            action=action,
            action_input=action_input,
        )
