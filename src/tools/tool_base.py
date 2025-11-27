"""
Clases base para el sistema de orquestación de Tools.

Define las interfaces y modelos de datos fundamentales para todos los tools.
"""
from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ToolCategory(str, Enum):
    """Categorías de tools disponibles."""
    DATABASE = "database"
    SYSTEM = "system"
    USER_MANAGEMENT = "user_management"
    ANALYTICS = "analytics"
    UTILITY = "utility"
    INTEGRATION = "integration"


class ParameterType(str, Enum):
    """Tipos de parámetros soportados."""
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    LIST = "list"
    DICT = "dict"


@dataclass
class ToolParameter:
    """
    Define un parámetro de entrada para un tool.

    Attributes:
        name: Nombre del parámetro
        type: Tipo de dato esperado
        description: Descripción del parámetro
        required: Si es obligatorio
        default: Valor por defecto (opcional)
        validation_rules: Reglas de validación adicionales
    """
    name: str
    type: ParameterType
    description: str
    required: bool = True
    default: Optional[Any] = None
    validation_rules: Dict[str, Any] = field(default_factory=dict)

    def validate(self, value: Any) -> tuple[bool, Optional[str]]:
        """
        Validar un valor contra las reglas del parámetro.

        Args:
            value: Valor a validar

        Returns:
            tuple: (es_válido, mensaje_error)
        """
        # Validar tipo básico
        type_validators = {
            ParameterType.STRING: str,
            ParameterType.INTEGER: int,
            ParameterType.FLOAT: (int, float),
            ParameterType.BOOLEAN: bool,
            ParameterType.LIST: list,
            ParameterType.DICT: dict
        }

        expected_type = type_validators.get(self.type)
        if expected_type and not isinstance(value, expected_type):
            return False, f"Parámetro '{self.name}' debe ser de tipo {self.type.value}"

        # Validar reglas adicionales
        if "min_length" in self.validation_rules:
            if len(value) < self.validation_rules["min_length"]:
                return False, f"Parámetro '{self.name}' debe tener al menos {self.validation_rules['min_length']} caracteres"

        if "max_length" in self.validation_rules:
            if len(value) > self.validation_rules["max_length"]:
                return False, f"Parámetro '{self.name}' debe tener máximo {self.validation_rules['max_length']} caracteres"

        if "min_value" in self.validation_rules:
            if value < self.validation_rules["min_value"]:
                return False, f"Parámetro '{self.name}' debe ser mayor o igual a {self.validation_rules['min_value']}"

        if "max_value" in self.validation_rules:
            if value > self.validation_rules["max_value"]:
                return False, f"Parámetro '{self.name}' debe ser menor o igual a {self.validation_rules['max_value']}"

        return True, None


@dataclass
class ToolMetadata:
    """
    Metadatos descriptivos de un tool.

    Attributes:
        name: Nombre único del tool
        description: Descripción breve del tool
        commands: Lista de comandos que activan este tool
        category: Categoría del tool
        requires_auth: Si requiere autenticación
        required_permissions: Permisos necesarios para ejecutar
        version: Versión del tool
        author: Autor del tool
    """
    name: str
    description: str
    commands: List[str]
    category: ToolCategory
    requires_auth: bool = True
    required_permissions: List[str] = field(default_factory=list)
    version: str = "1.0.0"
    author: str = "System"

    def __post_init__(self):
        """Validar metadatos después de la inicialización."""
        if not self.name:
            raise ValueError("El nombre del tool no puede estar vacío")
        if not self.commands:
            raise ValueError("El tool debe tener al menos un comando")
        if self.requires_auth and not self.required_permissions:
            logger.warning(f"Tool '{self.name}' requiere auth pero no tiene permisos definidos")


