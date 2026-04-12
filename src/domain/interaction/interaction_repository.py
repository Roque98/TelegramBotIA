"""
InteractionRepository - Persistencia de interacciones del bot en SQL Server.

Guarda:
- BotIAv2_InteractionLogs: una fila por request con tiempos de cada etapa del pipeline
- BotIAv2_AgentRouting: decisiones de ruteo del IntentClassifier
- BotIAv2_InteractionSteps: pasos del loop ReAct
- BotIAv2_ApplicationLogs: logs WARNING/ERROR con correlation_id para diagnóstico
"""

import json
import logging
from typing import Any, Optional

logger = logging.getLogger(__name__)


class InteractionRepository:
    """Repositorio para persistir interacciones del bot en SQL Server."""

    def __init__(self, db_manager) -> None:
        self.db_manager = db_manager

    async def save_interaction(
        self,
        correlation_id: str,
        user_id: Optional[str],
        username: Optional[str],
        query: Optional[str],
        respuesta: Optional[str],
        channel: str,
        memory_ms: int,
        react_ms: int,
        save_ms: int,
        total_ms: int,
        error_message: Optional[str] = None,
        tools_used: Optional[list[str]] = None,
        steps_count: int = 0,
        agente_nombre: Optional[str] = None,
        total_input_tokens: Optional[int] = None,
        total_output_tokens: Optional[int] = None,
        llm_iteraciones: Optional[int] = None,
        used_fallback: bool = False,
        classify_ms: Optional[int] = None,
        agent_confidence: Optional[float] = None,
        cost_usd: Optional[float] = None,
    ) -> bool:
        """Persiste una interacción completa en BotIAv2_InteractionLogs."""
        try:
            chat_id_int = int(user_id) if user_id and str(user_id).lstrip("-").isdigit() else None
            sql = """
                EXEC abcmasplus..BotIAv2_sp_GuardarInteraccion
                    @correlationId     = :correlation_id,
                    @telegramChatId    = :chat_id_int,
                    @telegramUsername  = :username,
                    @query             = :query,
                    @respuesta         = :respuesta,
                    @mensajeError      = :error_message,
                    @toolsUsadas       = :tools_used,
                    @stepsTomados      = :steps_count,
                    @memoryMs          = :memory_ms,
                    @reactMs           = :react_ms,
                    @saveMs            = :save_ms,
                    @duracionMs        = :total_ms,
                    @channel           = :channel,
                    @agenteNombre      = :agente_nombre,
                    @totalInputTokens  = :total_input_tokens,
                    @totalOutputTokens = :total_output_tokens,
                    @llmIteraciones    = :llm_iteraciones,
                    @usedFallback      = :used_fallback,
                    @classifyMs        = :classify_ms,
                    @agentConfidence   = :agent_confidence,
                    @costUSD           = :cost_usd
            """
            await self.db_manager.execute_non_query_async(sql, {
                "correlation_id": correlation_id[:50] if correlation_id else None,
                "chat_id_int": chat_id_int,
                "username": username,
                "query": (query or "")[:500],
                "respuesta": respuesta,
                "error_message": error_message[:2000] if error_message else None,
                "tools_used": json.dumps(tools_used) if tools_used else None,
                "steps_count": steps_count,
                "memory_ms": memory_ms,
                "react_ms": react_ms,
                "save_ms": save_ms,
                "total_ms": total_ms,
                "channel": channel,
                "agente_nombre": agente_nombre[:100] if agente_nombre else None,
                "total_input_tokens": total_input_tokens,
                "total_output_tokens": total_output_tokens,
                "llm_iteraciones": llm_iteraciones,
                "used_fallback": 1 if used_fallback else 0,
                "classify_ms": classify_ms,
                "agent_confidence": agent_confidence,
                "cost_usd": cost_usd,
            })
            return True
        except Exception as e:
            logger.error(f"Error saving interaction: {e}")
            return False

    async def save_agent_routing(
        self,
        correlation_id: str,
        query: Optional[str],
        agente_seleccionado: str,
        classify_ms: int,
        confidence: Optional[float] = None,
        alternatives: Optional[list[str]] = None,
        used_fallback: bool = False,
    ) -> bool:
        """Persiste la decisión de ruteo en BotIAv2_AgentRouting."""
        try:
            alternatives_json = json.dumps(alternatives) if alternatives else None
            sql = """
                INSERT INTO abcmasplus..BotIAv2_AgentRouting (
                    correlationId, query, agenteSeleccionado,
                    confianza, alternativas, classifyMs, usedFallback
                ) VALUES (
                    :correlation_id, :query, :agente_seleccionado,
                    :confianza, :alternativas, :classify_ms, :used_fallback
                )
            """
            await self.db_manager.execute_non_query_async(sql, {
                "correlation_id": correlation_id[:50] if correlation_id else None,
                "query": (query or "")[:1000],
                "agente_seleccionado": agente_seleccionado[:100],
                "confianza": confidence,
                "alternativas": alternatives_json[:500] if alternatives_json else None,
                "classify_ms": classify_ms,
                "used_fallback": 1 if used_fallback else 0,
            })
            return True
        except Exception as e:
            logger.error(f"Error saving agent routing: {e}")
            return False

    async def save_steps(
        self,
        correlation_id: str,
        steps: list[dict[str, Any]],
    ) -> bool:
        """Persiste los pasos del loop ReAct en BotIAv2_InteractionSteps."""
        if not steps:
            return True
        try:
            sql = """
                INSERT INTO abcmasplus..BotIAv2_InteractionSteps (
                    correlationId, stepNum, tipo, nombre,
                    entrada, salida, tokensIn, tokensOut, costoUSD, duracionMs, fechaInicio
                ) VALUES (
                    :correlation_id, :step_num, :tipo, :nombre,
                    :entrada, :salida, :tokens_in, :tokens_out, :costo_usd, :duracion_ms, :fecha_inicio
                )
            """
            for step in steps:
                await self.db_manager.execute_non_query_async(sql, {
                    "correlation_id": correlation_id[:50] if correlation_id else None,
                    "step_num": step["stepNum"],
                    "tipo": step["tipo"],
                    "nombre": step.get("nombre"),
                    "entrada": step.get("entrada"),
                    "salida": step.get("salida"),
                    "tokens_in": step.get("tokensIn"),
                    "tokens_out": step.get("tokensOut"),
                    "costo_usd": step.get("costoUSD"),
                    "duracion_ms": step.get("duracionMs", 0),
                    "fecha_inicio": step.get("fechaInicio"),
                })
            return True
        except Exception as e:
            logger.error(f"Error saving steps: {e}")
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
        Guarda un log en BotIAv2_ApplicationLogs (versión síncrona).

        Usa execute_non_query (síncrono) para poder ser llamado desde threads
        de logging sin bloquear el event loop.
        Nunca lanza excepciones — si falla, simplemente no persiste.
        """
        try:
            sql = """
                INSERT INTO abcmasplus..BotIAv2_ApplicationLogs (
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
