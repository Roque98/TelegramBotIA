"""
Entidades del módulo de memoria.

Define los modelos de datos para perfiles de usuario, interacciones y cache.
"""

from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from typing import Any, Optional


class DatabaseManager:
    """Protocolo para el gestor de base de datos."""

    def execute_query(self, query: str, params: Optional[dict] = None) -> list:
        ...

    def execute_non_query(self, query: str, params: Optional[dict] = None) -> int:
        ...


@dataclass
class UserProfile:
    """Perfil de usuario con información de memoria."""

    user_id: str
    display_name: str = "Usuario"
    roles: list[str] = field(default_factory=list)
    long_term_summary: Optional[str] = None
    interaction_count: int = 0
    last_updated: Optional[datetime] = None
    preferences: dict[str, Any] = field(default_factory=dict)
    # Contexto organizacional (SEC-01)
    db_user_id: Optional[int] = None
    role_id: Optional[int] = None
    role_name: Optional[str] = None
    gerencia_ids: list[int] = field(default_factory=list)
    direccion_ids: list[int] = field(default_factory=list)

    def has_summary(self) -> bool:
        return self.long_term_summary is not None and len(self.long_term_summary) > 0


@dataclass
class Interaction:
    """Representa una interacción usuario-agente."""

    interaction_id: str
    user_id: str
    query: str
    response: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class CacheEntry:
    """Entrada de cache con TTL."""

    context: Any  # UserContext — typed as Any to avoid circular import
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    ttl_seconds: int = 300

    def is_expired(self) -> bool:
        return datetime.now(UTC) > self.created_at + timedelta(seconds=self.ttl_seconds)

    def time_remaining(self) -> float:
        remaining = (self.created_at + timedelta(seconds=self.ttl_seconds) - datetime.now(UTC)).total_seconds()
        return max(0, remaining)
