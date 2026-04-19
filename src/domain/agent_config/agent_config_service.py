"""
AgentConfigService — Cache LRU sobre AgentConfigRepository.

Provee acceso a la configuración de agentes con TTL de 5 minutos.
Invalida también el cache de instancias del AgentBuilder vía set_builder().
"""
import logging
import time
import threading
from typing import TYPE_CHECKING, Any, Optional

from .agent_config_entity import AgentDefinition
from .agent_config_repository import AgentConfigRepository
from src.infra.observability import get_metrics

if TYPE_CHECKING:
    from src.agents.factory.agent_builder import AgentBuilder

logger = logging.getLogger(__name__)

# Placeholders requeridos en todo systemPrompt almacenado en BD
_REQUIRED_PLACEHOLDERS = ("{tools_description}", "{usage_hints}")


class AgentConfigService:
    def __init__(
        self,
        repository: AgentConfigRepository,
        cache_ttl_seconds: int = 300,
    ) -> None:
        self._repo = repository
        self._ttl = cache_ttl_seconds
        self._cache: Optional[list[AgentDefinition]] = None
        self._cache_ts: float = 0.0
        self._lock = threading.Lock()
        self._builder: Optional["AgentBuilder"] = None

    def set_builder(self, builder: "AgentBuilder") -> None:
        """Inyección tardía para evitar dependencia circular en factory.py."""
        self._builder = builder

    def get_active_agents(self) -> list[AgentDefinition]:
        """Retorna agentes activos desde cache o BD."""
        with self._lock:
            if self._cache is not None and (time.monotonic() - self._cache_ts) < self._ttl:
                get_metrics().record_cache_hit()
                return self._cache

            get_metrics().record_cache_miss()
            agents = self._repo.get_all_active()
            valid = []
            for agent in agents:
                if self._validate_placeholders(agent):
                    valid.append(agent)

            self._cache = valid
            self._cache_ts = time.monotonic()
            logger.info(f"AgentConfigService: cargados {len(valid)} agentes desde BD")
            return valid

    def invalidate_cache(self) -> None:
        """Invalida el cache del service y el cache de instancias del builder."""
        with self._lock:
            self._cache = None
            self._cache_ts = 0.0
        if self._builder is not None:
            self._builder.clear_instance_cache()
        logger.info("AgentConfigService: cache invalidado")

    @staticmethod
    def _validate_placeholders(agent: AgentDefinition) -> bool:
        """
        Verifica que el systemPrompt contenga los placeholders requeridos.
        Si no los tiene, loguea WARNING y excluye el agente de la lista activa
        para evitar KeyError en runtime cuando build_system_prompt() intente formatear.
        """
        for placeholder in _REQUIRED_PLACEHOLDERS:
            if placeholder not in agent.system_prompt:
                logger.warning(
                    f"Agente '{agent.nombre}' excluido: systemPrompt no contiene "
                    f"'{placeholder}'. Editá el prompt en BotIAv2_AgenteDef."
                )
                return False
        return True
