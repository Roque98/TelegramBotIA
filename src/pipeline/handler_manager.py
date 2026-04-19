"""
handler_manager — Singleton para gestionar el ciclo de vida del MainHandler.

Responsabilidad única: garantizar que create_main_handler se llama
una sola vez y exponer el handler inicializado al resto del sistema.
"""

from __future__ import annotations

import logging
from typing import Any, Optional

from .handler import MainHandler

logger = logging.getLogger(__name__)


class HandlerManager:
    """Gestor singleton para el MainHandler."""

    _instance: Optional["HandlerManager"] = None
    _handler: Optional[MainHandler] = None

    def __new__(cls) -> "HandlerManager":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def initialize(self, db_manager: Any = None) -> MainHandler:
        if self._handler is None:
            from src.bootstrap.factory import create_main_handler
            self._handler, _, __ = create_main_handler(db_manager)
            logger.info("HandlerManager initialized")
        return self._handler

    @property
    def handler(self) -> Optional[MainHandler]:
        return self._handler

    def is_initialized(self) -> bool:
        return self._handler is not None

    @classmethod
    def reset(cls) -> None:
        cls._instance = None
        cls._handler = None


def get_handler_manager() -> HandlerManager:
    """Obtiene la instancia del HandlerManager."""
    return HandlerManager()
