"""
Permission Repository - Consultas de permisos desde BotPermisos y BotRecurso.
"""

import logging
from typing import Any

logger = logging.getLogger(__name__)


class PermissionRepository:
    """
    Repositorio de permisos del nuevo sistema SEC-01.

    La query principal usa UNION de dos partes:
    1. Filas de BotPermisos que aplican al usuario (por rol, gerencia, dirección, usuario)
    2. Recursos con esPublico=1 de BotRecurso — siempre permitidos sin consultar BotPermisos
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
        # Preparar listas para IN clause (SQL Server no acepta arrays directamente)
        gerencias_str = ",".join(str(g) for g in gerencia_ids) if gerencia_ids else "0"
        direcciones_str = ",".join(str(d) for d in direccion_ids) if direccion_ids else "0"

        query = f"""
            SELECT br.recurso, bp.permitido, bte.tipoResolucion
            FROM abcmasplus..BotPermisos bp
            INNER JOIN abcmasplus..BotRecurso     br  ON bp.idRecurso    = br.idRecurso
            INNER JOIN abcmasplus..BotTipoEntidad bte ON bp.idTipoEntidad = bte.idTipoEntidad
            WHERE bp.activo = 1
              AND br.activo = 1
              AND (bp.fechaExpiracion IS NULL OR bp.fechaExpiracion > GETDATE())
              AND (
                (bte.nombre = 'usuario' AND bp.idEntidad = :user_id)
                OR (bte.nombre = 'autenticado'
                    AND (bp.idRolRequerido IS NULL OR bp.idRolRequerido = :role_id))
                OR (bte.nombre = 'gerencia'
                    AND bp.idEntidad IN ({gerencias_str})
                    AND (bp.idRolRequerido IS NULL OR bp.idRolRequerido = :role_id))
                OR (bte.nombre = 'direccion'
                    AND bp.idEntidad IN ({direcciones_str})
                    AND (bp.idRolRequerido IS NULL OR bp.idRolRequerido = :role_id))
              )

            UNION ALL

            SELECT br.recurso, 1 AS permitido, 'permisivo' AS tipoResolucion
            FROM abcmasplus..BotRecurso br
            WHERE br.esPublico = 1
              AND br.activo = 1
        """

        params = {
            "user_id": user_id,
            "role_id": role_id,
        }

        return await self.db_manager.execute_query_async(query, params)

    async def is_public(self, recurso: str) -> bool:
        """Verifica si un recurso es público (shortcut sin cargar todo el contexto)."""
        query = """
            SELECT esPublico
            FROM abcmasplus..BotRecurso
            WHERE recurso = :recurso AND activo = 1
        """
        rows = await self.db_manager.execute_query_async(query, {"recurso": recurso})
        return bool(rows and rows[0].get("esPublico"))
