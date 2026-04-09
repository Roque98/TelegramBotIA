"""
Tests para src/bot/handlers/registration_handlers.py

Cobertura:
- cmd_register: ya registrado, ya registrado sin verificar, nuevo usuario
- handle_employee_id: employee no numérico, no encontrado, ya registrado, éxito
- cmd_verify: sin código, error, verificación correcta/incorrecta
- cmd_resend: éxito, error
- cmd_cancel
"""
import pytest
import sys
from unittest.mock import AsyncMock, MagicMock, patch
from contextlib import contextmanager


from src.bot.handlers.registration_handlers import RegistrationHandlers, WAITING_FOR_EMPLOYEE_ID
from telegram.ext import ConversationHandler

_END = ConversationHandler.END


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def make_update(user_id=123, username="user", first_name="Test", text=None, args=None):
    update = MagicMock()
    update.effective_user.id = user_id
    update.effective_user.username = username
    update.effective_user.first_name = first_name
    update.effective_user.last_name = None
    update.message.text = text or ""
    update.message.reply_text = AsyncMock()
    return update


def make_context(args=None):
    context = MagicMock()
    context.args = args or []
    context.user_data = {}
    return context


def make_db_with_service(user_service_mock):
    """Crea un db_manager cuya sesión retorna el UserService mockeado."""
    db_mock = MagicMock()

    @contextmanager
    def fake_session():
        yield MagicMock()

    db_mock.get_session = fake_session

    return db_mock


@pytest.fixture
def mock_service():
    return MagicMock()


@pytest.fixture
def handlers(mock_service):
    db = MagicMock()

    @contextmanager
    def fake_session():
        yield MagicMock()

    db.get_session = fake_session

    return RegistrationHandlers(db_manager=db), mock_service, db


# ---------------------------------------------------------------------------
# cmd_register
# ---------------------------------------------------------------------------

class TestCmdRegister:

    @pytest.mark.asyncio
    async def test_already_registered_and_verified(self):
        update = make_update()
        context = make_context()

        mock_user = MagicMock()
        mock_user.is_verified = True
        mock_user.nombre_completo = "Juan Pérez"

        with patch("src.bot.handlers.registration_handlers.UserService") as MockService:
            svc_instance = MockService.return_value
            svc_instance.is_user_registered.return_value = True
            svc_instance.get_user_by_chat_id.return_value = mock_user
            svc_instance.get_registration_info.return_value = {"verificado": True}

            h = RegistrationHandlers(db_manager=MagicMock())
            h.db_manager.get_session = MagicMock()
            h.db_manager.get_session.return_value.__enter__ = MagicMock(return_value=MagicMock())
            h.db_manager.get_session.return_value.__exit__ = MagicMock(return_value=False)

            with patch("src.bot.handlers.registration_handlers.UserService", return_value=svc_instance):
                result = await h.cmd_register(update, context)

        update.message.reply_text.assert_called_once()
        text = update.message.reply_text.call_args[0][0]
        assert "verificado" in text.lower() or "registrado" in text.lower()

    @pytest.mark.asyncio
    async def test_already_registered_not_verified(self):
        update = make_update()
        context = make_context()

        mock_user = MagicMock()
        mock_user.is_verified = False

        with patch("src.bot.handlers.registration_handlers.UserService") as MockService:
            svc_instance = MockService.return_value
            svc_instance.is_user_registered.return_value = True
            svc_instance.get_user_by_chat_id.return_value = mock_user
            svc_instance.get_registration_info.return_value = {"verificado": False}

            h = RegistrationHandlers(db_manager=MagicMock())
            h.db_manager.get_session = MagicMock()
            h.db_manager.get_session.return_value.__enter__ = MagicMock(return_value=MagicMock())
            h.db_manager.get_session.return_value.__exit__ = MagicMock(return_value=False)

            with patch("src.bot.handlers.registration_handlers.UserService", return_value=svc_instance):
                result = await h.cmd_register(update, context)

        update.message.reply_text.assert_called_once()
        text = update.message.reply_text.call_args[0][0]
        assert "verify" in text.lower() or "código" in text.lower() or "verificar" in text.lower()

    @pytest.mark.asyncio
    async def test_new_user_prompts_for_employee_id(self):
        update = make_update()
        context = make_context()

        with patch("src.bot.handlers.registration_handlers.UserService") as MockService:
            svc_instance = MockService.return_value
            svc_instance.is_user_registered.return_value = False

            h = RegistrationHandlers(db_manager=MagicMock())
            h.db_manager.get_session = MagicMock()
            h.db_manager.get_session.return_value.__enter__ = MagicMock(return_value=MagicMock())
            h.db_manager.get_session.return_value.__exit__ = MagicMock(return_value=False)

            with patch("src.bot.handlers.registration_handlers.UserService", return_value=svc_instance):
                result = await h.cmd_register(update, context)

        assert result == WAITING_FOR_EMPLOYEE_ID
        update.message.reply_text.assert_called_once()


