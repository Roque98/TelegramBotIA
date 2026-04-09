"""
Tests para StatusMessage — Fase 7: UX Avanzado.

Cobertura:
- set_tool_active(): muestra mensaje correcto por nombre de tool
- _TOOL_MESSAGES: contiene tools conocidas
- background_threshold: parámetro configurable
- _background_warning(): se cancela al completar
"""

import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock, patch


def _make_update():
    """Crea un Update de Telegram mockeado."""
    msg = MagicMock()
    msg.reply_text = AsyncMock()
    msg.edit_text = AsyncMock()
    msg.chat.send_action = AsyncMock()
    msg.message_id = 42

    update = MagicMock()
    update.message = msg
    update.effective_user = MagicMock()
    return update


# ---------------------------------------------------------------------------
# _TOOL_MESSAGES
# ---------------------------------------------------------------------------

class TestToolMessages:

    def test_contiene_database_query(self):
        from src.utils.status_message import StatusMessage
        assert "database_query" in StatusMessage._TOOL_MESSAGES

    def test_contiene_knowledge_search(self):
        from src.utils.status_message import StatusMessage
        assert "knowledge_search" in StatusMessage._TOOL_MESSAGES

    def test_contiene_calculate(self):
        from src.utils.status_message import StatusMessage
        assert "calculate" in StatusMessage._TOOL_MESSAGES

    def test_contiene_read_attachment(self):
        from src.utils.status_message import StatusMessage
        assert "read_attachment" in StatusMessage._TOOL_MESSAGES

    def test_mensajes_no_vacios(self):
        from src.utils.status_message import StatusMessage
        for tool, msg in StatusMessage._TOOL_MESSAGES.items():
            assert msg, f"Mensaje vacío para tool: {tool}"


# ---------------------------------------------------------------------------
# background_threshold
# ---------------------------------------------------------------------------

class TestBackgroundThreshold:

    def test_default_es_15_segundos(self):
        from src.utils.status_message import StatusMessage
        update = _make_update()
        status = StatusMessage(update)
        assert status.background_threshold == 15.0

    def test_configurable(self):
        from src.utils.status_message import StatusMessage
        update = _make_update()
        status = StatusMessage(update, background_threshold=30.0)
        assert status.background_threshold == 30.0


# ---------------------------------------------------------------------------
# set_tool_active()
# ---------------------------------------------------------------------------

class TestSetToolActive:

    @pytest.mark.asyncio
    async def test_llama_set_phase_con_mensaje_conocido(self):
        from src.utils.status_message import StatusMessage
        update = _make_update()
        status = StatusMessage(update)
        status._is_started = True
        status._status_message = MagicMock()
        status._status_message.edit_text = AsyncMock()
        # Cancelar auto-update antes
        status._auto_update_task = None

        await status.set_tool_active("database_query")

        status._status_message.edit_text.assert_called_once()
        call_args = status._status_message.edit_text.call_args[0][0]
        assert "base de datos" in call_args.lower() or "🗄️" in call_args

    @pytest.mark.asyncio
    async def test_tool_desconocida_usa_fallback(self):
        from src.utils.status_message import StatusMessage
        update = _make_update()
        status = StatusMessage(update)
        status._is_started = True
        status._status_message = MagicMock()
        status._status_message.edit_text = AsyncMock()
        status._auto_update_task = None

        await status.set_tool_active("herramienta_custom")

        call_args = status._status_message.edit_text.call_args[0][0]
        assert "herramienta_custom" in call_args

    @pytest.mark.asyncio
    async def test_no_falla_si_no_iniciado(self):
        from src.utils.status_message import StatusMessage
        update = _make_update()
        status = StatusMessage(update)
        # _is_started = False, no debe lanzar excepción
        await status.set_tool_active("database_query")


# ---------------------------------------------------------------------------
# _background_task se crea en start() y se cancela en complete()
# ---------------------------------------------------------------------------

class TestBackgroundTask:

    @pytest.mark.asyncio
    async def test_background_task_creada_en_start(self):
        from src.utils.status_message import StatusMessage
        update = _make_update()
        update.message.reply_text = AsyncMock(return_value=MagicMock(message_id=1))
        status = StatusMessage(update, background_threshold=999.0)

        await status.start()
        assert status._background_task is not None
        assert not status._background_task.done()

        # Limpiar
        status._background_task.cancel()
        if status._auto_update_task:
            status._auto_update_task.cancel()

    @pytest.mark.asyncio
    async def test_background_task_cancelada_en_complete(self):
        from src.utils.status_message import StatusMessage
        update = _make_update()
        mock_msg = MagicMock()
        mock_msg.edit_text = AsyncMock()
        mock_msg.message_id = 1
        update.message.reply_text = AsyncMock(return_value=mock_msg)

        status = StatusMessage(update, background_threshold=999.0)
        await status.start()

        assert status._background_task is not None

        await status.complete("¡Listo!")

        assert status._background_task is None

    @pytest.mark.asyncio
    async def test_background_warning_envia_mensaje_nuevo(self):
        """Después de background_threshold segundos, se envía un mensaje nuevo."""
        from src.utils.status_message import StatusMessage
        update = _make_update()

        call_count = 0
        async def fake_reply(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            return MagicMock(message_id=call_count)

        update.message.reply_text = fake_reply
        status = StatusMessage(update, background_threshold=0.05)  # 50ms para el test

        await status.start()
        # Esperar que dispare el warning
        await asyncio.sleep(0.15)

        # Debe haberse enviado al menos 2 mensajes: el inicial + el warning
        assert call_count >= 2

        # Limpiar
        if status._auto_update_task and not status._auto_update_task.done():
            status._auto_update_task.cancel()
        if status._background_task and not status._background_task.done():
            status._background_task.cancel()
