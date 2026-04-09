"""
Tests para src/api/chat_endpoint.py

Cobertura:
- POST /api/chat: validación, autenticación, procesamiento
- POST /api/chat/validate-token: validar token sin mensaje
- POST /api/chat/generate-token: endpoint deshabilitado
- GET /api/health: health check
"""
import pytest
from unittest.mock import MagicMock, patch, AsyncMock

# Mockear dependencias pesadas antes de importar
import sys
sys.modules.setdefault("telegram", MagicMock())
sys.modules.setdefault("telegram.ext", MagicMock())

from src.api.chat_endpoint import app


@pytest.fixture
def client():
    """Flask test client."""
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


# ---------------------------------------------------------------------------
# GET /api/health
# ---------------------------------------------------------------------------

class TestHealthEndpoint:

    def test_health_ok(self, client):
        resp = client.get("/api/health")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["status"] == "ok"
        assert "timestamp" in data


# ---------------------------------------------------------------------------
# POST /api/chat/generate-token  (deshabilitado)
# ---------------------------------------------------------------------------

class TestGenerateTokenEndpoint:

    def test_generate_token_disabled(self, client):
        resp = client.post(
            "/api/chat/generate-token",
            json={"numero_empleado": 123},
            content_type="application/json",
        )
        assert resp.status_code == 501
        data = resp.get_json()
        assert data["success"] is False
        assert data["error_code"] == "NOT_IMPLEMENTED"


# ---------------------------------------------------------------------------
# POST /api/chat/validate-token
# ---------------------------------------------------------------------------

class TestValidateTokenEndpoint:

    def test_missing_content_type(self, client):
        resp = client.post("/api/chat/validate-token", data="raw")
        assert resp.status_code == 400

    def test_missing_token_field(self, client):
        resp = client.post(
            "/api/chat/validate-token",
            json={},
            content_type="application/json",
        )
        assert resp.status_code == 400
        data = resp.get_json()
        assert data["success"] is False

    def test_invalid_token_returns_valid_false(self, client):
        with patch(
            "src.api.chat_endpoint.TokenMiddleware.validar_token",
            return_value=(False, None, "Token inválido"),
        ):
            resp = client.post(
                "/api/chat/validate-token",
                json={"token": "bad-token"},
                content_type="application/json",
            )
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["success"] is True
        assert data["valid"] is False
        assert "error" in data

    def test_valid_token_returns_employee_info(self, client):
        from datetime import datetime
        mock_token_data = {
            "numero_empleado": 42,
            "timestamp": "2026-03-30T10:00:00",
            "timestamp_parsed": datetime(2026, 3, 30, 10, 0, 0),
        }
        with patch(
            "src.api.chat_endpoint.TokenMiddleware.validar_token",
            return_value=(True, mock_token_data, None),
        ):
            resp = client.post(
                "/api/chat/validate-token",
                json={"token": "good-token"},
                content_type="application/json",
            )
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["success"] is True
        assert data["valid"] is True
        assert data["numero_empleado"] == 42


# ---------------------------------------------------------------------------
# POST /api/chat
# ---------------------------------------------------------------------------

