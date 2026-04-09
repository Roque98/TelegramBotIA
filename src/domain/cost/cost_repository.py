"""
Cost Repository - Persistencia de costos de sesión en BD.
"""

import logging
from typing import Any, Optional

from .cost_entity import CostSession

logger = logging.getLogger(__name__)


class CostRepository:
    """Repositorio para persistir y consultar costos de sesiones LLM."""

    def __init__(self, db_manager: Any) -> None:
        self.db_manager = db_manager

    async def save_session(self, session: CostSession) -> None:
        """Persiste el costo de una sesión en CostSesiones."""
        query = """
            INSERT INTO abcmasplus..BotIAv2_CostSesiones (
                telegramChatId, modelo, inputTokens, outputTokens,
                cacheReadTokens, llamadasLLM, costoUSD, pasos, correlationId, fechaSesion
            ) VALUES (
                :chat_id, :modelo, :input_tokens, :output_tokens,
                :cache_read_tokens, :llm_calls, :cost_usd, :pasos, :correlation_id, GETDATE()
            )
        """
        await self.db_manager.execute_non_query_async(query, {
            "chat_id": str(session.user_id),
            "modelo": session.model,
            "input_tokens": session.input_tokens,
            "output_tokens": session.output_tokens,
            "cache_read_tokens": session.cache_read_tokens,
            "llm_calls": session.llm_calls,
            "cost_usd": session.cost_usd,
            "pasos": session.steps,
            "correlation_id": session.correlation_id[:50] if session.correlation_id else None,
        })

    async def get_daily_costs(self, date_str: str) -> list[dict]:
        """Retorna el gasto del día agrupado por usuario. Usado por /costo."""
        query = """
            SELECT
                cs.telegramChatId                                       AS chat_id,
                COALESCE(u.Nombre, ut.telegramUsername, 'Desconocido') AS nombre,
                COUNT(*)                                                AS sesiones,
                SUM(cs.llamadasLLM)                                    AS llamadas,
                SUM(cs.inputTokens)                                    AS input_tokens,
                SUM(cs.outputTokens)                                   AS output_tokens,
                SUM(cs.costoUSD)                                       AS costo_usd
            FROM abcmasplus..BotIAv2_CostSesiones cs
            LEFT JOIN abcmasplus..BotIAv2_UsuariosTelegram ut ON cs.telegramChatId = ut.telegramChatId
            LEFT JOIN abcmasplus..Usuarios u ON ut.idUsuario = u.idUsuario
            WHERE cs.fechaSesion >= CAST(:fecha AS DATE)
            GROUP BY cs.telegramChatId, u.Nombre, ut.telegramUsername
            ORDER BY costo_usd DESC
        """
        return await self.db_manager.execute_query_async(query, {"fecha": date_str})
