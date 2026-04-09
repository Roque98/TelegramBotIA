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
        # OBS-36: campos de observabilidad multi-agente
        total_input_tokens: Optional[int] = None,
        total_output_tokens: Optional[int] = None,
        llm_iteraciones: Optional[int] = None,
        used_fallback: bool = False,
        classify_ms: Optional[int] = None,
        agent_confidence: Optional[float] = None,
        cost_usd: Optional[float] = None,
    ) -> bool:
        """
        Persiste una interacción completa en BotIAv2_InteractionLogs.

        Usa INSERT directo con subquery para idUsuario — nunca falla
        silenciosamente si el usuario no está registrado (idUsuario queda NULL).

        Args:
            agente_nombre: Nombre del agente que respondió (ARQ-35).
            total_input_tokens: Tokens de entrada agregados del request (OBS-36).
            total_output_tokens: Tokens de salida agregados del request (OBS-36).
            llm_iteraciones: Iteraciones del loop ReAct (OBS-36).
            used_fallback: Si se usó el agente generalista como fallback (OBS-36).
            classify_ms: Latencia del IntentClassifier en ms (OBS-36).
            agent_confidence: Confianza del clasificador 0.0–1.0 (OBS-36).
            cost_usd: Costo total del request en USD (OBS-36).
        """
        try:
            exitoso = 0 if error_message else 1
            sql = """
                INSERT INTO abcmasplus..BotIAv2_InteractionLogs (
                    correlationId, idUsuario, telegramChatId, telegramUsername,
                    comando, query, respuesta, mensajeError,
                    toolsUsadas, stepsTomados,
                    memoryMs, reactMs, saveMs, duracionMs, channel, exitoso,
                    agenteNombre,
                    totalInputTokens, totalOutputTokens, llmIteraciones,
                    usedFallback, classifyMs, agentConfidence, costUSD
                )
                VALUES (
                    :correlation_id,
                    (SELECT TOP 1 idUsuario FROM abcmasplus..BotIAv2_UsuariosTelegram
                     WHERE telegramChatId = :chat_id AND activo = 1),
                    :chat_id_int,
                    :username,
                    '/ia',
                    :query,
                    :respuesta,
                    :error_message,
                    :tools_used,
                    :steps_count,
                    :memory_ms, :react_ms, :save_ms, :total_ms,
                    :channel,
                    :exitoso,
                    :agente_nombre,
                    :total_input_tokens, :total_output_tokens, :llm_iteraciones,
                    :used_fallback, :classify_ms, :agent_confidence, :cost_usd
                )
            """
            chat_id_int = int(user_id) if user_id and str(user_id).lstrip("-").isdigit() else None
            await self.db_manager.execute_non_query_async(sql, {
                "correlation_id": correlation_id[:50] if correlation_id else None,
                "chat_id": str(user_id) if user_id else None,
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
                "exitoso": exitoso,
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
        """
        Persiste la decisión de ruteo en BotIAv2_AgentRouting (OBS-36).

        Args:
            correlation_id: ID de correlación del request.
            query: Texto de la consulta (truncado a 1000 chars).
            agente_seleccionado: Nombre del agente elegido.
            classify_ms: Latencia del clasificador en ms.
            confidence: Confianza del clasificador 0.0–1.0.
            alternatives: Lista de agentes alternativos detectados en la respuesta.
            used_fallback: True si se cayó al generalista por no encontrar el agente.
        """
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
        """
        Persiste los pasos del loop ReAct en BotIAv2_InteractionSteps.

        Cada paso es un dict con: stepNum, tipo, nombre, entrada, salida,
        tokensIn, tokensOut, duracionMs.
        """
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
        Guarda un log en ApplicationLogs (versión síncrona).

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
