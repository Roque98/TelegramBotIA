"""
Tests para src/domain/auth/

Cobertura:
- TelegramUser: propiedades y construcción
- PermissionResult: propiedades
- Operation: construcción
- UserService: lógica de registro, verificación, permisos
"""
import pytest
from unittest.mock import MagicMock
from datetime import datetime, timedelta

from src.domain.auth.user_entity import TelegramUser, PermissionResult, Operation, RegistrationError  # noqa: F401
from src.domain.auth.user_service import UserService


# ---------------------------------------------------------------------------
# TelegramUser
# ---------------------------------------------------------------------------

class TestTelegramUser:

    def test_nombre_completo(self):
        user = TelegramUser({"Nombre": "Juan Pérez"})
        assert user.nombre_completo == "Juan Pérez"

    def test_nombre_completo_none(self):
        user = TelegramUser({})
        assert user.nombre_completo == ""

    def test_is_active_true(self):
        user = TelegramUser({"Activa": 1, "estado": "ACTIVO"})
        assert user.is_active is True

    def test_is_active_false_when_inactive(self):
        user = TelegramUser({"Activa": 0, "estado": "ACTIVO"})
        assert user.is_active is False

    def test_is_active_false_when_blocked(self):
        user = TelegramUser({"Activa": 1, "estado": "BLOQUEADO"})
        assert user.is_active is False

    def test_is_verified(self):
        user = TelegramUser({"verificado": True})
        assert user.is_verified is True

    def test_is_verified_default_false(self):
        user = TelegramUser({})
        assert user.is_verified is False

    def test_repr(self):
        user = TelegramUser({"idUsuario": 1, "Nombre": "Ana", "telegramChatId": 100, "rolNombre": "admin"})
        r = repr(user)
        assert "TelegramUser" in r
        assert "Ana" in r

    def test_defaults(self):
        """Defaults seguros: inactivo y bloqueado hasta confirmar desde BD."""
        user = TelegramUser({})
        assert user.activo == 0          # default seguro
        assert user.estado == "BLOQUEADO"  # default seguro
        assert user.es_principal is False
        assert user.verificado is False


# ---------------------------------------------------------------------------
# PermissionResult
# ---------------------------------------------------------------------------

class TestPermissionResult:

    def test_is_allowed_true(self):
        perm = PermissionResult({"TienePermiso": True, "Mensaje": "OK"})
        assert perm.is_allowed is True

    def test_is_allowed_false(self):
        perm = PermissionResult({"TienePermiso": False, "Mensaje": "Sin permiso"})
        assert perm.is_allowed is False

    def test_defaults(self):
        perm = PermissionResult({})
        assert perm.tiene_permiso is False
        assert perm.mensaje == ""
        assert perm.requiere_parametros is False

    def test_repr(self):
        perm = PermissionResult({"TienePermiso": True, "NombreOperacion": "ventas"})
        assert "PermissionResult" in repr(perm)


# ---------------------------------------------------------------------------
# Operation
# ---------------------------------------------------------------------------

class TestOperation:

    def test_defaults(self):
        op = Operation({})
        assert op.permitido is False
        assert op.nivel_criticidad == 1
        assert op.requiere_parametros is False

    def test_from_data(self):
        op = Operation({
            "comando": "/ventas",
            "Permitido": True,
            "nivelCriticidad": 3,
        })
        assert op.comando == "/ventas"
        assert op.permitido is True
        assert op.nivel_criticidad == 3

    def test_repr(self):
        op = Operation({"comando": "/help", "Permitido": True})
        assert "Operation" in repr(op)


# ---------------------------------------------------------------------------
# RegistrationError
# ---------------------------------------------------------------------------

class TestRegistrationError:

    def test_is_exception(self):
        with pytest.raises(RegistrationError):
            raise RegistrationError("test error")


# ---------------------------------------------------------------------------
# UserService
# ---------------------------------------------------------------------------

@pytest.fixture
def mock_repo():
    return MagicMock()


@pytest.fixture
def service(mock_repo):
    svc = UserService.__new__(UserService)
    svc.repository = mock_repo
    return svc


class TestUserServiceGenerate:

    def test_generate_verification_code_length(self, service):
        code = service.generate_verification_code()
        assert len(code) == UserService.VERIFICATION_CODE_LENGTH
        assert code.isdigit()

    def test_generate_verification_code_different_each_time(self, service):
        codes = {service.generate_verification_code() for _ in range(20)}
        # Con 6 dígitos y 20 intentos, muy improbable que todos sean iguales
        assert len(codes) > 1


