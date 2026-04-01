"""
ObservabilityRepository - Persistencia de datos de observabilidad en SQL Server.

Guarda:
- TransactionLogs: una fila por request con tiempos de cada etapa del pipeline
- ApplicationLogs: logs WARNING/ERROR con correlation_id para diagnóstico
"""

import json
import logging
from typing import Any, Optional

logger = logging.getLogger(__name__)


class ObservabilityRepository:
    """Repositorio para persistir datos de observabilidad en SQL Server."""

    def __init__(self, db_manager) -> None:
        self.db_manager = db_manager

    async def save_transaction(
        self,
        correlation_id: str,
        user_id: Optional[str],
        username: Optional[str],
        query: Optional[str],
        channel: str,
        memory_ms: int,
        react_ms: int,
        save_ms: int,
        total_ms: int,
        success: bool,
        error_message: Optional[str] = None,
        tools_used: Optional[list[str]] = None,
        steps_count: int = 0,
    ) -> bool:
        """
        Guarda una traza de transacción en TransactionLogs.

        Llamar al final de cada request para registrar el flujo completo.
        """
        try:
            sql = """
                INSERT INTO abcmasplus..TransactionLogs (
                    correlationId, userId, username, query, channel,
                    memoryMs, reactMs, saveMs, totalMs, success,
                    errorMessage, toolsUsed, stepsCount
                ) VALUES (
                    :correlation_id, :user_id, :username, :query, :channel,
                    :memory_ms, :react_ms, :save_ms, :total_ms, :success,
                    :error_message, :tools_used, :steps_count
                )
            """
            await self.db_manager.execute_non_query_async(sql, {
                "correlation_id": correlation_id[:50] if correlation_id else None,
                "user_id": str(user_id) if user_id else None,
                "username": username,
                "query": (query or "")[:500],
                "channel": channel,
                "memory_ms": memory_ms,
                "react_ms": react_ms,
                "save_ms": save_ms,
                "total_ms": total_ms,
                "success": 1 if success else 0,
                "error_message": error_message[:1000] if error_message else None,
                "tools_used": json.dumps(tools_used) if tools_used else None,
                "steps_count": steps_count,
            })
            return True
        except Exception as e:
            logger.error(f"Error saving transaction trace: {e}")
            return False

    def save_log_sync(
        self,
        level: str,
        event: str,
        message: str,
        correlation_id: Optional[str] = None,
        user_id: Optional[str] = None,
        module: Optional[str] = None,
        duration_ms: Optional[int] = None,
        extra: Optional[dict[str, Any]] = None,
    ) -> bool:
        """
        Guarda un log en ApplicationLogs (versión síncrona).

        Usa execute_non_query (síncrono) para poder ser llamado desde threads
        de logging sin bloquear el event loop.
        Nunca lanza excepciones — si falla, simplemente no persiste.
        """
        try:
            sql = """
                INSERT INTO abcmasplus..ApplicationLogs (
                    correlationId, userId, level, event, message, module, durationMs, extra
                ) VALUES (
                    :correlation_id, :user_id, :level, :event, :message, :module, :duration_ms, :extra
                )
            """
            self.db_manager.execute_non_query(sql, {
                "correlation_id": correlation_id[:50] if correlation_id else None,
                "user_id": str(user_id) if user_id else None,
                "level": level,
                "event": event[:100],
                "message": message[:2000] if message else None,
                "module": module[:100] if module else None,
                "duration_ms": duration_ms,
                "extra": json.dumps(extra)[:2000] if extra else None,
            })
            return True
        except Exception:
            return False
