"""
DatabaseRegistry — Gestión de múltiples conexiones SQL Server.

Instancia y cachea un DatabaseManager por alias de conexión.
Los alias y sus parámetros se leen desde .env vía Settings.get_db_connections().

Uso:
    registry = DatabaseRegistry.from_settings()
    db = registry.get("ventas")          # lazy — crea la conexión al primer uso
    db_core = registry.get()             # "core" es el default
    registry.close_all()                 # shutdown
"""

import logging
import threading
from typing import Optional

from src.config.settings import DbConnectionConfig, settings
from .connection import DatabaseManager

logger = logging.getLogger(__name__)


class DatabaseRegistry:
    """
    Registro de conexiones a bases de datos.

    Instancia DatabaseManagers de forma lazy: cada alias se conecta
    solo cuando se solicita por primera vez, no al iniciar el sistema.

    Thread-safe con threading.Lock por slot de alias.

    Example:
        >>> registry = DatabaseRegistry.from_settings()
        >>> db = registry.get("ventas")
        >>> rows = db.execute_query("SELECT TOP 5 * FROM Clientes")
        >>> registry.close_all()
    """

    def __init__(self, configs: dict[str, DbConnectionConfig]) -> None:
        self._configs = configs          # alias → DbConnectionConfig
        self._managers: dict[str, DatabaseManager] = {}
        self._lock = threading.Lock()

    @classmethod
    def from_settings(cls) -> "DatabaseRegistry":
        """
        Crea un DatabaseRegistry con las conexiones definidas en .env.

        Siempre incluye "core" (las vars DB_HOST/NAME/... actuales).
        Aliases adicionales se leen de DB_CONNECTIONS.
        """
        configs = settings.get_db_connections()
        logger.info(
            f"DatabaseRegistry: conexiones configuradas: {list(configs.keys())}"
        )
        return cls(configs)

    def get(self, alias: str = "core") -> DatabaseManager:
        """
        Retorna el DatabaseManager para el alias dado.

        Crea la instancia de forma lazy en el primer llamado.

        Args:
            alias: Nombre de la conexión (ej: "core", "ventas"). Default: "core".

        Raises:
            KeyError: Si el alias no está configurado en .env.
        """
        if alias not in self._configs:
            available = list(self._configs.keys())
            raise KeyError(
                f"Conexión '{alias}' no configurada. "
                f"Conexiones disponibles: {available}. "
                f"Agregar DB_{alias.upper()}_HOST/NAME/USER/PASSWORD en .env "
                f"e incluir '{alias}' en DB_CONNECTIONS."
            )

        with self._lock:
            if alias not in self._managers:
                config = self._configs[alias]
                logger.info(f"DatabaseRegistry: inicializando conexión '{alias}'")
                self._managers[alias] = DatabaseManager(config=config)

        return self._managers[alias]

    def get_aliases(self) -> list[str]:
        """Retorna la lista de alias configurados."""
        return list(self._configs.keys())

    def get_active_aliases(self) -> list[str]:
        """Retorna los alias que ya tienen una conexión activa (lazy init)."""
        with self._lock:
            return list(self._managers.keys())

    def is_configured(self, alias: str) -> bool:
        """Retorna True si el alias está configurado (puede no estar conectado aún)."""
        return alias in self._configs

    def close_all(self) -> None:
        """Cierra todas las conexiones activas. Llamar en shutdown del bot."""
        with self._lock:
            for alias, manager in self._managers.items():
                try:
                    manager.close()
                    logger.info(f"DatabaseRegistry: conexión '{alias}' cerrada")
                except Exception as e:
                    logger.warning(f"DatabaseRegistry: error cerrando '{alias}': {e}")
            self._managers.clear()