class TestChatEndpoint:

    def test_missing_content_type(self, client):
        resp = client.post("/api/chat", data="raw")
        assert resp.status_code == 400
        data = resp.get_json()
        assert data["error_code"] == "INVALID_CONTENT_TYPE"

    def test_missing_token_field(self, client):
        resp = client.post(
            "/api/chat",
            json={"message": "hola"},
            content_type="application/json",
        )
        assert resp.status_code == 400
        data = resp.get_json()
        assert data["error_code"] == "MISSING_FIELD"

    def test_missing_message_field(self, client):
        resp = client.post(
            "/api/chat",
            json={"token": "tok"},
            content_type="application/json",
        )
        assert resp.status_code == 400
        data = resp.get_json()
        assert data["error_code"] == "MISSING_FIELD"

    def test_empty_message(self, client):
        with patch(
            "src.api.chat_endpoint.TokenMiddleware.validar_token",
            return_value=(True, {"numero_empleado": 1}, None),
        ):
            resp = client.post(
                "/api/chat",
                json={"token": "tok", "message": "   "},
                content_type="application/json",
            )
        assert resp.status_code == 400
        data = resp.get_json()
        assert data["error_code"] == "EMPTY_MESSAGE"

    def test_invalid_token(self, client):
        with patch(
            "src.api.chat_endpoint.TokenMiddleware.validar_token",
            return_value=(False, None, "Token expirado"),
        ):
            resp = client.post(
                "/api/chat",
                json={"token": "bad", "message": "hola"},
                content_type="application/json",
            )
        assert resp.status_code == 401
        data = resp.get_json()
        assert data["success"] is False
        assert data["error_code"] == "EXPIRED_TOKEN"

    def test_invalid_token_generic_code(self, client):
        with patch(
            "src.api.chat_endpoint.TokenMiddleware.validar_token",
            return_value=(False, None, "Token inválido"),
        ):
            resp = client.post(
                "/api/chat",
                json={"token": "bad", "message": "hola"},
                content_type="application/json",
            )
        assert resp.status_code == 401
        assert resp.get_json()["error_code"] == "INVALID_TOKEN"

    def test_successful_chat(self, client):
        mock_response = MagicMock()
        mock_response.success = True
        mock_response.message = "Respuesta del bot"

        mock_handler = MagicMock()
        mock_handler.handle_api = AsyncMock(return_value=mock_response)

        mock_manager = MagicMock()
        mock_manager.handler = mock_handler

        with patch(
            "src.api.chat_endpoint.TokenMiddleware.validar_token",
            return_value=(True, {"numero_empleado": 99}, None),
        ), patch(
            "src.api.chat_endpoint.get_handler_manager",
            return_value=mock_manager,
        ):
            resp = client.post(
                "/api/chat",
                json={"token": "valid", "message": "¿Cuántas ventas hubo hoy?"},
                content_type="application/json",
            )

        assert resp.status_code == 200
        data = resp.get_json()
        assert data["success"] is True
        assert data["response"] == "Respuesta del bot"
        assert data["numero_empleado"] == 99

    def test_agent_error_returns_500(self, client):
        mock_handler = MagicMock()
        mock_handler.handle_api = AsyncMock(side_effect=RuntimeError("fallo"))

        mock_manager = MagicMock()
        mock_manager.handler = mock_handler

        with patch(
            "src.api.chat_endpoint.TokenMiddleware.validar_token",
            return_value=(True, {"numero_empleado": 1}, None),
        ), patch(
            "src.api.chat_endpoint.get_handler_manager",
            return_value=mock_manager,
        ):
            resp = client.post(
                "/api/chat",
                json={"token": "valid", "message": "consulta"},
                content_type="application/json",
            )

        assert resp.status_code == 500
        assert resp.get_json()["error_code"] == "PROCESSING_ERROR"

    def test_agent_failed_response(self, client):
        """Cuando agent.success=False, la respuesta usa agent.error."""
        mock_response = MagicMock()
        mock_response.success = False
        mock_response.error = "No tengo esa información"

        mock_handler = MagicMock()
        mock_handler.handle_api = AsyncMock(return_value=mock_response)

        mock_manager = MagicMock()
        mock_manager.handler = mock_handler

        with patch(
            "src.api.chat_endpoint.TokenMiddleware.validar_token",
            return_value=(True, {"numero_empleado": 5}, None),
        ), patch(
            "src.api.chat_endpoint.get_handler_manager",
            return_value=mock_manager,
        ):
            resp = client.post(
                "/api/chat",
                json={"token": "valid", "message": "algo"},
                content_type="application/json",
            )

        assert resp.status_code == 200
        assert resp.get_json()["response"] == "No tengo esa información"
