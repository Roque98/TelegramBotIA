"""
Tests para los contratos base de agentes.

Cobertura:
- AgentResponse: Factory methods y serialización
- UserContext: Creación y métodos auxiliares
- ConversationEvent: Creación desde diferentes canales
- EventBus: Pub/Sub y manejo de errores
- Exceptions: Todas las excepciones personalizadas
"""

import pytest
from datetime import datetime
from unittest.mock import AsyncMock

from src.agents.base.agent import AgentResponse, BaseAgent
from src.agents.base.events import ConversationEvent, UserContext
from src.agents.base.exceptions import (
    AgentException,
    ToolException,
    ValidationException,
    MaxIterationsException,
    LLMException,
)
from src.infra.events.bus import EventBus


class TestAgentResponse:
    """Tests para AgentResponse."""

    def test_success_response_creates_valid_response(self):
        """success_response debe crear una respuesta exitosa."""
        response = AgentResponse.success_response(
            agent_name="test_agent",
            message="Test message",
            data={"key": "value"},
            steps_taken=3,
        )

        assert response.success is True
        assert response.message == "Test message"
        assert response.agent_name == "test_agent"
        assert response.data == {"key": "value"}
        assert response.steps_taken == 3
        assert response.error is None

    def test_error_response_creates_valid_response(self):
        """error_response debe crear una respuesta de error."""
        response = AgentResponse.error_response(
            agent_name="test_agent",
            error="Something went wrong",
            steps_taken=2,
        )

        assert response.success is False
        assert response.error == "Something went wrong"
        assert response.agent_name == "test_agent"
        assert response.steps_taken == 2
        assert response.message is None

    def test_response_has_timestamp(self):
        """La respuesta debe tener timestamp automático."""
        response = AgentResponse.success_response(
            agent_name="test",
            message="test",
        )

        assert response.timestamp is not None
        assert isinstance(response.timestamp, datetime)

    def test_response_metadata_defaults_to_empty_dict(self):
        """metadata debe ser dict vacío por defecto."""
        response = AgentResponse.success_response(
            agent_name="test",
            message="test",
        )

        assert response.metadata == {}


class TestUserContext:
    """Tests para UserContext."""

    def test_empty_creates_minimal_context(self):
        """empty() debe crear contexto con valores por defecto."""
        context = UserContext.empty("user_123")

        assert context.user_id == "user_123"
        assert context.display_name == "Usuario"
        assert context.roles == []
        assert context.working_memory == []
        assert context.long_term_summary is None

    def test_add_message_appends_to_working_memory(self):
        """add_message debe agregar mensaje a working_memory."""
        context = UserContext.empty("user_123")

        context.add_message("user", "Hola")
        context.add_message("assistant", "¡Hola! ¿En qué puedo ayudarte?")

        assert len(context.working_memory) == 2
        assert context.working_memory[0]["role"] == "user"
        assert context.working_memory[0]["content"] == "Hola"
        assert context.working_memory[1]["role"] == "assistant"

    def test_get_recent_messages_returns_limited_messages(self):
        """get_recent_messages debe retornar solo los últimos N mensajes."""
        context = UserContext.empty("user_123")

        for i in range(15):
            context.add_message("user", f"Message {i}")

        recent = context.get_recent_messages(limit=5)

        assert len(recent) == 5
        assert recent[0]["content"] == "Message 10"
        assert recent[4]["content"] == "Message 14"

    def test_to_prompt_context_includes_basic_info(self):
        """to_prompt_context debe incluir info básica."""
        context = UserContext(
            user_id="123",
            display_name="Juan",
            roles=["admin", "ventas"],
        )

        prompt = context.to_prompt_context()

        assert "Juan" in prompt
        assert "admin" in prompt
        assert "ventas" in prompt


class TestConversationEvent:
    """Tests para ConversationEvent."""

    def test_from_telegram_creates_valid_event(self):
        """from_telegram debe crear evento válido."""
        event = ConversationEvent.from_telegram(
            user_id=123456,
            text="¿Cuántas ventas hubo ayer?",
            chat_id=789,
            username="juanperez",
            first_name="Juan",
        )

        assert event.user_id == "123456"
        assert event.channel == "telegram"
        assert event.text == "¿Cuántas ventas hubo ayer?"
        assert event.correlation_id == "789"
        assert event.metadata["username"] == "juanperez"
        assert event.metadata["first_name"] == "Juan"

    def test_from_api_creates_valid_event(self):
        """from_api debe crear evento válido."""
        event = ConversationEvent.from_api(
            user_id="user_abc",
            text="Hello world",
            session_id="session_123",
            metadata={"source": "mobile"},
        )

        assert event.user_id == "user_abc"
        assert event.channel == "api"
        assert event.text == "Hello world"
        assert event.correlation_id == "session_123"
        assert event.metadata["source"] == "mobile"

    def test_event_has_auto_generated_ids(self):
        """El evento debe tener IDs autogenerados."""
        event = ConversationEvent(
            user_id="123",
            channel="test",
            text="test",
        )

        assert event.event_id is not None
        assert len(event.event_id) > 0
        assert event.correlation_id is not None


