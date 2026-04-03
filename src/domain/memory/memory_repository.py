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
            query = """
                SELECT
                    u.idUsuario AS Id_Usuario,
                    u.Nombre AS Nombre,
                    u.idRol AS role_id,
                    r.nombre AS role_name,
                    STUFF((
                        SELECT ',' + CAST(gu.idGerencia AS VARCHAR)
                        FROM abcmasplus..GerenciasUsuarios gu
                        WHERE gu.idUsuario = u.idUsuario
                        FOR XML PATH('')
                    ), 1, 1, '') AS gerencia_ids_csv,
                    STUFF((
                        SELECT ',' + CAST(du.idDireccion AS VARCHAR)
                        FROM abcmasplus..DireccionesUsuarios du
                        WHERE du.idUsuario = u.idUsuario
                        FOR XML PATH('')
                    ), 1, 1, '') AS direccion_ids_csv,
                    ump.resumenContextoLaboral AS resumen_contexto_laboral,
                    ump.resumenTemasRecientes AS resumen_temas_recientes,
                    ump.resumenHistorialBreve AS resumen_historial_breve,
                    ump.numInteracciones AS num_interacciones,
                    ump.ultimaActualizacion AS ultima_actualizacion,
                    ump.preferencias AS preferencias
                FROM abcmasplus..UsuariosTelegram ut
                INNER JOIN abcmasplus..Usuarios u ON ut.idUsuario = u.idUsuario
                LEFT JOIN abcmasplus..Roles r ON u.idRol = r.idRol
                LEFT JOIN abcmasplus..UserMemoryProfiles ump ON u.idUsuario = ump.idUsuario
                WHERE ut.telegramChatId = :user_id AND ut.activo = 1
            """
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
            direccion_csv = row.get("direccion_ids_csv")
            gerencia_ids = [int(x) for x in gerencia_csv.split(",") if x] if gerencia_csv else []
            direccion_ids = [int(x) for x in direccion_csv.split(",") if x] if direccion_csv else []

            role_name = row.get("role_name")

            profile = UserProfile(
                user_id=user_id,
                display_name=display_name,
                long_term_summary="\n\n".join(summaries) if summaries else None,
                interaction_count=row.get("num_interacciones", 0),
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
                MERGE INTO abcmasplus..UserMemoryProfiles AS target
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
                SELECT TOP (:limit)
                    lo.idOperacion AS Comando,
                    lo.parametros AS Parametros,
                    lo.resultado AS Resultado,
                    lo.fechaEjecucion AS Fecha_Hora
                FROM abcmasplus..LogOperaciones lo
                INNER JOIN abcmasplus..UsuariosTelegram ut ON lo.idUsuario = ut.idUsuario
                WHERE ut.telegramChatId = :user_id AND ut.activo = 1
                  AND lo.mensajeError IS NULL
                ORDER BY lo.fechaEjecucion DESC
            """
            results = await self.db_manager.execute_query_async(query, {"user_id": str(user_id), "limit": limit})

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

    async def save_interaction(
        self,
        user_id: str,
        query: str,
        response: str,
        error: Optional[str] = None,
        metadata: Optional[dict[str, Any]] = None,
    ) -> bool:
        if not self.db_manager:
            return True

        try:
            params_json = json.dumps({"query": query, **(metadata or {})})
            duration_ms = (metadata or {}).get("execution_time_ms", 0)
            username = (metadata or {}).get("username")
            resultado = response[:4000] if not error else "ERROR"

            query_sql = """
                INSERT INTO abcmasplus..LogOperaciones (
                    idUsuario, idOperacion, telegramChatId, telegramUsername,
                    parametros, resultado, mensajeError, duracionMs, fechaEjecucion
                )
                SELECT
                    ut.idUsuario,
                    (SELECT idOperacion FROM abcmasplus..Operaciones WHERE comando = :operation AND activo = 1),
                    :chat_id, :username, :params, :result, :error, :duration_ms, GETDATE()
                FROM abcmasplus..UsuariosTelegram ut
                WHERE ut.telegramChatId = :chat_id_lookup AND ut.activo = 1
            """
            await self.db_manager.execute_non_query_async(query_sql, {
                "operation": "/ia",
                "chat_id": str(user_id),
                "username": username,
                "params": params_json,
                "result": resultado,
                "error": error[:2000] if error else None,
                "duration_ms": int(duration_ms),
                "chat_id_lookup": str(user_id),
            })
            return True

        except Exception as e:
            logger.error(f"Error saving interaction for {user_id}: {e}")
            return False

    async def get_user_stats(self, user_id: str) -> dict:
        """Retorna estadísticas de uso del usuario desde LogOperaciones."""
        if not self.db_manager:
            return {}

        try:
            query = """
                SELECT
                    COUNT(*)                                            AS total,
                    SUM(CASE WHEN lo.mensajeError IS NULL THEN 1 ELSE 0 END) AS exitosos,
                    SUM(CASE WHEN lo.mensajeError IS NOT NULL THEN 1 ELSE 0 END) AS errores,
                    AVG(CAST(lo.duracionMs AS FLOAT))                   AS avg_ms,
                    MAX(lo.duracionMs)                                  AS max_ms,
                    MIN(lo.fechaEjecucion)                              AS primera,
                    MAX(lo.fechaEjecucion)                              AS ultima
                FROM abcmasplus..LogOperaciones lo
                INNER JOIN abcmasplus..UsuariosTelegram ut ON lo.idUsuario = ut.idUsuario
                WHERE ut.telegramChatId = :user_id AND ut.activo = 1
            """
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
            profile.interaction_count += 1
        await self.save_profile(profile)
        return profile.interaction_count

    def invalidate_cache(self, user_id: str) -> None:
        self._profiles_cache.pop(user_id, None)

    def clear_cache(self) -> None:
        self._profiles_cache.clear()
