"""
AgentBuilder — Construye instancias de ReActAgent a partir de AgentDefinition.

Cache de instancias keyed por (idAgente, version). Cuando el trigger de BD
incrementa la versión del prompt, la próxima llamada a build() genera una
nueva instancia con el prompt actualizado.

Thread-safe con threading.Lock.
"""

import logging
import threading
from typing import TYPE_CHECKING, Any, Optional

from src.agents.react.agent import ReActAgent
from src.agents.tools.registry import ToolRegistry
from src.config.settings import settings

if TYPE_CHECKING:
    from src.domain.agent_config.agent_config_entity import AgentDefinition

logger = logging.getLogger(__name__)


class AgentBuilder:
    """
    Construye y cachea instancias de ReActAgent desde configuración en BD.

    Cada agente se construye una vez por (idAgente, version) y se reutiliza
    en requests subsiguientes. El trigger TR_AgenteDef_VersionHistorial
    garantiza que version cambia al editar el prompt, invalidando el cache.

    Example:
        >>> builder = AgentBuilder(tool_registry=registry, openai_api_key="sk-...")
        >>> agent = builder.build(definition)
        >>> response = await agent.execute(query, context)
    """

    def __init__(
        self,
        tool_registry: ToolRegistry,
        openai_api_key: Optional[str] = None,
    ) -> None:
        self.tool_registry = tool_registry
        self._api_key = openai_api_key or settings.openai_api_key
        self._cache: dict[tuple[int, int], ReActAgent] = {}
        self._lock = threading.Lock()

    def build(self, definition: "AgentDefinition") -> ReActAgent:
        """
        Construye o retorna del cache un ReActAgent para el AgentDefinition dado.

        Args:
            definition: Configuración del agente leída desde BD

        Returns:
            ReActAgent configurado según la definición
        """
        key = (definition.id, definition.version)
        with self._lock:
            if key not in self._cache:
                self._cache[key] = self._do_build(definition)
                logger.debug(
                    f"AgentBuilder: instancia construida para "
                    f"agente='{definition.nombre}' v{definition.version}"
                )
            return self._cache[key]

    def _do_build(self, definition: "AgentDefinition") -> ReActAgent:
        """Construye la instancia real del agente."""
        from src.agents.providers.openai_provider import OpenAIProvider

        # Seleccionar modelo: override del agente o default del sistema
        model = definition.modelo_override or settings.openai_loop_model
        llm = OpenAIProvider(api_key=self._api_key, model=model)

        # tool_scope: None para generalista (ve todos sus permisos),
        # set de nombres para especialistas (intersección con permisos del usuario)
        tool_scope: Optional[set[str]] = (
            None if definition.es_generalista else set(definition.tools)
        )

        agent = ReActAgent(
            llm=llm,
            tool_registry=self.tool_registry,
            max_iterations=definition.max_iteraciones,
            temperature=float(definition.temperatura),
            system_prompt_override=definition.system_prompt,
            tool_scope=tool_scope,
        )

        logger.info(
            f"AgentBuilder: '{definition.nombre}' "
            f"model={model} "
            f"max_iter={definition.max_iteraciones} "
            f"temp={definition.temperatura} "
            f"scope={'all' if tool_scope is None else list(tool_scope)}"
        )
        return agent

    def clear_instance_cache(self) -> None:
        """
        Limpia el cache de instancias.

        Llamado por AgentConfigService.invalidate_cache() para forzar
        reconstrucción de agentes tras una recarga de configuración.
        """
        with self._lock:
            count = len(self._cache)
            self._cache.clear()
        logger.info(f"AgentBuilder: cache limpiado ({count} instancias eliminadas)")

    def cache_size(self) -> int:
        """Retorna la cantidad de instancias en cache."""
        with self._lock:
            return len(self._cache)
