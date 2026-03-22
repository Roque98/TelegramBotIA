"""
Tracing - Logs estructurados con correlation ID.

Proporciona contexto de tracing para seguimiento de requests
a través de todos los componentes del sistema.
"""

import contextvars
import logging
import time
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any, Optional
from uuid import uuid4

# Context variable para el trace actual
_current_trace: contextvars.ContextVar[Optional["TraceContext"]] = contextvars.ContextVar(
    "current_trace", default=None
)

logger = logging.getLogger(__name__)


@dataclass
class TraceSpan:
    """
    Un span representa una operación dentro de un trace.

    Attributes:
        name: Nombre de la operación
        span_id: ID único del span
        start_time: Tiempo de inicio
        end_time: Tiempo de fin (None si está activo)
        attributes: Atributos adicionales
        events: Eventos durante el span
    """

    name: str
    span_id: str = field(default_factory=lambda: str(uuid4())[:8])
    start_time: float = field(default_factory=time.perf_counter)
    end_time: Optional[float] = None
    attributes: dict[str, Any] = field(default_factory=dict)
    events: list[dict[str, Any]] = field(default_factory=list)

    def end(self) -> None:
        """Finaliza el span."""
        self.end_time = time.perf_counter()

    @property
    def duration_ms(self) -> float:
        """Duración del span en milisegundos."""
        if self.end_time is None:
            return (time.perf_counter() - self.start_time) * 1000
        return (self.end_time - self.start_time) * 1000

    def add_event(self, name: str, attributes: Optional[dict[str, Any]] = None) -> None:
        """Agrega un evento al span."""
        self.events.append({
            "name": name,
            "timestamp": time.perf_counter(),
            "attributes": attributes or {},
        })

    def set_attribute(self, key: str, value: Any) -> None:
        """Establece un atributo del span."""
        self.attributes[key] = value

    def to_dict(self) -> dict[str, Any]:
        """Convierte el span a diccionario."""
        return {
            "name": self.name,
            "span_id": self.span_id,
            "duration_ms": self.duration_ms,
            "attributes": self.attributes,
            "events": self.events,
        }


@dataclass
class TraceContext:
    """
    Contexto de tracing para un request completo.

    Attributes:
        trace_id: ID único del trace
        correlation_id: ID para correlación con sistemas externos
        user_id: ID del usuario
        channel: Canal de origen (telegram, api, etc.)
        spans: Lista de spans del trace
        start_time: Tiempo de inicio
        metadata: Metadata adicional
    """

    trace_id: str = field(default_factory=lambda: str(uuid4()))
    correlation_id: Optional[str] = None
    user_id: Optional[str] = None
    channel: Optional[str] = None
    spans: list[TraceSpan] = field(default_factory=list)
    start_time: datetime = field(default_factory=lambda: datetime.now(UTC))
    metadata: dict[str, Any] = field(default_factory=dict)

    _current_span: Optional[TraceSpan] = field(default=None, repr=False)

    def start_span(self, name: str, attributes: Optional[dict[str, Any]] = None) -> TraceSpan:
        """
        Inicia un nuevo span.

        Args:
            name: Nombre del span
            attributes: Atributos iniciales

        Returns:
            TraceSpan creado
        """
        span = TraceSpan(name=name, attributes=attributes or {})
        self.spans.append(span)
        self._current_span = span
        return span

    def end_span(self) -> None:
        """Finaliza el span actual."""
        if self._current_span:
            self._current_span.end()
            self._current_span = None

    @property
    def current_span(self) -> Optional[TraceSpan]:
        """Retorna el span actual."""
        return self._current_span

    @property
    def duration_ms(self) -> float:
        """Duración total del trace en milisegundos."""
        return (datetime.now(UTC) - self.start_time).total_seconds() * 1000

    def to_dict(self) -> dict[str, Any]:
        """Convierte el trace a diccionario."""
        return {
            "trace_id": self.trace_id,
            "correlation_id": self.correlation_id,
            "user_id": self.user_id,
            "channel": self.channel,
            "duration_ms": self.duration_ms,
            "spans": [s.to_dict() for s in self.spans],
            "metadata": self.metadata,
        }


