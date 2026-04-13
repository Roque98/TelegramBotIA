"""
Observability Package.

Proporciona herramientas de observabilidad para el sistema:
- Tracing: Logs estructurados con correlation ID
- Metrics: Contadores y estadísticas de rendimiento
"""

from .metrics import (
    Counter,
    LatencyStats,
    MetricsCollector,
    get_metrics,
    reset_metrics,
)
from .tracing import (
    SpanContextManager,
    TraceContext,
    TraceSpan,
    Tracer,
    TracingFilter,
    configure_tracing,
    get_tracer,
)

__all__ = [
    # Tracing
    "Tracer",
    "TraceContext",
    "TraceSpan",
    "SpanContextManager",
    "TracingFilter",
    "get_tracer",
    "configure_tracing",
    # Metrics
    "MetricsCollector",
    "LatencyStats",
    "Counter",
    "get_metrics",
    "reset_metrics",
]
