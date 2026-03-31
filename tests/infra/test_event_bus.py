"""
Tests para src/infra/events/bus.py

Cobertura:
- EventBus: singleton, subscribe, unsubscribe, publish
- Historial de eventos
- Manejo de errores en handlers
- reset para tests
"""
import asyncio
import pytest
from unittest.mock import AsyncMock

from src.infra.events.bus import EventBus


@pytest.fixture(autouse=True)
def reset_bus():
    """Resetea el singleton antes de cada test."""
    EventBus.reset()
    yield
    EventBus.reset()


class TestEventBusSingleton:

    def test_singleton_returns_same_instance(self):
        bus1 = EventBus()
        bus2 = EventBus()
        assert bus1 is bus2

    def test_reset_clears_handlers_and_history(self):
        bus = EventBus()
        handler = AsyncMock()
        bus.subscribe("test.event", handler)
        bus._add_to_history({"event_type": "test.event", "data": {}})

        EventBus.reset()

        assert len(bus.get_history()) == 0
        # Después de reset, no hay handlers
        assert len(bus._handlers.get("test.event", [])) == 0


class TestEventBusSubscribe:

    def test_subscribe_registers_handler(self):
        bus = EventBus()
        handler = AsyncMock()
        bus.subscribe("query.received", handler)
        assert handler in bus._handlers["query.received"]

    def test_subscribe_same_handler_once(self):
        bus = EventBus()
        handler = AsyncMock()
        bus.subscribe("query.received", handler)
        bus.subscribe("query.received", handler)
        assert bus._handlers["query.received"].count(handler) == 1

    def test_subscribe_multiple_handlers(self):
        bus = EventBus()
        h1, h2 = AsyncMock(), AsyncMock()
        bus.subscribe("query.received", h1)
        bus.subscribe("query.received", h2)
        assert len(bus._handlers["query.received"]) == 2

    def test_unsubscribe_removes_handler(self):
        bus = EventBus()
        handler = AsyncMock()
        bus.subscribe("query.received", handler)
        bus.unsubscribe("query.received", handler)
        assert handler not in bus._handlers["query.received"]

    def test_unsubscribe_nonexistent_does_nothing(self):
        bus = EventBus()
        handler = AsyncMock()
        # No debería lanzar excepción
        bus.unsubscribe("nonexistent.event", handler)


class TestEventBusPublish:

    @pytest.mark.asyncio
    async def test_publish_calls_handler(self):
        bus = EventBus()
        handler = AsyncMock()
        bus.subscribe("query.received", handler)

        await bus.publish("query.received", {"user": "123", "text": "hola"})

        handler.assert_called_once()
        event = handler.call_args[0][0]
        assert event["event_type"] == "query.received"
        assert event["data"]["user"] == "123"

    @pytest.mark.asyncio
    async def test_publish_calls_multiple_handlers(self):
        bus = EventBus()
        h1, h2 = AsyncMock(), AsyncMock()
        bus.subscribe("response.sent", h1)
        bus.subscribe("response.sent", h2)

        await bus.publish("response.sent", {"text": "respuesta"})

        h1.assert_called_once()
        h2.assert_called_once()

    @pytest.mark.asyncio
    async def test_publish_no_handlers_does_nothing(self):
        bus = EventBus()
        # No debe lanzar excepción aunque no haya handlers
        await bus.publish("empty.event", {"data": "test"})

    @pytest.mark.asyncio
    async def test_publish_event_has_metadata(self):
        bus = EventBus()
        received = []

        async def capture(event):
            received.append(event)

        bus.subscribe("test.event", capture)
        await bus.publish("test.event", {"key": "value"})

        assert len(received) == 1
        event = received[0]
        assert "event_id" in event
        assert "timestamp" in event
        assert "event_type" in event
        assert "data" in event

    @pytest.mark.asyncio
    async def test_failing_handler_does_not_stop_others(self):
        bus = EventBus()

        async def bad_handler(event):
            raise RuntimeError("Error intencional")

        good_handler = AsyncMock()

        bus.subscribe("test.event", bad_handler)
        bus.subscribe("test.event", good_handler)

        # No debe lanzar excepción
        await bus.publish("test.event", {})

        good_handler.assert_called_once()


class TestEventBusHistory:

    @pytest.mark.asyncio
    async def test_publish_adds_to_history(self):
        bus = EventBus()
        await bus.publish("test.event", {"data": "x"})
        history = bus.get_history()
        assert len(history) == 1

    @pytest.mark.asyncio
    async def test_get_history_filtered_by_type(self):
        bus = EventBus()
        await bus.publish("event.a", {})
        await bus.publish("event.b", {})
        await bus.publish("event.a", {})

        history_a = bus.get_history("event.a")
        assert len(history_a) == 2
        assert all(e["event_type"] == "event.a" for e in history_a)

    @pytest.mark.asyncio
    async def test_history_max_size(self):
        bus = EventBus()
        bus._max_history = 5

        for i in range(10):
            await bus.publish(f"event.{i}", {})

        assert len(bus.get_history()) == 5

    def test_clear_history(self):
        bus = EventBus()
        bus._add_to_history({"event_type": "x", "data": {}})
        bus.clear_history()
        assert len(bus.get_history()) == 0

    def test_clear_handlers(self):
        bus = EventBus()
        bus.subscribe("test", AsyncMock())
        bus.clear_handlers()
        assert len(bus._handlers) == 0
