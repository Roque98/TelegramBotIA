"""
Metrics - Contadores y métricas para monitoreo del sistema.

Proporciona métricas para:
- Latencia de requests
- Steps por request
- Errores por tipo
- Uso de tools
- Cache hits/misses
"""

import logging
import threading
import time
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any, Optional

logger = logging.getLogger(__name__)


@dataclass
class LatencyStats:
    """
    Estadísticas de latencia.

    Attributes:
        count: Número de muestras
        total_ms: Total de milisegundos
        min_ms: Mínimo
        max_ms: Máximo
        last_ms: Última medición
    """

    count: int = 0
    total_ms: float = 0.0
    min_ms: float = float("inf")
    max_ms: float = 0.0
    last_ms: float = 0.0

    def record(self, duration_ms: float) -> None:
        """Registra una nueva medición."""
        self.count += 1
        self.total_ms += duration_ms
        self.min_ms = min(self.min_ms, duration_ms)
        self.max_ms = max(self.max_ms, duration_ms)
        self.last_ms = duration_ms

    @property
    def avg_ms(self) -> float:
        """Promedio en milisegundos."""
        if self.count == 0:
            return 0.0
        return self.total_ms / self.count

    def to_dict(self) -> dict[str, Any]:
        """Convierte a diccionario."""
        return {
            "count": self.count,
            "avg_ms": round(self.avg_ms, 2),
            "min_ms": round(self.min_ms, 2) if self.min_ms != float("inf") else 0,
            "max_ms": round(self.max_ms, 2),
            "last_ms": round(self.last_ms, 2),
        }


@dataclass
class Counter:
    """
    Contador simple con labels.

    Attributes:
        name: Nombre del contador
        value: Valor actual
        labels: Labels asociados
    """

    name: str
    value: int = 0
    labels: dict[str, str] = field(default_factory=dict)

    def inc(self, amount: int = 1) -> None:
        """Incrementa el contador."""
        self.value += amount

    def to_dict(self) -> dict[str, Any]:
        """Convierte a diccionario."""
        return {
            "name": self.name,
            "value": self.value,
            "labels": self.labels,
        }


# ---------------------------------------------------------------------------
# Clases internas de métricas (responsabilidad única por dominio)
# ---------------------------------------------------------------------------

class _RequestMetrics:
    """Latencia, contadores de requests, pasos ReAct y errores."""

    def __init__(self) -> None:
        self.latency: dict[str, LatencyStats] = defaultdict(LatencyStats)
        self.steps_distribution: dict[int, int] = defaultdict(int)
        self.total = Counter("requests_total")
        self.success = Counter("requests_success")
        self.error = Counter("requests_error")
        self.fallbacks = Counter("fallbacks_used")
        self.errors_by_type: dict[str, int] = defaultdict(int)

    def record(
        self,
        channel: str,
        duration_ms: float,
        steps: int,
        success: bool,
        used_fallback: bool = False,
        error_type: Optional[str] = None,
    ) -> None:
        self.latency[channel].record(duration_ms)
        self.latency["_total"].record(duration_ms)
        self.steps_distribution[steps] += 1
        self.total.inc()
        if success:
            self.success.inc()
        else:
            self.error.inc()
        if used_fallback:
            self.fallbacks.inc()
        if error_type:
            self.errors_by_type[error_type] += 1

    def reset(self) -> None:
        self.latency.clear()
        self.steps_distribution.clear()
        self.total = Counter("requests_total")
        self.success = Counter("requests_success")
        self.error = Counter("requests_error")
        self.fallbacks = Counter("fallbacks_used")
        self.errors_by_type.clear()


class _ToolMetrics:
    """Uso de tools por nombre."""

    def __init__(self) -> None:
        self.usage: dict[str, int] = defaultdict(int)

    def record(self, tool_name: str) -> None:
        self.usage[tool_name] += 1

    def reset(self) -> None:
        self.usage.clear()


class _CacheMetrics:
    """Hits y misses de caché."""

    def __init__(self) -> None:
        self.hits = Counter("cache_hits")
        self.misses = Counter("cache_misses")

    def hit(self) -> None:
        self.hits.inc()

    def miss(self) -> None:
        self.misses.inc()

    def reset(self) -> None:
        self.hits = Counter("cache_hits")
        self.misses = Counter("cache_misses")


# ---------------------------------------------------------------------------
# Facade público (API sin cambios para callers existentes)
# ---------------------------------------------------------------------------

class MetricsCollector:
    """
    Colector de métricas para el sistema ReAct.

    Facade que compone _RequestMetrics, _ToolMetrics y _CacheMetrics.
    La API pública es idéntica a la versión anterior.

    Example:
        ```python
        metrics = MetricsCollector()

        # Registrar request
        metrics.record_request(
            channel="telegram",
            duration_ms=150,
            steps=2,
            success=True
        )

        # Obtener métricas
        stats = metrics.get_stats()
        ```
    """

    def __init__(self):
        """Inicializa el colector de métricas."""
        self._lock = threading.Lock()
        self._requests = _RequestMetrics()
        self._tools = _ToolMetrics()
        self._cache = _CacheMetrics()
        self._start_time = datetime.now(UTC)

        logger.info("MetricsCollector initialized")

    def record_request(
        self,
        channel: str,
        duration_ms: float,
        steps: int,
        success: bool,
        used_fallback: bool = False,
        error_type: Optional[str] = None,
    ) -> None:
        """
        Registra una request completada.

        Args:
            channel: Canal de origen (telegram, api, etc.)
            duration_ms: Duración en milisegundos
            steps: Número de steps tomados
            success: Si fue exitosa
            used_fallback: Si se usó el fallback
            error_type: Tipo de error si hubo
        """
        with self._lock:
            self._requests.record(channel, duration_ms, steps, success, used_fallback, error_type)

        logger.debug(
            f"Request recorded: channel={channel}, duration={duration_ms:.0f}ms, "
            f"steps={steps}, success={success}"
        )

    def record_tool_usage(self, tool_name: str) -> None:
        """
        Registra el uso de un tool.

        Args:
            tool_name: Nombre del tool
        """
        with self._lock:
            self._tools.record(tool_name)

    def record_cache_hit(self) -> None:
        """Registra un cache hit."""
        with self._lock:
            self._cache.hit()

    def record_cache_miss(self) -> None:
        """Registra un cache miss."""
        with self._lock:
            self._cache.miss()

    def get_stats(self) -> dict[str, Any]:
        """
        Obtiene todas las estadísticas.

        Returns:
            Diccionario con todas las métricas
        """
        with self._lock:
            uptime = (datetime.now(UTC) - self._start_time).total_seconds()

            total_requests = sum(self._requests.steps_distribution.values())
            total_steps = sum(k * v for k, v in self._requests.steps_distribution.items())
            avg_steps = total_steps / total_requests if total_requests > 0 else 0

            success_rate = (
                self._requests.success.value / self._requests.total.value * 100
                if self._requests.total.value > 0
                else 0
            )

            cache_total = self._cache.hits.value + self._cache.misses.value
            cache_hit_rate = (
                self._cache.hits.value / cache_total * 100
                if cache_total > 0
                else 0
            )

            return {
                "uptime_seconds": round(uptime, 0),
                "requests": {
                    "total": self._requests.total.value,
                    "success": self._requests.success.value,
                    "error": self._requests.error.value,
                    "success_rate_percent": round(success_rate, 2),
                    "fallbacks_used": self._requests.fallbacks.value,
                },
                "latency": {
                    channel: stats.to_dict()
                    for channel, stats in self._requests.latency.items()
                },
                "steps": {
                    "distribution": dict(self._requests.steps_distribution),
                    "average": round(avg_steps, 2),
                },
                "errors_by_type": dict(self._requests.errors_by_type),
                "tools_usage": dict(self._tools.usage),
                "cache": {
                    "hits": self._cache.hits.value,
                    "misses": self._cache.misses.value,
                    "hit_rate_percent": round(cache_hit_rate, 2),
                },
            }

    def get_summary(self) -> str:
        """
        Obtiene un resumen en texto de las métricas.

        Returns:
            String con resumen
        """
        stats = self.get_stats()
        lines = [
            "=== ReAct Agent Metrics ===",
            f"Uptime: {stats['uptime_seconds']:.0f}s",
            f"Requests: {stats['requests']['total']} "
            f"(success: {stats['requests']['success_rate_percent']:.1f}%)",
            f"Avg Steps: {stats['steps']['average']:.1f}",
            f"Avg Latency: {stats['latency'].get('_total', {}).get('avg_ms', 0):.0f}ms",
            f"Cache Hit Rate: {stats['cache']['hit_rate_percent']:.1f}%",
            f"Fallbacks: {stats['requests']['fallbacks_used']}",
        ]

        if stats["tools_usage"]:
            lines.append("Tools Usage:")
            for tool, count in sorted(
                stats["tools_usage"].items(), key=lambda x: -x[1]
            ):
                lines.append(f"  - {tool}: {count}")

        return "\n".join(lines)

    def reset(self) -> None:
        """Resetea todas las métricas."""
        with self._lock:
            self._requests.reset()
            self._tools.reset()
            self._cache.reset()
            self._start_time = datetime.now(UTC)

        logger.info("Metrics reset")


# Instancia global del colector de métricas
_metrics: Optional[MetricsCollector] = None


def get_metrics() -> MetricsCollector:
    """Obtiene la instancia global del colector de métricas."""
    global _metrics
    if _metrics is None:
        _metrics = MetricsCollector()
    return _metrics


def reset_metrics() -> None:
    """Resetea el colector de métricas global."""
    global _metrics
    _metrics = MetricsCollector()


class MetricsMiddleware:
    """
    Middleware para registrar métricas automáticamente.

    Example:
        ```python
        @metrics_middleware
        async def handle_request(request):
            return await process(request)
        ```
    """

    def __init__(self, metrics: Optional[MetricsCollector] = None):
        self.metrics = metrics or get_metrics()

    def __call__(self, func):
        """Decorador para funciones async."""
        import functools

        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.perf_counter()
            success = True
            error_type = None

            try:
                result = await func(*args, **kwargs)
                return result
            except Exception as e:
                success = False
                error_type = type(e).__name__
                raise
            finally:
                duration_ms = (time.perf_counter() - start_time) * 1000
                channel = kwargs.get("channel", "unknown")
                steps = kwargs.get("steps", 1)

                self.metrics.record_request(
                    channel=channel,
                    duration_ms=duration_ms,
                    steps=steps,
                    success=success,
                    error_type=error_type,
                )

        return wrapper
