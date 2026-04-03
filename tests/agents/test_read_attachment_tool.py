"""
Tests para ReadAttachmentTool — Fase 7: soporte de archivos adjuntos.

Cobertura:
- Búsqueda de metadatos en session_notes
- Descarga exitosa → retorna contenido de texto
- Archivo no encontrado → error descriptivo
- Contenido binario → retorna metadatos sin content
- Truncado de contenido largo
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from src.agents.tools.read_attachment_tool import ReadAttachmentTool, _MAX_CONTENT_CHARS


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

FILE_ID = "BQACAgIAAx"


def _make_context(session_notes: list[str]) -> MagicMock:
    ctx = MagicMock()
    ctx.session_notes = session_notes
    return ctx


def _note(file_id=FILE_ID, name="report.pdf", size="42KB", path="docs/report.pdf") -> str:
    return f"[ATTACHMENT:{file_id}] name={name} size={size} path={path}"


# ---------------------------------------------------------------------------
# _find_attachment
# ---------------------------------------------------------------------------

class TestFindAttachment:

    def test_encuentra_adjunto_existente(self):
        tool = ReadAttachmentTool(bot_token="tok")
        notes = [_note()]
        result = tool._find_attachment(FILE_ID, notes)
        assert result is not None
        assert result["name"] == "report.pdf"
        assert result["path"] == "docs/report.pdf"

    def test_retorna_none_si_no_existe(self):
        tool = ReadAttachmentTool(bot_token="tok")
        result = tool._find_attachment("otro_id", [_note()])
        assert result is None

    def test_retorna_none_si_notes_vacio(self):
        tool = ReadAttachmentTool(bot_token="tok")
        assert tool._find_attachment(FILE_ID, []) is None


# ---------------------------------------------------------------------------
# execute() — casos de error
# ---------------------------------------------------------------------------

class TestExecuteErrors:

    @pytest.mark.asyncio
    async def test_sin_file_id_retorna_error(self):
        tool = ReadAttachmentTool(bot_token="tok")
        result = await tool.execute(file_id="")
        assert result.success is False
        assert "file_id" in result.error.lower()

    @pytest.mark.asyncio
    async def test_sin_user_context_retorna_error(self):
        tool = ReadAttachmentTool(bot_token="tok")
        result = await tool.execute(file_id=FILE_ID, user_context=None)
        assert result.success is False
        assert "contexto" in result.error.lower() or "sesión" in result.error.lower()

    @pytest.mark.asyncio
    async def test_adjunto_no_en_session_retorna_error(self):
        tool = ReadAttachmentTool(bot_token="tok")
        ctx = _make_context([])
        result = await tool.execute(file_id=FILE_ID, user_context=ctx)
        assert result.success is False
        assert "no encontrado" in result.error.lower() or "no hay archivos" in result.error.lower()

    @pytest.mark.asyncio
    async def test_error_descarga_retorna_error(self):
        tool = ReadAttachmentTool(bot_token="tok")
        ctx = _make_context([_note()])

        with patch.object(tool, "_download_sync", side_effect=Exception("timeout")):
            result = await tool.execute(file_id=FILE_ID, user_context=ctx)

        assert result.success is False
        assert "descargar" in result.error.lower() or "timeout" in result.error.lower()


# ---------------------------------------------------------------------------
# execute() — casos exitosos
# ---------------------------------------------------------------------------

class TestExecuteSuccess:

    @pytest.mark.asyncio
    async def test_retorna_contenido_de_texto(self):
        tool = ReadAttachmentTool(bot_token="tok")
        ctx = _make_context([_note()])
        texto = "Contenido del reporte\nLínea 2"

        with patch.object(tool, "_download_sync", return_value=texto.encode("utf-8")):
            result = await tool.execute(file_id=FILE_ID, user_context=ctx)

        assert result.success is True
        assert result.data["content"] == texto
        assert result.data["name"] == "report.pdf"

    @pytest.mark.asyncio
    async def test_trunca_contenido_largo(self):
        tool = ReadAttachmentTool(bot_token="tok")
        ctx = _make_context([_note()])
        largo = "x" * (_MAX_CONTENT_CHARS + 500)

        with patch.object(tool, "_download_sync", return_value=largo.encode("utf-8")):
            result = await tool.execute(file_id=FILE_ID, user_context=ctx)

        assert result.success is True
        assert len(result.data["content"]) <= _MAX_CONTENT_CHARS + 50  # margen por el mensaje de truncado
        assert "truncado" in result.data["content"]

    @pytest.mark.asyncio
    async def test_archivo_binario_retorna_metadatos(self):
        tool = ReadAttachmentTool(bot_token="tok")
        ctx = _make_context([_note(name="imagen.png")])
        # Bytes con muchos nulos → binario
        binary = bytes([0x89, 0x50, 0x4E, 0x47, 0x00, 0x00, 0x00, 0x00] * 100)

        with patch.object(tool, "_download_sync", return_value=binary):
            result = await tool.execute(file_id=FILE_ID, user_context=ctx)

        assert result.success is True
        assert result.data["content"] is None
        assert "binario" in result.data["note"].lower()


# ---------------------------------------------------------------------------
# _decode()
# ---------------------------------------------------------------------------

class TestDecode:

    def test_decodifica_utf8(self):
        tool = ReadAttachmentTool(bot_token="tok")
        assert tool._decode("hola mundo".encode("utf-8")) == "hola mundo"

    def test_decodifica_latin1(self):
        tool = ReadAttachmentTool(bot_token="tok")
        result = tool._decode("café".encode("latin-1"))
        assert result is not None

    def test_retorna_none_para_binario_con_nulos(self):
        tool = ReadAttachmentTool(bot_token="tok")
        binary = bytes([0x00] * 50 + [0x41] * 50)  # 50% nulos → binario
        assert tool._decode(binary) is None
