"""
Memory Repository - Persistencia de memoria para el ReAct Agent.
"""

import json
import logging
import time
from datetime import UTC, datetime
from typing import Any, Optional

from src.domain.memory.memory_entity import DatabaseManager, UserProfile

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
            _start = time.perf_counter()
            query = "EXEC abcmasplus..BotIAv2_sp_GetPerfilMemoria @telegramChatId = :user_id"
            results = await self.db_manager.execute_query_async(query, {"user_id": str(user_id)})
            logger.debug(f"get_profile query for {user_id}: {(time.perf_counter() - _start) * 1000:.1f}ms")

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

            gerencia_csv = row.get("gerencia_ids_csv")
            gerencia_ids = [int(x) for x in gerencia_csv.split(",") if x] if gerencia_csv else []
            direccion_ids: list[int] = []  # DireccionesUsuarios no existe en BD

            role_name = row.get("role_name")

            profile = UserProfile(
                user_id=user_id,
                display_name=display_name,
                long_term_summary="\n\n".join(summaries) if summaries else None,
                interaction_count=row.get("num_interacciones") or 0,
                last_updated=row.get("ultima_actualizacion"),
                preferences=preferences,
                db_user_id=row.get("Id_Usuario"),
                role_id=row.get("role_id"),
                role_name=role_name,
                roles=[role_name] if role_name else [],
                gerencia_ids=gerencia_ids,
                direccion_ids=direccion_ids,
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
                MERGE INTO abcmasplus..BotIAv2_UserMemoryProfiles AS target
                USING (SELECT :user_id AS idUsuario) AS source
                ON target.idUsuario = source.idUsuario
                WHEN MATCHED THEN
                    UPDATE SET
                        resumenHistorialBreve = :summary,
                        numInteracciones = :count,
                        ultimaActualizacion = GETDATE()
                WHEN NOT MATCHED THEN
                    INSERT (idUsuario, resumenHistorialBreve, numInteracciones, fechaCreacion, ultimaActualizacion)
                    VALUES (:user_id, :summary, :count, GETDATE(), GETDATE());
            """
            await self.db_manager.execute_non_query_async(query, {
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
                EXEC abcmasplus..BotIAv2_sp_GetMensajesRecientes
                    @telegramChatId = :user_id,
                    @limit          = :limit
            """
            results = await self.db_manager.execute_query_async(query, {"user_id": str(user_id), "limit": limit})

            messages = []
            for row in reversed(results):
                user_query = row.get("user_query", "")
                if user_query:
                    messages.append({
                        "role": "user",
                        "content": user_query,
                        "timestamp": row.get("fecha", datetime.now(UTC)).isoformat(),
                    })
                respuesta = row.get("respuesta", "")
                if respuesta:
                    messages.append({
                        "role": "assistant",
                        "content": respuesta,
                        "timestamp": row.get("fecha", datetime.now(UTC)).isoformat(),
                    })

            return messages

        except Exception as e:
            logger.error(f"Error getting messages for {user_id}: {e}")
            return []

    # save_interaction eliminado — las interacciones ahora las persiste
    # ObservabilityRepository.save_interaction() en BotIAv2_InteractionLogs (OBS-31)

    async def get_user_stats(self, user_id: str) -> dict:
        """Retorna estadísticas de uso del usuario desde InteractionLogs."""
        if not self.db_manager:
            return {}

        try:
            query = "EXEC abcmasplus..BotIAv2_sp_GetEstadisticasUsuario @telegramChatId = :user_id"
            results = await self.db_manager.execute_query_async(query, {"user_id": str(user_id)})
            return results[0] if results else {}
        except Exception as e:
            logger.error(f"Error getting stats for {user_id}: {e}")
            return {}

    async def get_interaction_count(self, user_id: str) -> int:
        profile = await self.get_profile(user_id)
        return profile.interaction_count if profile else 0

    async def increment_interaction_count(self, user_id: str) -> int:
        profile = await self.get_profile(user_id)
        if not profile:
            profile = UserProfile(user_id=user_id, interaction_count=1)
        else:
            profile.interaction_count = (profile.interaction_count or 0) + 1
        await self.save_profile(profile)
        return profile.interaction_count

    def invalidate_cache(self, user_id: str) -> None:
        self._profiles_cache.pop(user_id, None)

    def clear_cache(self) -> None:
        self._profiles_cache.clear()