class TestEventBus:
    """Tests para EventBus."""

    @pytest.fixture
    def event_bus(self):
        """Crea un EventBus limpio para cada test."""
        bus = EventBus()
        bus.clear_handlers()
        bus.clear_history()
        return bus

    @pytest.mark.asyncio
    async def test_subscribe_and_publish(self, event_bus):
        """Un handler suscrito debe recibir eventos publicados."""
        received_events = []

        async def handler(event):
            received_events.append(event)

        event_bus.subscribe("test.event", handler)
        await event_bus.publish("test.event", {"message": "hello"})

        assert len(received_events) == 1
        assert received_events[0]["data"]["message"] == "hello"

    @pytest.mark.asyncio
    async def test_unsubscribe_stops_receiving(self, event_bus):
        """Un handler desuscrito no debe recibir más eventos."""
        received_events = []

        async def handler(event):
            received_events.append(event)

        event_bus.subscribe("test.event", handler)
        event_bus.unsubscribe("test.event", handler)
        await event_bus.publish("test.event", {"message": "hello"})

        assert len(received_events) == 0

    @pytest.mark.asyncio
    async def test_multiple_handlers_receive_event(self, event_bus):
        """Múltiples handlers deben recibir el mismo evento."""
        results = []

        async def handler1(event):
            results.append("handler1")

        async def handler2(event):
            results.append("handler2")

        event_bus.subscribe("test.event", handler1)
        event_bus.subscribe("test.event", handler2)
        await event_bus.publish("test.event", {})

        assert "handler1" in results
        assert "handler2" in results

    @pytest.mark.asyncio
    async def test_handler_error_does_not_stop_others(self, event_bus):
        """Un error en un handler no debe detener otros handlers."""
        results = []

        async def failing_handler(event):
            raise ValueError("Test error")

        async def success_handler(event):
            results.append("success")

        event_bus.subscribe("test.event", failing_handler)
        event_bus.subscribe("test.event", success_handler)
        await event_bus.publish("test.event", {})

        assert "success" in results

    def test_get_history_returns_events(self, event_bus):
        """get_history debe retornar eventos publicados."""
        import asyncio

        asyncio.run(event_bus.publish("test.event", {"value": 1}))
        asyncio.run(event_bus.publish("test.event", {"value": 2}))

        history = event_bus.get_history()

        assert len(history) == 2

    def test_get_history_filters_by_type(self, event_bus):
        """get_history debe filtrar por tipo de evento."""
        import asyncio

        asyncio.run(event_bus.publish("type_a", {"value": 1}))
        asyncio.run(event_bus.publish("type_b", {"value": 2}))

        history = event_bus.get_history("type_a")

        assert len(history) == 1
        assert history[0]["event_type"] == "type_a"


class TestExceptions:
    """Tests para excepciones personalizadas."""

    def test_agent_exception_str(self):
        """AgentException debe formatear mensaje correctamente."""
        exc = AgentException("Error message", agent_name="TestAgent")

        assert str(exc) == "[TestAgent] Error message"

    def test_agent_exception_without_agent_name(self):
        """AgentException sin agent_name debe mostrar solo mensaje."""
        exc = AgentException("Error message")

        assert str(exc) == "Error message"

    def test_tool_exception_includes_tool_name(self):
        """ToolException debe incluir nombre del tool."""
        exc = ToolException(
            message="Query failed",
            tool_name="database_query",
            action_input={"query": "SELECT *"},
        )

        assert exc.tool_name == "database_query"
        assert exc.action_input == {"query": "SELECT *"}
        assert "Tool:database_query" in str(exc)

    def test_validation_exception_includes_field(self):
        """ValidationException debe incluir campo y valor."""
        exc = ValidationException(
            message="Invalid value",
            field="email",
            value="invalid-email",
        )

        assert exc.field == "email"
        assert exc.value == "invalid-email"

    def test_max_iterations_exception(self):
        """MaxIterationsException debe incluir detalles de iteraciones."""
        exc = MaxIterationsException(
            max_iterations=10,
            steps_taken=10,
            partial_result="Partial answer",
        )

        assert exc.max_iterations == 10
        assert exc.steps_taken == 10
        assert exc.partial_result == "Partial answer"
        assert "10" in str(exc)

    def test_llm_exception_includes_provider(self):
        """LLMException debe incluir proveedor."""
        exc = LLMException(
            message="Rate limit exceeded",
            provider="openai",
            status_code=429,
        )

        assert exc.provider == "openai"
        assert exc.status_code == 429
        assert "LLM:openai" in str(exc)