class Tracer:
    """
    Gestor de tracing para el sistema.

    Proporciona métodos para crear y gestionar traces.

    Example:
        ```python
        tracer = Tracer()

        # Iniciar trace
        trace = tracer.start_trace(user_id="123", channel="telegram")

        # Crear span
        with tracer.span("process_query"):
            result = await process(query)

        # Finalizar
        tracer.end_trace()
        ```
    """

    def __init__(self, service_name: str = "react-agent"):
        """
        Inicializa el tracer.

        Args:
            service_name: Nombre del servicio
        """
        self.service_name = service_name
        logger.info(f"Tracer initialized for service: {service_name}")

    def start_trace(
        self,
        user_id: Optional[str] = None,
        channel: Optional[str] = None,
        correlation_id: Optional[str] = None,
        metadata: Optional[dict[str, Any]] = None,
    ) -> TraceContext:
        """
        Inicia un nuevo trace.

        Args:
            user_id: ID del usuario
            channel: Canal de origen
            correlation_id: ID de correlación externo
            metadata: Metadata adicional

        Returns:
            TraceContext creado
        """
        trace = TraceContext(
            correlation_id=correlation_id or str(uuid4()),
            user_id=user_id,
            channel=channel,
            metadata=metadata or {},
        )
        _current_trace.set(trace)

        logger.debug(
            f"Trace started: {trace.trace_id}",
            extra={"trace_id": trace.trace_id, "user_id": user_id},
        )

        return trace

    def get_current_trace(self) -> Optional[TraceContext]:
        """Obtiene el trace actual."""
        return _current_trace.get()

    def end_trace(self) -> Optional[dict[str, Any]]:
        """
        Finaliza el trace actual.

        Returns:
            Diccionario con el trace completo
        """
        trace = _current_trace.get()
        if trace:
            # Finalizar spans pendientes
            for span in trace.spans:
                if span.end_time is None:
                    span.end()

            trace_dict = trace.to_dict()

            logger.info(
                f"Trace completed: {trace.trace_id} ({trace.duration_ms:.0f}ms)",
                extra={
                    "trace_id": trace.trace_id,
                    "duration_ms": trace.duration_ms,
                    "spans_count": len(trace.spans),
                },
            )

            _current_trace.set(None)
            return trace_dict

        return None

    def span(self, name: str, attributes: Optional[dict[str, Any]] = None):
        """
        Context manager para crear un span.

        Args:
            name: Nombre del span
            attributes: Atributos iniciales

        Example:
            ```python
            with tracer.span("database_query", {"table": "users"}):
                result = await db.query(...)
            ```
        """
        return SpanContextManager(self, name, attributes)

    def add_event(self, name: str, attributes: Optional[dict[str, Any]] = None) -> None:
        """
        Agrega un evento al span actual.

        Args:
            name: Nombre del evento
            attributes: Atributos del evento
        """
        trace = _current_trace.get()
        if trace and trace.current_span:
            trace.current_span.add_event(name, attributes)

    def set_attribute(self, key: str, value: Any) -> None:
        """
        Establece un atributo en el span actual.

        Args:
            key: Clave del atributo
            value: Valor del atributo
        """
        trace = _current_trace.get()
        if trace and trace.current_span:
            trace.current_span.set_attribute(key, value)


class SpanContextManager:
    """Context manager para spans."""

    def __init__(
        self,
        tracer: Tracer,
        name: str,
        attributes: Optional[dict[str, Any]] = None,
    ):
        self.tracer = tracer
        self.name = name
        self.attributes = attributes
        self.span: Optional[TraceSpan] = None

    def __enter__(self) -> TraceSpan:
        trace = _current_trace.get()
        if trace:
            self.span = trace.start_span(self.name, self.attributes)
            return self.span
        # Crear span dummy si no hay trace
        return TraceSpan(name=self.name, attributes=self.attributes or {})

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        if self.span:
            if exc_type:
                self.span.set_attribute("error", True)
                self.span.set_attribute("error.type", exc_type.__name__)
                self.span.set_attribute("error.message", str(exc_val))
            self.span.end()


class TracingFilter(logging.Filter):
    """
    Filtro de logging que agrega trace_id a los logs.

    Útil para correlacionar logs con traces.
    """

    def filter(self, record: logging.LogRecord) -> bool:
        trace = _current_trace.get()
        if trace:
            record.trace_id = trace.trace_id
            record.correlation_id = trace.correlation_id
            record.user_id = trace.user_id
        else:
            record.trace_id = "-"
            record.correlation_id = "-"
            record.user_id = "-"
        return True


# Instancia global del tracer
_tracer: Optional[Tracer] = None


def get_tracer() -> Tracer:
    """Obtiene la instancia global del tracer."""
    global _tracer
    if _tracer is None:
        _tracer = Tracer()
    return _tracer


def configure_tracing(service_name: str = "react-agent") -> Tracer:
    """
    Configura el tracing para el servicio.

    Args:
        service_name: Nombre del servicio

    Returns:
        Tracer configurado
    """
    global _tracer
    _tracer = Tracer(service_name=service_name)
    return _tracer
