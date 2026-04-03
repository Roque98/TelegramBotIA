"""
Constantes del módulo de autenticación.

Reemplaza magic strings dispersos en middleware, handlers y servicios.
"""

from enum import Enum


class AccountState(str, Enum):
    ACTIVE = "ACTIVO"
    BLOCKED = "BLOQUEADO"
    PENDING = "PENDIENTE"


class OperationResult(str, Enum):
    SUCCESS = "EXITOSO"
    ERROR = "ERROR"
    DENIED = "DENEGADO"


class EntityType(str, Enum):
    USUARIO = "usuario"
    AUTENTICADO = "autenticado"
    GERENCIA = "gerencia"
    DIRECCION = "direccion"


class ResolutionType(str, Enum):
    DEFINITIVE = "definitivo"
    PERMISSIVE = "permisivo"


class ResourceType(str, Enum):
    TOOL = "tool"
    CMD = "cmd"
