"""
Tests para PermissionService — lógica de resolución de permisos.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import time

from src.domain.auth.permission_service import PermissionService
from src.domain.auth.permission_repository import PermissionRepository


def make_row(recurso, permitido, tipo_resolucion="permisivo"):
    return {"recurso": recurso, "permitido": permitido, "tipoResolucion": tipo_resolucion}


@pytest.fixture
def mock_repo():
    return AsyncMock(spec=PermissionRepository)


@pytest.fixture
def service(mock_repo):
    return PermissionService(repository=mock_repo)


class TestResolucion:

    @pytest.mark.asyncio
    async def test_rol_permite(self, service, mock_repo):
        """Rol autenticado con permiso → True."""
        mock_repo.get_all_for_user.return_value = [
            make_row("tool:database_query", True, "permisivo"),
        ]
        permisos = await service.get_all_for_user(1, 1, [], [])
        assert permisos["tool:database_query"] is True

    @pytest.mark.asyncio
    async def test_usuario_deniega_sobre_rol_que_permite(self, service, mock_repo):
        """Override definitivo de usuario con permitido=False pisa al rol."""
        mock_repo.get_all_for_user.return_value = [
            make_row("tool:database_query", True,  "permisivo"),   # rol permite
            make_row("tool:database_query", False, "definitivo"),  # usuario deniega
        ]
        permisos = await service.get_all_for_user(1, 1, [], [])
        assert permisos["tool:database_query"] is False

    @pytest.mark.asyncio
    async def test_gerencia_permite_sin_rol_especifico(self, service, mock_repo):
        """Gerencia permite (permisivo) → True aunque no haya regla de rol."""
        mock_repo.get_all_for_user.return_value = [
            make_row("tool:knowledge_search", True, "permisivo"),
        ]
        permisos = await service.get_all_for_user(1, 3, [10], [])
        assert permisos["tool:knowledge_search"] is True

    @pytest.mark.asyncio
    async def test_permiso_expirado_no_llega(self, service, mock_repo):
        """El repo ya filtra fechaExpiracion — sin filas → DENEGADO."""
        mock_repo.get_all_for_user.return_value = []
        permisos = await service.get_all_for_user(1, 1, [], [])
        assert permisos.get("tool:database_query", False) is False

    @pytest.mark.asyncio
    async def test_recurso_publico_siempre_permitido(self, service, mock_repo):
        """esPublico=1 llega como fila permisiva desde el UNION del repo."""
        mock_repo.get_all_for_user.return_value = [
            make_row("cmd:/start", True, "permisivo"),
            make_row("tool:reload_permissions", True, "permisivo"),
        ]
        permisos = await service.get_all_for_user(1, 6, [], [])
        assert permisos["cmd:/start"] is True
        assert permisos["tool:reload_permissions"] is True

    @pytest.mark.asyncio
    async def test_sin_ninguna_regla_denegado(self, service, mock_repo):
        """Sin filas para un recurso → False (default deny)."""
        mock_repo.get_all_for_user.return_value = []
        permisos = await service.get_all_for_user(1, 1, [], [])
        assert permisos.get("tool:database_query", False) is False


class TestCache:

    @pytest.mark.asyncio
    async def test_cache_hit_no_hace_query(self, service, mock_repo):
        """Segundo llamado dentro del TTL no consulta el repo."""
        mock_repo.get_all_for_user.return_value = [
            make_row("tool:calculate", True, "permisivo"),
        ]
        await service.get_all_for_user(1, 1, [], [])
        await service.get_all_for_user(1, 1, [], [])
        assert mock_repo.get_all_for_user.call_count == 1

    @pytest.mark.asyncio
    async def test_invalidate_fuerza_requey(self, service, mock_repo):
        """invalidate(user_id) elimina el cache y el siguiente llamado consulta BD."""
        mock_repo.get_all_for_user.return_value = [
            make_row("tool:calculate", True, "permisivo"),
        ]
        await service.get_all_for_user(1, 1, [], [])
        service.invalidate(1)
        await service.get_all_for_user(1, 1, [], [])
        assert mock_repo.get_all_for_user.call_count == 2

    @pytest.mark.asyncio
    async def test_invalidate_all_vacia_cache(self, service, mock_repo):
        """invalidate_all() elimina todos los usuarios del cache."""
        mock_repo.get_all_for_user.return_value = []
        await service.get_all_for_user(1, 1, [], [])
        await service.get_all_for_user(2, 1, [], [])
        count = service.invalidate_all()
        assert count == 2
        await service.get_all_for_user(1, 1, [], [])
        assert mock_repo.get_all_for_user.call_count == 3