class TestUserServiceStartRegistration:

    def test_already_registered_returns_false(self, service, mock_repo):
        mock_repo.has_telegram_account.return_value = True
        ok, msg, code = service.start_registration(user_id=1, chat_id=100)
        assert ok is False
        assert "ya está registrada" in msg
        assert code is None

    def test_start_registration_success(self, service, mock_repo):
        mock_repo.has_telegram_account.return_value = False
        mock_repo.has_principal_account.return_value = False
        mock_repo.insert_telegram_account.return_value = None

        ok, msg, code = service.start_registration(
            user_id=1, chat_id=100, username="test"
        )
        assert ok is True
        assert code is not None
        assert len(code) == UserService.VERIFICATION_CODE_LENGTH

    def test_start_registration_exception_returns_false(self, service, mock_repo):
        mock_repo.has_telegram_account.side_effect = Exception("DB error")
        ok, msg, code = service.start_registration(user_id=1, chat_id=100)
        assert ok is False
        assert code is None


class TestUserServiceVerifyAccount:

    def test_account_not_found(self, service, mock_repo):
        mock_repo.get_pending_verification.return_value = None
        ok, msg = service.verify_account(chat_id=100, verification_code="123456")
        assert ok is False
        assert "no encontrada" in msg

    def test_already_verified(self, service, mock_repo):
        mock_repo.get_pending_verification.return_value = {"verificado": True}
        ok, msg = service.verify_account(chat_id=100, verification_code="123456")
        assert ok is True
        assert "ya está verificada" in msg

    def test_too_many_attempts_blocks_account(self, service, mock_repo):
        mock_repo.get_pending_verification.return_value = {
            "verificado": False,
            "intentosVerificacion": UserService.MAX_VERIFICATION_ATTEMPTS,
        }
        ok, msg = service.verify_account(chat_id=100, verification_code="000000")
        assert ok is False
        assert "bloqueada" in msg
        mock_repo.block_account.assert_called_once_with(100)

    def test_expired_code(self, service, mock_repo):
        mock_repo.get_pending_verification.return_value = {
            "verificado": False,
            "intentosVerificacion": 0,
            "fechaRegistro": datetime.now() - timedelta(hours=25),
            "codigoVerificacion": "123456",
        }
        ok, msg = service.verify_account(chat_id=100, verification_code="123456")
        assert ok is False
        assert "expirado" in msg

    def test_wrong_code_decrements_attempts(self, service, mock_repo):
        mock_repo.get_pending_verification.return_value = {
            "verificado": False,
            "intentosVerificacion": 2,
            "fechaRegistro": datetime.now(),
            "codigoVerificacion": "999999",
        }
        ok, msg = service.verify_account(chat_id=100, verification_code="000000")
        assert ok is False
        assert "Código incorrecto" in msg
        mock_repo.increment_verification_attempts.assert_called_once_with(100)

    def test_correct_code_marks_verified(self, service, mock_repo):
        mock_repo.get_pending_verification.return_value = {
            "verificado": False,
            "intentosVerificacion": 0,
            "fechaRegistro": datetime.now(),
            "codigoVerificacion": "123456",
        }
        ok, msg = service.verify_account(chat_id=100, verification_code="123456")
        assert ok is True
        mock_repo.mark_account_verified.assert_called_once_with(100)


class TestUserServiceResend:

    def test_resend_not_found(self, service, mock_repo):
        mock_repo.get_pending_verification.return_value = None
        ok, msg, code = service.resend_verification_code(chat_id=100)
        assert ok is False
        assert code is None

    def test_resend_already_verified(self, service, mock_repo):
        mock_repo.get_pending_verification.return_value = {"verificado": True}
        ok, msg, code = service.resend_verification_code(chat_id=100)
        assert ok is False

    def test_resend_blocked(self, service, mock_repo):
        mock_repo.get_pending_verification.return_value = {
            "verificado": False,
            "estado": "BLOQUEADO",
        }
        ok, msg, code = service.resend_verification_code(chat_id=100)
        assert ok is False
        assert "bloqueada" in msg

    def test_resend_success(self, service, mock_repo):
        mock_repo.get_pending_verification.return_value = {
            "verificado": False,
            "estado": "ACTIVO",
        }
        ok, msg, code = service.resend_verification_code(chat_id=100)
        assert ok is True
        assert code is not None
        mock_repo.update_verification_code.assert_called_once()


class TestUserServiceLogOperation:
    """UserService.log_operation delega al repository."""

    def test_log_operation_delegated(self, service, mock_repo):
        mock_repo.log_operation.return_value = True
        result = service.log_operation(user_id=1, comando="/ia")
        mock_repo.log_operation.assert_called_once_with(1, "/ia")
        assert result is True
