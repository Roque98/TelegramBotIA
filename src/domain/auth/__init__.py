"""
Sistema de autenticación y autorización para el bot de Telegram.
"""

from .user_entity import TelegramUser, PermissionResult, Operation, RegistrationError
from .user_repository import UserRepository
from .user_service import UserService

__all__ = [
    'TelegramUser',
    'PermissionResult',
    'Operation',
    'RegistrationError',
    'UserRepository',
    'UserService',
]
