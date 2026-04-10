"""
Preference Tool - Herramienta para guardar preferencias del usuario.

Permite al agente guardar preferencias como alias, idioma, formato, etc.
"""

import json
import logging
import time
from typing import Any, Optional

from .base import BaseTool, ToolCategory, ToolDefinition, ToolParameter, ToolResult

logger = logging.getLogger(__name__)


class SavePreferenceTool(BaseTool):
    """
    Herramienta para guardar preferencias del usuario.

    Guarda preferencias en la base de datos para personalizar
    futuras interacciones.

    Example:
        >>> tool = SavePreferenceTool(db_manager)
        >>> result = await tool.execute(
        ...     user_id="1835573278",
        ...     key="alias",
        ...     value="Angel"
        ... )
        >>> print(result.to_observation())
    """

    def __init__(self, db_manager: Any, memory_service: Optional[Any] = None):
        """
        Inicializa el SavePreferenceTool.

        Args:
            db_manager: Gestor de base de datos
            memory_service: Servicio de memoria (para invalidar cache tras guardar)
        """
        self.db_manager = db_manager
        self.memory_service = memory_service
        logger.info("SavePreferenceTool inicializado")

    @property
    def definition(self) -> ToolDefinition:
        """Definición del tool para el agente."""
        return ToolDefinition(
            name="save_preference",
            description=(
                "Guarda una preferencia del usuario (como su alias/nombre preferido, "
                "idioma, formato de respuesta, etc.). Usa esto cuando el usuario "
                "pida que lo llames de cierta forma o exprese una preferencia personal."
            ),
            category=ToolCategory.DATABASE,
            parameters=[
                ToolParameter(
                    name="key",
                    type="string",
                    description="Tipo de preferencia: 'alias', 'idioma', 'formato', etc.",
                    required=True,
                ),
                ToolParameter(
                    name="value",
                    type="string",
                    description="Valor de la preferencia",
                    required=True,
                ),
            ],
            examples=[
                {
                    "query": "Llámame Angel",
                    "action_input": {"key": "alias", "value": "Angel"},
                },
                {
                    "query": "Prefiero respuestas cortas",
                    "action_input": {"key": "formato", "value": "conciso"},
                },
            ],
            usage_hint="Para guardar preferencias del usuario (alias, idioma, formato de respuesta): usa `save_preference`",
        )

    async def execute(
        self,
        key: str,
        value: str,
        user_id: Optional[str] = None,
        **kwargs: Any,
    ) -> ToolResult:
        """
        Guarda una preferencia del usuario.

        Args:
            key: Tipo de preferencia (alias, idioma, etc.)
            value: Valor de la preferencia
            user_id: ID del usuario (Telegram chat ID)
            **kwargs: Argumentos adicionales (puede incluir context)

        Returns:
            ToolResult con el resultado de la operación
        """
        start_time = time.perf_counter()

        # Obtener user_id del contexto si no se proporciona directamente
        if not user_id:
            context = kwargs.get("context")
            if context:
                user_id = getattr(context, "user_id", None)

        if not user_id:
            return ToolResult(
                success=False,
                error="No se pudo identificar al usuario",
                execution_time_ms=(time.perf_counter() - start_time) * 1000,
            )

        if not self.db_manager:
            return ToolResult(
                success=False,
                error="Base de datos no disponible",
                execution_time_ms=(time.perf_counter() - start_time) * 1000,
            )

        try:
            # Obtener preferencias actuales
            results = self.db_manager.execute_query(
                "EXEC abcmasplus..BotIAv2_sp_GetPreferenciasUsuario @telegramChatId = :user_id",
                {"user_id": str(user_id)}
            )

            # Parsear preferencias existentes o crear nuevas
            if results and results[0].get("preferencias"):
                try:
                    preferences = json.loads(results[0]["preferencias"])
                except json.JSONDecodeError:
                    preferences = {}
            else:
                preferences = {}

            # Actualizar preferencia y guardar (upsert)
            preferences[key] = value
            self.db_manager.execute_non_query(
                """
                EXEC abcmasplus..BotIAv2_sp_GuardarPreferenciasUsuario
                    @telegramChatId = :user_id,
                    @preferencias   = :preferences
                """,
                {"user_id": str(user_id), "preferences": json.dumps(preferences, ensure_ascii=False)}
            )

            elapsed = (time.perf_counter() - start_time) * 1000
            logger.info(f"Preferencia guardada: {key}={value} para usuario {user_id}")

            # Actualizar user_context en el request actual y limpiar cache para el próximo
            user_context = kwargs.get("user_context")
            if user_context is not None:
                user_context.preferences[key] = value
            if self.memory_service:
                self.memory_service._invalidate_user_cache(str(user_id))

            return ToolResult(
                success=True,
                data={
                    "key": key,
                    "value": value,
                    "message": f"Preferencia '{key}' guardada correctamente",
                },
                execution_time_ms=elapsed,
            )

        except Exception as e:
            elapsed = (time.perf_counter() - start_time) * 1000
            logger.error(f"Error guardando preferencia: {e}")
            return ToolResult(
                success=False,
                error=str(e),
                execution_time_ms=elapsed,
            )
