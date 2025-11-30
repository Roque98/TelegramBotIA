"""
Tests unitarios para QueryTool.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from src.tools.builtin.query_tool import QueryTool
from src.tools.tool_base import ToolResult, ToolCategory
from src.tools.execution_context import ExecutionContext


class TestQueryTool:
    """Tests para QueryTool."""

    @pytest.fixture
    def query_tool(self):
        """Crear instancia de QueryTool."""
        return QueryTool()

    @pytest.fixture
    def mock_context(self):
        """Crear contexto mock con LLMAgent."""
        context = MagicMock(spec=ExecutionContext)

        # Mock LLMAgent
        mock_llm_agent = AsyncMock()
        mock_llm_agent.process_query = AsyncMock(return_value="Respuesta de prueba")

        context.llm_agent = mock_llm_agent
        context.validate_required_components = MagicMock(return_value=(True, None))

        return context

    def test_metadata(self, query_tool):
        """Test metadatos del tool."""
        assert query_tool.name == "query"
        assert query_tool.description == "Consultar base de datos en lenguaje natural"
        assert "/ia" in query_tool.commands
        assert "/query" in query_tool.commands
        assert query_tool.category == ToolCategory.DATABASE
        assert query_tool.requires_auth is True
        assert "/ia" in query_tool.required_permissions

    def test_parameters(self, query_tool):
        """Test parámetros del tool."""
        params = query_tool.get_parameters()

        assert len(params) == 1
        assert params[0].name == "query"
        assert params[0].required is True
        assert params[0].validation_rules["min_length"] == 3
        assert params[0].validation_rules["max_length"] == 1000

    def test_validate_parameters_valid(self, query_tool):
        """Test validación de parámetros válidos."""
        params = {"query": "¿Cuántos usuarios hay?"}

        is_valid, error = query_tool.validate_parameters(params)
        assert is_valid is True
        assert error is None

    def test_validate_parameters_too_short(self, query_tool):
        """Test validación con query muy corta."""
        params = {"query": "ab"}

        is_valid, error = query_tool.validate_parameters(params)
        assert is_valid is False
        assert "al menos 3 caracteres" in error

    def test_validate_parameters_too_long(self, query_tool):
        """Test validación con query muy larga."""
        params = {"query": "a" * 1001}

        is_valid, error = query_tool.validate_parameters(params)
        assert is_valid is False
        assert "máximo 1000 caracteres" in error

    def test_validate_parameters_missing_query(self, query_tool):
        """Test validación sin parámetro query."""
        params = {}

        is_valid, error = query_tool.validate_parameters(params)
        assert is_valid is False
        assert "requerido" in error
        assert "query" in error

    @pytest.mark.asyncio
    async def test_execute_success(self, query_tool, mock_context):
        """Test ejecución exitosa."""
        params = {"query": "¿Cuántos usuarios hay?"}

        result = await query_tool.execute(
            user_id=123,
            params=params,
            context=mock_context
        )

        assert result.success is True
        assert result.data == "Respuesta de prueba"
        assert result.error is None
        assert result.metadata["user_id"] == 123
        assert result.metadata["tool_version"] == "2.0.0"

    @pytest.mark.asyncio
    async def test_execute_no_llm_agent(self, query_tool):
        """Test ejecución sin LLMAgent disponible."""
        context = MagicMock(spec=ExecutionContext)
        context.llm_agent = None
        context.validate_required_components = MagicMock(
            return_value=(False, "LLMAgent no disponible")
        )

        params = {"query": "test"}

        result = await query_tool.execute(
            user_id=123,
            params=params,
            context=context
        )

        assert result.success is False
        assert "no está disponible" in result.user_friendly_error

    @pytest.mark.asyncio
    async def test_execute_llm_error(self, query_tool, mock_context):
        """Test ejecución con error del LLM."""
        # Configurar LLMAgent para lanzar excepción
        mock_context.llm_agent.process_query = AsyncMock(
            side_effect=Exception("Error de conexión")
        )

        params = {"query": "test"}

        result = await query_tool.execute(
            user_id=123,
            params=params,
            context=mock_context
        )

        assert result.success is False
        assert result.error == "Error de conexión"
        assert "No pude procesar tu consulta" in result.user_friendly_error

    @pytest.mark.asyncio
    async def test_execute_calls_llm_agent(self, query_tool, mock_context):
        """Test que execute llama correctamente al LLMAgent."""
        params = {"query": "¿Cuántos usuarios hay registrados?"}

        await query_tool.execute(
            user_id=123,
            params=params,
            context=mock_context
        )

        # Verificar que se llamó al LLMAgent con la query correcta
        mock_context.llm_agent.process_query.assert_called_once_with(
            "¿Cuántos usuarios hay registrados?"
        )

    @pytest.mark.asyncio
    async def test_execute_metadata_includes_query_info(self, query_tool, mock_context):
        """Test que metadata incluye información de la query."""
        params = {"query": "test query"}

        result = await query_tool.execute(
            user_id=456,
            params=params,
            context=mock_context
        )

        assert "query_length" in result.metadata
        assert result.metadata["query_length"] == len("test query")
        assert result.metadata["user_id"] == 456

    def test_tool_version(self, query_tool):
        """Test que la versión del tool es 2.0.0."""
        metadata = query_tool.get_metadata()
        assert metadata.version == "2.0.0"


class TestIACommandHandler:
    """Tests para IACommandHandler."""

    @pytest.fixture
    def mock_components(self):
        """Crear componentes mock."""
        tool_orchestrator = AsyncMock()
        tool_orchestrator.execute_command = AsyncMock(
            return_value=ToolResult.success_result("Respuesta")
        )

        db_manager = MagicMock()
        llm_agent = MagicMock()

        return tool_orchestrator, db_manager, llm_agent

    @pytest.fixture
    def handler(self, mock_components):
        """Crear handler."""
        from src.tools.builtin.query_tool import IACommandHandler

        orchestrator, db_manager, llm_agent = mock_components
        return IACommandHandler(orchestrator, db_manager, llm_agent)

    @pytest.fixture
    def mock_update(self):
        """Crear update mock de Telegram."""
        update = MagicMock()
        update.effective_user.id = 123
        update.message.text = "/ia ¿Cuántos usuarios hay?"
        update.message.reply_text = AsyncMock()
        return update

    @pytest.fixture
    def mock_telegram_context(self):
        """Crear context mock de Telegram."""
        return MagicMock()

    @pytest.mark.asyncio
    async def test_handle_ia_command_success(
        self,
        handler,
        mock_update,
        mock_telegram_context
    ):
        """Test comando /ia exitoso."""
        with patch('src.utils.status_message.StatusMessage') as mock_status:
            mock_status_instance = AsyncMock()
            mock_status.return_value = mock_status_instance

            await handler.handle_ia_command(mock_update, mock_telegram_context)

            # Verificar que se envió respuesta
            mock_update.message.reply_text.assert_called_once()

            # Verificar que se eliminó mensaje de estado
            mock_status_instance.delete.assert_called_once()

    @pytest.mark.asyncio
    async def test_handle_ia_command_no_query(
        self,
        handler,
        mock_update,
        mock_telegram_context
    ):
        """Test comando /ia sin query."""
        mock_update.message.text = "/ia"

        await handler.handle_ia_command(mock_update, mock_telegram_context)

        # Verificar mensaje de error
        call_args = mock_update.message.reply_text.call_args[0][0]
        assert "proporciona una consulta" in call_args.lower()

    @pytest.mark.asyncio
    async def test_handle_ia_command_error(
        self,
        handler,
        mock_update,
        mock_telegram_context,
        mock_components
    ):
        """Test comando /ia con error."""
        orchestrator, _, _ = mock_components
        orchestrator.execute_command = AsyncMock(
            side_effect=Exception("Error de prueba")
        )

        with patch('src.utils.status_message.StatusMessage') as mock_status:
            mock_status_instance = AsyncMock()
            mock_status.return_value = mock_status_instance

            await handler.handle_ia_command(mock_update, mock_telegram_context)

            # Verificar que se envió mensaje de error
            mock_update.message.reply_text.assert_called()
            call_args = mock_update.message.reply_text.call_args[0][0]
            assert "error" in call_args.lower()
