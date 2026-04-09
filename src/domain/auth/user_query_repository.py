"""
User Query Repository - Consultas de lectura de usuarios.

Reemplaza los métodos de consulta de UserRepository (god repository).
Usa db_manager async, consistente con el resto del código nuevo.
"""

import logging
from typing import Any, Optional

from .user_entity import TelegramUser

logger = logging.getLogger(__name__)


class UserQueryRepository:
    """Consultas de lectura de usuarios y sus cuentas de Telegram."""

    def __init__(self, db_manager: Any) -> None:
        self.db_manager = db_manager

    async def get_by_chat_id(self, chat_id: int) -> Optional[TelegramUser]:
        """Obtiene usuario completo a partir del telegramChatId."""
        query = "EXEC abcmasplus..BotIAv2_sp_GetUsuarioByChatId @telegramChatId = :chat_id"
        rows = await self.db_manager.execute_query_async(query, {"chat_id": chat_id})
        return TelegramUser(rows[0]) if rows else None

    async def get_by_user_id(self, user_id: int) -> Optional[TelegramUser]:
        """Obtiene usuario por idUsuario (cuenta principal de Telegram)."""
        query = "EXEC abcmasplus..BotIAv2_sp_GetUsuarioById @idUsuario = :user_id"
        rows = await self.db_manager.execute_query_async(query, {"user_id": user_id})
        return TelegramUser(rows[0]) if rows else None

    async def get_profile_for_permissions(self, chat_id: int) -> Optional[dict]:
        """
        Query liviana para AuthMiddleware — solo trae lo necesario para resolver permisos.
        Retorna: user_id, role_id, gerencia_ids, direccion_ids
        """
        query = "EXEC abcmasplus..BotIAv2_sp_GetPerfilUsuario @telegramChatId = :chat_id"
        rows = await self.db_manager.execute_query_async(query, {"chat_id": chat_id})
        if not rows:
            return None
        row = rows[0]
        gerencia_ids = [int(x) for x in row["gerencia_ids_csv"].split(",") if x] if row.get("gerencia_ids_csv") else []
        return {
            "user_id": row["user_id"],
            "role_id": row["role_id"],
            "gerencia_ids": gerencia_ids,
            "direccion_ids": [],
        }

    async def get_admin_chat_ids(self, admin_role_id: int = 1) -> list[int]:
        """
        Retorna los telegramChatId de usuarios con rol admin verificados y activos.

        Se usa para enviar notificaciones críticas sin depender de admin_chat_ids
        hardcodeados en settings. Se actualiza automáticamente cuando cambia el
        equipo de admins en el sistema.

        Args:
            admin_role_id: idRol considerado administrador (default 1)

        Returns:
            Lista de chat IDs de Telegram
        """
        query = "EXEC abcmasplus..BotIAv2_sp_GetAdminChatIds @idRolAdmin = :role_id"
        rows = await self.db_manager.execute_query_async(query, {"role_id": admin_role_id})
        return [row["telegramChatId"] for row in rows if row.get("telegramChatId")]

    async def update_last_activity(self, chat_id: int) -> None:
        """Actualiza fechaUltimaActividad del usuario."""
        query = "EXEC abcmasplus..BotIAv2_sp_ActualizarActividad @telegramChatId = :chat_id"
        await self.db_manager.execute_non_query_async(query, {"chat_id": chat_id})
