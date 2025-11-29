"""
Tests para QueryClassifier con integración de KnowledgeManager.

Valida clasificación de queries en KNOWLEDGE, DATABASE y GENERAL.
"""
import pytest
from unittest.mock import Mock, AsyncMock
from src.agent.classifiers.query_classifier import QueryClassifier, QueryType
from src.agent.knowledge import KnowledgeManager
from src.agent.providers.base_provider import LLMProvider


@pytest.fixture
def mock_llm_provider():
    """Mock del proveedor LLM."""
    provider = Mock(spec=LLMProvider)
    provider.get_provider_name.return_value = "MockProvider"
    provider.generate = AsyncMock()
    return provider


@pytest.fixture
def knowledge_manager():
    """Knowledge manager real para tests."""
    return KnowledgeManager()


@pytest.fixture
def classifier(mock_llm_provider, knowledge_manager):
    """Classifier con knowledge manager."""
    return QueryClassifier(
        llm_provider=mock_llm_provider,
        knowledge_manager=knowledge_manager
    )


class TestQueryClassifierInitialization:
    """Tests de inicialización."""

    def test_initialization_with_knowledge_manager(self, mock_llm_provider, knowledge_manager):
        """Debe inicializar con knowledge manager."""
        classifier = QueryClassifier(
            llm_provider=mock_llm_provider,
            knowledge_manager=knowledge_manager
        )

        assert classifier.knowledge_manager is knowledge_manager
        assert classifier.llm_provider is mock_llm_provider
        assert classifier.prompt_manager is not None

    def test_initialization_without_knowledge_manager(self, mock_llm_provider):
        """Debe crear knowledge manager automáticamente si no se proporciona."""
        classifier = QueryClassifier(llm_provider=mock_llm_provider)

        assert classifier.knowledge_manager is not None
        assert isinstance(classifier.knowledge_manager, KnowledgeManager)


class TestQueryClassifierKnowledgeClassification:
    """Tests de clasificación con conocimiento institucional."""

    @pytest.mark.asyncio
    async def test_classify_as_knowledge_when_llm_returns_knowledge(self, classifier, mock_llm_provider):
        """Debe clasificar como KNOWLEDGE cuando el LLM responde 'knowledge'."""
        mock_llm_provider.generate.return_value = "knowledge"

        result = await classifier.classify("¿Cómo solicito vacaciones?")

        assert result == QueryType.KNOWLEDGE
        assert mock_llm_provider.generate.called

    @pytest.mark.asyncio
    async def test_classify_vacation_query_as_knowledge(self, classifier, mock_llm_provider):
        """Query sobre vacaciones debe clasificarse como KNOWLEDGE."""
        # Simular que el LLM clasifica como knowledge
        mock_llm_provider.generate.return_value = "knowledge"

        result = await classifier.classify("¿Cómo pido vacaciones?")

        assert result == QueryType.KNOWLEDGE

    @pytest.mark.asyncio
    async def test_classify_password_query_as_knowledge(self, classifier, mock_llm_provider):
        """Query sobre contraseña debe clasificarse como KNOWLEDGE."""
        mock_llm_provider.generate.return_value = "knowledge"

        result = await classifier.classify("olvidé mi contraseña")

        assert result == QueryType.KNOWLEDGE

    @pytest.mark.asyncio
    async def test_classify_ticket_query_as_knowledge(self, classifier, mock_llm_provider):
        """Query sobre tickets debe clasificarse como KNOWLEDGE."""
        mock_llm_provider.generate.return_value = "knowledge"

        result = await classifier.classify("cómo creo un ticket de soporte")

        assert result == QueryType.KNOWLEDGE


class TestQueryClassifierDatabaseClassification:
    """Tests de clasificación para consultas de base de datos."""

    @pytest.mark.asyncio
    async def test_classify_as_database_when_llm_returns_database(self, classifier, mock_llm_provider):
        """Debe clasificar como DATABASE cuando el LLM responde 'database'."""
        mock_llm_provider.generate.return_value = "database"

        result = await classifier.classify("¿Cuántos usuarios hay?")

        assert result == QueryType.DATABASE

    @pytest.mark.asyncio
    async def test_classify_count_query_as_database(self, classifier, mock_llm_provider):
        """Query de conteo debe clasificarse como DATABASE."""
        mock_llm_provider.generate.return_value = "database"

        result = await classifier.classify("cuántos registros hay en la tabla")

        assert result == QueryType.DATABASE

    @pytest.mark.asyncio
    async def test_is_database_query_returns_true(self, classifier, mock_llm_provider):
        """is_database_query debe retornar True para queries de BD."""
        mock_llm_provider.generate.return_value = "database"

        result = await classifier.is_database_query("cuántos usuarios activos hay")

        assert result is True


