"""
TicketAnalysisCacheRepository — Caché de análisis LLM de tickets históricos.

Evita llamadas redundantes al LLM cuando los datos no han cambiado.
Invalidación: si cambia total_tickets o la accionCorrectiva del último ticket.
"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)


class TicketAnalysisCacheRepository:
    """Repositorio de caché de análisis de tickets en BotIAv2_TicketAnalysisCache."""

    def __init__(self, db_manager) -> None:
        self._db = db_manager

    async def lookup(self, ip: str, sensor: str, total_tickets: int, ultima_accion: str) -> Optional[str]:
        """Retorna el análisis cacheado si la clave coincide, None si hay cache miss."""
        try:
            rows = await self._db.execute_query_async(
                """
                SELECT analisis FROM abcmasplus..BotIAv2_TicketAnalysisCache
                WHERE ip = :ip AND sensor = :sensor
                  AND total_tickets = :total AND ultima_accion = :ultima_accion
                """,
                {"ip": ip, "sensor": sensor, "total": total_tickets, "ultima_accion": ultima_accion[:500]},
            )
            return rows[0]["analisis"] if rows else None
        except Exception as e:
            logger.warning(f"TicketAnalysisCache lookup error: {e}")
            return None

    async def save(self, ip: str, sensor: str, total_tickets: int, ultima_accion: str, analisis: str) -> None:
        """Guarda o actualiza el análisis en caché para la clave dada."""
        try:
            await self._db.execute_non_query_async(
                """
                MERGE abcmasplus..BotIAv2_TicketAnalysisCache AS target
                USING (
                    SELECT :ip AS ip, :sensor AS sensor,
                           :total AS total_tickets, :ultima_accion AS ultima_accion
                ) AS src
                    ON  target.ip            = src.ip
                    AND target.sensor        = src.sensor
                    AND target.total_tickets = src.total_tickets
                    AND target.ultima_accion = src.ultima_accion
                WHEN MATCHED THEN
                    UPDATE SET analisis = :analisis, fechaCreacion = GETDATE()
                WHEN NOT MATCHED THEN
                    INSERT (ip, sensor, total_tickets, ultima_accion, analisis)
                    VALUES (:ip, :sensor, :total, :ultima_accion, :analisis);
                """,
                {"ip": ip, "sensor": sensor, "total": total_tickets, "ultima_accion": ultima_accion[:500], "analisis": analisis},
            )
        except Exception as e:
            logger.warning(f"TicketAnalysisCache save error: {e}")
