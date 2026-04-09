"""
ReloadPermissionsTool — Tool para que el agente recargue los permisos del usuario.

El agente puede invocar esta tool cuando detecta que el usuario menciona
problemas de acceso o cuando cambia de rol/gerencia.

Recurso SEC-01: tool:reload_permissions (esPublico=1)
"""

import logging
from typing import Any, Optional

from .base import BaseTool, ToolCategory, ToolDefinition, ToolParameter, ToolResult

logger = logging.getLogger(__name__)


class ReloadPermissionsTool(BaseTool):
    """
    Recarga los permisos del usuario actual invalidando el cache.

    El agente llama esta tool cuando:
    - El usuario menciona que no puede acceder a algo que debería poder
    - El usuario indica que su rol o gerencia cambió recientemente
    - Se detecta una posible inconsistencia de permisos
    """

    name = "reload_permissions"
    definition = ToolDefinition(
        name="reload_permissions",
        description=(
            "Recarga los permisos del usuario actual invalidando el cache. "
            "Úsala cuando el usuario mencione problemas de acceso o cuando su rol haya cambiado. "
            "Después de ejecutarla, informa al usuario qué capacidades están ahora disponibles."
        ),
        category=ToolCategory.UTILITY,
        parameters=[],
        returns="Confirmación de recarga con lista de permisos actualizados.",
    )

    def __init__(self, permission_service: Optional[Any] = None) -> None:
        self._permission_service = permission_service

    async def execute(self, user_id: Optional[str] = None, user_context: Optional[Any] = None, **kwargs) -> ToolResult:
        """
        Invalida el cache de permisos y retorna los nuevos permisos cargados.

        El user_context es inyectado por ToolRegistry.execute() antes de llamar esta tool.
        """
        db_user_id = getattr(user_context, "db_user_id", None) if user_context else None
        role_id = getattr(user_context, "role_id", None) if user_context else None
        gerencia_ids = getattr(user_context, "gerencia_ids", []) if user_context else []
        direccion_ids = getattr(user_context, "direccion_ids", []) if user_context else []

        if not self._permission_service or not db_user_id:
            return ToolResult(
                success=True,
                data={"message": "Permisos recargados (sin cambios detectados)."},
            )

        try:
            # Invalidar cache y recargar
            self._permission_service.invalidate(db_user_id)
            new_permisos = await self._permission_service.get_all_for_user(
                user_id=db_user_id,
                role_id=role_id or 0,
                gerencia_ids=gerencia_ids,
                direccion_ids=direccion_ids,
            )

            # Actualizar permisos en el contexto actual (efecto inmediato este request)
            if user_context is not None:
                user_context.permisos = new_permisos

            allowed = [r for r, ok in new_permisos.items() if ok]
            denied = [r for r, ok in new_permisos.items() if not ok]

            logger.info(
                f"ReloadPermissionsTool: user={db_user_id} "
                f"permisos recargados — {len(allowed)} permitidos, {len(denied)} denegados"
            )

            return ToolResult(
                success=True,
                data={
                    "message": "Permisos recargados exitosamente.",
                    "allowed": allowed,
                    "denied": denied,
                },
            )

        except Exception as e:
            logger.error(f"ReloadPermissionsTool error para user={db_user_id}: {e}")
            return ToolResult(success=False, data=None, error=f"Error recargando permisos: {e}")
