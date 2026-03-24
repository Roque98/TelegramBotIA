"""
Memory Service - Servicio principal de memoria para el ReAct Agent.

Coordina MemoryRepository y construcción de contexto con caching.
Absorbe la lógica de ContextBuilder.
"""

import asyncio
import logging
from datetime import UTC, datetime
from typing import Any, Optional

from src.agents.base.events import UserContext
from src.memory.memory_entity import CacheEntry, UserProfile
from src.memory.memory_repository import MemoryRepository

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
        cache_ttl_seconds: int = 300,
        max_cache_size: int = 1000,
        max_working_memory: int = 10,
    ):
        self.repository = repository or MemoryRepository()
        self.cache_ttl_seconds = cache_ttl_seconds
        self.max_cache_size = max_cache_size
        self.max_working_memory = max_working_memory
        self._cache: dict[str, CacheEntry] = {}
        self._lock = asyncio.Lock()
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
            role = "Usuario" if msg.get("role") == "user" else "Asistente"
            content = msg.get("content", "")[:200]
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
                return cached

        logger.debug(f"Cache miss for user {user_id}, building context")
        context = await self.build_context(
            user_id=user_id,
            include_working_memory=include_working_memory,
            include_long_term=include_long_term,
        )

        logger.info(
            f"[DEBUG] Context built for {user_id}: "
            f"name={context.display_name}, "
            f"working_memory={len(context.working_memory)} msgs, "
            f"has_summary={context.long_term_summary is not None}"
        )

        await self._add_to_cache(cache_key, context)
        return context

    async def get_minimal_context(self, user_id: str) -> UserContext:
        return await self.build_minimal_context(user_id)

    # -------------------------------------------------------------------------
    # Interactions & summaries
    # -------------------------------------------------------------------------

    async def record_interaction(
        self,
        user_id: str,
        query: str,
        response: str,
        metadata: Optional[dict[str, Any]] = None,
    ) -> bool:
        try:
            saved = await self.repository.save_interaction(user_id=user_id, query=query, response=response, metadata=metadata)
            if saved:
                await self.repository.increment_interaction_count(user_id)
                self._invalidate_user_cache(user_id)
                logger.debug(f"Interaction recorded for user {user_id}")
            return saved
        except Exception as e:
            logger.error(f"Error recording interaction for {user_id}: {e}")
            return False

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
            return entry.context
        elif entry:
            del self._cache[key]
        return None

    async def _add_to_cache(self, key: str, context: UserContext) -> None:
        async with self._lock:
            if len(self._cache) >= self.max_cache_size:
                self._cleanup_cache()
            self._cache[key] = CacheEntry(context=context, ttl_seconds=self.cache_ttl_seconds)

    def _invalidate_user_cache(self, user_id: str) -> None:
        keys_to_delete = [k for k in self._cache if k.startswith(f"{user_id}:")]
        for key in keys_to_delete:
            del self._cache[key]
        self.repository.invalidate_cache(user_id)

    def _cleanup_cache(self) -> None:
        expired_keys = [k for k, v in self._cache.items() if v.is_expired()]
        for key in expired_keys:
            del self._cache[key]
        if len(self._cache) >= self.max_cache_size:
            sorted_keys = sorted(self._cache.keys(), key=lambda k: self._cache[k].created_at)
            for key in sorted_keys[:max(1, len(sorted_keys) // 4)]:
                del self._cache[key]

    def clear_cache(self) -> None:
        self._cache.clear()
        self.repository.clear_cache()
        logger.info("Memory cache cleared")

    def get_cache_stats(self) -> dict[str, Any]:
        expired = sum(1 for v in self._cache.values() if v.is_expired())
        return {
            "total_entries": len(self._cache),
            "active_entries": len(self._cache) - expired,
            "expired_entries": expired,
            "max_size": self.max_cache_size,
            "ttl_seconds": self.cache_ttl_seconds,
        }

    async def health_check(self) -> bool:
        try:
            context = await self.get_minimal_context("__health_check__")
            return context is not None
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False
