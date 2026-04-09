"""
Tests para AuthMiddleware — verificación de comandos públicos.

Cobertura:
- Comandos públicos registrados en PUBLIC_COMMANDS
- Extracción de comando desde texto del mensaje
- /recargar_permisos es público (cualquier usuario autenticado puede usarlo)
"""

import pytest
from unittest.mock import MagicMock

from src.bot.middleware.auth_middleware import AuthMiddleware


def _extract_command(message_text: str) -> str | None:
    """Replica la lógica de extracción de comando del middleware."""
    if not message_text.startswith("/"):
        return None
    return message_text.split()[0].split("@")[0].lower()


class TestPublicCommandDetection:
    """Tests para la lógica de detección de comandos públicos."""

    @pytest.fixture
    def middleware(self):
        db_manager = MagicMock()
        return AuthMiddleware(db_manager)

    # --- Comandos públicos en lista ---

    def test_start_es_publico(self, middleware):
        assert "/start" in middleware.PUBLIC_COMMANDS

    def test_help_es_publico(self, middleware):
        assert "/help" in middleware.PUBLIC_COMMANDS

    def test_register_es_publico(self, middleware):
        assert "/register" in middleware.PUBLIC_COMMANDS

    def test_verify_es_publico(self, middleware):
        assert "/verify" in middleware.PUBLIC_COMMANDS

    def test_recargar_permisos_es_publico(self, middleware):
        """/recargar_permisos debe ser público — cualquier usuario puede recargarlo."""
        assert "/recargar_permisos" in middleware.PUBLIC_COMMANDS

    # --- Extracción de comando y detección ---

    def test_extract_command_exacto(self):
        assert _extract_command("/start") == "/start"

    def test_extract_command_con_argumento(self):
        assert _extract_command("/verify 123456") == "/verify"

    def test_extract_command_con_bot_username(self):
        assert _extract_command("/start@IrisBot") == "/start"

    def test_extract_command_texto_libre_returns_none(self):
        assert _extract_command("hola cómo estás") is None

    def test_extract_command_vacio_returns_none(self):
        assert _extract_command("") is None

    def test_comando_publico_detectado_correctamente(self, middleware):
        """/recargar_permisos con argumento debe ser público."""
        cmd = _extract_command("/recargar_permisos")
        assert cmd in middleware.PUBLIC_COMMANDS

    def test_comando_privado_no_publico(self, middleware):
        """/ia no debe estar en PUBLIC_COMMANDS."""
        cmd = _extract_command("/ia consulta")
        assert cmd not in middleware.PUBLIC_COMMANDS

    def test_comando_desconocido_no_publico(self, middleware):
        cmd = _extract_command("/admin secreto")
        assert cmd not in middleware.PUBLIC_COMMANDS

    # --- Texto libre → no es comando →  no es público ---

    def test_texto_libre_no_es_comando(self):
        assert _extract_command("¿cuántas ventas tuve este mes?") is None

    def test_substring_no_confunde(self):
        """Texto que contiene '/start' en medio no extrae comando."""
        assert _extract_command("hacer restart del bot") is None
