"""
ReloadAgentConfigTool — Tool de admin para recargar la configuración de agentes desde BD.

Invalida el cache de AgentConfigService y el cache de instancias del AgentBuilder,
forzando que la próxima consulta use los prompts y configuraciones actualizados.

Recurso ARQ-35: tool:reload_agent_config (esPublico=0, solo admins)
"""

import logging
from typing import Any, Optional

from .base import BaseTool, ToolCategory, ToolDefinition, ToolResult

logger = logging.getLogger(__name__)


class ReloadAgentConfigTool(BaseTool):
    """
    Recarga la configuración de agentes desde BD invalidando el cache.

    Solo disponible para administradores (esPublico=0 en BotIAv2_Recurso).
    Usar después de modificar prompts, agregar/desactivar agentes en BD
    o cambiar el scope de tools de un agente.

    Uso típico:
        1. Admin edita systemPrompt en BotIAv2_AgenteDef (trigger incrementa version)
        2. Admin invoca esta tool para aplicar el cambio sin reiniciar el bot
        3. La próxima consulta usa el prompt actualizado
    """

    name = "reload_agent_config"
    definition = ToolDefinition(
        name="reload_agent_config",
        description=(
            "Recarga la configuración de agentes LLM desde la base de datos, "
            "invalidando el cache. Úsala después de modificar prompts, "
            "agregar/desactivar agentes o cambiar el scope de tools en BotIAv2_AgenteDef. "
            "Los cambios se aplican en la siguiente consulta sin reiniciar el bot. "
            "Solo disponible para administradores."
        ),
        category=ToolCategory.UTILITY,
        parameters=[],
        returns=(
            "Confirmación de recarga con lista de agentes activos cargados desde BD."
        ),
    )

    def __init__(self, agent_config_service: Optional[Any] = None) -> None:
        self._agent_config_service = agent_config_service

    async def execute(
        self,
        user_id: Optional[str] = None,
        user_context: Optional[Any] = None,
        **kwargs: Any,
    ) -> ToolResult:
        """
        Invalida el cache y retorna el estado actualizado de los agentes.

        El user_context es inyectado por ToolRegistry.execute().
        """
        if not self._agent_config_service:
            return ToolResult(
                success=True,
                data={"message": "Configuración de agentes recargada (servicio no disponible)."},
            )

        try:
            # Invalida cache del service + cache de instancias del builder
            self._agent_config_service.invalidate_cache()

            # Cargar nueva configuración para confirmar que todo funciona
            agents = self._agent_config_service.get_active_agents()

            agentes_info = [
                {
                    "nombre": a.nombre,
                    "tools": a.tools,
                    "es_generalista": a.es_generalista,
                    "version": a.version,
                }
                for a in agents
            ]

            logger.info(
                f"ReloadAgentConfigTool: configuración recargada por user={user_id} "
                f"— {len(agents)} agentes activos"
            )

            return ToolResult(
                success=True,
                data={
                    "message": (
                        f"Configuración de agentes recargada exitosamente. "
                        f"{len(agents)} agentes activos."
                    ),
                    "agentes": agentes_info,
                },
            )

        except Exception as e:
            logger.error(f"ReloadAgentConfigTool error para user={user_id}: {e}")
            return ToolResult(
                success=False,
                data=None,
                error=f"Error recargando configuración de agentes: {e}",
            )
