"""
Endpoint REST para chat con autenticación por token encriptado.
"""
import asyncio
import logging
import time
import uuid
from datetime import datetime

from flask import Flask, g, jsonify, request
from flask_cors import CORS

from src.api.dashboard_api import dashboard_bp
from src.api.decorators import require_json, require_token
from src.bot.middleware.token_middleware import TokenMiddleware
from src.pipeline.handler_manager import get_handler_manager

logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)
app.register_blueprint(dashboard_bp)


@app.route("/api/chat", methods=["POST"])
@require_json
@require_token
def chat():
    """
    Procesa un mensaje de chat autenticado por token.

    Request:  { "token": "...", "message": "..." }
    Response: { "success": true, "response": "...", "numero_empleado": 123, "timestamp": "..." }
    Errors:   400 MISSING_FIELD | 400 EMPTY_MESSAGE | 500 PROCESSING_ERROR
    """
    data = request.get_json()
    datos_token = g.token_data

    if "message" not in data:
        return jsonify({"success": False, "error": "Falta campo 'message'", "error_code": "MISSING_FIELD"}), 400
    message = data["message"].strip()
    if not message:
        return jsonify({"success": False, "error": "El mensaje no puede estar vacío", "error_code": "EMPTY_MESSAGE"}), 400

    numero_empleado: int = datos_token["numero_empleado"]
    logger.info(f"Chat request de empleado {numero_empleado}: {message[:50]}...")

    try:
        handler = get_handler_manager().handler
        agent_response = asyncio.run(
            handler.handle_api(
                user_id=str(numero_empleado),
                text=message,
                metadata={
                    "source": "api",
                    "empleado": numero_empleado,
                    "id_gerencias": datos_token.get("idGerencias", []),
                    "id_consola": datos_token.get("idConsola"),
                },
            )
        )
        respuesta = agent_response.message if agent_response.success else agent_response.error
    except Exception as e:
        logger.error(f"Error procesando consulta: {e}", exc_info=True)
        return jsonify({"success": False, "error": "Error interno procesando el mensaje", "error_code": "PROCESSING_ERROR"}), 500

    return jsonify({
        "success": True,
        "response": respuesta,
        "numero_empleado": numero_empleado,
        "timestamp": datetime.now().isoformat(),
    }), 200


@app.route("/api/chat/validate-token", methods=["POST"])
@require_json
def validate_token():
    """
    Valida un token sin enviar mensaje. Siempre responde 200.

    Request:  { "token": "..." }
    Response: { "success": true, "valid": bool, "numero_empleado"?: int, "error"?: str }
    """
    data = request.get_json()
    if "token" not in data:
        return jsonify({"success": False, "error": "Falta campo 'token'"}), 400

    valido, datos_token, error_token = TokenMiddleware.validar_token(data["token"])
    if not valido:
        return jsonify({"success": True, "valid": False, "error": error_token}), 200

    edad = (datetime.now() - datos_token["timestamp_parsed"]).total_seconds()
    return jsonify({
        "success": True,
        "valid": True,
        "numero_empleado": datos_token["numero_empleado"],
        "timestamp_token": datos_token["timestamp"],
        "edad_segundos": int(edad),
    }), 200


@app.route("/api/chat/generate-token", methods=["POST"])
def generate_token():
    """Deshabilitado — los tokens deben generarse en la plataforma externa (C#)."""
    return jsonify({
        "success": False,
        "error": "Este endpoint está deshabilitado. Los tokens deben ser generados por la plataforma externa.",
        "error_code": "NOT_IMPLEMENTED",
        "help": "Para generar tokens: usar clase Encrypt en C# o scripts/generar_token.py para testing local",
    }), 501


