"""
Tests de permisos en ToolRegistry — Fase 4 SEC-01.

Verifica que:
- Tools sin permiso no aparecen en get_tools_prompt()
- Tools denegadas en ejecución retornan error sin ejecutar
- Tools permitidas ejecutan normalmente
- Sin permisos en UserContext → incluye todas (backward compat)
"""

import pytest

from src.agents.base.events import UserContext
from src.agents.tools.base import BaseTool, ToolCategory, ToolDefinition, ToolParameter, ToolResult
from src.agents.tools.registry import ToolRegistry


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

class EchoTool(BaseTool):
    """Tool de prueba que devuelve el input."""

    name = "echo"
    definition = ToolDefinition(
        name="echo",
        description="Devuelve el texto recibido.",
        category=ToolCategory.UTILITY,
        parameters=[ToolParameter(name="text", description="Texto a devolver")],
    )

    async def execute(self, text: str = "", **kwargs) -> ToolResult:
        return ToolResult(success=True, data={"result": text})


class PingTool(BaseTool):
    """Segunda tool de prueba."""

    name = "ping"
    definition = ToolDefinition(
        name="ping",
        description="Retorna pong.",
        category=ToolCategory.UTILITY,
    )

    async def execute(self, **kwargs) -> ToolResult:
        return ToolResult(success=True, data={"result": "pong"})


@pytest.fixture
def registry():
    ToolRegistry.reset()
    r = ToolRegistry()
    r.register(EchoTool())
    r.register(PingTool())
    yield r
    ToolRegistry.reset()


# ---------------------------------------------------------------------------
# get_tools_prompt — filtrado
# ---------------------------------------------------------------------------

def test_prompt_sin_permisos_incluye_todas(registry):
    """Sin UserContext o sin permisos → todas las tools visibles (backward compat)."""
    prompt = registry.get_tools_prompt()
    assert "echo" in prompt
    assert "ping" in prompt


def test_prompt_permisos_vacios_incluye_todas(registry):
    """permisos={} → backward compat, igual que sin contexto."""
    ctx = UserContext(user_id="1", permisos={})
    prompt = registry.get_tools_prompt(user_context=ctx)
    assert "echo" in prompt
    assert "ping" in prompt


def test_prompt_filtra_tool_no_permitida(registry):
    """Tool ausente en permisos no aparece en el prompt."""
    ctx = UserContext(user_id="1", permisos={"tool:echo": True})
    prompt = registry.get_tools_prompt(user_context=ctx)
    assert "echo" in prompt
    assert "ping" not in prompt


def test_prompt_tool_denegada_no_aparece(registry):
    """Tool con permitido=False no aparece en el prompt."""
    ctx = UserContext(user_id="1", permisos={"tool:echo": False, "tool:ping": True})
    prompt = registry.get_tools_prompt(user_context=ctx)
    assert "echo" not in prompt
    assert "ping" in prompt


def test_prompt_sin_tools_visibles(registry):
    """Si ninguna tool está permitida → 'No tools available.'"""
    ctx = UserContext(user_id="1", permisos={"tool:other": True})
    prompt = registry.get_tools_prompt(user_context=ctx)
    assert prompt == "No tools available."


# ---------------------------------------------------------------------------
# execute — segunda línea de defensa
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_execute_tool_permitida(registry):
    """Tool permitida ejecuta normalmente."""
    ctx = UserContext(user_id="1", permisos={"tool:echo": True})
    result = await registry.execute("echo", {"text": "hola"}, user_context=ctx)
    assert result.success is True
    assert result.data["result"] == "hola"


@pytest.mark.asyncio
async def test_execute_tool_denegada_retorna_error(registry):
    """Tool denegada en ejecución retorna ToolResult de error sin ejecutar."""
    ctx = UserContext(user_id="1", permisos={"tool:ping": True})
    result = await registry.execute("echo", {"text": "hola"}, user_context=ctx)
    assert result.success is False
    assert "permiso" in result.error.lower()


@pytest.mark.asyncio
async def test_execute_sin_permisos_ejecuta(registry):
    """Sin permisos cargados → ejecuta sin restricción (backward compat)."""
    ctx = UserContext(user_id="1")  # permisos vacío
    result = await registry.execute("echo", {"text": "test"}, user_context=ctx)
    assert result.success is True


@pytest.mark.asyncio
async def test_execute_tool_inexistente(registry):
    """Tool que no existe retorna error de not found."""
    result = await registry.execute("nonexistent", {}, user_context=None)
    assert result.success is False
    assert "not found" in result.error
