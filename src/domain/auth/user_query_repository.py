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
        query = """
            SELECT
                u.idUsuario, u.Nombre, u.email, u.idRol, u.puesto,
                u.Empresa, u.Activa,
                r.nombre AS rolNombre,
                ut.idUsuarioTelegram, ut.telegramChatId, ut.telegramUsername,
                ut.telegramFirstName, ut.telegramLastName, ut.alias,
                ut.esPrincipal, ut.estado, ut.verificado, ut.fechaUltimaActividad
            FROM abcmasplus..UsuariosTelegram ut
            INNER JOIN abcmasplus..Usuarios u ON ut.idUsuario = u.idUsuario
            LEFT JOIN abcmasplus..Roles r ON u.idRol = r.idRol
            WHERE ut.telegramChatId = :chat_id AND ut.activo = 1
        """
        rows = await self.db_manager.execute_query_async(query, {"chat_id": chat_id})
        return TelegramUser(rows[0]) if rows else None

    async def get_by_user_id(self, user_id: int) -> Optional[TelegramUser]:
        """Obtiene usuario por idUsuario (cuenta principal de Telegram)."""
        query = """
            SELECT
                u.idUsuario, u.Nombre, u.email, u.idRol, u.puesto,
                u.Empresa, u.Activa,
                r.nombre AS rolNombre,
                ut.idUsuarioTelegram, ut.telegramChatId, ut.telegramUsername,
                ut.telegramFirstName, ut.telegramLastName, ut.alias,
                ut.esPrincipal, ut.estado, ut.verificado, ut.fechaUltimaActividad
            FROM abcmasplus..Usuarios u
            LEFT JOIN abcmasplus..Roles r ON u.idRol = r.idRol
            LEFT JOIN abcmasplus..UsuariosTelegram ut
                ON u.idUsuario = ut.idUsuario AND ut.esPrincipal = 1 AND ut.activo = 1
            WHERE u.idUsuario = :user_id
        """
        rows = await self.db_manager.execute_query_async(query, {"user_id": user_id})
        return TelegramUser(rows[0]) if rows else None

    async def get_profile_for_permissions(self, chat_id: int) -> Optional[dict]:
        """
        Query liviana para AuthMiddleware — solo trae lo necesario para resolver permisos.
        Retorna: user_id, role_id, gerencia_ids, direccion_ids
        """
        query = """
            SELECT
                u.idUsuario                                         AS user_id,
                u.idRol                                             AS role_id,
                STUFF((
                    SELECT ',' + CAST(gu.idGerencia AS VARCHAR)
                    FROM abcmasplus..GerenciasUsuarios gu
                    WHERE gu.idUsuario = u.idUsuario AND gu.activo = 1
                    FOR XML PATH('')
                ), 1, 1, '')                                        AS gerencia_ids_csv,
                STUFF((
                    SELECT ',' + CAST(du.idDireccion AS VARCHAR)
                    FROM abcmasplus..DireccionesUsuarios du
                    WHERE du.idUsuario = u.idUsuario AND du.activo = 1
                    FOR XML PATH('')
                ), 1, 1, '')                                        AS direccion_ids_csv
            FROM abcmasplus..UsuariosTelegram ut
            INNER JOIN abcmasplus..Usuarios u ON ut.idUsuario = u.idUsuario
            WHERE ut.telegramChatId = :chat_id AND ut.activo = 1
        """
        rows = await self.db_manager.execute_query_async(query, {"chat_id": chat_id})
        if not rows:
            return None
        row = rows[0]
        gerencia_ids = [int(x) for x in row["gerencia_ids_csv"].split(",") if x] if row.get("gerencia_ids_csv") else []
        direccion_ids = [int(x) for x in row["direccion_ids_csv"].split(",") if x] if row.get("direccion_ids_csv") else []
        return {
            "user_id": row["user_id"],
            "role_id": row["role_id"],
            "gerencia_ids": gerencia_ids,
            "direccion_ids": direccion_ids,
        }

    async def update_last_activity(self, chat_id: int) -> None:
        """Actualiza fechaUltimaActividad del usuario."""
        query = """
            UPDATE abcmasplus..UsuariosTelegram
            SET fechaUltimaActividad = GETDATE()
            WHERE telegramChatId = :chat_id AND activo = 1
        """
        await self.db_manager.execute_non_query_async(query, {"chat_id": chat_id})
