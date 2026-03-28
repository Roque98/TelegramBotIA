"""
Tests para el módulo de observabilidad.

Cobertura:
- TraceSpan: Spans individuales
- TraceContext: Contexto de tracing
- Tracer: Gestor de traces
- LatencyStats: Estadísticas de latencia
- MetricsCollector: Colector de métricas
"""

import pytest
import time
from datetime import UTC, datetime

from src.infra.observability.tracing import (
    TraceSpan,
    TraceContext,
    Tracer,
    TracingFilter,
    get_tracer,
    configure_tracing,
)
from src.infra.observability.metrics import (
    LatencyStats,
    Counter,
    MetricsCollector,
    get_metrics,
    reset_metrics,
)


class TestTraceSpan:
    """Tests para TraceSpan."""

    def test_span_creation(self):
        """Crear un span con valores por defecto."""
        span = TraceSpan(name="test_operation")

        assert span.name == "test_operation"
        assert span.span_id is not None
        assert span.end_time is None
        assert span.attributes == {}
        assert span.events == []

    def test_span_with_attributes(self):
        """Crear span con atributos."""
        span = TraceSpan(
            name="db_query",
            attributes={"table": "users", "operation": "select"},
        )

        assert span.attributes["table"] == "users"
        assert span.attributes["operation"] == "select"

    def test_span_end(self):
        """Finalizar un span debe registrar end_time."""
        span = TraceSpan(name="test")
        time.sleep(0.01)  # 10ms
        span.end()

        assert span.end_time is not None
        assert span.duration_ms >= 10

    def test_span_duration_active(self):
        """Duration de span activo debe calcular tiempo actual."""
        span = TraceSpan(name="test")
        time.sleep(0.01)

        # Sin end(), duration debe ser > 0
        assert span.duration_ms >= 10

    def test_add_event(self):
        """Agregar evento a un span."""
        span = TraceSpan(name="test")
        span.add_event("checkpoint", {"progress": 50})

        assert len(span.events) == 1
        assert span.events[0]["name"] == "checkpoint"
        assert span.events[0]["attributes"]["progress"] == 50

    def test_set_attribute(self):
        """Establecer atributo en span."""
        span = TraceSpan(name="test")
        span.set_attribute("result_count", 42)

        assert span.attributes["result_count"] == 42

    def test_to_dict(self):
        """Convertir span a diccionario."""
        span = TraceSpan(name="test", attributes={"key": "value"})
        span.add_event("event1")
        span.end()

        data = span.to_dict()

        assert data["name"] == "test"
        assert "span_id" in data
        assert "duration_ms" in data
        assert data["attributes"]["key"] == "value"
        assert len(data["events"]) == 1


class TestTraceContext:
    """Tests para TraceContext."""

    def test_trace_creation(self):
        """Crear un trace con valores por defecto."""
        trace = TraceContext()

        assert trace.trace_id is not None
        assert trace.spans == []
        assert trace.start_time is not None

    def test_trace_with_user_info(self):
        """Crear trace con información de usuario."""
        trace = TraceContext(
            user_id="user123",
            channel="telegram",
            correlation_id="corr456",
        )

        assert trace.user_id == "user123"
        assert trace.channel == "telegram"
        assert trace.correlation_id == "corr456"

    def test_start_span(self):
        """Iniciar un span en el trace."""
        trace = TraceContext()
        span = trace.start_span("operation1", {"key": "value"})

        assert len(trace.spans) == 1
        assert trace.current_span == span
        assert span.name == "operation1"

    def test_end_span(self):
        """Finalizar el span actual."""
        trace = TraceContext()
        trace.start_span("op1")
        trace.end_span()

        assert trace.current_span is None
        assert trace.spans[0].end_time is not None

    def test_multiple_spans(self):
        """Crear múltiples spans en secuencia."""
        trace = TraceContext()

        trace.start_span("op1")
        trace.end_span()

        trace.start_span("op2")
        trace.end_span()

        assert len(trace.spans) == 2
        assert trace.spans[0].name == "op1"
        assert trace.spans[1].name == "op2"

    def test_to_dict(self):
        """Convertir trace a diccionario."""
        trace = TraceContext(user_id="123", channel="api")
        trace.start_span("test")
        trace.end_span()

        data = trace.to_dict()

        assert "trace_id" in data
        assert data["user_id"] == "123"
        assert data["channel"] == "api"
        assert len(data["spans"]) == 1


