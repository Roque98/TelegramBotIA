"""
Telegram Account Repository - Registro, verificación y bloqueo de cuentas Telegram.

Reemplaza los métodos de registro/verificación de UserRepository (god repository).
Usa db_manager async, consistente con el resto del código nuevo.
"""

import logging
from typing import Any, Optional

logger = logging.getLogger(__name__)


class TelegramAccountRepository:
    """Registro, verificación y bloqueo de cuentas de Telegram."""

    def __init__(self, db_manager: Any) -> None:
        self.db_manager = db_manager

    async def find_user_by_email(self, email: str) -> Optional[dict]:
        query = """
            SELECT idUsuario, Nombre, email, idRol, puesto, Activa
            FROM abcmasplus..Usuarios
            WHERE email = :email AND Activa = 1
        """
        rows = await self.db_manager.execute_query_async(query, {"email": email})
        return rows[0] if rows else None

    async def find_user_by_employee_id(self, employee_id: int) -> Optional[dict]:
        query = """
            SELECT idUsuario, Nombre, email, idRol, puesto, Activa
            FROM abcmasplus..Usuarios
            WHERE idUsuario = :employee_id AND Activa = 1
        """
        rows = await self.db_manager.execute_query_async(query, {"employee_id": employee_id})
        return rows[0] if rows else None

    async def has_telegram_account(self, chat_id: int) -> bool:
        query = """
            SELECT COUNT(*) AS cnt FROM abcmasplus..BotIAv2_UsuariosTelegram
            WHERE telegramChatId = :chat_id AND activo = 1
        """
        rows = await self.db_manager.execute_query_async(query, {"chat_id": chat_id})
        return bool(rows and rows[0].get("cnt", 0) > 0)

    async def has_principal_account(self, user_id: int) -> bool:
        query = """
            SELECT COUNT(*) AS cnt FROM abcmasplus..BotIAv2_UsuariosTelegram
            WHERE idUsuario = :user_id AND esPrincipal = 1 AND activo = 1
        """
        rows = await self.db_manager.execute_query_async(query, {"user_id": user_id})
        return bool(rows and rows[0].get("cnt", 0) > 0)

    async def insert_telegram_account(
        self,
        user_id: int,
        chat_id: int,
        verification_code: str,
        es_principal: bool,
        username: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        alias: Optional[str] = None,
    ) -> None:
        query = """
            INSERT INTO abcmasplus..BotIAv2_UsuariosTelegram (
                idUsuario, telegramChatId, telegramUsername,
                telegramFirstName, telegramLastName, alias,
                esPrincipal, estado, codigoVerificacion,
                verificado, intentosVerificacion, fechaRegistro, activo
            ) VALUES (
                :user_id, :chat_id, :username, :first_name, :last_name,
                :alias, :es_principal, :estado, :verification_code,
                0, 0, GETDATE(), 1
            )
        """
        from .constants import AccountState
        await self.db_manager.execute_non_query_async(query, {
            "user_id": user_id,
            "chat_id": chat_id,
            "username": username,
            "first_name": first_name,
            "last_name": last_name,
            "alias": alias,
            "es_principal": 1 if es_principal else 0,
            "estado": AccountState.ACTIVE,
            "verification_code": verification_code,
        })

    async def get_pending_verification(self, chat_id: int) -> Optional[dict]:
        query = """
            SELECT idUsuarioTelegram, idUsuario, codigoVerificacion,
                   intentosVerificacion, fechaRegistro, verificado
            FROM abcmasplus..BotIAv2_UsuariosTelegram
            WHERE telegramChatId = :chat_id AND activo = 1
        """
        rows = await self.db_manager.execute_query_async(query, {"chat_id": chat_id})
        return rows[0] if rows else None

    async def mark_account_verified(self, chat_id: int) -> None:
        query = """
            UPDATE abcmasplus..BotIAv2_UsuariosTelegram
            SET verificado = 1, fechaVerificacion = GETDATE(), codigoVerificacion = NULL
            WHERE telegramChatId = :chat_id
        """
        await self.db_manager.execute_non_query_async(query, {"chat_id": chat_id})

    async def increment_verification_attempts(self, chat_id: int) -> None:
        query = """
            UPDATE abcmasplus..BotIAv2_UsuariosTelegram
            SET intentosVerificacion = intentosVerificacion + 1
            WHERE telegramChatId = :chat_id
        """
        await self.db_manager.execute_non_query_async(query, {"chat_id": chat_id})

    async def update_verification_code(self, chat_id: int, new_code: str) -> None:
        query = """
            UPDATE abcmasplus..BotIAv2_UsuariosTelegram
            SET codigoVerificacion = :new_code,
                intentosVerificacion = 0,
                fechaRegistro = GETDATE()
            WHERE telegramChatId = :chat_id
        """
        await self.db_manager.execute_non_query_async(query, {"new_code": new_code, "chat_id": chat_id})

    async def block_account(self, chat_id: int) -> None:
        from .constants import AccountState
        query = """
            UPDATE abcmasplus..BotIAv2_UsuariosTelegram
            SET estado = :estado
            WHERE telegramChatId = :chat_id
        """
        await self.db_manager.execute_non_query_async(query, {
            "estado": AccountState.BLOCKED,
            "chat_id": chat_id,
        })
        logger.warning(f"Cuenta bloqueada: chat_id={chat_id}")

    async def get_registration_status(self, chat_id: int) -> Optional[dict]:
        query = """
            SELECT ut.verificado, ut.estado, ut.intentosVerificacion,
                   ut.fechaRegistro, u.Nombre, u.email
            FROM abcmasplus..BotIAv2_UsuariosTelegram ut
            INNER JOIN abcmasplus..Usuarios u ON ut.idUsuario = u.idUsuario
            WHERE ut.telegramChatId = :chat_id AND ut.activo = 1
        """
        rows = await self.db_manager.execute_query_async(query, {"chat_id": chat_id})
        return rows[0] if rows else None
