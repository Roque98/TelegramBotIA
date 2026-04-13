"""Re-export de compatibilidad hacia src.infra.observability.logging_config."""
from src.infra.observability.logging_config import (
    SqlLogHandler,
    configure_logging,
    get_sql_handler,
)

__all__ = ["SqlLogHandler", "configure_logging", "get_sql_handler"]
