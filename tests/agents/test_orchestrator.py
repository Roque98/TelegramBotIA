"""
Tests para AgentOrchestrator e IntentClassifier.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock

from src.agents.orchestrator import AgentOrchestrator, IntentClassifier, Intent
from src.agents.base.events import UserContext
from src.agents.base.agent import AgentResponse


class TestIntentClassifier:
    """Tests para IntentClassifier."""

    @pytest.fixture
    def mock_llm(self):
        return AsyncMock()

    @pytest.mark.asyncio
    async def test_classifies_business_data(self, mock_llm):
        """Consultas de negocio deben clasificarse como business_data."""
        mock_llm.generate_messages.return_value = "business_data"
        classifier = IntentClassifier(llm=mock_llm)

        intent = await classifier.classify("cuántas ventas hubo ayer?")

        assert intent == Intent.BUSINESS_DATA

    @pytest.mark.asyncio
    async def test_classifies_casual(self, mock_llm):
        """Saludos deben clasificarse como casual."""
        mock_llm.generate_messages.return_value = "casual"
        classifier = IntentClassifier(llm=mock_llm)

        intent = await classifier.classify("hola, cómo estás?")

        assert intent == Intent.CASUAL

    @pytest.mark.asyncio
    async def test_defaults_to_business_data_on_error(self, mock_llm):
        """Si el LLM falla, debe usar business_data para no perder calidad."""
        mock_llm.generate_messages.side_effect = Exception("LLM error")
        classifier = IntentClassifier(llm=mock_llm)

        intent = await classifier.classify("alguna consulta")

        assert intent == Intent.BUSINESS_DATA

    @pytest.mark.asyncio
    async def test_partial_match_in_response(self, mock_llm):
        """Debe extraer intent aunque el LLM responda con texto extra."""
        mock_llm.generate_messages.return_value = "Categoría: business_data (ventas)"
        classifier = IntentClassifier(llm=mock_llm)

        intent = await classifier.classify("reporte de ventas")

        assert intent == Intent.BUSINESS_DATA

    @pytest.mark.asyncio
    async def test_unknown_response_defaults_to_casual(self, mock_llm):
        """Respuesta no reconocida (sin 'business_data') → casual."""
        mock_llm.generate_messages.return_value = "no sé"
        classifier = IntentClassifier(llm=mock_llm)

        intent = await classifier.classify("hola")

        assert intent == Intent.CASUAL


class TestAgentOrchestrator:
    """Tests para AgentOrchestrator."""

    @pytest.fixture
    def user_context(self):
        return UserContext.empty("user_test")

    @pytest.fixture
    def casual_agent(self):
        agent = AsyncMock()
        agent.execute.return_value = AgentResponse.success_response(
            agent_name="casual", message="Respuesta casual"
        )
        agent.health_check.return_value = True
        return agent

    @pytest.fixture
    def data_agent(self):
        agent = AsyncMock()
        agent.execute.return_value = AgentResponse.success_response(
            agent_name="data", message="Respuesta con datos"
        )
        agent.health_check.return_value = True
        return agent

    @pytest.fixture
    def intent_classifier(self):
        return AsyncMock(spec=IntentClassifier)

    @pytest.mark.asyncio
    async def test_routes_to_casual_agent(self, casual_agent, data_agent, intent_classifier, user_context):
        """Intent casual debe rutear al casual_agent."""
        intent_classifier.classify.return_value = Intent.CASUAL
        orchestrator = AgentOrchestrator(casual_agent, data_agent, intent_classifier)

        response = await orchestrator.execute("hola!", user_context)

        casual_agent.execute.assert_called_once()
        data_agent.execute.assert_not_called()
        assert response.message == "Respuesta casual"

    @pytest.mark.asyncio
    async def test_routes_to_data_agent(self, casual_agent, data_agent, intent_classifier, user_context):
        """Intent business_data debe rutear al data_agent."""
        intent_classifier.classify.return_value = Intent.BUSINESS_DATA
        orchestrator = AgentOrchestrator(casual_agent, data_agent, intent_classifier)

        response = await orchestrator.execute("cuántas ventas hubo?", user_context)

        data_agent.execute.assert_called_once()
        casual_agent.execute.assert_not_called()
        assert response.message == "Respuesta con datos"

    @pytest.mark.asyncio
    async def test_passes_event_callback(self, casual_agent, data_agent, intent_classifier, user_context):
        """El event_callback debe pasarse al agente seleccionado."""
        intent_classifier.classify.return_value = Intent.CASUAL
        orchestrator = AgentOrchestrator(casual_agent, data_agent, intent_classifier)
        callback = AsyncMock()

        await orchestrator.execute("hola", user_context, event_callback=callback)

        _, kwargs = casual_agent.execute.call_args
        assert kwargs.get("event_callback") == callback

    @pytest.mark.asyncio
    async def test_health_check_both_agents(self, casual_agent, data_agent, intent_classifier):
        """health_check debe verificar ambos agentes."""
        orchestrator = AgentOrchestrator(casual_agent, data_agent, intent_classifier)

        result = await orchestrator.health_check()

        assert result is True
        casual_agent.health_check.assert_called_once()
        data_agent.health_check.assert_called_once()

    @pytest.mark.asyncio
    async def test_health_check_fails_if_one_down(self, casual_agent, data_agent, intent_classifier):
        """Si uno de los agentes falla, health_check debe retornar False."""
        casual_agent.health_check.return_value = False
        orchestrator = AgentOrchestrator(casual_agent, data_agent, intent_classifier)

        result = await orchestrator.health_check()

        assert result is False
