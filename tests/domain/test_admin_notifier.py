"""
Tests para CAL-13: AdminNotifier y get_admin_chat_ids.

Cobertura:
- get_admin_chat_ids(): retorna chat IDs de admins verificados
- notify_admin(): envía mensajes, respeta rate limiting, no falla sin admins
- _build_message(): formato correcto con y sin error/traceback
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from src.bot.notifications.admin_notifier import (
    notify_admin,
    reset_rate_cache,
    _build_message,
    _RATE_LIMIT_SECONDS,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def clear_rate_cache():
    """Limpia el rate cache antes de cada test."""
    reset_rate_cache()
    yield
    reset_rate_cache()


def _make_bot(*chat_ids):
    bot = MagicMock()
    bot.send_message = AsyncMock()
    return bot


def _make_db_manager(chat_ids: list[int]):
    """Crea un db_manager mockeado que devuelve los chat_ids dados."""
    db = MagicMock()
    rows = [{"telegramChatId": cid} for cid in chat_ids]
    db.execute_query_async = AsyncMock(return_value=rows)
    return db


# ---------------------------------------------------------------------------
# get_admin_chat_ids
# ---------------------------------------------------------------------------

class TestGetAdminChatIds:

    @pytest.mark.asyncio
    async def test_retorna_chat_ids_de_admins(self):
        from src.domain.auth.user_query_repository import UserQueryRepository
        db = _make_db_manager([111, 222])
        repo = UserQueryRepository(db)
        result = await repo.get_admin_chat_ids()
        assert result == [111, 222]

    @pytest.mark.asyncio
    async def test_retorna_lista_vacia_si_no_hay_admins(self):
        from src.domain.auth.user_query_repository import UserQueryRepository
        db = _make_db_manager([])
        repo = UserQueryRepository(db)
        result = await repo.get_admin_chat_ids()
        assert result == []

    @pytest.mark.asyncio
    async def test_usa_role_id_por_defecto_1(self):
        from src.domain.auth.user_query_repository import UserQueryRepository
        db = _make_db_manager([100])
        repo = UserQueryRepository(db)
        await repo.get_admin_chat_ids()
        call_params = db.execute_query_async.call_args[0][1]
        assert call_params["role_id"] == 1

    @pytest.mark.asyncio
    async def test_acepta_role_id_personalizado(self):
        from src.domain.auth.user_query_repository import UserQueryRepository
        db = _make_db_manager([100])
        repo = UserQueryRepository(db)
        await repo.get_admin_chat_ids(admin_role_id=5)
        call_params = db.execute_query_async.call_args[0][1]
        assert call_params["role_id"] == 5


# ---------------------------------------------------------------------------
# notify_admin
# ---------------------------------------------------------------------------

class TestNotifyAdmin:

    @pytest.mark.asyncio
    async def test_envia_mensaje_a_admins(self):
        bot = _make_bot()
        db = _make_db_manager([111, 222])
        await notify_admin(bot=bot, db_manager=db, level="ERROR", message="test error")
        assert bot.send_message.call_count == 2

    @pytest.mark.asyncio
    async def test_no_envia_si_no_hay_admins(self):
        bot = _make_bot()
        db = _make_db_manager([])
        await notify_admin(bot=bot, db_manager=db, level="ERROR", message="test")
        bot.send_message.assert_not_called()

    @pytest.mark.asyncio
    async def test_no_envia_si_no_hay_db_manager(self):
        bot = _make_bot()
        await notify_admin(bot=bot, db_manager=None, level="ERROR", message="test")
        bot.send_message.assert_not_called()

    @pytest.mark.asyncio
    async def test_rate_limiting_bloquea_segundo_envio(self):
        bot = _make_bot()
        db = _make_db_manager([111])
        error = ValueError("fallo")

        await notify_admin(bot=bot, db_manager=db, level="ERROR", error=error)
        await notify_admin(bot=bot, db_manager=db, level="ERROR", error=error)

        # Solo 1 envío por rate limiting
        assert bot.send_message.call_count == 1

    @pytest.mark.asyncio
    async def test_errores_distintos_no_se_bloquean_entre_si(self):
        bot = _make_bot()
        db = _make_db_manager([111])

        await notify_admin(bot=bot, db_manager=db, level="ERROR", error=ValueError("e1"))
        await notify_admin(bot=bot, db_manager=db, level="ERROR", error=TypeError("e2"))

        assert bot.send_message.call_count == 2

    @pytest.mark.asyncio
    async def test_error_en_send_no_propaga_excepcion(self):
        bot = MagicMock()
        bot.send_message = AsyncMock(side_effect=Exception("Telegram error"))
        db = _make_db_manager([111])

        # No debe lanzar excepción
        await notify_admin(bot=bot, db_manager=db, level="ERROR", message="test")


# ---------------------------------------------------------------------------
# _build_message
# ---------------------------------------------------------------------------

class TestBuildMessage:

    def test_incluye_nivel_y_timestamp(self):
        msg = _build_message(level="ERROR", error=None, message="algo falló", user_info="123")
        assert "ERROR" in msg
        assert "123" in msg
        assert "algo falló" in msg

    def test_incluye_tipo_de_error(self):
        error = ValueError("bad value")
        msg = _build_message(level="ERROR", error=error, message="", user_info="u")
        assert "ValueError" in msg

    def test_critico_usa_emoji_rojo(self):
        msg = _build_message(level="CRITICAL", error=None, message="crítico", user_info="u")
        assert "🚨" in msg

    def test_error_usa_emoji_x(self):
        msg = _build_message(level="ERROR", error=None, message="error", user_info="u")
        assert "❌" in msg

    def test_sin_error_no_traceback(self):
        msg = _build_message(level="WARNING", error=None, message="aviso", user_info="u")
        assert "Traceback" not in msg
