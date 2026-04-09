"""
Permission Repository - Consultas de permisos desde BotPermisos y BotRecurso.
"""

import logging
from typing import Any

logger = logging.getLogger(__name__)


class PermissionRepository:
    """
    Repositorio de permisos del nuevo sistema SEC-01.
    Todas las consultas se delegan a stored procedures BotIAv2_sp_*.
    """

    def __init__(self, db_manager: Any) -> None:
        self.db_manager = db_manager

    async def get_all_for_user(
        self,
        user_id: int,
        role_id: int,
        gerencia_ids: list[int],
        direccion_ids: list[int],
    ) -> list[dict]:
        """
        Retorna todas las filas de permisos que aplican al usuario.
        Cada fila tiene: recurso (str), permitido (bool), tipoResolucion (str)
        """
        gerencias_str = ",".join(str(g) for g in gerencia_ids) if gerencia_ids else None
        direcciones_str = ",".join(str(d) for d in direccion_ids) if direccion_ids else None

        query = """
            EXEC abcmasplus..BotIAv2_sp_GetPermisosUsuario
                @idUsuario    = :user_id,
                @idRol        = :role_id,
                @gerenciaIds  = :gerencia_ids,
                @direccionIds = :direccion_ids
        """
        return await self.db_manager.execute_query_async(query, {
            "user_id": user_id,
            "role_id": role_id,
            "gerencia_ids": gerencias_str,
            "direccion_ids": direcciones_str,
        })

    async def is_public(self, recurso: str) -> bool:
        """Verifica si un recurso es público (shortcut sin cargar todo el contexto)."""
        query = "EXEC abcmasplus..BotIAv2_sp_EsRecursoPublico @recurso = :recurso"
        rows = await self.db_manager.execute_query_async(query, {"recurso": recurso})
        return bool(rows and rows[0].get("esPublico"))

    async def get_active_tool_names(self) -> list[str]:
        """
        Retorna los nombres de las tools activas en BotIAv2_Recurso.
        El campo `recurso` tiene formato 'tool:<nombre>' (ej: 'tool:calculate').
        Se retorna solo la parte después de 'tool:'.
        """
        query = "EXEC abcmasplus..BotIAv2_sp_GetToolsActivas"
        rows = await self.db_manager.execute_query_async(query, {})
        names = []
        for row in rows:
            recurso = row.get("recurso", "")
            if recurso.startswith("tool:"):
                names.append(recurso[len("tool:"):])
        return names
