"""
Logging Config - Configuración de logging estructurado.

Configura:
- Formato con correlation_id inyectado por TracingFilter
- SqlLogHandler: persiste WARNING/ERROR en ApplicationLogs (en background thread)

Uso:
    # En main.py, llamar una sola vez al inicio:
    sql_handler = configure_logging()

    # Cuando la BD esté disponible (en factory.py):
    from src.infra.observability.sql_repository import ObservabilityRepository
    sql_handler.set_repository(ObservabilityRepository(db_manager))
"""

import logging
import threading
from typing import Optional

from src.infra.observability.tracing import TracingFilter


class SqlLogHandler(logging.Handler):
    """
    Handler de logging que persiste registros WARNING/ERROR en ApplicationLogs.

    Escribe en un thread daemon separado para no bloquear el event loop.
    El repositorio se inyecta después de la inicialización de la BD.
    """

    def __init__(self) -> None:
        super().__init__(level=logging.WARNING)
        self._repository = None

    def set_repository(self, repository) -> None:
        """Inyecta el repositorio cuando la BD está disponible."""
        self._repository = repository

    def emit(self, record: logging.LogRecord) -> None:
        if self._repository is None:
            return
        try:
            level = record.levelname
            event = f"{record.module}.{record.funcName}"
            message = self.format(record)
            module = record.name

            correlation_id = getattr(record, "correlation_id", None)
            if correlation_id == "-":
                correlation_id = None

            user_id = getattr(record, "user_id", None)
            if user_id == "-":
                user_id = None

            repo = self._repository
            t = threading.Thread(
                target=repo.save_log_sync,
                kwargs={
                    "level": level,
                    "event": event,
                    "message": message,
                    "correlation_id": correlation_id,
                    "user_id": user_id,
                    "module": module,
                },
                daemon=True,
            )
            t.start()
        except Exception:
            self.handleError(record)


_sql_handler: Optional[SqlLogHandler] = None


def configure_logging(log_level: str = "INFO") -> SqlLogHandler:
    """
    Configura el sistema de logging del proyecto.

    Debe llamarse una sola vez al inicio (en main.py), antes de iniciar el bot.
    Reemplaza la llamada a basicConfig para agregar el formato con correlation_id.

    Args:
        log_level: Nivel de log raíz (default INFO)

    Returns:
        SqlLogHandler — para inyectar el repositorio cuando la BD esté lista
    """
    global _sql_handler

    # Formato con correlation_id (TracingFilter lo inyecta en cada record)
    fmt = "%(asctime)s [%(correlation_id)-8s] %(name)-35s %(levelname)-8s %(message)s"
    tracing_filter = TracingFilter()

    # Handler de consola
    console = logging.StreamHandler()
    console.setFormatter(logging.Formatter(fmt, datefmt="%H:%M:%S"))
    console.addFilter(tracing_filter)

    # SQL handler (solo WARNING+, mensaje limpio sin timestamp duplicado)
    _sql_handler = SqlLogHandler()
    _sql_handler.setFormatter(logging.Formatter("%(message)s"))
    _sql_handler.addFilter(tracing_filter)

    # Configurar logger raíz
    root = logging.getLogger()
    root.setLevel(getattr(logging, log_level.upper(), logging.INFO))
    root.addHandler(console)
    root.addHandler(_sql_handler)

    # Silenciar librerías externas ruidosas
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("telegram").setLevel(logging.WARNING)

    return _sql_handler


def get_sql_handler() -> Optional[SqlLogHandler]:
    """Retorna el SqlLogHandler global (None si configure_logging no fue llamado)."""
    return _sql_handler
