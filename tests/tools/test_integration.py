"""
Tests de integración para el sistema de Tools.

Tests end-to-end que verifican la integración completa:
QueryTool -> ToolOrchestrator -> LLMAgent -> DatabaseManager
"""
import pytest
from unittest.mock import AsyncMock, MagicMock
from src.tools import (
    get_registry,
    ToolOrchestrator,
    ExecutionContextBuilder,
    initialize_builtin_tools
)
from src.tools.builtin.query_tool import QueryTool


class TestToolsIntegration:
    """Tests de integración del sistema de Tools."""

    @pytest.fixture(autouse=True)
    def setup_and_teardown(self):
        """Limpiar registry antes y después de cada test."""
        registry = get_registry()
        registry.clear()
        yield
        registry.clear()

    @pytest.fixture
    def mock_llm_agent(self):
        """Crear LLMAgent mock."""
        mock_agent = AsyncMock()
        mock_agent.process_query = AsyncMock(
            return_value="Hay 10 usuarios registrados en el sistema."
        )
        return mock_agent

    @pytest.fixture
    def mock_db_manager(self):
        """Crear DatabaseManager mock."""
        return MagicMock()

    def test_initialize_builtin_tools(self):
        """Test inicialización de tools built-in."""
        registry = get_registry()

        # Inicializar tools
        initialize_builtin_tools()

        # Verificar que QueryTool fue registrado
        assert registry.get_tools_count() > 0

        query_tool = registry.get_tool_by_name("query")
        assert query_tool is not None
        assert query_tool.name == "query"

        # Verificar comandos
        assert registry.get_tool_by_command("/ia") is not None
        assert registry.get_tool_by_command("/query") is not None

    @pytest.mark.asyncio
    async def test_end_to_end_query_execution(self, mock_llm_agent, mock_db_manager):
        """Test ejecución end-to-end de una query."""
        # 1. Inicializar sistema
        registry = get_registry()
        registry.clear()
        initialize_builtin_tools()

        orchestrator = ToolOrchestrator(registry)

        # 2. Crear contexto de ejecución
        context = (
            ExecutionContextBuilder()
            .with_llm_agent(mock_llm_agent)
            .with_db_manager(mock_db_manager)
            .build()
        )

        # 3. Ejecutar query a través del orquestador
        result = await orchestrator.execute_command(
            user_id=123,
            command="/ia",
            params={"query": "¿Cuántos usuarios hay registrados?"},
            context=context
        )

        # 4. Verificar resultado
        assert result.success is True
        assert "10 usuarios" in result.data
        assert result.execution_time_ms is not None

        # 5. Verificar que se llamó al LLMAgent
        mock_llm_agent.process_query.assert_called_once_with(
            "¿Cuántos usuarios hay registrados?"
        )

    @pytest.mark.asyncio
    async def test_query_tool_with_orchestrator(self, mock_llm_agent):
        """Test QueryTool integrado con ToolOrchestrator."""
        # Setup
        registry = get_registry()
        registry.clear()
        query_tool = QueryTool()
        registry.register(query_tool)

        orchestrator = ToolOrchestrator(registry)

        context = (
            ExecutionContextBuilder()
            .with_llm_agent(mock_llm_agent)
            .build()
        )

        # Execute
        result = await orchestrator.execute_command(
            user_id=456,
            command="/query",
            params={"query": "Test query"},
            context=context
        )

        # Assert
        assert result.success is True
        assert result.execution_time_ms is not None

    @pytest.mark.asyncio
    async def test_query_validation_in_orchestrator(self, mock_llm_agent):
        """Test que el orquestador valida parámetros."""
        # Setup
        registry = get_registry()
        registry.clear()
        initialize_builtin_tools()

        orchestrator = ToolOrchestrator(registry)

        context = (
            ExecutionContextBuilder()
            .with_llm_agent(mock_llm_agent)
            .build()
        )

        # Execute con parámetros inválidos (query muy corta)
        result = await orchestrator.execute_command(
            user_id=123,
            command="/ia",
            params={"query": "ab"},  # Menor a min_length=3
            context=context
        )

        # Assert
        assert result.success is False
        assert "al menos 3 caracteres" in result.user_friendly_error

    @pytest.mark.asyncio
    async def test_nonexistent_command(self, mock_llm_agent):
        """Test comando inexistente."""
        # Setup
        registry = get_registry()
        registry.clear()
        initialize_builtin_tools()

        orchestrator = ToolOrchestrator(registry)

        context = (
            ExecutionContextBuilder()
            .with_llm_agent(mock_llm_agent)
            .build()
        )

        # Execute
        result = await orchestrator.execute_command(
            user_id=123,
            command="/nonexistent",
            params={},
            context=context
        )

        # Assert
        assert result.success is False
        assert "no encontrado" in result.error.lower()

    @pytest.mark.asyncio
    async def test_query_without_llm_agent(self):
        """Test query sin LLMAgent disponible."""
        # Setup
        registry = get_registry()
        registry.clear()
        initialize_builtin_tools()

        orchestrator = ToolOrchestrator(registry)

        # Context sin LLMAgent
        context = ExecutionContextBuilder().build()

        # Execute
        result = await orchestrator.execute_command(
            user_id=123,
            command="/ia",
            params={"query": "test"},
            context=context
        )

        # Assert
        assert result.success is False
        assert "no disponible" in result.user_friendly_error.lower()

    def test_tool_discovery(self):
        """Test descubrimiento de tools registrados."""
        from src.tools import get_tool_summary

        # Setup
        registry = get_registry()
        registry.clear()
        initialize_builtin_tools()

        # Get summary
        summary = get_tool_summary()

        # Assert
        assert summary["total_tools"] >= 1
        assert len(summary["commands"]) >= 2  # /ia y /query
        assert "/ia" in summary["commands"]
        assert "/query" in summary["commands"]

        # Verificar información de QueryTool
        query_tool_info = next(
            (t for t in summary["tools"] if t["name"] == "query"),
            None
        )
        assert query_tool_info is not None
        assert query_tool_info["category"] == "database"
        assert query_tool_info["requires_auth"] is True
        assert query_tool_info["version"] == "2.0.0"

    @pytest.mark.asyncio
    async def test_orchestrator_statistics(self, mock_llm_agent):
        """Test estadísticas del orquestador."""
        # Setup
        registry = get_registry()
        registry.clear()
        initialize_builtin_tools()

        orchestrator = ToolOrchestrator(registry)

        context = (
            ExecutionContextBuilder()
            .with_llm_agent(mock_llm_agent)
            .build()
        )

        # Execute multiple queries
        for i in range(3):
            await orchestrator.execute_command(
                user_id=123,
                command="/ia",
                params={"query": f"query {i}"},
                context=context
            )

        # Get stats
        stats = orchestrator.get_stats()

        # Assert
        assert stats["total_executions"] == 3
        assert stats["total_errors"] == 0
        assert stats["success_rate"] == 100.0

    @pytest.mark.asyncio
    async def test_orchestrator_error_tracking(self, mock_llm_agent):
        """Test tracking de errores del orquestador."""
        # Setup con LLMAgent que falla
        mock_llm_agent.process_query = AsyncMock(
            side_effect=Exception("Test error")
        )

        registry = get_registry()
        registry.clear()
        initialize_builtin_tools()

        orchestrator = ToolOrchestrator(registry)

        context = (
            ExecutionContextBuilder()
            .with_llm_agent(mock_llm_agent)
            .build()
        )

        # Execute query que falla
        result = await orchestrator.execute_command(
            user_id=123,
            command="/ia",
            params={"query": "test"},
            context=context
        )

        # Assert
        assert result.success is False

        stats = orchestrator.get_stats()
        assert stats["total_executions"] == 1
        assert stats["total_errors"] == 1
        assert stats["success_rate"] == 0.0
