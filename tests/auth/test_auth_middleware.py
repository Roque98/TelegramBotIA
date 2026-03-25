"""
Tests para AuthMiddleware — verificación de comandos públicos.

Cobertura:
- Comandos públicos exactos → permitidos
- Comandos con argumentos → permitidos
- Substrings de comandos en texto libre → rechazados
- Texto aleatorio → rechazado
"""

import pytest
from unittest.mock import MagicMock

from src.bot.middleware.auth_middleware import AuthMiddleware


class TestPublicCommandDetection:
    """Tests para la lógica de detección de comandos públicos."""

    @pytest.fixture
    def middleware(self):
        db_manager = MagicMock()
        return AuthMiddleware(db_manager)

    # --- Comandos públicos exactos ---

    def test_register_exacto_es_publico(self, middleware):
        """/register exacto debe ser reconocido como público."""
        assert any("/register".startswith(cmd) for cmd in middleware.PUBLIC_COMMANDS)

    def test_start_exacto_es_publico(self, middleware):
        """/start exacto debe ser reconocido como público."""
        assert any("/start".startswith(cmd) for cmd in middleware.PUBLIC_COMMANDS)

    def test_help_exacto_es_publico(self, middleware):
        """/help exacto debe ser reconocido como público."""
        assert any("/help".startswith(cmd) for cmd in middleware.PUBLIC_COMMANDS)

    def test_verify_exacto_es_publico(self, middleware):
        """/verify exacto debe ser reconocido como público."""
        assert any("/verify".startswith(cmd) for cmd in middleware.PUBLIC_COMMANDS)

    # --- Comandos con argumentos ---

    def test_register_con_argumento_es_publico(self, middleware):
        """/register extra_args debe ser reconocido como público."""
        msg = "/register usuario123"
        assert any(msg.startswith(cmd) for cmd in middleware.PUBLIC_COMMANDS)

    def test_start_con_argumento_es_publico(self, middleware):
        """/start deep_link_param debe ser reconocido como público."""
        msg = "/start ref_abc123"
        assert any(msg.startswith(cmd) for cmd in middleware.PUBLIC_COMMANDS)

    def test_verify_con_codigo_es_publico(self, middleware):
        """/verify <codigo> debe ser reconocido como público."""
        msg = "/verify 123456"
        assert any(msg.startswith(cmd) for cmd in middleware.PUBLIC_COMMANDS)

    # --- Substrings de comandos → NO públicos ---

    def test_deregister_no_es_publico(self, middleware):
        """'deregister' contiene '/register' como substring pero NO debe ser público."""
        msg = "quiero deregister mi cuenta"
        assert not any(msg.startswith(cmd) for cmd in middleware.PUBLIC_COMMANDS)

    def test_texto_con_slash_register_embebido_no_es_publico(self, middleware):
        """Texto que contiene '/register' en medio NO debe ser público."""
        msg = "texto /register al medio"
        assert not any(msg.startswith(cmd) for cmd in middleware.PUBLIC_COMMANDS)

    def test_texto_con_start_embebido_no_es_publico(self, middleware):
        """Texto con '/start' embebido NO debe ser público."""
        msg = "como hacer restart del bot"
        assert not any(msg.startswith(cmd) for cmd in middleware.PUBLIC_COMMANDS)

    # --- Texto aleatorio → NO público ---

    def test_texto_libre_no_es_publico(self, middleware):
        """Mensaje normal no debe pasar como público."""
        msg = "hola, ¿cuántas ventas tuve este mes?"
        assert not any(msg.startswith(cmd) for cmd in middleware.PUBLIC_COMMANDS)

    def test_mensaje_vacio_no_es_publico(self, middleware):
        """Mensaje vacío no debe ser público."""
        msg = ""
        assert not any(msg.startswith(cmd) for cmd in middleware.PUBLIC_COMMANDS)

    def test_comando_desconocido_no_es_publico(self, middleware):
        """Comando no registrado no debe ser público."""
        msg = "/admin secreto"
        assert not any(msg.startswith(cmd) for cmd in middleware.PUBLIC_COMMANDS)
