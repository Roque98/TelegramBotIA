from functools import wraps
from typing import Callable

from flask import g, jsonify, request

from src.bot.middleware.token_middleware import TokenMiddleware


def require_json(f: Callable) -> Callable:
    @wraps(f)
    def decorated(*args, **kwargs):
        if not request.is_json:
            return jsonify({
                "success": False,
                "error": "Content-Type debe ser application/json",
                "error_code": "INVALID_CONTENT_TYPE",
            }), 400
        return f(*args, **kwargs)
    return decorated


def require_token(f: Callable) -> Callable:
    """Valida el token y expone los datos decodificados en flask.g.token_data."""
    @wraps(f)
    def decorated(*args, **kwargs):
        data = request.get_json()
        if "token" not in data:
            return jsonify({
                "success": False,
                "error": "Falta campo 'token'",
                "error_code": "MISSING_FIELD",
            }), 400

        valido, datos_token, error_token = TokenMiddleware.validar_token(data["token"])
        if not valido:
            error_code = "EXPIRED_TOKEN" if error_token and "expirado" in error_token.lower() else "INVALID_TOKEN"
            return jsonify({
                "success": False,
                "error": error_token,
                "error_code": error_code,
            }), 401

        g.token_data = datos_token
        return f(*args, **kwargs)
    return decorated