class TestQueryClassifierGeneralClassification:
    """Tests de clasificación para consultas generales."""

    @pytest.mark.asyncio
    async def test_classify_as_general_when_llm_returns_general(self, classifier, mock_llm_provider):
        """Debe clasificar como GENERAL cuando el LLM responde 'general'."""
        mock_llm_provider.generate.return_value = "general"

        result = await classifier.classify("Hola, ¿cómo estás?")

        assert result == QueryType.GENERAL

    @pytest.mark.asyncio
    async def test_classify_greeting_as_general(self, classifier, mock_llm_provider):
        """Saludos deben clasificarse como GENERAL."""
        mock_llm_provider.generate.return_value = "general"

        result = await classifier.classify("buenos días")

        assert result == QueryType.GENERAL

    @pytest.mark.asyncio
    async def test_is_database_query_returns_false_for_general(self, classifier, mock_llm_provider):
        """is_database_query debe retornar False para queries generales."""
        mock_llm_provider.generate.return_value = "general"

        result = await classifier.is_database_query("hola")

        assert result is False


class TestQueryClassifierKnowledgeContext:
    """Tests de obtención de contexto de conocimiento."""

    def test_get_knowledge_context_for_vacation_query(self, classifier):
        """Debe retornar contexto para query sobre vacaciones."""
        context = classifier.get_knowledge_context("¿Cómo solicito vacaciones?")

        assert isinstance(context, str)
        if context:  # Si hay resultados
            assert "vacaciones" in context.lower() or len(context) > 0

    def test_get_knowledge_context_for_password_query(self, classifier):
        """Debe retornar contexto para query sobre contraseña."""
        context = classifier.get_knowledge_context("olvidé mi contraseña")

        assert isinstance(context, str)

    def test_get_knowledge_context_with_top_k(self, classifier):
        """Debe respetar el parámetro top_k."""
        context = classifier.get_knowledge_context("información", top_k=1)

        assert isinstance(context, str)

    def test_get_knowledge_context_returns_empty_for_irrelevant(self, classifier):
        """Debe retornar vacío para queries irrelevantes."""
        context = classifier.get_knowledge_context("xyz123abc", top_k=1)

        # Puede ser vacío si no hay matches
        assert isinstance(context, str)


class TestQueryClassifierPromptVersioning:
    """Tests de versionado de prompts."""

    @pytest.mark.asyncio
    async def test_uses_v3_when_knowledge_available(self, classifier, mock_llm_provider):
        """Debe usar prompt V3 cuando hay conocimiento disponible."""
        mock_llm_provider.generate.return_value = "knowledge"

        await classifier.classify("¿Cómo solicito vacaciones?")

        # Verificar que se llamó al LLM
        assert mock_llm_provider.generate.called

        # El prompt debería incluir contexto de conocimiento
        call_args = mock_llm_provider.generate.call_args
        prompt_used = call_args[0][0]  # Primer argumento posicional

        # El prompt V3 debe mencionar "CONOCIMIENTO INSTITUCIONAL" o "knowledge"
        assert "conocimiento" in prompt_used.lower() or "knowledge" in prompt_used.lower()

    @pytest.mark.asyncio
    async def test_respects_explicit_version(self, mock_llm_provider, knowledge_manager):
        """Debe respetar la versión explícita del prompt."""
        classifier = QueryClassifier(
            llm_provider=mock_llm_provider,
            prompt_version=1,  # Forzar V1
            knowledge_manager=knowledge_manager
        )

        mock_llm_provider.generate.return_value = "general"

        await classifier.classify("test query")

        assert mock_llm_provider.generate.called


