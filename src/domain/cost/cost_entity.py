"""
Entidades del módulo de costos.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class CostSession:
    """Representa el costo de una sesión de agente persistida en BD."""

    user_id: str
    model: str
    input_tokens: int
    output_tokens: int
    cache_read_tokens: int
    llm_calls: int
    cost_usd: float
    steps: int
    correlation_id: Optional[str] = None
    fecha_sesion: datetime = field(default_factory=datetime.utcnow)

    @classmethod
    def from_summary(
        cls,
        user_id: str,
        summary: dict,
        steps: int,
        correlation_id: Optional[str] = None,
    ) -> "CostSession":
        """Construye una CostSession desde el dict retornado por CostTracker.get_summary()."""
        return cls(
            user_id=user_id,
            model=summary.get("model", "unknown"),
            input_tokens=summary.get("input_tokens", 0),
            output_tokens=summary.get("output_tokens", 0),
            cache_read_tokens=summary.get("cache_read_tokens", 0),
            llm_calls=summary.get("llm_calls", 1),
            cost_usd=summary.get("cost_usd", 0.0),
            steps=steps,
            correlation_id=correlation_id,
        )
