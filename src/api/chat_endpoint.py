"""
Endpoint REST para chat con autenticación por token encriptado.

Este endpoint actúa como middleware para implementar el chat en otras plataformas.
"""
import asyncio
import logging
from datetime import datetime

from flask import Flask, request, jsonify
from flask_cors import CORS

from src.bot.middleware.token_middleware import TokenMiddleware
from src.config.settings import settings
from src.gateway.factory import get_handler_manager

logger = logging.getLogger(__name__)

# Crear app Flask
app = Flask(__name__)
CORS(app)  # Habilitar CORS para permitir requests desde otras plataformas


@app.route('/api/chat', methods=['POST'])
def chat():
    """
    Endpoint de chat con autenticación por token.

    Request Body:
        {
            "token": "base64_encrypted_token",
            "message": "mensaje del usuario"
        }

    Token (encriptado) debe contener:
        {
            "numero_empleado": 12345,
            "timestamp": "2025-12-23T10:30:00"
        }

    Response (Success):
        {
            "success": true,
            "response": "respuesta del bot",
            "numero_empleado": 12345,
            "timestamp": "2025-12-23T10:33:15"
        }

    Response (Error):
        {
            "success": false,
            "error": "mensaje de error",
            "error_code": "INVALID_TOKEN" | "EXPIRED_TOKEN" | "MISSING_FIELDS" | "INTERNAL_ERROR"
        }

    Status Codes:
        200: Success
        401: Unauthorized (token inválido/expirado)
        400: Bad Request (campos faltantes)
        500: Internal Server Error
    """
    try:
        # 1. Validar que el request tenga JSON
        if not request.is_json:
            return jsonify({
                "success": False,
                "error": "Content-Type debe ser application/json",
                "error_code": "INVALID_CONTENT_TYPE"
            }), 400

        data = request.get_json()

        # 2. Validar campos requeridos
        if "token" not in data:
            return jsonify({
                "success": False,
                "error": "Falta campo 'token'",
                "error_code": "MISSING_FIELD"
            }), 400

        if "message" not in data:
            return jsonify({
                "success": False,
                "error": "Falta campo 'message'",
                "error_code": "MISSING_FIELD"
            }), 400

        token = data["token"]
        message = data["message"]

        # Validar que message no esté vacío
        if not message or not message.strip():
            return jsonify({
                "success": False,
                "error": "El mensaje no puede estar vacío",
                "error_code": "EMPTY_MESSAGE"
            }), 400

        # 3. Validar token
        valido, datos_token, error_token = TokenMiddleware.validar_token(token)

        if not valido:
            logger.warning(f"Token inválido: {error_token}")

            # Determinar código de error
            error_code = "INVALID_TOKEN"
            if error_token and "expirado" in error_token.lower():
                error_code = "EXPIRED_TOKEN"

            return jsonify({
                "success": False,
                "error": error_token,
                "error_code": error_code
            }), 401

        # 4. Extraer número de empleado
        numero_empleado = datos_token["numero_empleado"]

        logger.info(f"Chat request de empleado {numero_empleado}: {message[:50]}...")

        # 5. Procesar mensaje con MainHandler
        handler = get_handler_manager().handler

        try:
            agent_response = asyncio.run(
                handler.handle_api(
                    user_id=str(numero_empleado),
                    text=message,
                    metadata={"source": "api", "empleado": numero_empleado},
                )
            )
            respuesta = agent_response.message if agent_response.success else agent_response.error
        except Exception as e:
            logger.error(f"Error procesando consulta: {e}", exc_info=True)
            return jsonify({
                "success": False,
                "error": "Error interno procesando el mensaje",
                "error_code": "PROCESSING_ERROR"
            }), 500

        # 6. Retornar respuesta
        return jsonify({
            "success": True,
            "response": respuesta,
            "numero_empleado": numero_empleado,
            "timestamp": datetime.now().isoformat()
        }), 200

    except Exception as e:
        logger.error(f"Error inesperado en endpoint /api/chat: {e}", exc_info=True)
        return jsonify({
            "success": False,
            "error": "Error interno del servidor",
            "error_code": "INTERNAL_ERROR"
        }), 500


@app.route('/api/chat/validate-token', methods=['POST'])
def validate_token():
    """
    Endpoint para validar token sin enviar mensaje.

    Útil para verificar si un token es válido antes de enviar mensajes.

    Request Body:
        {
            "token": "base64_encrypted_token"
        }

    Response (Success):
        {
            "success": true,
            "valid": true,
            "numero_empleado": 12345,
            "timestamp_token": "2025-12-23T10:30:00",
            "edad_segundos": 45
        }

    Response (Error):
        {
            "success": true,
            "valid": false,
            "error": "mensaje de error"
        }
    """
    try:
        if not request.is_json:
            return jsonify({
                "success": False,
                "error": "Content-Type debe ser application/json"
            }), 400

        data = request.get_json()

        if "token" not in data:
            return jsonify({
                "success": False,
                "error": "Falta campo 'token'"
            }), 400

        token = data["token"]

        # Validar token
        valido, datos_token, error_token = TokenMiddleware.validar_token(token)

        if valido:
            # Calcular edad del token
            timestamp_token = datos_token["timestamp_parsed"]
            edad = (datetime.now() - timestamp_token).total_seconds()

            return jsonify({
                "success": True,
                "valid": True,
                "numero_empleado": datos_token["numero_empleado"],
                "timestamp_token": datos_token["timestamp"],
                "edad_segundos": int(edad)
            }), 200
        else:
            return jsonify({
                "success": True,
                "valid": False,
                "error": error_token
            }), 200

    except Exception as e:
        logger.error(f"Error en /api/chat/validate-token: {e}", exc_info=True)
        return jsonify({
            "success": False,
            "error": "Error interno del servidor"
        }), 500


@app.route('/api/chat/generate-token', methods=['POST'])
def generate_token():
    """
    Endpoint DESHABILITADO - La generación de tokens es responsabilidad de la plataforma.

    El token debe ser generado por la plataforma externa (C#) usando la clase Encrypt.
    Este endpoint existe solo para documentación y retorna error 501 (Not Implemented).

    ⚠️ IMPORTANTE: Los tokens deben generarse en la plataforma que integra el chat,
    NO en este API.

    Para testing local, usar: python scripts/generar_token.py <numero_empleado>
    """
    return jsonify({
        "success": False,
        "error": "Este endpoint está deshabilitado. Los tokens deben ser generados por la plataforma externa.",
        "error_code": "NOT_IMPLEMENTED",
        "help": "Para generar tokens: usar clase Encrypt en C# o scripts/generar_token.py para testing local"
    }), 501  # Not Implemented


@app.route('/api/health', methods=['GET'])
def health():
    """
    Health check endpoint.

    Response:
        {
            "status": "ok",
            "timestamp": "2025-12-23T10:30:00"
        }
    """
    return jsonify({
        "status": "ok",
        "timestamp": datetime.now().isoformat()
    }), 200


if __name__ == "__main__":
    # Configurar logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Inicializar handler antes de arrancar el servidor (evita race condition)
    from src.database.connection import DatabaseManager
    get_handler_manager().initialize(DatabaseManager())
    logger.info("HandlerManager inicializado correctamente")

    # Ejecutar servidor
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )
