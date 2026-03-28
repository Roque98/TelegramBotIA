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


class MetricsCollector:
    """
    Colector de métricas para el sistema ReAct.

    Recolecta:
    - Latencia de requests por canal
    - Steps tomados por request
    - Errores por tipo
    - Uso de tools
    - Cache hits/misses
    - Fallbacks utilizados

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

        # Latencia por canal
        self._latency: dict[str, LatencyStats] = defaultdict(LatencyStats)

        # Steps por request
        self._steps_distribution: dict[int, int] = defaultdict(int)

        # Contadores
        self._requests_total = Counter("requests_total")
        self._requests_success = Counter("requests_success")
        self._requests_error = Counter("requests_error")
        self._fallbacks_used = Counter("fallbacks_used")

        # Errores por tipo
        self._errors_by_type: dict[str, int] = defaultdict(int)

        # Tools usage
        self._tools_usage: dict[str, int] = defaultdict(int)

        # Cache stats
        self._cache_hits = Counter("cache_hits")
        self._cache_misses = Counter("cache_misses")

        # Timestamp de inicio
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
            # Latencia
            self._latency[channel].record(duration_ms)
            self._latency["_total"].record(duration_ms)

            # Steps
            self._steps_distribution[steps] += 1

            # Contadores
            self._requests_total.inc()
            if success:
                self._requests_success.inc()
            else:
                self._requests_error.inc()

            if used_fallback:
                self._fallbacks_used.inc()

            if error_type:
                self._errors_by_type[error_type] += 1

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
            self._tools_usage[tool_name] += 1

    def record_cache_hit(self) -> None:
        """Registra un cache hit."""
        with self._lock:
            self._cache_hits.inc()

    def record_cache_miss(self) -> None:
        """Registra un cache miss."""
        with self._lock:
            self._cache_misses.inc()

    def get_stats(self) -> dict[str, Any]:
        """
        Obtiene todas las estadísticas.

        Returns:
            Diccionario con todas las métricas
        """
        with self._lock:
            uptime = (datetime.now(UTC) - self._start_time).total_seconds()

            # Calcular promedio de steps
            total_requests = sum(self._steps_distribution.values())
            total_steps = sum(k * v for k, v in self._steps_distribution.items())
            avg_steps = total_steps / total_requests if total_requests > 0 else 0

            # Calcular tasa de éxito
            success_rate = (
                self._requests_success.value / self._requests_total.value * 100
                if self._requests_total.value > 0
                else 0
            )

            # Calcular cache hit rate
            cache_total = self._cache_hits.value + self._cache_misses.value
            cache_hit_rate = (
                self._cache_hits.value / cache_total * 100
                if cache_total > 0
                else 0
            )

            return {
                "uptime_seconds": round(uptime, 0),
                "requests": {
                    "total": self._requests_total.value,
                    "success": self._requests_success.value,
                    "error": self._requests_error.value,
                    "success_rate_percent": round(success_rate, 2),
                    "fallbacks_used": self._fallbacks_used.value,
                },
                "latency": {
                    channel: stats.to_dict()
                    for channel, stats in self._latency.items()
                },
                "steps": {
                    "distribution": dict(self._steps_distribution),
                    "average": round(avg_steps, 2),
                },
                "errors_by_type": dict(self._errors_by_type),
                "tools_usage": dict(self._tools_usage),
                "cache": {
                    "hits": self._cache_hits.value,
                    "misses": self._cache_misses.value,
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
            self._latency.clear()
            self._steps_distribution.clear()
            self._requests_total = Counter("requests_total")
            self._requests_success = Counter("requests_success")
            self._requests_error = Counter("requests_error")
            self._fallbacks_used = Counter("fallbacks_used")
            self._errors_by_type.clear()
            self._tools_usage.clear()
            self._cache_hits = Counter("cache_hits")
            self._cache_misses = Counter("cache_misses")
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
                # Intentar extraer channel de kwargs
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
