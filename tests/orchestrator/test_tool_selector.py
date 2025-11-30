"""
Tests para ToolSelector - Selección automática de tools.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from src.orchestrator.tool_selector import ToolSelector, ToolSelectionResult
from src.tools import BaseTool, ToolMetadata, ToolParameter, ToolResult


@pytest.fixture
def mock_llm_provider():
    """Crear mock de LLM provider."""
    provider = MagicMock()
    provider.generate = AsyncMock()
    return provider


@pytest.fixture
def mock_registry():
    """Crear mock de registry con tools de prueba."""
    # Crear QueryTool mock
    query_tool = MagicMock(spec=BaseTool)
    query_tool.name = "query"

    # Crear metadata sin parameters (parameters se definen en el tool directamente)
    metadata = ToolMetadata(
        name="query",
        description="Herramienta para consultas a la base de datos",
        commands=["/ia", "/query"],
        category="database"
    )

    # Agregar parámetros al metadata manualmente
    metadata.parameters = {
        "query": ToolParameter(
            name="query",
            type="string",
            description="Consulta del usuario",
            required=True
        )
    }

    query_tool.get_metadata.return_value = metadata

    # Crear mock del registry
    registry = MagicMock()
    registry.get_all_tools.return_value = [query_tool]
    registry.get_tool_by_name.return_value = query_tool

    return registry


@pytest.fixture
def tool_selector(mock_llm_provider, mock_registry):
    """Crear instancia de ToolSelector con mocks."""
    with patch('src.orchestrator.tool_selector.get_registry', return_value=mock_registry):
        selector = ToolSelector(mock_llm_provider)
        return selector


class TestToolSelectionResult:
    """Tests para ToolSelectionResult."""

    def test_create_result(self):
        """Test crear resultado de selección."""
        result = ToolSelectionResult(
            selected_tool="query",
            confidence=0.9,
            reasoning="Consulta de datos"
        )

        assert result.selected_tool == "query"
        assert result.confidence == 0.9
        assert result.reasoning == "Consulta de datos"
        assert result.has_selection is True
        assert result.fallback_used is False

    def test_result_without_selection(self):
        """Test resultado sin selección."""
        result = ToolSelectionResult()

        assert result.selected_tool is None
        assert result.confidence == 0.0
        assert result.has_selection is False

    def test_result_with_fallback(self):
        """Test resultado con fallback."""
        result = ToolSelectionResult(
            selected_tool="query",
            confidence=0.3,
            fallback_used=True
        )

        assert result.has_selection is True
        assert result.fallback_used is True

    def test_result_repr(self):
        """Test representación de resultado."""
        result = ToolSelectionResult(selected_tool="query", confidence=0.85)
        repr_str = repr(result)

        assert "query" in repr_str
        assert "0.85" in repr_str


class TestToolSelector:
    """Tests para ToolSelector."""

    def test_initialization(self, tool_selector):
        """Test inicialización correcta."""
        assert tool_selector.llm_provider is not None
        assert tool_selector.prompt_manager is not None
        assert tool_selector.registry is not None

    @pytest.mark.asyncio
    async def test_select_tool_json_response(self, tool_selector, mock_llm_provider):
        """Test selección con respuesta JSON válida."""
        # Configurar respuesta JSON del LLM
        mock_llm_provider.generate.return_value = """
        {
            "tool": "query",
            "confidence": 0.9,
            "reasoning": "El usuario solicita datos de la base de datos"
        }
        """

        result = await tool_selector.select_tool("¿Cuántos usuarios hay?")

        assert result.has_selection is True
        assert result.selected_tool == "query"
        assert result.confidence == 0.9
        assert "datos" in result.reasoning.lower()
        assert result.fallback_used is False

    @pytest.mark.asyncio
    async def test_select_tool_case_insensitive(self, tool_selector, mock_llm_provider):
        """Test que la selección sea case-insensitive."""
        # El LLM devuelve nombre en mayúsculas
        mock_llm_provider.generate.return_value = """
        {
            "tool": "QUERY",
            "confidence": 0.85,
            "reasoning": "Data query needed"
        }
        """

        result = await tool_selector.select_tool("Show me users")

        assert result.has_selection is True
        assert result.selected_tool == "query"  # Normalizado

    @pytest.mark.asyncio
    async def test_select_tool_simple_parse(self, tool_selector, mock_llm_provider):
        """Test parseo simple cuando falla JSON."""
        # Respuesta sin JSON válido pero menciona el tool
        mock_llm_provider.generate.return_value = "I recommend using the query tool for this"

        result = await tool_selector.select_tool("Get users")

        assert result.has_selection is True
        assert result.selected_tool == "query"
        assert result.confidence == 0.5  # Confianza media
        assert result.fallback_used is True

    @pytest.mark.asyncio
    async def test_select_tool_invalid_tool_name(self, tool_selector, mock_llm_provider):
        """Test cuando el LLM sugiere un tool que no existe."""
        mock_llm_provider.generate.return_value = """
        {
            "tool": "nonexistent",
            "confidence": 0.8,
            "reasoning": "Trying to use unknown tool"
        }
        """

        result = await tool_selector.select_tool("Do something")

        # Debe fallar gracefully
        assert result.has_selection is False

    @pytest.mark.asyncio
    async def test_select_tool_no_tools_available(self, tool_selector, mock_llm_provider, mock_registry):
        """Test cuando no hay tools disponibles."""
        mock_registry.get_all_tools.return_value = []

        result = await tool_selector.select_tool("Test query")

        assert result.has_selection is False
        assert "no hay tools" in result.reasoning.lower()

    @pytest.mark.asyncio
    async def test_select_tool_error_uses_fallback(self, tool_selector, mock_llm_provider):
        """Test que usa fallback cuando hay error."""
        # Simular error en LLM
        mock_llm_provider.generate.side_effect = Exception("LLM error")

        result = await tool_selector.select_tool("Test query")

        assert result.has_selection is True
        assert result.selected_tool == "query"  # Fallback tool
        assert result.fallback_used is True
        assert result.confidence < 0.5

    @pytest.mark.asyncio
    async def test_select_tool_with_specific_tools(self, tool_selector, mock_llm_provider):
        """Test selección con lista específica de tools."""
        mock_llm_provider.generate.return_value = """
        {
            "tool": "query",
            "confidence": 0.95,
            "reasoning": "Perfect match"
        }
        """

        result = await tool_selector.select_tool(
            "Get data",
            available_tools=["query"]
        )

        assert result.has_selection is True
        assert result.selected_tool == "query"

    def test_generate_tools_description(self, tool_selector):
        """Test generación de descripción de tools."""
        tools = tool_selector._get_available_tools()
        description = tool_selector._generate_tools_description(tools)

        assert "query" in description.lower()
        assert "database" in description.lower()
        assert "/ia" in description or "/query" in description

    def test_get_stats(self, tool_selector):
        """Test obtener estadísticas del selector."""
        stats = tool_selector.get_stats()

        assert "tools_available" in stats
        assert isinstance(stats["tools_available"], int)
        assert stats["tools_available"] >= 0


class TestToolSelectorIntegration:
    """Tests de integración con componentes reales."""

    @pytest.mark.asyncio
    async def test_full_selection_flow(self, tool_selector, mock_llm_provider):
        """Test flujo completo de selección."""
        # Simular respuesta completa del LLM
        mock_llm_provider.generate.return_value = """
        Based on the user query, I will select the most appropriate tool.

        {
            "tool": "query",
            "confidence": 0.92,
            "reasoning": "The user is asking for database information about users"
        }
        """

        result = await tool_selector.select_tool("¿Cuántos usuarios registrados hay en el sistema?")

        # Verificar que el LLM fue llamado
        assert mock_llm_provider.generate.called
        call_kwargs = mock_llm_provider.generate.call_args[1]
        assert call_kwargs['max_tokens'] == 200

        # Verificar resultado
        assert result.has_selection
        assert result.selected_tool == "query"
        assert result.confidence > 0.9
        assert not result.fallback_used
