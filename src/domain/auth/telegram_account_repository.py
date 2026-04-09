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
        query = "EXEC abcmasplus..BotIAv2_sp_BuscarPorEmail @email = :email"
        rows = await self.db_manager.execute_query_async(query, {"email": email})
        return rows[0] if rows else None

    async def find_user_by_employee_id(self, employee_id: int) -> Optional[dict]:
        query = "EXEC abcmasplus..BotIAv2_sp_GetUsuarioById @idUsuario = :employee_id"
        rows = await self.db_manager.execute_query_async(query, {"employee_id": employee_id})
        return rows[0] if rows else None

    async def has_telegram_account(self, chat_id: int) -> bool:
        query = "EXEC abcmasplus..BotIAv2_sp_TieneCuentaTelegram @telegramChatId = :chat_id"
        rows = await self.db_manager.execute_query_async(query, {"chat_id": chat_id})
        return bool(rows and rows[0].get("tieneCuenta"))

    async def has_principal_account(self, user_id: int) -> bool:
        query = "EXEC abcmasplus..BotIAv2_sp_TieneCuentaPrincipal @idUsuario = :user_id"
        rows = await self.db_manager.execute_query_async(query, {"user_id": user_id})
        return bool(rows and rows[0].get("tienePrincipal"))

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
        from .constants import AccountState
        query = """
            EXEC abcmasplus..BotIAv2_sp_InsertarCuentaTelegram
                @idUsuario          = :user_id,
                @telegramChatId     = :chat_id,
                @telegramUsername   = :username,
                @telegramFirstName  = :first_name,
                @telegramLastName   = :last_name,
                @alias              = :alias,
                @esPrincipal        = :es_principal,
                @estado             = :estado,
                @codigoVerificacion = :verification_code
        """
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
        query = "EXEC abcmasplus..BotIAv2_sp_GetPendienteVerificacion @telegramChatId = :chat_id"
        rows = await self.db_manager.execute_query_async(query, {"chat_id": chat_id})
        return rows[0] if rows else None

    async def mark_account_verified(self, chat_id: int) -> None:
        query = "EXEC abcmasplus..BotIAv2_sp_MarcarCuentaVerificada @telegramChatId = :chat_id"
        await self.db_manager.execute_non_query_async(query, {"chat_id": chat_id})

    async def increment_verification_attempts(self, chat_id: int) -> None:
        query = "EXEC abcmasplus..BotIAv2_sp_IncrementarIntentos @telegramChatId = :chat_id"
        await self.db_manager.execute_non_query_async(query, {"chat_id": chat_id})

    async def update_verification_code(self, chat_id: int, new_code: str) -> None:
        query = """
            EXEC abcmasplus..BotIAv2_sp_ActualizarCodigoVerificacion
                @telegramChatId     = :chat_id,
                @codigoVerificacion = :new_code
        """
        await self.db_manager.execute_non_query_async(query, {"chat_id": chat_id, "new_code": new_code})

    async def block_account(self, chat_id: int) -> None:
        query = "EXEC abcmasplus..BotIAv2_sp_BloquearCuenta @telegramChatId = :chat_id"
        await self.db_manager.execute_non_query_async(query, {"chat_id": chat_id})
        logger.warning(f"Cuenta bloqueada: chat_id={chat_id}")

    async def get_registration_status(self, chat_id: int) -> Optional[dict]:
        query = "EXEC abcmasplus..BotIAv2_sp_GetEstadoRegistro @telegramChatId = :chat_id"
        rows = await self.db_manager.execute_query_async(query, {"chat_id": chat_id})
        return rows[0] if rows else None
