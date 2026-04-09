"""
Save Memory Tool - Permite al agente guardar hechos importantes en memoria.

Soporta tres scopes:
- session: notas temporales del run actual (en UserContext, se borran al terminar)
- user: hechos persistentes del usuario (se guardan en DB via MemoryService)
"""

import logging
import time
from typing import Any, Optional

from .base import BaseTool, ToolCategory, ToolDefinition, ToolParameter, ToolResult

logger = logging.getLogger(__name__)


class SaveMemoryTool(BaseTool):
    """
    Herramienta para que el agente guarde hechos importantes en memoria.

    Scope 'session': guarda en UserContext.session_notes (solo dura el run actual).
    Scope 'user': guarda en DB como nota persistente del usuario.

    Example:
        >>> tool = SaveMemoryTool(memory_service)
        >>> result = await tool.execute(
        ...     scope="session",
        ...     fact="El usuario preguntó por ventas de marzo",
        ...     user_context=context,
        ... )
    """

    is_read_only = False

    def __init__(self, memory_service: Optional[Any] = None):
        self.memory_service = memory_service

    @property
    def definition(self) -> ToolDefinition:
        return ToolDefinition(
            name="save_memory",
            description=(
                "Save an important fact to memory for later use in this conversation. "
                "Use 'session' scope for temporary notes (current run only). "
                "Use 'user' scope for persistent facts about the user."
            ),
            category=ToolCategory.UTILITY,
            parameters=[
                ToolParameter(
                    name="scope",
                    param_type="string",
                    description="Memory scope: 'session' (temporary) or 'user' (persistent)",
                    required=True,
                    examples=["session", "user"],
                ),
                ToolParameter(
                    name="fact",
                    param_type="string",
                    description="The fact to remember, written as a clear, concise statement",
                    required=True,
                    examples=[
                        "User is interested in Q1 sales data",
                        "User prefers summaries in bullet points",
                    ],
                ),
            ],
            examples=[
                {"scope": "session", "fact": "User asked about sales from last month"},
                {"scope": "user", "fact": "User prefers responses in Spanish with bullet points"},
            ],
            returns="Confirmation that the fact was saved",
            usage_hint="Para recordar datos del usuario entre sesiones (hechos persistentes): usa `save_memory`",
        )

    async def execute(self, **kwargs: Any) -> ToolResult:
        start_time = time.perf_counter()
        scope = kwargs.get("scope", "session")
        fact = kwargs.get("fact", "").strip()
        user_context = kwargs.get("user_context")

        if not fact:
            return ToolResult.error_result("fact cannot be empty")

        if scope not in ("session", "user"):
            return ToolResult.error_result(f"Invalid scope '{scope}'. Use 'session' or 'user'.")

        elapsed_ms = (time.perf_counter() - start_time) * 1000

        try:
            if scope == "session":
                if user_context is not None:
                    user_context.session_notes.append(fact)
                    logger.debug(f"Session note saved: {fact[:60]}")
                    return ToolResult.success_result(
                        data="Nota de sesión guardada.",
                        execution_time_ms=elapsed_ms,
                    )
                return ToolResult.error_result("No user context available for session scope")

            elif scope == "user":
                if self.memory_service and user_context:
                    user_id = user_context.user_id
                    existing = user_context.long_term_summary or ""
                    new_summary = f"{existing}\n- {fact}".strip() if existing else f"- {fact}"
                    await self.memory_service.update_summary(user_id, new_summary)
                    user_context.long_term_summary = new_summary
                    logger.info(f"User memory updated for {user_id}: {fact[:60]}")
                    return ToolResult.success_result(
                        data="Hecho guardado en memoria del usuario.",
                        execution_time_ms=elapsed_ms,
                    )
                return ToolResult.error_result("Memory service not available for user scope")

        except Exception as e:
            logger.error(f"Error saving memory: {e}")
            return ToolResult.error_result(f"Error saving memory: {e}")