class TestTracer:
    """Tests para Tracer."""

    def test_tracer_creation(self):
        """Crear un tracer."""
        tracer = Tracer(service_name="test-service")
        assert tracer.service_name == "test-service"

    def test_start_trace(self):
        """Iniciar un trace."""
        tracer = Tracer()
        trace = tracer.start_trace(user_id="123", channel="telegram")

        assert trace is not None
        assert trace.user_id == "123"
        assert trace.channel == "telegram"

    def test_get_current_trace(self):
        """Obtener trace actual."""
        tracer = Tracer()
        trace = tracer.start_trace()

        current = tracer.get_current_trace()

        assert current == trace

    def test_end_trace(self):
        """Finalizar un trace."""
        tracer = Tracer()
        tracer.start_trace(user_id="123")

        result = tracer.end_trace()

        assert result is not None
        assert "trace_id" in result
        assert tracer.get_current_trace() is None

    def test_span_context_manager(self):
        """Usar span como context manager."""
        tracer = Tracer()
        tracer.start_trace()

        with tracer.span("test_operation", {"key": "value"}) as span:
            time.sleep(0.01)
            span.set_attribute("result", "ok")

        trace = tracer.get_current_trace()
        assert len(trace.spans) == 1
        assert trace.spans[0].attributes["result"] == "ok"
        assert trace.spans[0].end_time is not None

        tracer.end_trace()

    def test_span_with_error(self):
        """Span debe registrar errores."""
        tracer = Tracer()
        tracer.start_trace()

        try:
            with tracer.span("failing_op"):
                raise ValueError("Test error")
        except ValueError:
            pass

        trace = tracer.get_current_trace()
        span = trace.spans[0]

        assert span.attributes.get("error") is True
        assert span.attributes.get("error.type") == "ValueError"

        tracer.end_trace()

    def test_add_event(self):
        """Agregar evento al span actual."""
        tracer = Tracer()
        tracer.start_trace()

        with tracer.span("op"):
            tracer.add_event("checkpoint", {"step": 1})

        trace = tracer.get_current_trace()
        assert len(trace.spans[0].events) == 1

        tracer.end_trace()

    def test_set_attribute(self):
        """Establecer atributo en span actual."""
        tracer = Tracer()
        tracer.start_trace()

        with tracer.span("op"):
            tracer.set_attribute("custom_key", "custom_value")

        trace = tracer.get_current_trace()
        assert trace.spans[0].attributes["custom_key"] == "custom_value"

        tracer.end_trace()


class TestTracingFilter:
    """Tests para TracingFilter."""

    def test_filter_with_trace(self):
        """Filter debe agregar trace_id cuando hay trace."""
        import logging

        tracer = Tracer()
        trace = tracer.start_trace(user_id="123")

        filter = TracingFilter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="test",
            args=(),
            exc_info=None,
        )

        filter.filter(record)

        assert record.trace_id == trace.trace_id
        assert record.user_id == "123"

        tracer.end_trace()

    def test_filter_without_trace(self):
        """Filter debe usar '-' cuando no hay trace."""
        import logging

        filter = TracingFilter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="test",
            args=(),
            exc_info=None,
        )

        filter.filter(record)

        assert record.trace_id == "-"


class TestLatencyStats:
    """Tests para LatencyStats."""

    def test_empty_stats(self):
        """Stats vacías deben tener valores iniciales."""
        stats = LatencyStats()

        assert stats.count == 0
        assert stats.avg_ms == 0.0

    def test_record_single(self):
        """Registrar una medición."""
        stats = LatencyStats()
        stats.record(100.0)

        assert stats.count == 1
        assert stats.avg_ms == 100.0
        assert stats.min_ms == 100.0
        assert stats.max_ms == 100.0

    def test_record_multiple(self):
        """Registrar múltiples mediciones."""
        stats = LatencyStats()
        stats.record(100.0)
        stats.record(200.0)
        stats.record(150.0)

        assert stats.count == 3
        assert stats.avg_ms == 150.0
        assert stats.min_ms == 100.0
        assert stats.max_ms == 200.0
        assert stats.last_ms == 150.0

    def test_to_dict(self):
        """Convertir a diccionario."""
        stats = LatencyStats()
        stats.record(100.0)

        data = stats.to_dict()

        assert data["count"] == 1
        assert data["avg_ms"] == 100.0


class TestCounter:
    """Tests para Counter."""

    def test_counter_creation(self):
        """Crear contador."""
        counter = Counter(name="test_counter")

        assert counter.name == "test_counter"
        assert counter.value == 0

    def test_counter_inc(self):
        """Incrementar contador."""
        counter = Counter(name="test")
        counter.inc()
        counter.inc(5)

        assert counter.value == 6

    def test_counter_with_labels(self):
        """Contador con labels."""
        counter = Counter(name="requests", labels={"method": "GET"})

        assert counter.labels["method"] == "GET"


