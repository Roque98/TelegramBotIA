"""
Tests para tools_handlers - Integración de Tools con Telegram.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
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
