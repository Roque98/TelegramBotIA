"""
Tests para el módulo de agente LLM.
"""
import pytest
from src.agent.llm_agent import LLMAgent


class TestLLMAgent:
    """Tests para la clase LLMAgent."""

    @pytest.fixture
    def agent(self):
        """Fixture que crea una instancia del agente."""
        return LLMAgent()

    def test_agent_initialization(self, agent):
        """Verificar que el agente se inicializa correctamente."""
        assert agent is not None
        assert agent.db_manager is not None

    @pytest.mark.asyncio
    async def test_process_query(self, agent):
        """Test básico de procesamiento de consulta."""
        # Este es un ejemplo - necesitarás adaptarlo a tu caso real
        query = "¿Cuántos usuarios hay?"
        # En un test real, usarías mocks para evitar llamadas reales a BD/LLM
        # response = await agent.process_query(query)
        # assert response is not None
        pass