@app.route("/api/tickets", methods=["POST"])
@require_json
@require_token
def tickets():
    """
    Consulta tickets históricos de un equipo/IP con análisis de causa raíz por LLM.

    Request:  { "token": "...", "ip": "10.x.x.x", "sensor": "Memoria" (opcional), "mensaje_alerta": "..." (opcional) }
    Response: { "success": true, "ip": "...", "sensor": "...", "total_tickets": N, "analisis": "...", "timestamp": "..." }
    Errors:   400 MISSING_FIELD | 503 NOT_READY
    """
    data = request.get_json()
    datos_token = g.token_data

    if "ip" not in data or not data["ip"].strip():
        return jsonify({"success": False, "error": "Falta campo 'ip'", "error_code": "MISSING_FIELD"}), 400

    numero_empleado: int = datos_token["numero_empleado"]
    ip: str = data["ip"].strip()
    sensor: str = data.get("sensor", "").strip()
    mensaje_alerta: str = data.get("mensaje_alerta", data.get("mensaje", "")).strip()
    dynatrace_host: dict = data.get("dynatraceHost") or {}
    servicios: list = data.get("servicios") or []
    eventos_dynatrace: list = data.get("eventosDynatrace") or []

    db_registry = get_handler_manager().db_registry
    if db_registry is None:
        return jsonify({"success": False, "error": "Servicio no inicializado", "error_code": "NOT_READY"}), 503

    from src.agents.providers.openai_provider import OpenAIProvider
    from src.agents.tools.get_historical_tickets_tool import GetHistoricalTicketsTool
    from src.config.settings import settings
    from src.domain.alerts.alert_repository import AlertRepository
    from src.domain.alerts.ticket_cache_repository import TicketAnalysisCacheRepository
    from src.domain.interaction.interaction_repository import InteractionRepository
    from src.infra.database.connection import DatabaseManager

    tiene_datos_dynatrace = bool(dynatrace_host or servicios or eventos_dynatrace)

    def _build_dynatrace_context() -> str:
        parts = []
        if dynatrace_host:
            tags_str = ", ".join(
                f"{t['key']}={t['value']}" for t in dynatrace_host.get("tags", []) if isinstance(t, dict)
            )
            zones_str = ", ".join(dynatrace_host.get("managementZones", []))
            lines = [
                "\nDatos Dynatrace del host:",
                f"- Nombre: {dynatrace_host.get('displayName', 'N/D')}",
                f"- SO: {dynatrace_host.get('os', 'N/D')}",
                f"- Modo de monitoreo: {dynatrace_host.get('monitoringMode', 'N/D')}",
                f"- OneAgent: {dynatrace_host.get('oneAgentVersion', 'N/D')}",
                f"- Network Zone: {dynatrace_host.get('networkZone', 'N/D')}",
                f"- Estado: {dynatrace_host.get('state', 'N/D')}",
                f"- Zonas de gestión: {zones_str or 'N/D'}",
            ]
            if tags_str:
                lines.append(f"- Tags: {tags_str}")
            parts.append("\n".join(lines))
        if servicios:
            lines = ["\nServicios detectados en el host:"]
            for s in servicios:
                db = s.get("baseDatos") or "N/D"
                lines.append(f"- {s.get('nombre', '?')} ({s.get('tipo', '?')}) — {s.get('tecnologia', '?')} — BD: {db}")
            parts.append("\n".join(lines))
        if eventos_dynatrace:
            lines = ["\nEventos recientes en Dynatrace:"]
            for e in eventos_dynatrace:
                lines.append(f"- [{e.get('tipo', '?')}] {e.get('titulo', '?')} (hace {e.get('hace', '?')})")
            parts.append("\n".join(lines))
        return "\n".join(parts)

    async def _run():
        t0 = time.perf_counter()
        repo = AlertRepository(db_registry.get("monitoreo"))
        tool = GetHistoricalTicketsTool(repo=repo)
        tickets_result = await tool.execute(ip=ip, sensor=sensor)

        analisis_text = tickets_result.data or tickets_result.error
        total = (tickets_result.metadata or {}).get("total_tickets", 0)
        error_msg = None

        if tickets_result.success and tickets_result.data:
            sensor_info = f" (sensor: {sensor})" if sensor else ""

            # Extraer última acción correctiva para clave de caché e inventario del equipo
            tickets_raw, inventario = await asyncio.gather(
                repo.get_historical_tickets(ip=ip, sensor=sensor or ""),
                repo.get_inventory_by_ip(ip),
            )
            ultima_accion = tickets_raw[0].accion_correctiva if tickets_raw else ""

            cache_repo = TicketAnalysisCacheRepository(DatabaseManager())
            # Saltear caché cuando hay datos Dynatrace para incorporarlos al análisis
            cached = None if tiene_datos_dynatrace else await cache_repo.lookup(ip, sensor, total, ultima_accion)
            if cached:
                analisis_text = cached
                logger.info(f"Cache hit /api/tickets ip={ip} sensor={sensor} total={total}")
            else:
                llm = OpenAIProvider(api_key=settings.openai_api_key, model=settings.openai_data_model)
                DIV = "───────────────────"
                alerta_context = (
                    f"\nAlerta activa: {mensaje_alerta}" if mensaje_alerta
                    else "\n(No se proporcionó mensaje de alerta activa)"
                )
                dynatrace_context = _build_dynatrace_context()
                if inventario:
                    inv = inventario
                    inventario_context = (
                        f"\nEquipo en inventario:"
                        f"\n- Hostname: {inv.hostname or 'N/D'}"
                        f"\n- SO: {inv.version_os or 'N/D'}"
                        f"\n- Tipo: {inv.tipo_equipo or inv.fuente or 'N/D'}"
                        f"\n- Ambiente: {inv.ambiente or 'N/D'}"
                        f"\n- Capa: {inv.capa or 'N/D'}"
                        f"\n- Impacto: {inv.impacto or 'N/D'}"
                    )
                else:
                    inventario_context = "\n(Equipo no encontrado en inventario)"
                messages = [
                    {"role": "system", "content": (
                        "Eres un analista experto en operaciones de TI e infraestructura de red. "
                        "Analizas tickets históricos de equipos monitoreados y generas diagnósticos estructurados. "
                        "Usa únicamente la información de los tickets proporcionados — no inventes datos. "
                        "El resultado DEBE estar en formato Markdown completo: "
                        "usa ## para títulos de sección, ### para subtítulos, "
                        "emojis como íconos junto a cada título, "
                        "viñetas (- o •) para listas, y bloques de código (```) para comandos de terminal.\n\n"
                        "IMPORTANTE: Antes de recomendar acciones, evalúa si los tickets históricos son "
                        "relevantes para la alerta activa. Si los tickets corresponden a fallas distintas "
                        "a la alerta actual, indícalo explícitamente en la sección de Causa Raíz y basa "
                        "las acciones en conocimiento técnico general, no en esos tickets.\n\n"
                        f"Genera el análisis con EXACTAMENTE esta estructura:\n\n"
                        f"# 🖥 Historial de Tickets — {ip}{sensor_info}\n\n"
                        f"{DIV}\n"
                        f"## 📊 Resumen\n"
                        f"- Tickets analizados: [N]\n"
                        f"- Falla más frecuente en historial: [tipo de falla]\n"
                        f"- Relevancia para alerta actual: [Alta / Parcial / Baja — una línea de justificación]\n"
                        f"- Sensor: [nombre del sensor o 'No especificado']\n\n"
                        f"{DIV}\n"
                        f"## 🔍 Causa Raíz Probable\n"
                        f"[1-2 oraciones basadas en la alerta activa y el historial. "
                        f"Si el historial no es relevante, indicarlo y basar la hipótesis en la alerta activa. "
                        f"Citar tickets solo si son relevantes: (tickets #ID, #ID)]\n\n"
                        f"{DIV}\n"
                        f"## 🛠 Acciones Recomendadas\n"
                        f"1. [acción concreta; usa ``` para comandos de terminal si aplica]\n"
                        f"   - Si proviene de un ticket relevante con acción documentada: agregar `(ref: ticket #ID)`\n"
                        f"   - Si es conocimiento técnico general: agregar `(práctica estándar)`\n"
                        f"2. [ídem — máximo 5 acciones]\n\n"
                        f"{DIV}\n"
                        f"## 📋 Patrón Detectado\n"
                        f"[Una oración sobre la tendencia del historial y su relación con la alerta actual]\n\n"
                        f"---\n"
                        f"⚠️ *Estas sugerencias son orientativas. La decisión de ejecutar cualquier acción "
                        f"es responsabilidad exclusiva del operador.*"
                    )},
                    {"role": "user", "content": (
                        f"Equipo: {ip}{sensor_info}{alerta_context}{inventario_context}{dynatrace_context}\n\n"
                        f"Tickets históricos:\n{tickets_result.data}"
                    )},
                ]
                analysis = await llm.generate_messages(messages=messages, max_tokens=1024)
                analisis_text = str(analysis)
                if not tiene_datos_dynatrace:
                    await cache_repo.save(ip, sensor, total, ultima_accion, analisis_text)
                    logger.info(f"Cache guardado /api/tickets ip={ip} sensor={sensor} total={total}")
        else:
            error_msg = tickets_result.error

        total_ms = int((time.perf_counter() - t0) * 1000)

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

    try:
        analisis, total = asyncio.run(_run())
    except Exception as e:
        logger.error(f"Error en /api/tickets: {e}", exc_info=True)
        return jsonify({"success": False, "error": "Error interno del servidor", "error_code": "INTERNAL_ERROR"}), 500

    return jsonify({
        "success": True,
        "ip": ip,
        "sensor": sensor,
        "total_tickets": total,
        "analisis": analisis,
        "timestamp": datetime.now().isoformat(),
    }), 200


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "timestamp": datetime.now().isoformat()}), 200


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    from src.config.settings import settings
    from src.infra.database.connection import DatabaseManager
    get_handler_manager().initialize(DatabaseManager())
    logger.info("HandlerManager inicializado correctamente")
    app.run(host="0.0.0.0", port=settings.api_port, debug=True)
