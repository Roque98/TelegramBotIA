"""
Tests para el catálogo de tools driven by BotIAv2_Recurso.

Cubre:
- create_tool_registry con lista de tools activas desde BD
- Fallback cuando BD no disponible (active_tool_names=None)
- Tools con dependencia faltante se omiten sin explotar
- Tool en BD pero no en catálogo genera warning y se ignora
- get_active_tool_names filtra por prefijo 'tool:'
- Mapa completo: cada nombre del catálogo instancia la tool correcta
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from src.agents.tools.registry import ToolRegistry
from src.pipeline.factory import create_tool_registry, _build_tool_catalog
from src.domain.auth.permission_repository import PermissionRepository


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_deps(**overrides):
    """Crea un conjunto mínimo de dependencias mockeadas."""
    defaults = dict(
        db_manager=MagicMock(),
        knowledge_manager=MagicMock(),
        memory_service=MagicMock(),
        permission_service=MagicMock(),
        agent_config_service=MagicMock(),
        data_llm=MagicMock(),
        db_registry=None,
        bot_token="fake-token",
    )
    defaults.update(overrides)
    return defaults


# ---------------------------------------------------------------------------
# _build_tool_catalog
# ---------------------------------------------------------------------------

class TestBuildToolCatalog:
    """El catálogo debe contener exactamente los nombres del codebase."""

    EXPECTED_KEYS = {
        "database_query",
        "knowledge_search",
        "calculate",
        "datetime",
        "save_preference",
        "save_memory",
        "reload_permissions",
        "reload_agent_config",
        "read_attachment",
    }

    def test_catalog_contains_all_known_tools(self):
        catalog = _build_tool_catalog(**_make_deps())
        assert self.EXPECTED_KEYS == set(catalog.keys())

    def test_catalog_values_are_callable(self):
        catalog = _build_tool_catalog(**_make_deps())
        for name, fn in catalog.items():
            assert callable(fn), f"'{name}' no es callable"

    def test_calculate_instantiates_without_deps(self):
        catalog = _build_tool_catalog(**_make_deps())
        tool = catalog["calculate"]()
        assert tool is not None
        assert tool.name == "calculate"

    def test_datetime_instantiates_without_deps(self):
        catalog = _build_tool_catalog(**_make_deps())
        tool = catalog["datetime"]()
        assert tool is not None
        assert tool.name == "datetime"

    def test_knowledge_search_returns_none_when_no_manager(self):
        """Sin knowledge_manager la lambda debe retornar None."""
        catalog = _build_tool_catalog(**_make_deps(knowledge_manager=None))
        result = catalog["knowledge_search"]()
        assert result is None

    def test_read_attachment_returns_none_when_no_token(self):
        """Sin bot_token la lambda debe retornar None."""
        # El catálogo recibe el token ya resuelto; None significa que no hay token.
        catalog = _build_tool_catalog(**_make_deps(bot_token=None))
        # bot_token=None → lambda retorna None (sin fallback a settings aquí)
        result = catalog["read_attachment"]()
        assert result is None  # token=None → no se instancia

    def test_read_attachment_instantiates_with_token(self):
        catalog = _build_tool_catalog(**_make_deps(bot_token="tok123"))
        tool = catalog["read_attachment"]()
        assert tool is not None
        assert tool.name == "read_attachment"


# ---------------------------------------------------------------------------
# create_tool_registry — BD-driven
# ---------------------------------------------------------------------------

class TestCreateToolRegistryFromDB:
    """El registry debe solo registrar lo que viene en active_tool_names."""

    def test_only_active_tools_are_registered(self):
        registry = create_tool_registry(
            active_tool_names=["calculate", "datetime"],
        )
        assert set(registry.get_tool_names()) == {"calculate", "datetime"}

    def test_single_tool(self):
        registry = create_tool_registry(active_tool_names=["calculate"])
        assert registry.has_tool("calculate")
        assert len(registry) == 1

    def test_empty_list_registers_nothing(self):
        registry = create_tool_registry(active_tool_names=[])
        assert len(registry) == 0

    def test_tool_not_in_catalog_is_ignored(self):
        """Una tool activa en BD pero sin código en el catálogo se descarta silenciosamente."""
        registry = create_tool_registry(
            active_tool_names=["calculate", "tool_que_no_existe"],
        )
        assert registry.has_tool("calculate")
        assert not registry.has_tool("tool_que_no_existe")

    def test_tool_with_missing_dep_is_skipped(self):
        """knowledge_search sin knowledge_manager retorna None → se omite."""
        registry = create_tool_registry(
            knowledge_manager=None,
            active_tool_names=["calculate", "knowledge_search"],
        )
        assert registry.has_tool("calculate")
        assert not registry.has_tool("knowledge_search")

    def test_read_attachment_skipped_without_token(self):
        # Parchamos settings.telegram_bot_token para garantizar None en el test
        with patch("src.pipeline.factory.settings") as mock_settings:
            mock_settings.telegram_bot_token = None
            mock_settings.openai_api_key = "fake"
            mock_settings.openai_loop_model = "gpt-4"
            mock_settings.openai_data_model = "gpt-4"
            registry = create_tool_registry(
                bot_token=None,
                active_tool_names=["calculate", "read_attachment"],
            )
        assert registry.has_tool("calculate")
        assert not registry.has_tool("read_attachment")

    def test_all_catalog_tools_register_when_all_active(self):
        """Con todas las dependencias presentes y toda la lista, se registra todo."""
        all_names = [
            "database_query", "knowledge_search", "calculate", "datetime",
            "save_preference", "save_memory", "reload_permissions",
            "reload_agent_config", "read_attachment",
        ]
        registry = create_tool_registry(
            db_manager=MagicMock(),
            knowledge_manager=MagicMock(),
            memory_service=MagicMock(),
            permission_service=MagicMock(),
            agent_config_service=MagicMock(),
            bot_token="tok",
            data_llm=MagicMock(),
            active_tool_names=all_names,
        )
        assert set(registry.get_tool_names()) == set(all_names)

    def test_returns_tool_registry_instance(self):
        registry = create_tool_registry(active_tool_names=["calculate"])
        assert isinstance(registry, ToolRegistry)


# ---------------------------------------------------------------------------
# create_tool_registry — Fallback (BD no disponible)
# ---------------------------------------------------------------------------

class TestCreateToolRegistryFallback:
    """Cuando active_tool_names=None debe registrar todo el catálogo."""

    def test_none_registers_all_instantiatable_tools(self):
        """Con todas las deps, active_tool_names=None registra todo."""
        registry = create_tool_registry(
            db_manager=MagicMock(),
            knowledge_manager=MagicMock(),
            memory_service=MagicMock(),
            permission_service=MagicMock(),
            agent_config_service=MagicMock(),
            bot_token="tok",
            data_llm=MagicMock(),
            active_tool_names=None,
        )
        # Deben estar al menos las tools que no necesitan deps opcionales
        assert registry.has_tool("calculate")
        assert registry.has_tool("datetime")

    def test_none_with_missing_deps_skips_those_tools(self):
        """Con active_tool_names=None y sin deps opcionales, esas tools se omiten."""
        with patch("src.pipeline.factory.settings") as mock_settings:
            mock_settings.telegram_bot_token = None
            mock_settings.openai_api_key = "fake"
            mock_settings.openai_loop_model = "gpt-4"
            mock_settings.openai_data_model = "gpt-4"
            registry = create_tool_registry(
                knowledge_manager=None,
                bot_token=None,
                data_llm=None,
                active_tool_names=None,
            )
        assert not registry.has_tool("knowledge_search")
        assert not registry.has_tool("read_attachment")
        assert not registry.has_tool("database_query")  # sin data_llm
        assert registry.has_tool("calculate")
        assert registry.has_tool("datetime")


# ---------------------------------------------------------------------------
# get_active_tool_names — PermissionRepository
# ---------------------------------------------------------------------------

class TestGetActiveToolNames:
    """get_active_tool_names debe filtrar por 'tool:' y retornar solo el sufijo."""

    @pytest.mark.asyncio
    async def test_returns_suffix_without_prefix(self):
        mock_db = MagicMock()
        mock_db.execute_query_async = AsyncMock(return_value=[
            {"recurso": "tool:calculate"},
            {"recurso": "tool:datetime"},
        ])
        repo = PermissionRepository(db_manager=mock_db)
        result = await repo.get_active_tool_names()
        assert result == ["calculate", "datetime"]

    @pytest.mark.asyncio
    async def test_ignores_non_tool_resources(self):
        """Recursos cmd: u otros tipos no deben aparecer."""
        mock_db = MagicMock()
        mock_db.execute_query_async = AsyncMock(return_value=[
            {"recurso": "tool:calculate"},
            {"recurso": "cmd:/stats"},       # debe ignorarse
            {"recurso": "other:something"},  # debe ignorarse
        ])
        repo = PermissionRepository(db_manager=mock_db)
        result = await repo.get_active_tool_names()
        assert result == ["calculate"]

    @pytest.mark.asyncio
    async def test_empty_table_returns_empty_list(self):
        mock_db = MagicMock()
        mock_db.execute_query_async = AsyncMock(return_value=[])
        repo = PermissionRepository(db_manager=mock_db)
        result = await repo.get_active_tool_names()
        assert result == []

    @pytest.mark.asyncio
    async def test_queries_only_active_tools(self):
        """Verificar que la query incluye tipoRecurso='tool' y activo=1."""
        mock_db = MagicMock()
        mock_db.execute_query_async = AsyncMock(return_value=[])
        repo = PermissionRepository(db_manager=mock_db)
        await repo.get_active_tool_names()

        call_args = mock_db.execute_query_async.call_args
        query: str = call_args[0][0]
        assert "tipoRecurso = 'tool'" in query
        assert "activo = 1" in query

    @pytest.mark.asyncio
    async def test_all_catalog_tool_names_recognized(self):
        """Todos los nombres del TOOL_CATALOG deben ser parseables desde el prefijo."""
        catalog_names = [
            "database_query", "knowledge_search", "calculate", "datetime",
            "save_preference", "save_memory", "reload_permissions",
            "reload_agent_config", "read_attachment",
        ]
        rows = [{"recurso": f"tool:{n}"} for n in catalog_names]
        mock_db = MagicMock()
        mock_db.execute_query_async = AsyncMock(return_value=rows)
        repo = PermissionRepository(db_manager=mock_db)
        result = await repo.get_active_tool_names()
        assert set(result) == set(catalog_names)
