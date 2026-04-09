"""
Tool Registry - Registro singleton de herramientas para ReAct Agent.

Mantiene un registro de todas las herramientas disponibles y genera
la descripción de herramientas para el prompt del LLM.
"""

import logging
import threading
from typing import TYPE_CHECKING, Optional

from .base import BaseTool, ToolCategory, ToolResult

if TYPE_CHECKING:
    from src.agents.base.events import UserContext

logger = logging.getLogger(__name__)


class ToolRegistry:
    """
    Registro singleton de herramientas para el ReAct Agent.

    Permite registrar, buscar y generar prompts de herramientas.

    Example:
        >>> registry = ToolRegistry()
        >>> registry.register(DatabaseTool())
        >>> tool = registry.get("database_query")
        >>> prompt = registry.get_tools_prompt()
    """

    _instance: Optional["ToolRegistry"] = None
    _lock: threading.Lock = threading.Lock()

    def __new__(cls) -> "ToolRegistry":
        """Implementar patrón Singleton con double-checked locking (thread-safe)."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._tools: dict[str, BaseTool] = {}
                    cls._instance._initialized = True
                    logger.info("ToolRegistry inicializado")
        return cls._instance

    def register(self, tool: BaseTool) -> None:
        """
        Registra una herramienta en el registro.

        Args:
            tool: Herramienta a registrar

        Raises:
            ValueError: Si ya existe una herramienta con ese nombre
        """
        tool_name = tool.name

        if tool_name in self._tools:
            raise ValueError(f"Tool '{tool_name}' ya está registrado")

        self._tools[tool_name] = tool
        logger.info(f"Tool registrado: {tool_name} ({tool.category.value})")

    def unregister(self, tool_name: str) -> bool:
        """
        Desregistra una herramienta.

        Args:
            tool_name: Nombre de la herramienta

        Returns:
            True si se desregistró, False si no existía
        """
        if tool_name not in self._tools:
            return False

        del self._tools[tool_name]
        logger.info(f"Tool desregistrado: {tool_name}")
        return True

    def get(self, tool_name: str) -> Optional[BaseTool]:
        """
        Obtiene una herramienta por nombre.

        Args:
            tool_name: Nombre de la herramienta

        Returns:
            BaseTool o None si no existe
        """
        return self._tools.get(tool_name)

    def get_all(self) -> list[BaseTool]:
        """
        Obtiene todas las herramientas registradas.

        Returns:
            Lista de todas las herramientas
        """
        return list(self._tools.values())

    def get_by_category(self, category: ToolCategory) -> list[BaseTool]:
        """
        Obtiene herramientas de una categoría específica.

        Args:
            category: Categoría a filtrar

        Returns:
            Lista de herramientas de esa categoría
        """
        return [tool for tool in self._tools.values() if tool.category == category]

    def get_tools_prompt(
        self,
        context_budget_used: float = 0.0,
        user_context: Optional["UserContext"] = None,
    ) -> str:
        """
        Genera la descripción de herramientas para el prompt del LLM.

        Si `user_context.permisos` está cargado, solo incluye las tools
        donde `permisos.get("tool:<name>", False) == True`.
        Sin permisos cargados: incluye todas (backward compat).

        Adapta el nivel de detalle según el presupuesto de contexto disponible:
        - < 90% usado: descripción completa con parámetros y ejemplos
        - 90–95% usado: descripción truncada a 250 chars por tool
        - > 95% usado: solo nombres de tools

        Args:
            context_budget_used: Fracción del contexto usada (0.0 – 1.0)
            user_context: Contexto del usuario (con permisos precargados)

        Returns:
            String formateado con las herramientas disponibles para el usuario
        """
        permisos: dict[str, bool] = getattr(user_context, "permisos", {}) if user_context else {}

        permisos_loaded: bool = getattr(user_context, "permisos_loaded", False) if user_context else False

        # Filtrar herramientas según permisos
        # - permisos_loaded=True → mostrar solo las autorizadas para este usuario
        # - permisos_loaded=False → usuario sin perfil o API sin permisos resueltos;
        #   mostrar solo las tools públicas (esPublico) registradas en el registry.
        #   En la práctica, las tools "privadas" desactivadas en BotIAv2_Recurso no
        #   aparecerán aquí de todas formas porque execute() las bloqueará, pero
        #   es mejor no mostrárselas al LLM en primer lugar.
        if permisos_loaded:
            visible_tools = {
                name: tool for name, tool in self._tools.items()
                if permisos.get(f"tool:{name}", False)
            }
        else:
            # Sin permisos: solo tools que el registry considera "siempre activas"
            # (reload_permissions, finish) — el resto requiere perfil de usuario
            _ALWAYS_VISIBLE = {"reload_permissions", "finish"}
            visible_tools = {
                name: tool for name, tool in self._tools.items()
                if name in _ALWAYS_VISIBLE
            }

        if not visible_tools:
            return "No tools available."

        # Modo solo nombres si el contexto está casi lleno
        if context_budget_used >= 0.95:
            names = ", ".join(visible_tools.keys())
            return f"## Available Tools\n{names}"

        lines = ["## Available Tools\n"]
        MAX_DESC_CHARS = 250
        compact = context_budget_used >= 0.90

        # Agrupar por categoría
        by_category: dict[ToolCategory, list[BaseTool]] = {}
        for tool in visible_tools.values():
            if tool.category not in by_category:
                by_category[tool.category] = []
            by_category[tool.category].append(tool)

        # Generar descripción por categoría
        for category in ToolCategory:
            tools = by_category.get(category, [])
            if tools:
                lines.append(f"### {category.value.title()}\n")
                for tool in tools:
                    if compact:
                        desc = tool.definition.description
                        if len(desc) > MAX_DESC_CHARS:
                            desc = desc[:MAX_DESC_CHARS] + "..."
                        lines.append(f"- **{tool.name}**: {desc}")
                    else:
                        lines.append(tool.definition.to_prompt_format())
                    lines.append("")

        return "\n".join(lines)

    async def execute(
        self,
        tool_name: str,
        action_input: dict,
        user_context: Optional["UserContext"] = None,
    ) -> ToolResult:
        """
        Ejecuta un tool con verificación de permisos (segunda línea de defensa).

        Verifica `user_context.permisos` antes de ejecutar. Si el permiso
        está denegado, retorna un ToolResult de error sin ejecutar el tool.
        Si no hay permisos cargados, ejecuta sin restricción (backward compat).

        Args:
            tool_name: Nombre del tool a ejecutar
            action_input: Parámetros del tool
            user_context: Contexto del usuario con permisos precargados

        Returns:
            ToolResult con el resultado o error de permiso
        """
        tool = self._tools.get(tool_name)
        if tool is None:
            return ToolResult(success=False, data=None, error=f"Tool '{tool_name}' not found")

        # Verificar permisos si están cargados
        permisos: dict[str, bool] = getattr(user_context, "permisos", {}) if user_context else {}
        permisos_loaded: bool = getattr(user_context, "permisos_loaded", False) if user_context else False
        if permisos_loaded and not permisos.get(f"tool:{tool_name}", False):
            user_id = getattr(user_context, "user_id", "unknown") if user_context else "unknown"
            logger.warning(
                f"Permission denied: user={user_id} tool={tool_name} "
                f"(possible prompt injection or bypass attempt)"
            )
            return ToolResult(
                success=False,
                data=None,
                error="No tenés permiso para usar esta herramienta",
            )

        return await tool.execute(**action_input)

    def get_tool_names(self) -> list[str]:
        """
        Obtiene los nombres de todas las herramientas.

        Returns:
            Lista de nombres de herramientas
        """
        return list(self._tools.keys())

    def has_tool(self, tool_name: str) -> bool:
        """
        Verifica si existe una herramienta.

        Args:
            tool_name: Nombre de la herramienta

        Returns:
            True si existe, False si no
        """
        return tool_name in self._tools

    def clear(self) -> None:
        """
        Limpia todas las herramientas del registro.

        .. warning::
            **Solo para uso en tests.** No llamar en código de producción.
            Elimina todas las herramientas registradas sin posibilidad de recuperación.
        """
        self._tools.clear()
        logger.warning("ToolRegistry limpiado completamente")

    @classmethod
    def reset(cls) -> None:
        """
        Resetea el singleton completo (instancia + herramientas).

        .. warning::
            **Solo para uso en tests.** No llamar en código de producción.
            Destruye la instancia singleton; el próximo acceso creará una nueva.
        """
        with cls._lock:
            if cls._instance:
                cls._instance._tools.clear()
            cls._instance = None

    def get_stats(self) -> dict[str, int]:
        """
        Obtiene estadísticas del registro.

        Returns:
            Diccionario con estadísticas
        """
        stats = {
            "total_tools": len(self._tools),
            "by_category": {},
        }

        for category in ToolCategory:
            count = len(self.get_by_category(category))
            if count > 0:
                stats["by_category"][category.value] = count

        return stats

    def __repr__(self) -> str:
        return f"<ToolRegistry(tools={len(self._tools)})>"

    def __len__(self) -> int:
        return len(self._tools)

    def __contains__(self, tool_name: str) -> bool:
        return tool_name in self._tools


# Instancia global del registro
_global_registry: Optional[ToolRegistry] = None


def get_tool_registry() -> ToolRegistry:
    """
    Obtiene la instancia global del registro de herramientas.

    Returns:
        ToolRegistry singleton
    """
    global _global_registry
    if _global_registry is None:
        _global_registry = ToolRegistry()
    return _global_registry
