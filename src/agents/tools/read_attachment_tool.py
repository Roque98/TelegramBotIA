"""
ReadAttachmentTool — Herramienta para leer archivos adjuntos enviados por el usuario.

El handler de documentos de Telegram almacena los metadatos del archivo en
`user_context.session_notes` con el formato:
    [ATTACHMENT:{file_id}] name=archivo.pdf size=42KB path=documents/xxx.pdf

Esta tool recupera esos metadatos, descarga el contenido desde la API de Telegram
y lo retorna al agente como texto (truncado a 3000 chars si es necesario).
"""

import asyncio
import logging
from typing import Any, Optional
from urllib.request import urlopen

from .base import BaseTool, ToolCategory, ToolDefinition, ToolParameter, ToolResult

logger = logging.getLogger(__name__)

_MAX_DOWNLOAD_BYTES = 5 * 1024 * 1024   # 5 MB
_MAX_CONTENT_CHARS = 3_000              # Límite para el contexto del agente


class ReadAttachmentTool(BaseTool):
    """
    Lee el contenido de un archivo adjunto enviado por el usuario en Telegram.

    Requiere que el archivo haya sido previamente registrado en session_notes
    por el handler de documentos. Descarga el contenido desde la API de Telegram
    usando el bot token configurado.

    Example:
        >>> tool = ReadAttachmentTool(bot_token="123:ABC...")
        >>> result = await tool.execute(file_id="BQACAgIAAxkB...", user_context=ctx)
        >>> print(result.to_observation())
    """

    name = "read_attachment"
    definition = ToolDefinition(
        name="read_attachment",
        description=(
            "Lee el contenido de un archivo adjunto que el usuario envió en este chat. "
            "Úsala cuando el usuario haya enviado un documento y quiera que lo analices o leas. "
            "Retorna el texto del archivo (o metadatos si es binario)."
        ),
        category=ToolCategory.UTILITY,
        parameters=[
            ToolParameter(
                name="file_id",
                param_type="string",
                description="ID del archivo adjunto (visible en el contexto de sesión)",
                required=True,
            )
        ],
        returns="Contenido de texto del archivo, o descripción de sus metadatos si es binario.",
        examples=[{"file_id": "BQACAgIAAxkBAAIBd2..."}],
        usage_hint="Para leer o analizar archivos adjuntos que el usuario envió en el chat: usa `read_attachment`",
    )

    def __init__(self, bot_token: str) -> None:
        self._bot_token = bot_token

    async def execute(
        self,
        file_id: str = "",
        user_context: Optional[Any] = None,
        **kwargs: Any,
    ) -> ToolResult:
        """
        Descarga y retorna el contenido del archivo adjunto.

        Args:
            file_id: ID del archivo en Telegram
            user_context: Contexto del usuario con session_notes
            **kwargs: Parámetros adicionales ignorados

        Returns:
            ToolResult con el contenido del archivo o error descriptivo
        """
        if not file_id:
            return ToolResult.error_result("Se requiere el parámetro file_id")

        if not user_context or not getattr(user_context, "session_notes", None):
            return ToolResult.error_result(
                f"No hay archivos adjuntos en la sesión actual. "
                f"Asegúrate de haber enviado el archivo en este chat."
            )

        # Buscar metadatos en session_notes
        attachment = self._find_attachment(file_id, user_context.session_notes)
        if not attachment:
            return ToolResult.error_result(
                f"Archivo con ID '{file_id}' no encontrado en esta sesión. "
                f"Por favor envía el archivo nuevamente."
            )

        file_path = attachment.get("path")
        name = attachment.get("name", "archivo")

        if not file_path:
            return ToolResult.error_result(f"Ruta del archivo '{name}' no disponible.")

        url = f"https://api.telegram.org/file/bot{self._bot_token}/{file_path}"

        try:
            content_bytes = await asyncio.to_thread(self._download_sync, url)
        except Exception as e:
            logger.warning(f"ReadAttachmentTool: error descargando {name}: {e}")
            return ToolResult.error_result(f"No se pudo descargar el archivo '{name}': {e}")

        # Intentar decodificar como texto
        text_content = self._decode(content_bytes)
        if text_content is None:
            size_kb = attachment.get("size", "?")
            return ToolResult.success_result(
                data={
                    "name": name,
                    "file_id": file_id,
                    "size": f"{size_kb}KB",
                    "content": None,
                    "note": "Archivo binario — no se puede mostrar el contenido como texto.",
                }
            )

        if len(text_content) > _MAX_CONTENT_CHARS:
            text_content = text_content[:_MAX_CONTENT_CHARS] + "\n\n[... contenido truncado ...]"

        logger.info(f"ReadAttachmentTool: leído '{name}' ({len(text_content)} chars)")
        return ToolResult.success_result(
            data={"name": name, "file_id": file_id, "content": text_content}
        )

    # ------------------------------------------------------------------
    # Helpers internos
    # ------------------------------------------------------------------

    def _find_attachment(self, file_id: str, session_notes: list[str]) -> Optional[dict]:
        """
        Busca los metadatos del adjunto en session_notes.

        Formato de la nota: [ATTACHMENT:{file_id}] name=X size=YKB path=Z
        """
        prefix = f"[ATTACHMENT:{file_id}]"
        for note in session_notes:
            if note.startswith(prefix):
                rest = note[len(prefix):].strip()
                parts = {}
                for token in rest.split():
                    if "=" in token:
                        k, _, v = token.partition("=")
                        parts[k] = v
                return parts
        return None

    def _download_sync(self, url: str) -> bytes:
        """Descarga síncrona envuelta en asyncio.to_thread."""
        with urlopen(url, timeout=15) as resp:
            return resp.read(_MAX_DOWNLOAD_BYTES)

    def _decode(self, data: bytes) -> Optional[str]:
        """Intenta decodificar bytes como texto. Retorna None si es binario."""
        # Heurística previa: si contiene demasiados bytes nulos es binario
        null_ratio = data.count(0) / max(len(data), 1)
        if null_ratio > 0.01:
            return None
        try:
            return data.decode("utf-8")
        except UnicodeDecodeError:
            pass
        return data.decode("latin-1", errors="replace")
