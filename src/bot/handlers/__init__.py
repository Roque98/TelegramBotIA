"""Handlers para el bot de Telegram."""
from .command_handlers import register_command_handlers
from .query_handlers import register_query_handlers
from .registration_handlers import register_registration_handlers
from .tools_handlers import register_tools_handlers

__all__ = [
    'register_command_handlers',
    'register_query_handlers',
    'register_registration_handlers',
    'register_tools_handlers'
]
