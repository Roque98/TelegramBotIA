"""
Permission Service - Lógica de resolución de permisos con cache LRU.

Jerarquía de resolución:
1. esPublico=1 en BotRecurso → PERMITIDO inmediatamente
2. Entrada 'definitivo' (usuario) → es la respuesta final
3. Entre entradas 'permisivo' → si ALGUNA permite, PERMITIDO
4. Sin ninguna fila → DENEGADO (default deny)
"""

import logging
import time
from collections import OrderedDict
from typing import Any, Optional

from .constants import ResolutionType
from .permission_repository import PermissionRepository

logger = logging.getLogger(__name__)

_CACHE_TTL_SECONDS = 60
_CACHE_MAX_SIZE = 500


class PermissionService:
    """
    Servicio de permisos con cache LRU TTL.

    - Cache por user_id con TTL de 60s
    - invalidate(user_id): forzar recarga para un usuario
    - invalidate_all(): vaciar todo el cache
    """

    def __init__(self, repository: PermissionRepository) -> None:
        self.repository = repository
        # OrderedDict como LRU: {user_id: {"data": dict, "ts": float}}
        self._cache: OrderedDict[int, dict] = OrderedDict()

    # ------------------------------------------------------------------
    # API pública
    # ------------------------------------------------------------------

    async def get_all_for_user(
        self,
        user_id: int,
        role_id: int,
        gerencia_ids: list[int],
        direccion_ids: list[int],
    ) -> dict[str, bool]:
        """
        Retorna dict[recurso, permitido] para el usuario.
        Usa cache LRU TTL — si expiró o no existe, consulta BD.
        """
        cached = self._cache.get(user_id)
        if cached and (time.monotonic() - cached["ts"]) < _CACHE_TTL_SECONDS:
            self._cache.move_to_end(user_id)
            return cached["data"]

        rows = await self.repository.get_all_for_user(
            user_id, role_id, gerencia_ids, direccion_ids
        )
        resolved = self._resolve(rows)

        self._cache[user_id] = {"data": resolved, "ts": time.monotonic()}
        self._cache.move_to_end(user_id)
        if len(self._cache) > _CACHE_MAX_SIZE:
            self._cache.popitem(last=False)

        logger.debug(f"PermissionService: user={user_id} permisos cargados ({len(resolved)} recursos)")
        return resolved

    async def can(
        self,
        user_id: int,
        recurso: str,
        role_id: int,
        gerencia_ids: list[int],
        direccion_ids: list[int],
    ) -> bool:
        """Verifica si el usuario puede acceder a un recurso específico."""
        permisos = await self.get_all_for_user(user_id, role_id, gerencia_ids, direccion_ids)
        return permisos.get(recurso, False)

    def invalidate(self, user_id: int) -> None:
        """Invalida el cache de un usuario — fuerza recarga en el próximo request."""
        self._cache.pop(user_id, None)
        logger.debug(f"PermissionService: cache invalidado para user={user_id}")

    def invalidate_all(self) -> int:
        """Vacía todo el cache. Retorna la cantidad de entradas eliminadas."""
        count = len(self._cache)
        self._cache.clear()
        logger.info(f"PermissionService: cache completo invalidado ({count} entradas)")
        return count

    # ------------------------------------------------------------------
    # Lógica de resolución
    # ------------------------------------------------------------------

    def _resolve(self, rows: list[dict]) -> dict[str, bool]:
        """
        Aplica la jerarquía de resolución sobre las filas de BotPermisos.

        Por cada recurso:
        - Si hay entrada 'definitivo' → su valor es final
        - Si hay entradas 'permisivo' → permitido si ALGUNA tiene permitido=True
        - Sin filas → False (default deny)
        """
        # Agrupar por recurso
        by_resource: dict[str, list[dict]] = {}
        for row in rows:
            recurso = row.get("recurso") or row.get("Recurso") or ""
            if recurso:
                by_resource.setdefault(recurso, []).append(row)

        result: dict[str, bool] = {}
        for recurso, entries in by_resource.items():
            result[recurso] = self._resolve_resource(entries)

        return result

    def _resolve_resource(self, entries: list[dict]) -> bool:
        # Paso 1: buscar entrada definitiva (usuario individual)
        for e in entries:
            tipo = e.get("tipoResolucion") or e.get("TipoResolucion") or ""
            if tipo == ResolutionType.DEFINITIVE:
                return bool(e.get("permitido") or e.get("Permitido"))

        # Paso 2: entre permisivos, cualquiera que permita es suficiente
        for e in entries:
            if bool(e.get("permitido") or e.get("Permitido")):
                return True

        # Paso 3: default deny
        return False