class TestMetricsCollector:
    """Tests para MetricsCollector."""

    @pytest.fixture
    def collector(self):
        """Collector de prueba."""
        return MetricsCollector()

    def test_record_request_success(self, collector):
        """Registrar request exitosa."""
        collector.record_request(
            channel="telegram",
            duration_ms=150.0,
            steps=2,
            success=True,
        )

        stats = collector.get_stats()

        assert stats["requests"]["total"] == 1
        assert stats["requests"]["success"] == 1
        assert stats["requests"]["error"] == 0
        assert stats["steps"]["distribution"][2] == 1

    def test_record_request_error(self, collector):
        """Registrar request con error."""
        collector.record_request(
            channel="api",
            duration_ms=50.0,
            steps=1,
            success=False,
            error_type="ValidationError",
        )

        stats = collector.get_stats()

        assert stats["requests"]["error"] == 1
        assert stats["errors_by_type"]["ValidationError"] == 1

    def test_record_with_fallback(self, collector):
        """Registrar request con fallback."""
        collector.record_request(
            channel="telegram",
            duration_ms=200.0,
            steps=3,
            success=True,
            used_fallback=True,
        )

        stats = collector.get_stats()

        assert stats["requests"]["fallbacks_used"] == 1

    def test_record_tool_usage(self, collector):
        """Registrar uso de tools."""
        collector.record_tool_usage("database_query")
        collector.record_tool_usage("database_query")
        collector.record_tool_usage("calculate")

        stats = collector.get_stats()

        assert stats["tools_usage"]["database_query"] == 2
        assert stats["tools_usage"]["calculate"] == 1

    def test_cache_stats(self, collector):
        """Registrar cache hits/misses."""
        collector.record_cache_hit()
        collector.record_cache_hit()
        collector.record_cache_miss()

        stats = collector.get_stats()

        assert stats["cache"]["hits"] == 2
        assert stats["cache"]["misses"] == 1
        assert stats["cache"]["hit_rate_percent"] == pytest.approx(66.67, rel=0.1)

    def test_latency_by_channel(self, collector):
        """Latencia debe registrarse por canal."""
        collector.record_request("telegram", 100.0, 1, True)
        collector.record_request("telegram", 200.0, 1, True)
        collector.record_request("api", 50.0, 1, True)

        stats = collector.get_stats()

        assert stats["latency"]["telegram"]["count"] == 2
        assert stats["latency"]["telegram"]["avg_ms"] == 150.0
        assert stats["latency"]["api"]["count"] == 1

    def test_get_summary(self, collector):
        """Obtener resumen en texto."""
        collector.record_request("telegram", 100.0, 2, True)
        collector.record_tool_usage("database_query")

        summary = collector.get_summary()

        assert "ReAct Agent Metrics" in summary
        assert "Requests:" in summary

    def test_reset(self, collector):
        """Resetear métricas."""
        collector.record_request("telegram", 100.0, 1, True)
        collector.reset()

        stats = collector.get_stats()

        assert stats["requests"]["total"] == 0

    def test_success_rate(self, collector):
        """Calcular tasa de éxito."""
        collector.record_request("api", 100.0, 1, True)
        collector.record_request("api", 100.0, 1, True)
        collector.record_request("api", 100.0, 1, False)

        stats = collector.get_stats()

        assert stats["requests"]["success_rate_percent"] == pytest.approx(66.67, rel=0.1)

    def test_average_steps(self, collector):
        """Calcular promedio de steps."""
        collector.record_request("api", 100.0, 1, True)
        collector.record_request("api", 100.0, 3, True)
        collector.record_request("api", 100.0, 2, True)

        stats = collector.get_stats()

        assert stats["steps"]["average"] == 2.0


class TestGlobalFunctions:
    """Tests para funciones globales."""

    def test_get_tracer_singleton(self):
        """get_tracer debe retornar singleton."""
        tracer1 = get_tracer()
        tracer2 = get_tracer()

        assert tracer1 is tracer2

    def test_configure_tracing(self):
        """configure_tracing debe crear nuevo tracer."""
        tracer = configure_tracing("my-service")

        assert tracer.service_name == "my-service"

    def test_get_metrics_singleton(self):
        """get_metrics debe retornar singleton."""
        reset_metrics()  # Resetear para test aislado

        metrics1 = get_metrics()
        metrics2 = get_metrics()

        assert metrics1 is metrics2

    def test_reset_metrics(self):
        """reset_metrics debe crear nuevo collector."""
        metrics1 = get_metrics()
        metrics1.record_request("test", 100.0, 1, True)

        reset_metrics()

        metrics2 = get_metrics()
        stats = metrics2.get_stats()

        assert stats["requests"]["total"] == 0
