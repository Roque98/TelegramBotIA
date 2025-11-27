"""Keyboards para el bot de Telegram."""
from .main_keyboard import get_main_keyboard
from .inline_keyboards import get_pagination_keyboard

__all__ = ['get_main_keyboard', 'get_pagination_keyboard']
