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
        query = "EXEC abcmasplus..BotIAv2_sp_GetCostosDiarios @fecha = :fecha"
        return await self.db_manager.execute_query_async(query, {"fecha": date_str})
