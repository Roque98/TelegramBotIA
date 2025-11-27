"""
Tests unitarios para las clases base del sistema de Tools.
"""
import pytest
from datetime import datetime
from src.tools.tool_base import (
    ToolCategory,
    ParameterType,
    ToolParameter,
    ToolMetadata,
    ToolResult,
    BaseTool
)


class TestToolParameter:
    """Tests para ToolParameter."""

    def test_create_parameter(self):
        """Test crear parámetro básico."""
        param = ToolParameter(
            name="query",
            type=ParameterType.STRING,
            description="Consulta del usuario",
            required=True
        )

        assert param.name == "query"
        assert param.type == ParameterType.STRING
        assert param.required is True

    def test_parameter_with_default(self):
        """Test parámetro con valor por defecto."""
        param = ToolParameter(
            name="limit",
            type=ParameterType.INTEGER,
            description="Límite de resultados",
            required=False,
            default=10
        )

        assert param.default == 10
        assert param.required is False

    def test_validate_string_type(self):
        """Test validar tipo string."""
        param = ToolParameter(
            name="name",
            type=ParameterType.STRING,
            description="Nombre"
        )

        is_valid, error = param.validate("test")
        assert is_valid is True
        assert error is None

    def test_validate_wrong_type(self):
        """Test validar tipo incorrecto."""
        param = ToolParameter(
            name="age",
            type=ParameterType.INTEGER,
            description="Edad"
        )

        is_valid, error = param.validate("not_an_int")
        assert is_valid is False
        assert "debe ser de tipo integer" in error

    def test_validate_min_length(self):
        """Test validar longitud mínima."""
        param = ToolParameter(
            name="password",
            type=ParameterType.STRING,
            description="Contraseña",
            validation_rules={"min_length": 8}
        )

        is_valid, error = param.validate("short")
        assert is_valid is False
        assert "al menos 8 caracteres" in error

        is_valid, error = param.validate("longpassword")
        assert is_valid is True

    def test_validate_max_length(self):
        """Test validar longitud máxima."""
        param = ToolParameter(
            name="username",
            type=ParameterType.STRING,
            description="Usuario",
            validation_rules={"max_length": 20}
        )

        is_valid, error = param.validate("a" * 30)
        assert is_valid is False
        assert "máximo 20 caracteres" in error

    def test_validate_min_value(self):
        """Test validar valor mínimo."""
        param = ToolParameter(
            name="age",
            type=ParameterType.INTEGER,
            description="Edad",
            validation_rules={"min_value": 18}
        )

        is_valid, error = param.validate(15)
        assert is_valid is False
        assert "mayor o igual a 18" in error

        is_valid, error = param.validate(25)
        assert is_valid is True


class TestToolMetadata:
    """Tests para ToolMetadata."""

    def test_create_metadata(self):
        """Test crear metadata básico."""
        metadata = ToolMetadata(
            name="query",
            description="Consultar base de datos",
            commands=["/ia", "/query"],
            category=ToolCategory.DATABASE,
            requires_auth=True,
            required_permissions=["/ia"]
        )

        assert metadata.name == "query"
        assert len(metadata.commands) == 2
        assert metadata.category == ToolCategory.DATABASE
        assert metadata.requires_auth is True

    def test_metadata_empty_name_raises_error(self):
        """Test que nombre vacío lanza error."""
        with pytest.raises(ValueError, match="nombre del tool no puede estar vacío"):
            ToolMetadata(
                name="",
                description="Test",
                commands=["/test"],
                category=ToolCategory.UTILITY
            )

    def test_metadata_no_commands_raises_error(self):
        """Test que sin comandos lanza error."""
        with pytest.raises(ValueError, match="debe tener al menos un comando"):
            ToolMetadata(
                name="test",
                description="Test",
                commands=[],
                category=ToolCategory.UTILITY
            )

    def test_metadata_default_version(self):
        """Test versión por defecto."""
        metadata = ToolMetadata(
            name="test",
            description="Test",
            commands=["/test"],
            category=ToolCategory.UTILITY
        )

        assert metadata.version == "1.0.0"
        assert metadata.author == "System"


class TestToolResult:
    """Tests para ToolResult."""

    def test_create_success_result(self):
        """Test crear resultado exitoso."""
        result = ToolResult.success_result(
            data={"message": "Success"},
            metadata={"execution_time": 100}
        )

        assert result.success is True
        assert result.data == {"message": "Success"}
        assert result.metadata["execution_time"] == 100
        assert result.error is None

    def test_create_error_result(self):
        """Test crear resultado de error."""
        result = ToolResult.error_result(
            error="Database connection failed",
            user_friendly_error="No se pudo conectar a la base de datos"
        )

        assert result.success is False
        assert result.error == "Database connection failed"
        assert result.user_friendly_error == "No se pudo conectar a la base de datos"
        assert result.data is None

    def test_result_to_dict(self):
        """Test convertir resultado a diccionario."""
        result = ToolResult.success_result(data="test")
        result_dict = result.to_dict()

        assert "success" in result_dict
        assert "data" in result_dict
        assert "timestamp" in result_dict
        assert result_dict["success"] is True

    def test_result_timestamp(self):
        """Test que timestamp se genera automáticamente."""
        result = ToolResult.success_result(data="test")
        assert isinstance(result.timestamp, datetime)


class TestBaseTool:
    """Tests para BaseTool."""

    class MockTool(BaseTool):
        """Tool de prueba."""

        def get_metadata(self):
            return ToolMetadata(
                name="mock",
                description="Tool de prueba",
                commands=["/mock"],
                category=ToolCategory.UTILITY,
                requires_auth=False
            )

        def get_parameters(self):
            return [
                ToolParameter(
                    name="message",
                    type=ParameterType.STRING,
                    description="Mensaje",
                    required=True
                )
            ]

        async def execute(self, user_id, params, context):
            return ToolResult.success_result(
                data=f"Mock: {params['message']}"
            )

    def test_create_tool(self):
        """Test crear tool básico."""
        tool = self.MockTool()

        assert tool.name == "mock"
        assert tool.description == "Tool de prueba"
        assert "/mock" in tool.commands
        assert tool.requires_auth is False

    def test_validate_parameters_success(self):
        """Test validar parámetros correctos."""
        tool = self.MockTool()
        params = {"message": "Hello"}

        is_valid, error = tool.validate_parameters(params)
        assert is_valid is True
        assert error is None

    def test_validate_parameters_missing_required(self):
        """Test validar parámetro requerido faltante."""
        tool = self.MockTool()
        params = {}

        is_valid, error = tool.validate_parameters(params)
        assert is_valid is False
        assert "requerido" in error
        assert "message" in error

    @pytest.mark.asyncio
    async def test_execute_tool(self):
        """Test ejecutar tool."""
        tool = self.MockTool()
        result = await tool.execute(
            user_id=123,
            params={"message": "test"},
            context=None
        )

        assert result.success is True
        assert "Mock: test" in result.data

    def test_tool_properties(self):
        """Test propiedades del tool."""
        tool = self.MockTool()

        assert tool.name == "mock"
        assert tool.description == "Tool de prueba"
        assert tool.commands == ["/mock"]
        assert tool.category == ToolCategory.UTILITY
        assert tool.requires_auth is False
        assert tool.required_permissions == []

    def test_tool_repr(self):
        """Test representación en string."""
        tool = self.MockTool()
        repr_str = repr(tool)

        assert "MockTool" in repr_str
        assert "mock" in repr_str
        assert "/mock" in repr_str