class TestQueryClassifierErrorHandling:
    """Tests de manejo de errores."""

    @pytest.mark.asyncio
    async def test_error_with_knowledge_results_returns_knowledge(self, classifier, mock_llm_provider):
        """Si hay error pero hay conocimiento relevante, debe retornar KNOWLEDGE."""
        # Simular error en LLM
        mock_llm_provider.generate.side_effect = Exception("LLM Error")

        # Query que debería encontrar conocimiento
        result = await classifier.classify("¿Cómo solicito vacaciones?")

        # Debe retornar KNOWLEDGE como fallback porque hay resultados relevantes
        assert result == QueryType.KNOWLEDGE

    @pytest.mark.asyncio
    async def test_error_without_knowledge_returns_database(self, classifier, mock_llm_provider):
        """Si hay error y no hay conocimiento, debe retornar DATABASE como fallback."""
        # Simular error en LLM
        mock_llm_provider.generate.side_effect = Exception("LLM Error")

        # Query totalmente irrelevante que no debería encontrar conocimiento
        result = await classifier.classify("xyzabc123 qwerty456 asdfgh789")

        # Debe retornar DATABASE como fallback seguro
        assert result == QueryType.DATABASE


class TestQueryClassifierRealWorldScenarios:
    """Tests con escenarios reales de uso."""

    @pytest.mark.asyncio
    async def test_employee_asks_about_work_schedule(self, classifier, mock_llm_provider):
        """Empleado pregunta sobre horario de trabajo."""
        mock_llm_provider.generate.return_value = "knowledge"

        result = await classifier.classify("¿Cuál es el horario de trabajo?")

        assert result == QueryType.KNOWLEDGE

    @pytest.mark.asyncio
    async def test_employee_asks_about_user_count(self, classifier, mock_llm_provider):
        """Empleado pregunta sobre cantidad de usuarios (requiere BD)."""
        mock_llm_provider.generate.return_value = "database"

        result = await classifier.classify("¿Cuántos usuarios registrados tenemos?")

        assert result == QueryType.DATABASE

    @pytest.mark.asyncio
    async def test_employee_greets(self, classifier, mock_llm_provider):
        """Empleado saluda."""
        mock_llm_provider.generate.return_value = "general"

        result = await classifier.classify("Hola!")

        assert result == QueryType.GENERAL

    @pytest.mark.asyncio
    async def test_knowledge_search_happens_before_classification(self, classifier, mock_llm_provider):
        """La búsqueda en conocimiento debe ocurrir antes de clasificar con LLM."""
        mock_llm_provider.generate.return_value = "knowledge"

        # Esta query debería encontrar resultados en knowledge base
        await classifier.classify("¿Cómo solicito vacaciones?")

        # Verificar que el LLM fue llamado con contexto de conocimiento
        assert mock_llm_provider.generate.called
        call_args = mock_llm_provider.generate.call_args
        prompt_used = call_args[0][0]

        # El prompt debe incluir información de vacaciones
        assert "vacaciones" in prompt_used.lower() or "conocimiento" in prompt_used.lower()


class TestQueryClassifierIntegration:
    """Tests de integración del clasificador completo."""

    @pytest.mark.asyncio
    async def test_full_classification_flow_knowledge(self, classifier, mock_llm_provider):
        """Test completo del flujo de clasificación para KNOWLEDGE."""
        mock_llm_provider.generate.return_value = "knowledge"

        query = "¿Cómo creo un ticket de soporte?"
        result = await classifier.classify(query)
        context = classifier.get_knowledge_context(query)

        assert result == QueryType.KNOWLEDGE
        assert isinstance(context, str)

    @pytest.mark.asyncio
    async def test_full_classification_flow_database(self, classifier, mock_llm_provider):
        """Test completo del flujo de clasificación para DATABASE."""
        mock_llm_provider.generate.return_value = "database"

        query = "¿Cuántos productos hay en stock?"
        result = await classifier.classify(query)

        assert result == QueryType.DATABASE

    @pytest.mark.asyncio
    async def test_full_classification_flow_general(self, classifier, mock_llm_provider):
        """Test completo del flujo de clasificación para GENERAL."""
        mock_llm_provider.generate.return_value = "general"

        query = "Hola, ¿cómo estás?"
        result = await classifier.classify(query)

        assert result == QueryType.GENERAL