# ---------------------------------------------------------------------------
# handle_employee_id
# ---------------------------------------------------------------------------

class TestHandleEmployeeId:

    @pytest.mark.asyncio
    async def test_non_numeric_employee_id(self):
        update = make_update(text="abc")
        context = make_context()

        h = RegistrationHandlers(db_manager=MagicMock())
        result = await h.handle_employee_id(update, context)

        assert result == WAITING_FOR_EMPLOYEE_ID
        update.message.reply_text.assert_called_once()
        text = update.message.reply_text.call_args[0][0]
        assert "numérico" in text

    @pytest.mark.asyncio
    async def test_employee_not_found(self):
        update = make_update(text="99999")
        context = make_context()

        with patch("src.bot.handlers.registration_handlers.UserService") as MockService:
            svc_instance = MockService.return_value
            svc_instance.find_user_by_employee_id.return_value = None

            h = RegistrationHandlers(db_manager=MagicMock())
            h.db_manager.get_session = MagicMock()
            h.db_manager.get_session.return_value.__enter__ = MagicMock(return_value=MagicMock())
            h.db_manager.get_session.return_value.__exit__ = MagicMock(return_value=False)

            with patch("src.bot.handlers.registration_handlers.UserService", return_value=svc_instance):
                result = await h.handle_employee_id(update, context)

        assert result == WAITING_FOR_EMPLOYEE_ID
        text = update.message.reply_text.call_args[0][0]
        assert "99999" in text

    @pytest.mark.asyncio
    async def test_registration_fails(self):
        update = make_update(text="12345")
        context = make_context()

        user_data = {"idUsuario": 1, "Nombre": "Juan", "email": "juan@test.com"}

        with patch("src.bot.handlers.registration_handlers.UserService") as MockService:
            svc_instance = MockService.return_value
            svc_instance.find_user_by_employee_id.return_value = user_data
            svc_instance.start_registration.return_value = (False, "Ya registrado", None)

            h = RegistrationHandlers(db_manager=MagicMock())
            h.db_manager.get_session = MagicMock()
            h.db_manager.get_session.return_value.__enter__ = MagicMock(return_value=MagicMock())
            h.db_manager.get_session.return_value.__exit__ = MagicMock(return_value=False)

            with patch("src.bot.handlers.registration_handlers.UserService", return_value=svc_instance):
                result = await h.handle_employee_id(update, context)

        assert result == _END  # ConversationHandler.END

    @pytest.mark.asyncio
    async def test_registration_success(self):
        update = make_update(text="12345")
        context = make_context()

        user_data = {"idUsuario": 1, "Nombre": "Juan", "email": "juan@test.com"}

        with patch("src.bot.handlers.registration_handlers.UserService") as MockService:
            svc_instance = MockService.return_value
            svc_instance.find_user_by_employee_id.return_value = user_data
            svc_instance.start_registration.return_value = (True, "OK", "123456")

            h = RegistrationHandlers(db_manager=MagicMock())
            h.db_manager.get_session = MagicMock()
            h.db_manager.get_session.return_value.__enter__ = MagicMock(return_value=MagicMock())
            h.db_manager.get_session.return_value.__exit__ = MagicMock(return_value=False)

            with patch("src.bot.handlers.registration_handlers.UserService", return_value=svc_instance):
                result = await h.handle_employee_id(update, context)

        assert result == _END  # ConversationHandler.END
        text = update.message.reply_text.call_args[0][0]
        assert "Juan" in text

    @pytest.mark.asyncio
    async def test_db_exception_returns_end(self):
        update = make_update(text="12345")
        context = make_context()

        h = RegistrationHandlers(db_manager=MagicMock())
        h.db_manager.get_session = MagicMock(side_effect=Exception("DB error"))

        result = await h.handle_employee_id(update, context)

        assert result == _END  # ConversationHandler.END
        update.message.reply_text.assert_called_once()


# ---------------------------------------------------------------------------
# cmd_verify
# ---------------------------------------------------------------------------

