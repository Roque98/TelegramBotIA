"""
Memory Service - Servicio principal de memoria para el ReAct Agent.

Coordina MemoryRepository y construcción de contexto con caching.
Absorbe la lógica de ContextBuilder.
"""

import asyncio
import logging
from collections import OrderedDict
from datetime import UTC, datetime
from typing import Any, Optional

from src.agents.base.events import UserContext
from src.domain.memory.memory_entity import CacheEntry, UserProfile
from src.domain.memory.memory_repository import MemoryRepository

logger = logging.getLogger(__name__)


class MemoryService:
    """
    Servicio de memoria para el agente conversacional.

    Responsabilidades:
    - Obtener contexto de usuario con caching
    - Registrar interacciones
    - Actualizar resúmenes de memoria a largo plazo
    - Construir UserContext (absorbe ContextBuilder)
    """

    def __init__(
        self,
        repository: Optional[MemoryRepository] = None,
        permission_service: Optional[Any] = None,
        cache_ttl_seconds: int = 300,
        max_cache_size: int = 1000,
        max_working_memory: int = 10,
    ):
        self.repository = repository or MemoryRepository()
        self._permission_service = permission_service
        self.cache_ttl_seconds = cache_ttl_seconds
        self.max_cache_size = max_cache_size
        self.max_working_memory = max_working_memory
        self._cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self._lock = asyncio.Lock()
        self._cache_hits = 0
        self._cache_misses = 0
        logger.info(f"MemoryService inicializado (cache_ttl={cache_ttl_seconds}s, max_cache={max_cache_size})")

    # -------------------------------------------------------------------------
    # Context building (absorbido de ContextBuilder)
    # -------------------------------------------------------------------------

    async def build_context(
        self,
        user_id: str,
        include_working_memory: bool = True,
        include_long_term: bool = True,
    ) -> UserContext:
        profile = await self.repository.get_profile(user_id)

        working_memory = []
        if include_working_memory:
            working_memory = await self.repository.get_recent_messages(
                user_id=user_id,
                limit=self.max_working_memory,
            )

        return UserContext(
            user_id=user_id,
            display_name=profile.display_name if profile else "Usuario",
            roles=profile.roles if profile else [],
            preferences=profile.preferences if profile else {},
            working_memory=working_memory,
            long_term_summary=(profile.long_term_summary if profile and include_long_term else None),
            db_user_id=profile.db_user_id if profile else None,
            role_id=profile.role_id if profile else None,
            gerencia_ids=profile.gerencia_ids if profile else [],
            direccion_ids=profile.direccion_ids if profile else [],
        )

    async def build_minimal_context(self, user_id: str) -> UserContext:
        profile = await self.repository.get_profile(user_id)
        return UserContext(
            user_id=user_id,
            display_name=profile.display_name if profile else "Usuario",
            roles=profile.roles if profile else [],
        )

    async def enrich_context(self, context: UserContext, additional_data: dict[str, Any]) -> UserContext:
        return UserContext(
            user_id=context.user_id,
            display_name=context.display_name,
            roles=context.roles,
            preferences={**context.preferences, **additional_data},
            working_memory=context.working_memory,
            long_term_summary=context.long_term_summary,
            current_date=context.current_date,
        )

    @staticmethod
    def format_working_memory(messages: list[dict[str, Any]]) -> str:
        if not messages:
            return "Sin conversaciones recientes."
        formatted = []
        for msg in messages[-5:]:
            role_key = msg.get("role", "user")
            role = "Usuario" if role_key == "user" else "Asistente"
            content = msg.get("content", "")
            limit = 120 if role_key == "user" else 600
            if len(content) > limit:
                cutoff = content.rfind("\n", 0, limit)
                content = content[: cutoff if cutoff > 0 else limit] + "…"
            formatted.append(f"{role}: {content}")
        return "\n".join(formatted)

    # -------------------------------------------------------------------------
    # Context retrieval with cache
    # -------------------------------------------------------------------------

    async def get_context(
        self,
        user_id: str,
        include_working_memory: bool = True,
        include_long_term: bool = True,
        force_refresh: bool = False,
    ) -> UserContext:
        cache_key = f"{user_id}:{include_working_memory}:{include_long_term}"

        if not force_refresh:
            cached = self._get_from_cache(cache_key)
            if cached:
                logger.debug(f"Cache hit for user {user_id}")
                context = cached
            else:
                context = None
        else:
            context = None

        if context is None:
            logger.debug(f"Cache miss for user {user_id}, building context")
            context = await self.build_context(
                user_id=user_id,
                include_working_memory=include_working_memory,
                include_long_term=include_long_term,
            )
            logger.debug(
                f"Context built for {user_id}: "
                f"name={context.display_name}, "
                f"working_memory={len(context.working_memory)} msgs, "
                f"has_summary={context.long_term_summary is not None}"
            )
            await self._add_to_cache(cache_key, context)

        # Permisos siempre frescos — TTL propio de 60s en PermissionService,
        # independiente del cache de contexto (300s).
        if self._permission_service and context.db_user_id and context.role_id is not None:
            try:
                context.permisos = await self._permission_service.get_all_for_user(
                    user_id=context.db_user_id,
                    role_id=context.role_id,
                    gerencia_ids=context.gerencia_ids,
                    direccion_ids=context.direccion_ids,
                )
            except Exception as e:
                logger.warning(f"Error cargando permisos para user {user_id}: {e}")

        return context

    async def get_minimal_context(self, user_id: str) -> UserContext:
        return await self.build_minimal_context(user_id)

    # -------------------------------------------------------------------------
    # Interactions & summaries
    # -------------------------------------------------------------------------

    # record_interaction eliminado — las interacciones las persiste
    # ObservabilityRepository.save_interaction() directamente (OBS-31)

    async def update_summary(self, user_id: str, new_summary: str) -> bool:
        try:
            profile = await self.repository.get_profile(user_id)
            if not profile:
                profile = UserProfile(user_id=user_id, long_term_summary=new_summary)
            else:
                profile.long_term_summary = new_summary
                profile.last_updated = datetime.now(UTC)

            saved = await self.repository.save_profile(profile)
            if saved:
                self._invalidate_user_cache(user_id)
                logger.info(f"Summary updated for user {user_id}")
            return saved
        except Exception as e:
            logger.error(f"Error updating summary for {user_id}: {e}")
            return False

    # -------------------------------------------------------------------------
    # Cache management
    # -------------------------------------------------------------------------

    def _get_from_cache(self, key: str) -> Optional[UserContext]:
        entry = self._cache.get(key)
        if entry and not entry.is_expired():
            self._cache.move_to_end(key)  # Marcar como recientemente usado (LRU)
            self._cache_hits += 1
            return entry.context
        elif entry:
            del self._cache[key]
        self._cache_misses += 1
        return None

    async def _add_to_cache(self, key: str, context: UserContext) -> None:
        async with self._lock:
            self._evict_if_needed()
            self._cache[key] = CacheEntry(context=context, ttl_seconds=self.cache_ttl_seconds)
            self._cache.move_to_end(key)  # Asegurar que la nueva entrada quede al final

    def _invalidate_user_cache(self, user_id: str) -> None:
        keys_to_delete = [k for k in self._cache if k.startswith(f"{user_id}:")]
        for key in keys_to_delete:
            del self._cache[key]
        self.repository.invalidate_cache(user_id)

    def _evict_if_needed(self) -> None:
        """
        Evictar entradas del cache cuando está lleno.

        Estrategia:
        1. Primero eliminar entradas expiradas (TTL vencido)
        2. Si sigue lleno, eliminar las entradas menos recientemente usadas (LRU)
           hasta quedar en el 75% de capacidad
        """
        # Paso 1: eliminar expiradas
        expired_keys = [k for k, v in self._cache.items() if v.is_expired()]
        for key in expired_keys:
            del self._cache[key]

        # Paso 2: si sigue lleno, eliminar LRU (primeros en OrderedDict = menos usados)
        if len(self._cache) >= self.max_cache_size:
            target_size = max(0, int(self.max_cache_size * 0.75))
            while len(self._cache) > target_size:
                self._cache.popitem(last=False)  # Elimina el menos recientemente usado
            logger.debug(
                f"Cache eviction: {len(expired_keys)} expiradas + LRU hasta {target_size} entradas"
            )

    def clear_cache(self) -> None:
        self._cache.clear()
        self._cache_hits = 0
        self._cache_misses = 0
        self.repository.clear_cache()
        logger.info("Memory cache cleared")

    def get_cache_stats(self) -> dict[str, Any]:
        expired = sum(1 for v in self._cache.values() if v.is_expired())
        total_requests = self._cache_hits + self._cache_misses
        hit_rate = round(self._cache_hits / total_requests, 3) if total_requests > 0 else 0.0
        return {
            "total_entries": len(self._cache),
            "active_entries": len(self._cache) - expired,
            "expired_entries": expired,
            "max_size": self.max_cache_size,
            "ttl_seconds": self.cache_ttl_seconds,
            "cache_hits": self._cache_hits,
            "cache_misses": self._cache_misses,
            "hit_rate": hit_rate,
        }

    async def health_check(self) -> bool:
        try:
            context = await self.get_minimal_context("__health_check__")
            return context is not None
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False
