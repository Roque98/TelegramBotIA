"""
Endpoint REST para chat con autenticación por token encriptado.

Este endpoint actúa como middleware para implementar el chat en otras plataformas.
"""
import asyncio
import logging
from datetime import datetime

from flask import Flask, request, jsonify
from flask_cors import CORS

from src.api.dashboard_api import dashboard_bp
from src.bot.middleware.token_middleware import TokenMiddleware
from src.config.settings import settings
from src.pipeline.handler_manager import get_handler_manager

logger = logging.getLogger(__name__)

# Crear app Flask
app = Flask(__name__)
CORS(app)
app.register_blueprint(dashboard_bp)


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
            metadata = {
                "source": "api",
                "empleado": numero_empleado,
                "id_gerencias": datos_token.get("idGerencias", []),
                "id_consola": datos_token.get("idConsola"),
            }
            agent_response = asyncio.run(
                handler.handle_api(
                    user_id=str(numero_empleado),
                    text=message,
                    metadata=metadata,
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


@app.route('/api/tickets', methods=['POST'])
def tickets():
    """
    Consulta tickets históricos de un equipo/IP directamente, sin pasar por el agente.

    Request Body:
        {
            "token": "base64_encrypted_token",
            "ip": "10.118.57.142",
            "sensor": "Memoria"          (opcional)
        }

    Response (Success):
        {
            "success": true,
            "ip": "10.118.57.142",
            "sensor": "Memoria",
            "total_tickets": 3,
            "resultado": "3 ticket(s) histórico(s)...",
            "timestamp": "..."
        }
    """
    try:
        if not request.is_json:
            return jsonify({"success": False, "error": "Content-Type debe ser application/json", "error_code": "INVALID_CONTENT_TYPE"}), 400

        data = request.get_json()

        if "token" not in data:
            return jsonify({"success": False, "error": "Falta campo 'token'", "error_code": "MISSING_FIELD"}), 400
        if "ip" not in data or not data["ip"].strip():
            return jsonify({"success": False, "error": "Falta campo 'ip'", "error_code": "MISSING_FIELD"}), 400

        valido, datos_token, error_token = TokenMiddleware.validar_token(data["token"])
        if not valido:
            error_code = "EXPIRED_TOKEN" if error_token and "expirado" in error_token.lower() else "INVALID_TOKEN"
            return jsonify({"success": False, "error": error_token, "error_code": error_code}), 401

        numero_empleado: int = datos_token["numero_empleado"]
        ip: str = data["ip"].strip()
        sensor: str = data.get("sensor", "").strip()

        db_registry = get_handler_manager().db_registry
        if db_registry is None:
            return jsonify({"success": False, "error": "Servicio no inicializado", "error_code": "NOT_READY"}), 503

        from src.domain.alerts.alert_repository import AlertRepository
        from src.agents.tools.get_historical_tickets_tool import GetHistoricalTicketsTool
        from src.agents.providers.openai_provider import OpenAIProvider
        from src.config.settings import settings

        import time, uuid
        from src.domain.interaction.interaction_repository import InteractionRepository

        async def _run():
            t0 = time.perf_counter()
            repo = AlertRepository(db_registry.get("monitoreo"))
            tool = GetHistoricalTicketsTool(repo=repo)
            tickets_result = await tool.execute(ip=ip, sensor=sensor)

            analisis_text = tickets_result.data or tickets_result.error
            total = (tickets_result.metadata or {}).get("total_tickets", 0)
            error_msg = None

            if tickets_result.success and tickets_result.data:
                llm = OpenAIProvider(api_key=settings.openai_api_key, model=settings.openai_data_model)
                messages = [
                    {"role": "system", "content": (
                        "Eres un analista de soporte técnico. Se te presentan tickets históricos de un equipo de red/infraestructura. "
                        "Analiza los patrones, identifica la causa raíz más probable y sugiere acciones correctivas concretas. "
                        "Sé conciso y estructurado."
                    )},
                    {"role": "user", "content": f"Analiza los siguientes tickets históricos del equipo {ip}:\n\n{tickets_result.data}"},
                ]
                analysis = await llm.generate_messages(messages=messages, max_tokens=1024)
                analisis_text = str(analysis)
            else:
                error_msg = tickets_result.error

            total_ms = int((time.perf_counter() - t0) * 1000)

            # Registrar en logs igual que /api/chat
            handler = get_handler_manager().handler
            if handler and handler.observability_repo:
                obs_repo: InteractionRepository = handler.observability_repo
                await obs_repo.save_interaction(
                    correlation_id=str(uuid.uuid4()),
                    user_id=str(numero_empleado),
                    username=None,
                    query=f"[tickets] ip={ip} sensor={sensor}",
                    respuesta=analisis_text if not error_msg else None,
                    channel="api",
                    memory_ms=0,
                    react_ms=total_ms,
                    save_ms=0,
                    total_ms=total_ms,
                    error_message=error_msg,
                    tools_used=["get_historical_tickets"],
                    steps_count=1,
                    agente_nombre="tickets_api",
                    id_usuario=numero_empleado,
                )

            return analisis_text, total

        analisis, total = asyncio.run(_run())

        return jsonify({
            "success": True,
            "ip": ip,
            "sensor": sensor,
            "total_tickets": total,
            "analisis": analisis,
            "timestamp": datetime.now().isoformat(),
        }), 200

    except Exception as e:
        logger.error(f"Error en /api/tickets: {e}", exc_info=True)
        return jsonify({"success": False, "error": "Error interno del servidor", "error_code": "INTERNAL_ERROR"}), 500


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
    from src.infra.database.connection import DatabaseManager
    get_handler_manager().initialize(DatabaseManager())
    logger.info("HandlerManager inicializado correctamente")

    # Ejecutar servidor
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )
