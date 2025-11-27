"""
Tests unitarios para ToolRegistry.
"""
import pytest
from src.tools.tool_base import (
    BaseTool,
    ToolMetadata,
    ToolParameter,
    ToolResult,
    ToolCategory,
    ParameterType
)
from src.tools.tool_registry import ToolRegistry, get_registry


class MockTool(BaseTool):
    """Tool de prueba."""

    def __init__(self, name="mock", commands=None, category=ToolCategory.UTILITY):
        self._custom_name = name
        self._custom_commands = commands or [f"/{name}"]
        self._custom_category = category
        super().__init__()

    def get_metadata(self):
        return ToolMetadata(
            name=self._custom_name,
            description=f"Tool {self._custom_name}",
            commands=self._custom_commands,
            category=self._custom_category,
            requires_auth=True,
            required_permissions=[f"/{self._custom_name}"]
        )

    def get_parameters(self):
        return []

    async def execute(self, user_id, params, context):
        return ToolResult.success_result(data=f"Executed {self._custom_name}")


class TestToolRegistry:
    """Tests para ToolRegistry."""

    @pytest.fixture(autouse=True)
    def setup_and_teardown(self):
        """Limpiar registry antes y después de cada test."""
        registry = ToolRegistry()
        registry.clear()
        yield
        registry.clear()

    def test_singleton_pattern(self):
        """Test que ToolRegistry es singleton."""
        registry1 = ToolRegistry()
        registry2 = ToolRegistry()

        assert registry1 is registry2

    def test_get_registry_function(self):
        """Test función get_registry."""
        registry1 = get_registry()
        registry2 = get_registry()

        assert registry1 is registry2

    def test_register_tool(self):
        """Test registrar tool."""
        registry = ToolRegistry()
        tool = MockTool("test")

        registry.register(tool)

        assert registry.get_tools_count() == 1
        assert registry.get_tool_by_name("test") is tool

    def test_register_duplicate_tool_raises_error(self):
        """Test que registrar tool duplicado lanza error."""
        registry = ToolRegistry()
        tool1 = MockTool("test")
        tool2 = MockTool("test")

        registry.register(tool1)

        with pytest.raises(ValueError, match="ya está registrado"):
            registry.register(tool2)

    def test_register_duplicate_command_raises_error(self):
        """Test que comandos duplicados lanzan error."""
        registry = ToolRegistry()
        tool1 = MockTool("tool1", commands=["/shared"])
        tool2 = MockTool("tool2", commands=["/shared"])

        registry.register(tool1)

        with pytest.raises(ValueError, match="ya está registrado por el tool"):
            registry.register(tool2)

    def test_unregister_tool(self):
        """Test desregistrar tool."""
        registry = ToolRegistry()
        tool = MockTool("test")

        registry.register(tool)
        assert registry.get_tools_count() == 1

        result = registry.unregister("test")
        assert result is True
        assert registry.get_tools_count() == 0

    def test_unregister_nonexistent_tool(self):
        """Test desregistrar tool inexistente."""
        registry = ToolRegistry()

        result = registry.unregister("nonexistent")
        assert result is False

    def test_get_tool_by_name(self):
        """Test buscar tool por nombre."""
        registry = ToolRegistry()
        tool = MockTool("test")

        registry.register(tool)

        found_tool = registry.get_tool_by_name("test")
        assert found_tool is tool

        not_found = registry.get_tool_by_name("nonexistent")
        assert not_found is None

    def test_get_tool_by_command(self):
        """Test buscar tool por comando."""
        registry = ToolRegistry()
        tool = MockTool("test", commands=["/test", "/t"])

        registry.register(tool)

        found_by_first = registry.get_tool_by_command("/test")
        assert found_by_first is tool

        found_by_second = registry.get_tool_by_command("/t")
        assert found_by_second is tool

        not_found = registry.get_tool_by_command("/nonexistent")
        assert not_found is None

    def test_get_all_tools(self):
        """Test obtener todos los tools."""
        registry = ToolRegistry()
        tool1 = MockTool("test1")
        tool2 = MockTool("test2")

        registry.register(tool1)
        registry.register(tool2)

        all_tools = registry.get_all_tools()
        assert len(all_tools) == 2
        assert tool1 in all_tools
        assert tool2 in all_tools

    def test_get_tools_by_category(self):
        """Test obtener tools por categoría."""
        registry = ToolRegistry()
        db_tool = MockTool("db", category=ToolCategory.DATABASE)
        util_tool1 = MockTool("util1", category=ToolCategory.UTILITY)
        util_tool2 = MockTool("util2", category=ToolCategory.UTILITY)

        registry.register(db_tool)
        registry.register(util_tool1)
        registry.register(util_tool2)

        db_tools = registry.get_tools_by_category(ToolCategory.DATABASE)
        assert len(db_tools) == 1
        assert db_tool in db_tools

        util_tools = registry.get_tools_by_category(ToolCategory.UTILITY)
        assert len(util_tools) == 2
        assert util_tool1 in util_tools
        assert util_tool2 in util_tools

        system_tools = registry.get_tools_by_category(ToolCategory.SYSTEM)
        assert len(system_tools) == 0

    def test_get_commands_list(self):
        """Test obtener lista de comandos."""
        registry = ToolRegistry()
        tool1 = MockTool("test1", commands=["/test1", "/t1"])
        tool2 = MockTool("test2", commands=["/test2"])

        registry.register(tool1)
        registry.register(tool2)

        commands = registry.get_commands_list()
        assert len(commands) == 3
        assert "/test1" in commands
        assert "/t1" in commands
        assert "/test2" in commands

    def test_get_stats(self):
        """Test obtener estadísticas."""
        registry = ToolRegistry()
        tool1 = MockTool("db1", category=ToolCategory.DATABASE, commands=["/db1", "/d1"])
        tool2 = MockTool("util1", category=ToolCategory.UTILITY)

        registry.register(tool1)
        registry.register(tool2)

        stats = registry.get_stats()

        assert stats["total_tools"] == 2
        assert stats["total_commands"] == 3
        assert "database" in stats["categories"]
        assert "utility" in stats["categories"]
        assert stats["categories"]["database"] == 1
        assert stats["categories"]["utility"] == 1

    def test_clear_registry(self):
        """Test limpiar registry."""
        registry = ToolRegistry()
        tool1 = MockTool("test1")
        tool2 = MockTool("test2")

        registry.register(tool1)
        registry.register(tool2)
        assert registry.get_tools_count() == 2

        registry.clear()
        assert registry.get_tools_count() == 0
        assert len(registry.get_all_tools()) == 0
        assert len(registry.get_commands_list()) == 0

    def test_registry_repr(self):
        """Test representación en string."""
        registry = ToolRegistry()
        tool = MockTool("test", commands=["/test", "/t"])

        registry.register(tool)

        repr_str = repr(registry)
        assert "ToolRegistry" in repr_str
        assert "tools=1" in repr_str
        assert "commands=2" in repr_str


class TestGetUserAvailableTools:
    """Tests para filtrado de tools por usuario."""

    @pytest.fixture(autouse=True)
    def setup_and_teardown(self):
        """Limpiar registry antes y después."""
        registry = ToolRegistry()
        registry.clear()
        yield
        registry.clear()

    class MockPermissionChecker:
        """Mock de PermissionChecker."""

        def __init__(self, user_permissions):
            self.user_permissions = user_permissions

        def has_permission(self, user_id, permission):
            return permission in self.user_permissions.get(user_id, [])

    def test_get_user_available_tools_no_auth(self):
        """Test obtener tools sin autenticación requerida."""
        registry = ToolRegistry()

        # Tool sin autenticación
        public_tool = MockTool("public")
        public_tool._metadata.requires_auth = False

        registry.register(public_tool)

        permission_checker = self.MockPermissionChecker({})
        available = registry.get_user_available_tools(999, permission_checker)

        assert len(available) == 1
        assert public_tool in available

    def test_get_user_available_tools_with_permissions(self):
        """Test obtener tools con permisos."""
        registry = ToolRegistry()

        tool1 = MockTool("tool1")  # requires /tool1
        tool2 = MockTool("tool2")  # requires /tool2

        registry.register(tool1)
        registry.register(tool2)

        # Usuario con solo permiso para tool1
        permission_checker = self.MockPermissionChecker({
            123: ["/tool1"]
        })

        available = registry.get_user_available_tools(123, permission_checker)

        assert len(available) == 1
        assert tool1 in available
        assert tool2 not in available

    def test_get_user_available_tools_no_permissions(self):
        """Test usuario sin permisos."""
        registry = ToolRegistry()

        tool = MockTool("tool")
        registry.register(tool)

        permission_checker = self.MockPermissionChecker({
            123: []
        })

        available = registry.get_user_available_tools(123, permission_checker)

        assert len(available) == 0
