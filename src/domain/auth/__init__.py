"""
Sistema de autenticación y autorización para el bot de Telegram.
"""

from .user_entity import TelegramUser, PermissionResult, Operation, RegistrationError
from .user_repository import UserRepository
from .user_service import UserService
from .constants import AccountState, OperationResult, EntityType, ResolutionType, ResourceType
from .permission_repository import PermissionRepository
from .permission_service import PermissionService

__all__ = [
    'TelegramUser',
    'PermissionResult',
    'Operation',
    'RegistrationError',
    'UserRepository',
    'UserService',
    'AccountState',
    'OperationResult',
    'EntityType',
    'ResolutionType',
    'ResourceType',
    'PermissionRepository',
    'PermissionService',
]
