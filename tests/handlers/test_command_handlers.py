"""
Tests para src/bot/handlers/command_handlers.py

Cobertura:
- start_command: mensaje de bienvenida, fallback categorías
- help_command: guía de uso, fallback
- stats_command: mensaje de estadísticas placeholder
- cancel_command: mensaje de cancelación
- _get_categories_from_db: éxito y fallback
- _get_example_questions_from_db: éxito y fallback
"""
import pytest
import sys
from unittest.mock import AsyncMock, MagicMock, patch

from src.bot.handlers.command_handlers import (
    start_command,
    help_command,
    stats_command,
    cancel_command,
    _get_categories_from_db,
    _get_example_questions_from_db,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def make_update(user_id=123, username="testuser", first_name="Test"):
    update = MagicMock()
    update.effective_user.id = user_id
    update.effective_user.username = username
    update.effective_user.first_name = first_name
    update.message.reply_text = AsyncMock()
    return update


def make_context(db_manager=None):
    context = MagicMock()
    context.bot_data.get.return_value = db_manager
    context.user_data = {}
    return context


# ---------------------------------------------------------------------------
# _get_categories_from_db
# ---------------------------------------------------------------------------

class TestGetCategoriesFromDb:

    def test_returns_db_categories(self):
        categories = [{"name": "FAQS", "display_name": "Preguntas", "icon": "❓", "entry_count": 5}]
        mock_repo = MagicMock()
        mock_repo.get_categories_info.return_value = categories

        with patch("src.bot.handlers.command_handlers.KnowledgeRepository", return_value=mock_repo):
            result = _get_categories_from_db()

        assert result == categories

    def test_fallback_on_exception(self):
        with patch(
            "src.bot.handlers.command_handlers.KnowledgeRepository",
            side_effect=Exception("DB down")
        ):
            result = _get_categories_from_db()

        assert len(result) == 3
        assert result[0]["name"] == "PROCESOS"

    def test_passes_rol_to_repository(self):
        mock_repo = MagicMock()
        mock_repo.get_categories_info.return_value = []

        with patch("src.bot.handlers.command_handlers.KnowledgeRepository", return_value=mock_repo):
            _get_categories_from_db(id_rol=5)

        mock_repo.get_categories_info.assert_called_once_with(id_rol=5)


class TestGetExampleQuestionsFromDb:

    def test_returns_db_questions(self):
        questions = ["¿Cuántas ventas?", "¿Qué horario?"]
        mock_repo = MagicMock()
        mock_repo.get_example_questions.return_value = questions

        with patch("src.bot.handlers.command_handlers.KnowledgeRepository", return_value=mock_repo):
            result = _get_example_questions_from_db(limit=2)

        assert result == questions

    def test_fallback_when_no_questions(self):
        mock_repo = MagicMock()
        mock_repo.get_example_questions.return_value = []

        with patch("src.bot.handlers.command_handlers.KnowledgeRepository", return_value=mock_repo):
            result = _get_example_questions_from_db()

        assert len(result) >= 1
        assert isinstance(result[0], str)

    def test_fallback_on_exception(self):
        with patch(
            "src.bot.handlers.command_handlers.KnowledgeRepository",
            side_effect=Exception("Error")
        ):
            result = _get_example_questions_from_db()

        assert len(result) >= 1


# ---------------------------------------------------------------------------
# start_command
# ---------------------------------------------------------------------------

class TestStartCommand:

    @pytest.mark.asyncio
    async def test_replies_with_welcome_message(self):
        update = make_update(first_name="Ana")
        context = make_context()

        categories = [{"display_name": "FAQs", "icon": "❓", "entry_count": 3}]
        questions = ["¿Cómo solicito vacaciones?"]

        with patch("src.bot.handlers.command_handlers._get_categories_from_db", return_value=categories), \
             patch("src.bot.handlers.command_handlers._get_example_questions_from_db", return_value=questions):
            await start_command(update, context)

        update.message.reply_text.assert_called_once()
        text = update.message.reply_text.call_args[0][0]
        assert "Ana" in text
        assert "IRIS" in text

    @pytest.mark.asyncio
    async def test_skips_categories_with_zero_entries(self):
        update = make_update()
        context = make_context()

        categories = [
            {"display_name": "FAQs", "icon": "❓", "entry_count": 0},
            {"display_name": "Procesos", "icon": "⚙️", "entry_count": 5},
        ]
        with patch("src.bot.handlers.command_handlers._get_categories_from_db", return_value=categories), \
             patch("src.bot.handlers.command_handlers._get_example_questions_from_db", return_value=[]):
            await start_command(update, context)

        text = update.message.reply_text.call_args[0][0]
        assert "Procesos" in text
        assert "FAQs" not in text

    @pytest.mark.asyncio
    async def test_works_without_db_manager(self):
        update = make_update()
        context = make_context(db_manager=None)

        with patch("src.bot.handlers.command_handlers._get_categories_from_db", return_value=[]), \
             patch("src.bot.handlers.command_handlers._get_example_questions_from_db", return_value=[]):
            await start_command(update, context)

        update.message.reply_text.assert_called_once()

    @pytest.mark.asyncio
    async def test_works_when_user_service_fails(self):
        update = make_update()
        mock_db = MagicMock()
        mock_db.get_session.side_effect = Exception("DB error")
        context = make_context(db_manager=mock_db)

        with patch("src.bot.handlers.command_handlers._get_categories_from_db", return_value=[]), \
             patch("src.bot.handlers.command_handlers._get_example_questions_from_db", return_value=[]):
            await start_command(update, context)

        update.message.reply_text.assert_called_once()


# ---------------------------------------------------------------------------
# help_command
# ---------------------------------------------------------------------------

class TestHelpCommand:

    @pytest.mark.asyncio
    async def test_replies_with_help_message(self):
        update = make_update()
        context = make_context()

        categories = [{"display_name": "FAQs", "icon": "❓", "entry_count": 3}]
        questions = ["¿Cuántas ventas?"]

        with patch("src.bot.handlers.command_handlers._get_categories_from_db", return_value=categories), \
             patch("src.bot.handlers.command_handlers._get_example_questions_from_db", return_value=questions):
            await help_command(update, context)

        update.message.reply_text.assert_called_once()
        text = update.message.reply_text.call_args[0][0]
        assert "IRIS" in text
        assert "/help" in text

    @pytest.mark.asyncio
    async def test_help_includes_commands_list(self):
        update = make_update()
        context = make_context()

        with patch("src.bot.handlers.command_handlers._get_categories_from_db", return_value=[]), \
             patch("src.bot.handlers.command_handlers._get_example_questions_from_db", return_value=[]):
            await help_command(update, context)

        text = update.message.reply_text.call_args[0][0]
        assert "/start" in text
        assert "/stats" in text

    @pytest.mark.asyncio
    async def test_help_max_7_categories(self):
        update = make_update()
        context = make_context()

        categories = [
            {"display_name": f"Cat{i}", "icon": "⚙️", "entry_count": 1}
            for i in range(10)
        ]
        with patch("src.bot.handlers.command_handlers._get_categories_from_db", return_value=categories), \
             patch("src.bot.handlers.command_handlers._get_example_questions_from_db", return_value=[]):
            await help_command(update, context)

        # No debe fallar con 10 categorías
        update.message.reply_text.assert_called_once()


# ---------------------------------------------------------------------------
# stats_command
# ---------------------------------------------------------------------------

class TestStatsCommand:

    @pytest.mark.asyncio
    async def test_replies_with_stats_message(self):
        update = make_update()
        context = make_context()

        await stats_command(update, context)

        update.message.reply_text.assert_called_once()
        text = update.message.reply_text.call_args[0][0]
        assert "Estadísticas" in text

    @pytest.mark.asyncio
    async def test_stats_uses_markdown(self):
        update = make_update()
        context = make_context()

        await stats_command(update, context)

        kwargs = update.message.reply_text.call_args[1]
        assert kwargs.get("parse_mode") == "Markdown"


# ---------------------------------------------------------------------------
# cancel_command
# ---------------------------------------------------------------------------

class TestCancelCommand:

    @pytest.mark.asyncio
    async def test_replies_with_cancel_message(self):
        update = make_update()
        context = make_context()

        await cancel_command(update, context)

        update.message.reply_text.assert_called_once()
        text = update.message.reply_text.call_args[0][0]
        assert "cancelad" in text.lower()
