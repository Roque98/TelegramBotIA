"""
Cost Tracker - Seguimiento de tokens y costo USD por sesión de agente.

Usa contextvars para ser async-safe: múltiples usuarios concurrentes
cada uno tiene su propio tracker independiente.

Uso típico:
    tracker = CostTracker()
    token = set_current_tracker(tracker)
    try:
        response = await agent.execute(query, context)
        print(tracker.get_summary())
    finally:
        reset_current_tracker(token)
"""

import contextvars
import logging
from dataclasses import dataclass, field
from typing import Any, Optional

logger = logging.getLogger(__name__)

# Precios por modelo (USD por token)
# Fuente: https://platform.openai.com/docs/pricing
_MODEL_PRICING: dict[str, dict[str, float]] = {
    # gpt-5 family
    "gpt-5-mini": {"input": 1.10 / 1_000_000, "output": 4.40 / 1_000_000},
    "gpt-5-nano-2025-08-07": {"input": 0.10 / 1_000_000, "output": 0.40 / 1_000_000},
    # gpt-4o family
    "gpt-4o": {"input": 2.50 / 1_000_000, "output": 10.00 / 1_000_000},
    "gpt-4o-mini": {"input": 0.15 / 1_000_000, "output": 0.60 / 1_000_000},
    "gpt-4o-mini-2024-07-18": {"input": 0.15 / 1_000_000, "output": 0.60 / 1_000_000},
}
_DEFAULT_PRICING = {"input": 1.00 / 1_000_000, "output": 4.00 / 1_000_000}

# ContextVar para tracking async-safe
_current_tracker: contextvars.ContextVar[Optional["CostTracker"]] = contextvars.ContextVar(
    "cost_tracker", default=None
)


@dataclass
class TurnCost:
    """Costo de una llamada individual al LLM."""
    model: str
    input_tokens: int = 0
    output_tokens: int = 0
    cache_read_tokens: int = 0
    cost_usd: float = 0.0


@dataclass
class CostTracker:
    """
    Acumula tokens y costo USD de todas las llamadas LLM en una sesión.

    Thread-safe via contextvars — cada request asyncio tiene su propio tracker.
    """
    turns: list[TurnCost] = field(default_factory=list)

    def add_turn(self, model: str, usage: Any) -> None:
        """
        Registra el uso de tokens de una llamada al LLM.

        Args:
            model: Nombre del modelo usado
            usage: Objeto usage de la respuesta OpenAI
        """
        if usage is None:
            return

        input_tokens = getattr(usage, "input_tokens", 0) or 0
        output_tokens = getattr(usage, "output_tokens", 0) or 0

        # Prompt caching (input_tokens_details)
        details = getattr(usage, "input_tokens_details", None)
        cache_read = getattr(details, "cached_tokens", 0) or 0

        pricing = _MODEL_PRICING.get(model, _DEFAULT_PRICING)
        # Los cached tokens cuestan ~10% del precio normal de input
        billable_input = input_tokens - cache_read
        cost = (
            billable_input * pricing["input"]
            + cache_read * pricing["input"] * 0.1
            + output_tokens * pricing["output"]
        )

        turn = TurnCost(
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cache_read_tokens=cache_read,
            cost_usd=cost,
        )
        self.turns.append(turn)
        logger.debug(
            f"CostTracker: {model} in={input_tokens} out={output_tokens} "
            f"cache={cache_read} cost=${cost:.6f}"
        )

    @property
    def total_input_tokens(self) -> int:
        return sum(t.input_tokens for t in self.turns)

    @property
    def total_output_tokens(self) -> int:
        return sum(t.output_tokens for t in self.turns)

    @property
    def total_cache_read_tokens(self) -> int:
        return sum(t.cache_read_tokens for t in self.turns)

    @property
    def total_cost_usd(self) -> float:
        return sum(t.cost_usd for t in self.turns)

    @property
    def llm_calls(self) -> int:
        return len(self.turns)

    def get_summary(self) -> dict[str, Any]:
        """Retorna resumen serializable para guardar en metadata."""
        return {
            "llm_calls": self.llm_calls,
            "input_tokens": self.total_input_tokens,
            "output_tokens": self.total_output_tokens,
            "cache_read_tokens": self.total_cache_read_tokens,
            "cost_usd": round(self.total_cost_usd, 6),
        }


def get_current_tracker() -> Optional[CostTracker]:
    """Obtiene el tracker activo en el contexto asyncio actual."""
    return _current_tracker.get()


def set_current_tracker(tracker: CostTracker) -> contextvars.Token:
    """Activa un tracker en el contexto actual. Guarda el token para restaurar."""
    return _current_tracker.set(tracker)


def reset_current_tracker(token: contextvars.Token) -> None:
    """Restaura el contexto anterior (limpia el tracker)."""
    _current_tracker.reset(token)
