"""
Test de integración del flujo completo de permisos — Fase 6 SEC-01.

Flujo verificado:
  PermissionService → UserContext.permisos → ToolRegistry filtrado → execute con check

Sin BD real: usa mocks de PermissionRepository y UserQueryRepository.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock

from src.agents.base.events import UserContext
from src.agents.tools.base import BaseTool, ToolCategory, ToolDefinition, ToolParameter, ToolResult
from src.agents.tools.registry import ToolRegistry
from src.domain.auth.constants import EntityType, ResolutionType
from src.domain.auth.permission_repository import PermissionRepository
from src.domain.auth.permission_service import PermissionService


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_row(recurso: str, permitido: bool, tipo: str = ResolutionType.PERMISSIVE) -> dict:
    return {"recurso": recurso, "permitido": permitido, "tipoResolucion": tipo}


class QueryTool(BaseTool):
    name = "database_query"
    definition = ToolDefinition(
        name="database_query",
        description="Consultas SQL.",
        category=ToolCategory.DATABASE,
    )

    async def execute(self, **kwargs) -> ToolResult:
        return ToolResult(success=True, data={"result": "data"})


class CalculateTool(BaseTool):
    name = "calculate"
    definition = ToolDefinition(
        name="calculate",
        description="Cálculos.",
        category=ToolCategory.UTILITY,
    )

    async def execute(self, **kwargs) -> ToolResult:
        return ToolResult(success=True, data={"result": 42})


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def registry():
    ToolRegistry.reset()
    r = ToolRegistry()
    r.register(QueryTool())
    r.register(CalculateTool())
    yield r
    ToolRegistry.reset()


@pytest.fixture
def permission_service():
    repo = MagicMock(spec=PermissionRepository)
    return PermissionService(repository=repo)


# ---------------------------------------------------------------------------
# Tests: PermissionService → UserContext → ToolRegistry
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_flujo_rol_permite_tools(permission_service, registry):
    """
    Gerente (rol 2) tiene permiso para database_query y calculate.
    ToolRegistry debe mostrar ambas y permitir ejecución.
    """
    rows = [
        _make_row("tool:database_query", True),
        _make_row("tool:calculate", True),
    ]
    permission_service.repository.get_all_for_user = AsyncMock(return_value=rows)

    permisos = await permission_service.get_all_for_user(
        user_id=10, role_id=2, gerencia_ids=[1], direccion_ids=[]
    )

    ctx = UserContext(user_id="100", db_user_id=10, role_id=2, gerencia_ids=[1], permisos=permisos)

    # Filtrado en prompt
    prompt = registry.get_tools_prompt(user_context=ctx)
    assert "database_query" in prompt
    assert "calculate" in prompt

    # Ejecución permitida
    result = await registry.execute("database_query", {}, user_context=ctx)
    assert result.success is True


@pytest.mark.asyncio
async def test_flujo_usuario_denegado_pisa_rol(permission_service, registry):
    """
    Rol permite database_query, pero el usuario tiene deny explícito (definitivo).
    Tool debe estar ausente del prompt y denegada en ejecución.
    """
    rows = [
        # deny definitivo de usuario
        _make_row("tool:database_query", False, ResolutionType.DEFINITIVE),
        # rol permisivo que dice sí
        _make_row("tool:database_query", True, ResolutionType.PERMISSIVE),
        _make_row("tool:calculate", True, ResolutionType.PERMISSIVE),
    ]
    permission_service.repository.get_all_for_user = AsyncMock(return_value=rows)

    permisos = await permission_service.get_all_for_user(
        user_id=10, role_id=2, gerencia_ids=[], direccion_ids=[]
    )

    ctx = UserContext(user_id="100", db_user_id=10, role_id=2, permisos=permisos)

    # database_query denegado, calculate permitido
    assert permisos.get("tool:database_query") is False
    assert permisos.get("tool:calculate") is True

    prompt = registry.get_tools_prompt(user_context=ctx)
    assert "database_query" not in prompt
    assert "calculate" in prompt

    # Ejecución denegada
    result = await registry.execute("database_query", {}, user_context=ctx)
    assert result.success is False
    assert "permiso" in result.error.lower()


@pytest.mark.asyncio
async def test_flujo_sin_permisos_backward_compat(registry):
    """
    Sin permisos cargados (UserContext vacío): todas las tools visibles y ejecutables.
    """
    ctx = UserContext(user_id="100")  # permisos = {}

    prompt = registry.get_tools_prompt(user_context=ctx)
    assert "database_query" in prompt
    assert "calculate" in prompt

    result = await registry.execute("calculate", {}, user_context=ctx)
    assert result.success is True


@pytest.mark.asyncio
async def test_flujo_cache_hit_evita_query(permission_service, registry):
    """
    Segunda llamada a get_all_for_user con mismo user_id usa cache — no hace query a BD.
    """
    rows = [_make_row("tool:calculate", True)]
    permission_service.repository.get_all_for_user = AsyncMock(return_value=rows)

    await permission_service.get_all_for_user(10, 2, [], [])
    await permission_service.get_all_for_user(10, 2, [], [])

    # Solo 1 llamada a BD aunque se invocó 2 veces
    assert permission_service.repository.get_all_for_user.call_count == 1


@pytest.mark.asyncio
async def test_flujo_invalidate_fuerza_recarga(permission_service, registry):
    """
    Después de invalidate(), la siguiente llamada vuelve a consultar BD.
    """
    rows = [_make_row("tool:calculate", True)]
    permission_service.repository.get_all_for_user = AsyncMock(return_value=rows)

    await permission_service.get_all_for_user(10, 2, [], [])
    permission_service.invalidate(10)
    await permission_service.get_all_for_user(10, 2, [], [])

    assert permission_service.repository.get_all_for_user.call_count == 2


@pytest.mark.asyncio
async def test_flujo_recurso_publico_siempre_permitido(permission_service, registry):
    """
    Recursos con esPublico=1 llegan como rows con permitido=True desde UNION en PermissionRepository.
    Siempre aparecen en permisos aunque el usuario no tenga regla explícita.
    """
    # El UNION en PermissionRepository ya incluye esPublico=1 rows
    rows = [
        _make_row("tool:datetime", True),   # público
        _make_row("tool:calculate", True),
    ]
    permission_service.repository.get_all_for_user = AsyncMock(return_value=rows)

    permisos = await permission_service.get_all_for_user(10, 6, [], [])  # rol=6 Consulta

    assert permisos.get("tool:datetime") is True
    assert permisos.get("tool:calculate") is True
    assert permisos.get("tool:database_query", False) is False  # sin regla → denegado
