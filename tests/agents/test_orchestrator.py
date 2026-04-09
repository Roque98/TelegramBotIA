"""
Tests para AgentOrchestrator e IntentClassifier (ARQ-35 — N-way dinámico).
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from src.agents.orchestrator import AgentOrchestrator, IntentClassifier
from src.agents.orchestrator.orchestrator import AgentConfigException
from src.agents.base.events import UserContext
from src.agents.base.agent import AgentResponse
from src.domain.agent_config.agent_config_entity import AgentDefinition


def make_agent_def(
    nombre: str,
    es_generalista: bool = False,
    tools: list[str] | None = None,
    version: int = 1,
) -> AgentDefinition:
    """Helper para crear AgentDefinition de prueba."""
    return AgentDefinition(
        id=hash(nombre) % 1000,
        nombre=nombre,
        descripcion=f"Agente de {nombre}",
        system_prompt="prompt {{tools_description}} {{usage_hints}}",
        temperatura=0.1,
        max_iteraciones=10,
        modelo_override=None,
        es_generalista=es_generalista,
        tools=tools or [],
        activo=True,
        version=version,
    )


AGENTS = [
    make_agent_def("datos", tools=["database_query", "calculate"]),
    make_agent_def("conocimiento", tools=["knowledge_search"]),
    make_agent_def("casual", tools=["save_preference"]),
    make_agent_def("generalista", es_generalista=True),
]


class TestIntentClassifier:
    """Tests para IntentClassifier — N-way dinámico."""

    @pytest.fixture
    def mock_llm(self):
        return AsyncMock()

    @pytest.mark.asyncio
    async def test_classifies_datos(self, mock_llm):
        """Consultas de negocio → agente 'datos'."""
        mock_llm.generate_messages.return_value = "datos"
        classifier = IntentClassifier(llm=mock_llm)

        result = await classifier.classify("cuántas ventas hubo ayer?", AGENTS)

        assert result == "datos"

    @pytest.mark.asyncio
    async def test_classifies_casual(self, mock_llm):
        """Saludos → agente 'casual'."""
        mock_llm.generate_messages.return_value = "casual"
        classifier = IntentClassifier(llm=mock_llm)

        result = await classifier.classify("hola, cómo estás?", AGENTS)

        assert result == "casual"

    @pytest.mark.asyncio
    async def test_classifies_conocimiento(self, mock_llm):
        """Preguntas de política → agente 'conocimiento'."""
        mock_llm.generate_messages.return_value = "conocimiento"
        classifier = IntentClassifier(llm=mock_llm)

        result = await classifier.classify("¿cuál es la política de licencias?", AGENTS)

        assert result == "conocimiento"

    @pytest.mark.asyncio
    async def test_defaults_to_generalista_on_error(self, mock_llm):
        """Si el LLM falla, fallback a 'generalista'."""
        mock_llm.generate_messages.side_effect = Exception("LLM error")
        classifier = IntentClassifier(llm=mock_llm)

        result = await classifier.classify("alguna consulta", AGENTS)

        assert result == "generalista"

    @pytest.mark.asyncio
    async def test_defaults_to_generalista_on_unknown_response(self, mock_llm):
        """Respuesta no reconocida → 'generalista'."""
        mock_llm.generate_messages.return_value = "no sé"
        classifier = IntentClassifier(llm=mock_llm)

        result = await classifier.classify("consulta", AGENTS)

        assert result == "generalista"

    @pytest.mark.asyncio
    async def test_partial_match_in_response(self, mock_llm):
        """Debe extraer agente aunque el LLM responda con texto extra."""
        mock_llm.generate_messages.return_value = "Categoría: datos (ventas del mes)"
        classifier = IntentClassifier(llm=mock_llm)

        result = await classifier.classify("reporte de ventas", AGENTS)

        assert result == "datos"

    @pytest.mark.asyncio
    async def test_returns_generalista_directly_if_no_especialistas(self, mock_llm):
        """Sin agentes especializados → generalista sin llamar al LLM."""
        agents_only_generalista = [make_agent_def("generalista", es_generalista=True)]
        classifier = IntentClassifier(llm=mock_llm)

        result = await classifier.classify("cualquier consulta", agents_only_generalista)

        assert result == "generalista"
        mock_llm.generate_messages.assert_not_called()


class TestAgentOrchestrator:
    """Tests para AgentOrchestrator — N-way dinámico."""

    @pytest.fixture
    def user_context(self):
        return UserContext.empty("user_test")

    def _make_agent_mock(self, name: str, message: str) -> AsyncMock:
        agent = AsyncMock()
        agent.execute.return_value = AgentResponse.success_response(
            agent_name=name, message=message
        )
        agent.health_check.return_value = True
        return agent

    def _make_orchestrator(self, agents=None, classifier_return="generalista"):
        """Helper para construir AgentOrchestrator con mocks."""
        mock_service = MagicMock()
        mock_service.get_active_agents.return_value = agents or AGENTS

        mock_builder = MagicMock()
        mock_builder.build.side_effect = lambda defn: self._make_agent_mock(
            defn.nombre, f"respuesta de {defn.nombre}"
        )

        mock_classifier = AsyncMock(spec=IntentClassifier)
        mock_classifier.classify.return_value = classifier_return

        return AgentOrchestrator(
            agent_config_service=mock_service,
            agent_builder=mock_builder,
            intent_classifier=mock_classifier,
        )

    @pytest.mark.asyncio
    async def test_routes_to_datos(self, user_context):
        """Intent 'datos' → agente datos."""
        orchestrator = self._make_orchestrator(classifier_return="datos")
        response = await orchestrator.execute("ventas", user_context)

        assert response.routed_agent == "datos"
        assert response.success is True

    @pytest.mark.asyncio
    async def test_routes_to_casual(self, user_context):
        """Intent 'casual' → agente casual."""
        orchestrator = self._make_orchestrator(classifier_return="casual")
        response = await orchestrator.execute("hola", user_context)

        assert response.routed_agent == "casual"

    @pytest.mark.asyncio
    async def test_fallback_to_generalista_on_unknown_intent(self, user_context):
        """Intent desconocido → fallback a generalista."""
        orchestrator = self._make_orchestrator(classifier_return="agente_inexistente")
        response = await orchestrator.execute("consulta rara", user_context)

        assert response.routed_agent == "generalista"

    @pytest.mark.asyncio
    async def test_fallback_to_generalista_when_classifier_returns_generalista(self, user_context):
        """Classifier devuelve 'generalista' → usa agente generalista."""
        orchestrator = self._make_orchestrator(classifier_return="generalista")
        response = await orchestrator.execute("consulta mixta", user_context)

        assert response.routed_agent == "generalista"

    @pytest.mark.asyncio
    async def test_error_when_no_generalista(self, user_context):
        """Sin agente generalista → retorna error gracioso."""
        agents_sin_generalista = [
            make_agent_def("datos", tools=["database_query"]),
            make_agent_def("casual", tools=["save_preference"]),
        ]
        orchestrator = self._make_orchestrator(
            agents=agents_sin_generalista,
            classifier_return="agente_inexistente",
        )
        response = await orchestrator.execute("consulta", user_context)

        assert response.success is False
        assert "no disponible" in response.error.lower()

    @pytest.mark.asyncio
    async def test_routed_agent_set_in_response(self, user_context):
        """routed_agent debe estar seteado en el AgentResponse."""
        orchestrator = self._make_orchestrator(classifier_return="conocimiento")
        response = await orchestrator.execute("política de vacaciones", user_context)

        assert response.routed_agent == "conocimiento"

    @pytest.mark.asyncio
    async def test_event_callback_passed_to_agent(self, user_context):
        """El event_callback debe pasarse al agente seleccionado."""
        mock_service = MagicMock()
        mock_service.get_active_agents.return_value = AGENTS

        executed_agent = AsyncMock()
        executed_agent.execute.return_value = AgentResponse.success_response(
            agent_name="datos", message="resp"
        )

        mock_builder = MagicMock()
        mock_builder.build.return_value = executed_agent

        mock_classifier = AsyncMock()
        mock_classifier.classify.return_value = "datos"

        orchestrator = AgentOrchestrator(
            agent_config_service=mock_service,
            agent_builder=mock_builder,
            intent_classifier=mock_classifier,
        )

        callback = AsyncMock()
        await orchestrator.execute("ventas", user_context, event_callback=callback)

        _, kwargs = executed_agent.execute.call_args
        assert kwargs.get("event_callback") == callback

    @pytest.mark.asyncio
    async def test_health_check_ok(self):
        """health_check OK cuando hay agentes activos con generalista."""
        orchestrator = self._make_orchestrator()
        result = await orchestrator.health_check()
        assert result is True

    @pytest.mark.asyncio
    async def test_health_check_fails_without_generalista(self):
        """health_check falla si no hay generalista."""
        agents_sin_generalista = [make_agent_def("datos")]
        orchestrator = self._make_orchestrator(agents=agents_sin_generalista)
        result = await orchestrator.health_check()
        assert result is False


class TestAgentBuilder:
    """Tests para AgentBuilder."""

    def test_build_sets_tool_scope_for_specialist(self):
        """Agentes especializados deben tener tool_scope."""
        from src.agents.factory.agent_builder import AgentBuilder
        from src.agents.tools.registry import ToolRegistry

        ToolRegistry.reset()
        registry = ToolRegistry()

        builder = AgentBuilder(tool_registry=registry, openai_api_key="sk-test")

        defn = make_agent_def("datos", tools=["database_query", "calculate"])
        agent = builder.build(defn)

        assert agent.tool_scope == {"database_query", "calculate"}

    def test_build_no_tool_scope_for_generalista(self):
        """Agente generalista debe tener tool_scope=None."""
        from src.agents.factory.agent_builder import AgentBuilder
        from src.agents.tools.registry import ToolRegistry

        ToolRegistry.reset()
        registry = ToolRegistry()

        builder = AgentBuilder(tool_registry=registry, openai_api_key="sk-test")

        defn = make_agent_def("generalista", es_generalista=True)
        agent = builder.build(defn)

        assert agent.tool_scope is None

    def test_cache_returns_same_instance(self):
        """build() dos veces con misma (id, version) retorna la misma instancia."""
        from src.agents.factory.agent_builder import AgentBuilder
        from src.agents.tools.registry import ToolRegistry

        ToolRegistry.reset()
        registry = ToolRegistry()

        builder = AgentBuilder(tool_registry=registry, openai_api_key="sk-test")
        defn = make_agent_def("datos", tools=["database_query"], version=3)

        inst1 = builder.build(defn)
        inst2 = builder.build(defn)

        assert inst1 is inst2

    def test_clear_instance_cache(self):
        """clear_instance_cache vacía el cache de instancias."""
        from src.agents.factory.agent_builder import AgentBuilder
        from src.agents.tools.registry import ToolRegistry

        ToolRegistry.reset()
        registry = ToolRegistry()

        builder = AgentBuilder(tool_registry=registry, openai_api_key="sk-test")
        defn = make_agent_def("datos", tools=["database_query"])

        inst1 = builder.build(defn)
        builder.clear_instance_cache()
        inst2 = builder.build(defn)

        assert inst1 is not inst2

    def teardown_method(self, method):
        from src.agents.tools.registry import ToolRegistry
        ToolRegistry.reset()
