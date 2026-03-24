"""
Servicio de usuarios.

Contiene la lógica de negocio de autenticación, registro y permisos.
Utiliza UserRepository para todo acceso a base de datos.
"""

import logging
import random
import string
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List, Tuple

from sqlalchemy.orm import Session

from src.auth.user_entity import TelegramUser, PermissionResult, Operation, RegistrationError
from src.auth.user_repository import UserRepository

logger = logging.getLogger(__name__)


class UserService:
    """Servicio de lógica de negocio para usuarios."""

    VERIFICATION_CODE_LENGTH = 6
    MAX_VERIFICATION_ATTEMPTS = 5
    VERIFICATION_CODE_EXPIRY_HOURS = 24

    def __init__(self, db_session: Session):
        self.repository = UserRepository(db_session)

    # -------------------------------------------------------------------------
    # Consultas de usuario (delegadas al repository)
    # -------------------------------------------------------------------------

    def get_user_by_chat_id(self, chat_id: int) -> Optional[TelegramUser]:
        return self.repository.get_user_by_chat_id(chat_id)

    def get_user_by_id(self, user_id: int) -> Optional[TelegramUser]:
        return self.repository.get_user_by_id(user_id)

    def get_user_by_telegram_chat_id(self, chat_id: int) -> Optional[TelegramUser]:
        return self.repository.get_user_by_chat_id(chat_id)

    def is_user_registered(self, chat_id: int) -> bool:
        return self.repository.is_user_registered(chat_id)

    def get_registration_info(self, chat_id: int) -> Optional[dict]:
        return self.repository.get_registration_info(chat_id)

    def update_last_activity(self, chat_id: int) -> bool:
        return self.repository.update_last_activity(chat_id)

    def get_user_stats(self, user_id: int) -> Optional[Dict[str, Any]]:
        return self.repository.get_user_stats(user_id)

    def get_all_user_telegram_accounts(self, user_id: int) -> list:
        return self.repository.get_all_user_telegram_accounts(user_id)

    def find_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        return self.repository.find_user_by_email(email)

    def find_user_by_employee_id(self, employee_id: int) -> Optional[Dict[str, Any]]:
        return self.repository.find_user_by_employee_id(employee_id)

    def get_registration_status(self, chat_id: int) -> Optional[Dict[str, Any]]:
        return self.repository.get_registration_status(chat_id)

    # -------------------------------------------------------------------------
    # Lógica de registro
    # -------------------------------------------------------------------------

    def generate_verification_code(self) -> str:
        return ''.join(random.choices(string.digits, k=self.VERIFICATION_CODE_LENGTH))

    def start_registration(
        self,
        user_id: int,
        chat_id: int,
        username: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        alias: Optional[str] = None
    ) -> Tuple[bool, str, Optional[str]]:
        try:
            if self.repository.has_telegram_account(chat_id):
                return (False, "Esta cuenta de Telegram ya está registrada.", None)

            es_principal = not self.repository.has_principal_account(user_id)
            verification_code = self.generate_verification_code()

            self.repository.insert_telegram_account(
                user_id=user_id,
                chat_id=chat_id,
                verification_code=verification_code,
                es_principal=es_principal,
                username=username,
                first_name=first_name,
                last_name=last_name,
                alias=alias
            )

            logger.info(f"Registro iniciado para usuario {user_id}, chat_id {chat_id}")
            return (
                True,
                "Registro iniciado exitosamente. "
                "Por favor, verifica tu cuenta con el código que recibirás.",
                verification_code
            )

        except Exception as e:
            logger.error(f"Error iniciando registro: {e}")
            return (False, f"Error al iniciar registro: {str(e)}", None)

    def verify_account(self, chat_id: int, verification_code: str) -> Tuple[bool, str]:
        try:
            data = self.repository.get_pending_verification(chat_id)

            if not data:
                return (False, "Cuenta no encontrada.")

            if data['verificado']:
                return (True, "Tu cuenta ya está verificada.")

            if data['intentosVerificacion'] >= self.MAX_VERIFICATION_ATTEMPTS:
                self.repository.block_account(chat_id)
                return (
                    False,
                    "Demasiados intentos fallidos. "
                    "Tu cuenta ha sido bloqueada. Contacta al administrador."
                )

            fecha_registro = data['fechaRegistro']
            if isinstance(fecha_registro, str):
                fecha_registro = datetime.fromisoformat(fecha_registro)

            if datetime.now() > fecha_registro + timedelta(hours=self.VERIFICATION_CODE_EXPIRY_HOURS):
                return (
                    False,
                    "El código de verificación ha expirado. "
                    "Por favor, solicita uno nuevo."
                )

            if data['codigoVerificacion'] == verification_code:
                self.repository.mark_account_verified(chat_id)
                logger.info(f"Cuenta verificada exitosamente: chat_id={chat_id}")
                return (True, "Cuenta verificada exitosamente.")
            else:
                self.repository.increment_verification_attempts(chat_id)
                intentos_restantes = self.MAX_VERIFICATION_ATTEMPTS - data['intentosVerificacion'] - 1
                return (False, f"Código incorrecto. Te quedan {intentos_restantes} intentos.")

        except Exception as e:
            logger.error(f"Error verificando cuenta: {e}")
            return (False, f"Error al verificar cuenta: {str(e)}")

    def resend_verification_code(self, chat_id: int) -> Tuple[bool, str, Optional[str]]:
        try:
            data = self.repository.get_pending_verification(chat_id)

            if not data:
                return (False, "Cuenta no encontrada.", None)

            if data['verificado']:
                return (False, "Tu cuenta ya está verificada.", None)

            if data.get('estado') == 'BLOQUEADO':
                return (False, "Tu cuenta está bloqueada. Contacta al administrador.", None)

            new_code = self.generate_verification_code()
            self.repository.update_verification_code(chat_id, new_code)

            logger.info(f"Código reenviado para chat_id={chat_id}")
            return (True, "Nuevo código de verificación generado.", new_code)

        except Exception as e:
            logger.error(f"Error reenviando código: {e}")
            return (False, f"Error al reenviar código: {str(e)}", None)

    # -------------------------------------------------------------------------
    # Lógica de permisos
    # -------------------------------------------------------------------------

    def check_permission(self, user_id: int, comando: str) -> PermissionResult:
        return self.repository.check_permission(user_id, comando)

    def get_user_operations(self, user_id: int) -> List[Operation]:
        return self.repository.get_user_operations(user_id)

    def get_user_operations_by_module(self, user_id: int) -> Dict[str, List[Operation]]:
        operations = self.repository.get_user_operations(user_id)
        by_module: Dict[str, List[Operation]] = {}
        for op in operations:
            module_name = op.modulo or 'Sin Módulo'
            if module_name not in by_module:
                by_module[module_name] = []
            by_module[module_name].append(op)
        return by_module

    def get_command_operations_map(self, user_id: int) -> Dict[str, Operation]:
        operations = self.repository.get_user_operations(user_id)
        return {op.comando: op for op in operations if op.comando and op.permitido}

    def is_operation_critical(self, user_id: int, comando: str) -> bool:
        operation = self.get_command_operations_map(user_id).get(comando)
        return operation.nivel_criticidad >= 3 if operation else False

    def log_operation(self, user_id: int, comando: str, **kwargs) -> bool:
        return self.repository.log_operation(user_id, comando, **kwargs)