class TestCmdVerify:

    @pytest.mark.asyncio
    async def test_no_code_provided(self):
        update = make_update()
        context = make_context(args=[])

        h = RegistrationHandlers(db_manager=MagicMock())
        await h.cmd_verify(update, context)

        text = update.message.reply_text.call_args[0][0]
        assert "verify" in text.lower() or "código" in text.lower()

    @pytest.mark.asyncio
    async def test_verify_success(self):
        update = make_update()
        context = make_context(args=["123456"])

        mock_user = MagicMock()
        mock_user.nombre_completo = "Juan Pérez"
        mock_user.rol_nombre = "Vendedor"
        mock_user.email = "juan@test.com"

        with patch("src.bot.handlers.registration_handlers.UserService") as MockService:
            svc_instance = MockService.return_value
            svc_instance.verify_account.return_value = (True, "OK")
            svc_instance.get_user_by_chat_id.return_value = mock_user

            h = RegistrationHandlers(db_manager=MagicMock())
            h.db_manager.get_session = MagicMock()
            h.db_manager.get_session.return_value.__enter__ = MagicMock(return_value=MagicMock())
            h.db_manager.get_session.return_value.__exit__ = MagicMock(return_value=False)

            with patch("src.bot.handlers.registration_handlers.UserService", return_value=svc_instance):
                await h.cmd_verify(update, context)

        text = update.message.reply_text.call_args[0][0]
        assert "exitosa" in text.lower() or "bienvenido" in text.lower()

    @pytest.mark.asyncio
    async def test_verify_failure(self):
        update = make_update()
        context = make_context(args=["000000"])

        with patch("src.bot.handlers.registration_handlers.UserService") as MockService:
            svc_instance = MockService.return_value
            svc_instance.verify_account.return_value = (False, "Código incorrecto")

            h = RegistrationHandlers(db_manager=MagicMock())
            h.db_manager.get_session = MagicMock()
            h.db_manager.get_session.return_value.__enter__ = MagicMock(return_value=MagicMock())
            h.db_manager.get_session.return_value.__exit__ = MagicMock(return_value=False)

            with patch("src.bot.handlers.registration_handlers.UserService", return_value=svc_instance):
                await h.cmd_verify(update, context)

        text = update.message.reply_text.call_args[0][0]
        assert "Código incorrecto" in text

    @pytest.mark.asyncio
    async def test_verify_db_exception(self):
        update = make_update()
        context = make_context(args=["123456"])

        h = RegistrationHandlers(db_manager=MagicMock())
        h.db_manager.get_session = MagicMock(side_effect=Exception("DB error"))

        await h.cmd_verify(update, context)

        update.message.reply_text.assert_called_once()
        text = update.message.reply_text.call_args[0][0]
        assert "error" in text.lower()


# ---------------------------------------------------------------------------
# cmd_resend
# ---------------------------------------------------------------------------

class TestCmdResend:

    @pytest.mark.asyncio
    async def test_resend_success(self):
        update = make_update()
        context = make_context()

        with patch("src.bot.handlers.registration_handlers.UserService") as MockService:
            svc_instance = MockService.return_value
            svc_instance.resend_verification_code.return_value = (True, "Código reenviado", "654321")

            h = RegistrationHandlers(db_manager=MagicMock())
            h.db_manager.get_session = MagicMock()
            h.db_manager.get_session.return_value.__enter__ = MagicMock(return_value=MagicMock())
            h.db_manager.get_session.return_value.__exit__ = MagicMock(return_value=False)

            with patch("src.bot.handlers.registration_handlers.UserService", return_value=svc_instance):
                await h.cmd_resend(update, context)

        text = update.message.reply_text.call_args[0][0]
        assert "Código reenviado" in text

    @pytest.mark.asyncio
    async def test_resend_failure(self):
        update = make_update()
        context = make_context()

        with patch("src.bot.handlers.registration_handlers.UserService") as MockService:
            svc_instance = MockService.return_value
            svc_instance.resend_verification_code.return_value = (False, "Cuenta bloqueada", None)

            h = RegistrationHandlers(db_manager=MagicMock())
            h.db_manager.get_session = MagicMock()
            h.db_manager.get_session.return_value.__enter__ = MagicMock(return_value=MagicMock())
            h.db_manager.get_session.return_value.__exit__ = MagicMock(return_value=False)

            with patch("src.bot.handlers.registration_handlers.UserService", return_value=svc_instance):
                await h.cmd_resend(update, context)

        text = update.message.reply_text.call_args[0][0]
        assert "Cuenta bloqueada" in text

    @pytest.mark.asyncio
    async def test_resend_db_exception(self):
        update = make_update()
        context = make_context()

        h = RegistrationHandlers(db_manager=MagicMock())
        h.db_manager.get_session = MagicMock(side_effect=Exception("DB error"))

        await h.cmd_resend(update, context)

        update.message.reply_text.assert_called_once()
        text = update.message.reply_text.call_args[0][0]
        assert "error" in text.lower()


# ---------------------------------------------------------------------------
# cmd_cancel
# ---------------------------------------------------------------------------

class TestCmdCancel:

    @pytest.mark.asyncio
    async def test_cancel_replies(self):
        update = make_update()
        context = make_context()

        h = RegistrationHandlers(db_manager=MagicMock())
        result = await h.cmd_cancel(update, context)

        update.message.reply_text.assert_called_once()
        assert result == _END  # ConversationHandler.END