@dataclass
class ToolResult:
    """
    Resultado de la ejecución de un tool.

    Attributes:
        success: Si la ejecución fue exitosa
        data: Datos resultantes de la ejecución
        error: Mensaje de error (si aplica)
        user_friendly_error: Mensaje de error amigable para el usuario
        metadata: Metadatos adicionales sobre la ejecución
        execution_time_ms: Tiempo de ejecución en milisegundos
        timestamp: Momento de la ejecución
    """
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    user_friendly_error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    execution_time_ms: Optional[float] = None
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Convertir el resultado a diccionario."""
        return {
            "success": self.success,
            "data": self.data,
            "error": self.error,
            "user_friendly_error": self.user_friendly_error,
            "metadata": self.metadata,
            "execution_time_ms": self.execution_time_ms,
            "timestamp": self.timestamp.isoformat()
        }

    @classmethod
    def success_result(cls, data: Any, metadata: Optional[Dict] = None) -> "ToolResult":
        """Crear un resultado exitoso."""
        return cls(
            success=True,
            data=data,
            metadata=metadata or {}
        )

    @classmethod
    def error_result(
        cls,
        error: str,
        user_friendly_error: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> "ToolResult":
        """Crear un resultado de error."""
        return cls(
            success=False,
            error=error,
            user_friendly_error=user_friendly_error or "Ocurrió un error al ejecutar el comando",
            metadata=metadata or {}
        )


class BaseTool(ABC):
    """
    Clase base abstracta para todos los tools.

    Todos los tools deben heredar de esta clase e implementar
    los métodos abstractos.
    """

    def __init__(self):
        """Inicializar el tool base."""
        self._metadata = self.get_metadata()
        self._parameters = self.get_parameters()
        self._validate_metadata()

    def _validate_metadata(self) -> None:
        """Validar que los metadatos del tool son correctos."""
        if not isinstance(self._metadata, ToolMetadata):
            raise TypeError("get_metadata() debe retornar un ToolMetadata")
        if not isinstance(self._parameters, list):
            raise TypeError("get_parameters() debe retornar una lista")
        for param in self._parameters:
            if not isinstance(param, ToolParameter):
                raise TypeError("Todos los parámetros deben ser ToolParameter")

    @abstractmethod
    def get_metadata(self) -> ToolMetadata:
        """
        Obtener los metadatos del tool.

        Returns:
            ToolMetadata: Metadatos del tool
        """
        pass

    @abstractmethod
    def get_parameters(self) -> List[ToolParameter]:
        """
        Obtener la lista de parámetros que acepta el tool.

        Returns:
            List[ToolParameter]: Lista de parámetros
        """
        pass

    @abstractmethod
    async def execute(
        self,
        user_id: int,
        params: Dict[str, Any],
        context: "ExecutionContext"
    ) -> ToolResult:
        """
        Ejecutar la lógica del tool.

        Args:
            user_id: ID del usuario que ejecuta el tool
            params: Parámetros de entrada
            context: Contexto de ejecución

        Returns:
            ToolResult: Resultado de la ejecución
        """
        pass

    def validate_parameters(self, params: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """
        Validar los parámetros de entrada.

        Args:
            params: Parámetros a validar

        Returns:
            tuple: (son_válidos, mensaje_error)
        """
        # Verificar parámetros requeridos
        for param_def in self._parameters:
            if param_def.required and param_def.name not in params:
                if param_def.default is not None:
                    params[param_def.name] = param_def.default
                else:
                    return False, f"Parámetro requerido '{param_def.name}' no proporcionado"

        # Validar cada parámetro
        for param_name, param_value in params.items():
            # Buscar definición del parámetro
            param_def = next(
                (p for p in self._parameters if p.name == param_name),
                None
            )

            if param_def:
                is_valid, error = param_def.validate(param_value)
                if not is_valid:
                    return False, error

        return True, None

    @property
    def name(self) -> str:
        """Obtener el nombre del tool."""
        return self._metadata.name

    @property
    def description(self) -> str:
        """Obtener la descripción del tool."""
        return self._metadata.description

    @property
    def commands(self) -> List[str]:
        """Obtener los comandos del tool."""
        return self._metadata.commands

    @property
    def category(self) -> ToolCategory:
        """Obtener la categoría del tool."""
        return self._metadata.category

    @property
    def requires_auth(self) -> bool:
        """Verificar si requiere autenticación."""
        return self._metadata.requires_auth

    @property
    def required_permissions(self) -> List[str]:
        """Obtener los permisos requeridos."""
        return self._metadata.required_permissions

    def __repr__(self) -> str:
        """Representación en string del tool."""
        return f"<{self.__class__.__name__}(name='{self.name}', commands={self.commands})>"
