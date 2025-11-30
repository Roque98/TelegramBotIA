"""
Tests para tools_handlers - Integración de Tools con Telegram.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch, ANY
from telegram import Update, User, Message, Chat
from telegram.ext import ContextTypes
from src.bot.handlers.tools_handlers import (
    handle_ia_command,
    handle_query_command,
    register_tools_handlers
)


@pytest.fixture
def mock_update():
    """Crear update mock."""
    update = MagicMock(spec=Update)
    update.effective_user = MagicMock(spec=User)
    update.effective_user.id = 123
    update.message = MagicMock(spec=Message)
    update.message.text = "/ia ¿Cuántos usuarios hay?"
    update.message.reply_text = AsyncMock()
    return update


@pytest.fixture
def mock_context():
    """Crear context mock."""
    context = MagicMock(spec=ContextTypes.DEFAULT_TYPE)
    context.bot_data = {
        'db_manager': MagicMock(),
        'agent': MagicMock()
    }
    context.user_data = {}
    return context


class TestHandleIACommand:
    """Tests para handle_ia_command."""

    @pytest.mark.asyncio
    async def test_ia_command_no_query(self, mock_update, mock_context):
        """Test comando /ia sin query."""
        mock_update.message.text = "/ia"

        await handle_ia_command(mock_update, mock_context)

        # Verificar que se envió mensaje de ayuda
        mock_update.message.reply_text.assert_called_once()
        call_args = mock_update.message.reply_text.call_args[0][0]
        assert "proporciona una consulta" in call_args.lower()

    @pytest.mark.asyncio
    async def test_ia_command_no_components(self, mock_update, mock_context):
        """Test comando /ia sin componentes en bot_data."""
        mock_context.bot_data = {}

        await handle_ia_command(mock_update, mock_context)

        # Verificar que se envió mensaje de error
        mock_update.message.reply_text.assert_called_once()
        call_args = mock_update.message.reply_text.call_args[0][0]
        assert "error de configuración" in call_args.lower()

    @pytest.mark.asyncio
    async def test_ia_command_uses_status_message_correctly(self, mock_update, mock_context):
        """Test que handle_ia_command usa StatusMessage correctamente."""
        mock_update.message.text = "/ia ¿Cuántos usuarios hay?"

        # Mock StatusMessage
        with patch('src.bot.handlers.tools_handlers.StatusMessage') as mock_status_class:
            mock_status = MagicMock()
            mock_status.start = AsyncMock()
            mock_status.complete = AsyncMock()
            mock_status.error = AsyncMock()
            mock_status_class.return_value = mock_status

            # Mock ToolOrchestrator y sus dependencias
            with patch('src.bot.handlers.tools_handlers.get_registry') as mock_get_registry, \
                 patch('src.bot.handlers.tools_handlers.ToolOrchestrator') as mock_orchestrator_class, \
                 patch('src.bot.handlers.tools_handlers.ExecutionContextBuilder') as mock_builder_class, \
                 patch('src.bot.handlers.tools_handlers.UserManager'), \
                 patch('src.bot.handlers.tools_handlers.PermissionChecker'):

                # Configurar mock de session
                mock_context.bot_data['db_manager'].get_session = MagicMock()
                mock_session = MagicMock()
                mock_session.__enter__ = MagicMock(return_value=mock_session)
                mock_session.__exit__ = MagicMock(return_value=False)
                mock_context.bot_data['db_manager'].get_session.return_value = mock_session

                # Configurar mock de ExecutionContextBuilder
                mock_builder = MagicMock()
                mock_builder.with_telegram.return_value = mock_builder
                mock_builder.with_db_manager.return_value = mock_builder
                mock_builder.with_llm_agent.return_value = mock_builder
                mock_builder.with_user_manager.return_value = mock_builder
                mock_builder.with_permission_checker.return_value = mock_builder
                mock_builder.build.return_value = MagicMock()
                mock_builder_class.return_value = mock_builder

                # Configurar mock de ToolOrchestrator
                mock_orchestrator = MagicMock()
                mock_result = MagicMock()
                mock_result.success = True
                mock_result.data = "Respuesta de prueba"
                mock_result.execution_time_ms = 100.0
                mock_orchestrator.execute_command = AsyncMock(return_value=mock_result)
                mock_orchestrator_class.return_value = mock_orchestrator

                # Ejecutar handler
                await handle_ia_command(mock_update, mock_context)

                # Verificar que StatusMessage se usó correctamente
                mock_status_class.assert_called_once_with(
                    mock_update,
                    initial_message="🔍 Analizando tu consulta..."
                )
                mock_status.start.assert_called_once()
                mock_status.complete.assert_called_once_with("Respuesta de prueba")
                mock_status.error.assert_not_called()


class TestHandleQueryCommand:
    """Tests para handle_query_command."""

    @pytest.mark.asyncio
    async def test_query_command_delegates_to_ia(self, mock_update, mock_context):
        """Test que /query delega a /ia."""
        mock_update.message.text = "/query test query"

        with patch('src.bot.handlers.tools_handlers.handle_ia_command') as mock_ia:
            mock_ia.return_value = AsyncMock()
            await handle_query_command(mock_update, mock_context)

            # Verificar que se llamó a handle_ia_command
            mock_ia.assert_called_once()


class TestRegisterToolsHandlers:
    """Tests para register_tools_handlers."""

    def test_register_handlers(self):
        """Test registro de handlers."""
        mock_app = MagicMock()

        register_tools_handlers(mock_app)

        # Verificar que se agregaron 2 handlers (/ia y /query)
        assert mock_app.add_handler.call_count == 2
