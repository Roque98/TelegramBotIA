"""
Memory Repository - Persistencia de memoria para el ReAct Agent.
"""

import json
import logging
from datetime import UTC, datetime
from typing import Any, Optional

from src.memory.memory_entity import DatabaseManager, UserProfile

logger = logging.getLogger(__name__)


class MemoryRepository:
    """Repository para acceso a memoria de usuarios."""

    def __init__(self, db_manager: Optional[DatabaseManager] = None):
        self.db_manager = db_manager
        self._profiles_cache: dict[str, UserProfile] = {}
        logger.info("MemoryRepository inicializado")

    async def get_profile(self, user_id: str) -> Optional[UserProfile]:
        if user_id in self._profiles_cache:
            return self._profiles_cache[user_id]

        if not self.db_manager:
            return None

        try:
            query = """
                SELECT
                    u.idUsuario AS Id_Usuario,
                    u.Nombre AS Nombre,
                    ump.resumenContextoLaboral AS resumen_contexto_laboral,
                    ump.resumenTemasRecientes AS resumen_temas_recientes,
                    ump.resumenHistorialBreve AS resumen_historial_breve,
                    ump.numInteracciones AS num_interacciones,
                    ump.ultimaActualizacion AS ultima_actualizacion,
                    ump.preferencias AS preferencias
                FROM abcmasplus..UsuariosTelegram ut
                INNER JOIN abcmasplus..Usuarios u ON ut.idUsuario = u.idUsuario
                LEFT JOIN abcmasplus..UserMemoryProfiles ump ON u.idUsuario = ump.idUsuario
                WHERE ut.telegramChatId = :user_id AND ut.activo = 1
            """
            results = self.db_manager.execute_query(query, {"user_id": str(user_id)})

            if not results:
                return None

            row = results[0]

            summaries = []
            for key in ("resumen_contexto_laboral", "resumen_temas_recientes", "resumen_historial_breve"):
                if row.get(key):
                    summaries.append(row[key])

            preferences = {}
            if row.get("preferencias"):
                try:
                    preferences = json.loads(row["preferencias"])
                except json.JSONDecodeError:
                    preferences = {}

            display_name = preferences.get("alias") or row.get("Nombre", "Usuario")

            profile = UserProfile(
                user_id=user_id,
                display_name=display_name,
                long_term_summary="\n\n".join(summaries) if summaries else None,
                interaction_count=row.get("num_interacciones", 0),
                last_updated=row.get("ultima_actualizacion"),
                preferences=preferences,
            )

            self._profiles_cache[user_id] = profile
            return profile

        except Exception as e:
            logger.error(f"Error getting profile for {user_id}: {e}")
            return None

    async def save_profile(self, profile: UserProfile) -> bool:
        if not self.db_manager:
            self._profiles_cache[profile.user_id] = profile
            return True

        try:
            query = """
                MERGE INTO abcmasplus..UserMemoryProfiles AS target
                USING (SELECT :user_id AS id_usuario) AS source
                ON target.id_usuario = source.id_usuario
                WHEN MATCHED THEN
                    UPDATE SET
                        resumen_historial_breve = :summary,
                        num_interacciones = :count,
                        ultima_actualizacion = GETDATE()
                WHEN NOT MATCHED THEN
                    INSERT (id_usuario, resumen_historial_breve, num_interacciones, fecha_creacion, ultima_actualizacion)
                    VALUES (:user_id, :summary, :count, GETDATE(), GETDATE());
            """
            self.db_manager.execute_non_query(query, {
                "user_id": int(profile.user_id),
                "summary": profile.long_term_summary,
                "count": profile.interaction_count,
            })
            self._profiles_cache[profile.user_id] = profile
            return True

        except Exception as e:
            logger.error(f"Error saving profile for {profile.user_id}: {e}")
            return False

    async def get_recent_messages(self, user_id: str, limit: int = 10) -> list[dict[str, Any]]:
        if not self.db_manager:
            return []

        try:
            query = """
                SELECT TOP (:limit)
                    lo.idOperacion AS Comando,
                    lo.parametros AS Parametros,
                    lo.resultado AS Resultado,
                    lo.fechaEjecucion AS Fecha_Hora
                FROM abcmasplus..LogOperaciones lo
                INNER JOIN abcmasplus..UsuariosTelegram ut ON lo.idUsuario = ut.idUsuario
                WHERE ut.telegramChatId = :user_id AND ut.activo = 1
                ORDER BY lo.fechaEjecucion DESC
            """
            results = self.db_manager.execute_query(query, {"user_id": str(user_id), "limit": limit})

            messages = []
            for row in reversed(results):
                params = row.get("Parametros", {})
                if isinstance(params, str):
                    try:
                        params = json.loads(params)
                    except json.JSONDecodeError:
                        params = {"query": params}

                user_query = params.get("query", "")
                if user_query:
                    messages.append({
                        "role": "user",
                        "content": user_query,
                        "timestamp": row.get("Fecha_Hora", datetime.now(UTC)).isoformat(),
                    })

                resultado = row.get("Resultado", "")
                if resultado and resultado != "EXITOSO":
                    messages.append({
                        "role": "assistant",
                        "content": resultado,
                        "timestamp": row.get("Fecha_Hora", datetime.now(UTC)).isoformat(),
                    })

            return messages

        except Exception as e:
            logger.error(f"Error getting messages for {user_id}: {e}")
            return []

    async def save_interaction(self, user_id: str, query: str, response: str, metadata: Optional[dict[str, Any]] = None) -> bool:
        if not self.db_manager:
            return True

        try:
            params_json = json.dumps({"query": query, **(metadata or {})})
            duration_ms = (metadata or {}).get("execution_time_ms", 0)

            query_sql = """
                INSERT INTO abcmasplus..LogOperaciones (
                    idUsuario, idOperacion, telegramChatId,
                    parametros, resultado, duracionMs, fechaEjecucion
                )
                SELECT
                    ut.idUsuario,
                    (SELECT idOperacion FROM abcmasplus..Operaciones WHERE comando = :operation AND activo = 1),
                    :chat_id, :params, :result, :duration_ms, GETDATE()
                FROM abcmasplus..UsuariosTelegram ut
                WHERE ut.telegramChatId = :chat_id_lookup AND ut.activo = 1
            """
            self.db_manager.execute_non_query(query_sql, {
                "operation": "/ia",
                "chat_id": str(user_id),
                "params": params_json,
                "result": response[:4000],
                "duration_ms": int(duration_ms),
                "chat_id_lookup": str(user_id),
            })
            return True

        except Exception as e:
            logger.error(f"Error saving interaction for {user_id}: {e}")
            return False

    async def get_interaction_count(self, user_id: str) -> int:
        profile = await self.get_profile(user_id)
        return profile.interaction_count if profile else 0

    async def increment_interaction_count(self, user_id: str) -> int:
        profile = await self.get_profile(user_id)
        if not profile:
            profile = UserProfile(user_id=user_id, interaction_count=1)
        else:
            profile.interaction_count += 1
        await self.save_profile(profile)
        return profile.interaction_count

    def invalidate_cache(self, user_id: str) -> None:
        self._profiles_cache.pop(user_id, None)

    def clear_cache(self) -> None:
        self._profiles_cache.clear()
