"""
Dashboard API — endpoints de solo lectura para el panel de administración.

Todos los endpoints son síncronos (Flask) excepto alertas que usa asyncio.run().
No requiere autenticación adicional al estar dentro de la red.
"""
import asyncio
import logging
import os
from datetime import date

from flask import Blueprint, jsonify, send_from_directory

from src.infra.database.connection import DatabaseManager
from src.infra.database.registry import DatabaseRegistry

logger = logging.getLogger(__name__)

dashboard_bp = Blueprint("dashboard", __name__)

_WWWROOT = os.path.join(os.path.dirname(__file__), "..", "..", "wwwroot")

_db: DatabaseManager | None = None
_registry: DatabaseRegistry | None = None


def _get_db() -> DatabaseManager:
    global _db
    if _db is None:
        _db = DatabaseManager()
    return _db


def _get_registry() -> DatabaseRegistry:
    global _registry
    if _registry is None:
        _registry = DatabaseRegistry.from_settings()
    return _registry


# ──────────────────────────────────────────────────────────────────────────────
# Serve dashboard HTML
# ──────────────────────────────────────────────────────────────────────────────

@dashboard_bp.route("/admin")
def admin():
    return send_from_directory(os.path.abspath(_WWWROOT), "dashboard-wireframe.html")


# ──────────────────────────────────────────────────────────────────────────────
# Overview
# ──────────────────────────────────────────────────────────────────────────────

@dashboard_bp.route("/api/admin/overview")
def overview():
    try:
        db = _get_db()

        stats = db.execute_query("""
            SELECT
                COUNT(*)                                                       AS total_mensajes,
                COUNT(DISTINCT telegramChatId)                                 AS usuarios_activos,
                SUM(CASE WHEN mensajeError IS NOT NULL THEN 1 ELSE 0 END)      AS errores,
                ISNULL(SUM(costoUSD), 0)                                       AS costo_total
            FROM abcmasplus..BotIAv2_InteractionLogs
            WHERE CAST(fechaCreacion AS DATE) = CAST(GETDATE() AS DATE)
        """)

        percentiles = db.execute_query("""
            SELECT TOP 1
                PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY duracionMs) OVER () AS p50_ms,
                PERCENTILE_CONT(0.9) WITHIN GROUP (ORDER BY duracionMs) OVER () AS p90_ms
            FROM abcmasplus..BotIAv2_InteractionLogs
            WHERE CAST(fechaCreacion AS DATE) = CAST(GETDATE() AS DATE)
        """)

        prev = db.execute_query("""
            SELECT COUNT(*) AS total_ayer
            FROM abcmasplus..BotIAv2_InteractionLogs
            WHERE CAST(fechaCreacion AS DATE) = CAST(DATEADD(DAY, -1, GETDATE()) AS DATE)
        """)

        agent_rows = db.execute_query("""
            SELECT
                ar.agenteSeleccionado,
                COUNT(*)                                                           AS requests,
                SUM(CASE WHEN il.mensajeError IS NULL THEN 1 ELSE 0 END)           AS exitosos,
                ISNULL(AVG(il.duracionMs), 0)                                      AS avg_ms,
                ISNULL(SUM(il.totalInputTokens + il.totalOutputTokens), 0)         AS total_tokens,
                ISNULL(SUM(il.costoUSD), 0)                                        AS costo
            FROM abcmasplus..BotIAv2_AgentRouting ar
            LEFT JOIN abcmasplus..BotIAv2_InteractionLogs il
                ON ar.correlationId = il.correlationId
            WHERE CAST(ar.fechaCreacion AS DATE) = CAST(GETDATE() AS DATE)
            GROUP BY ar.agenteSeleccionado
            ORDER BY requests DESC
        """)

        hourly_rows = db.execute_query("""
            SELECT DATEPART(HOUR, fechaCreacion) AS hora, COUNT(*) AS mensajes
            FROM abcmasplus..BotIAv2_InteractionLogs
            WHERE fechaCreacion >= DATEADD(HOUR, -12, GETDATE())
            GROUP BY DATEPART(HOUR, fechaCreacion)
            ORDER BY hora
        """)

        s = stats[0] if stats else {}
        pc = percentiles[0] if percentiles else {}
        p = prev[0] if prev else {}

        total_hoy = int(s.get("total_mensajes") or 0)
        total_ayer = int(p.get("total_ayer") or 0)
        pct = round((total_hoy - total_ayer) / total_ayer * 100) if total_ayer else 0

        return jsonify({
            "mensajes_hoy": total_hoy,
            "mensajes_pct_change": pct,
            "usuarios_activos": int(s.get("usuarios_activos") or 0),
            "errores_hoy": int(s.get("errores") or 0),
            "costo_hoy": round(float(s.get("costo_total") or 0), 2),
            "p50_s": round(float(pc.get("p50_ms") or 0) / 1000, 1),
            "p90_s": round(float(pc.get("p90_ms") or 0) / 1000, 1),
            "agentes": [
                {
                    "nombre": r["agenteSeleccionado"],
                    "requests": int(r["requests"] or 0),
                    "exito_pct": round(int(r["exitosos"] or 0) / int(r["requests"]) * 100) if r["requests"] else 0,
                    "avg_ms": int(r["avg_ms"] or 0),
                    "total_tokens": int(r["total_tokens"] or 0),
                    "costo": round(float(r["costo"] or 0), 2),
                }
                for r in agent_rows
            ],
            "actividad_por_hora": [
                {"hora": int(r["hora"]), "mensajes": int(r["mensajes"])}
                for r in hourly_rows
            ],
        })
    except Exception as e:
        logger.error(f"Dashboard /overview error: {e}")
        return jsonify({"error": str(e)}), 500


# ──────────────────────────────────────────────────────────────────────────────
# Logs
# ──────────────────────────────────────────────────────────────────────────────

@dashboard_bp.route("/api/admin/logs")
def logs():
    try:
        db = _get_db()
        rows = db.execute_query("""
            SELECT TOP 50
                correlationId,
                telegramUsername,
                query,
                agenteNombre,
                duracionMs,
                mensajeError,
                fechaCreacion,
                channel,
                stepsTomados,
                totalInputTokens,
                totalOutputTokens,
                costoUSD
            FROM abcmasplus..BotIAv2_InteractionLogs
            ORDER BY fechaCreacion DESC
        """)
        return jsonify([
            {
                "correlation_id": r["correlationId"],
                "username": r["telegramUsername"] or "api",
                "query": (r["query"] or "")[:120],
                "agente": r["agenteNombre"],
                "duracion_ms": int(r["duracionMs"] or 0),
                "error": r["mensajeError"] is not None,
                "fecha": str(r["fechaCreacion"]),
                "channel": r["channel"],
                "steps": int(r["stepsTomados"] or 0),
                "tokens_in": int(r["totalInputTokens"] or 0),
                "tokens_out": int(r["totalOutputTokens"] or 0),
                "costo": round(float(r["costoUSD"] or 0), 4),
            }
            for r in rows
        ])
    except Exception as e:
        logger.error(f"Dashboard /logs error: {e}")
        return jsonify({"error": str(e)}), 500


@dashboard_bp.route("/api/admin/logs/<correlation_id>")
def log_detail(correlation_id: str):
    try:
        db = _get_db()
        interaction = db.execute_query(
            """
            SELECT correlationId, telegramUsername, query, respuesta, agenteNombre,
                   duracionMs, mensajeError, fechaCreacion, channel, stepsTomados,
                   memoryMs, reactMs, classifyMs, totalInputTokens, totalOutputTokens, costoUSD
            FROM abcmasplus..BotIAv2_InteractionLogs
            WHERE correlationId = :cid
            """,
            {"cid": correlation_id},
        )
        if not interaction:
            return jsonify({"error": "not found"}), 404

        steps = db.execute_query(
            """
            SELECT stepNum, tipo, nombre, duracionMs, tokensIn, tokensOut, costoUSD, fechaInicio
            FROM abcmasplus..BotIAv2_InteractionSteps
            WHERE correlationId = :cid
            ORDER BY stepNum
            """,
            {"cid": correlation_id},
        )

        i = interaction[0]
        return jsonify({
            "correlation_id": i["correlationId"],
            "username": i["telegramUsername"] or "api",
            "query": i["query"],
            "respuesta": i["respuesta"],
            "agente": i["agenteNombre"],
            "duracion_ms": int(i["duracionMs"] or 0),
            "memory_ms": int(i["memoryMs"] or 0),
            "react_ms": int(i["reactMs"] or 0),
            "classify_ms": int(i["classifyMs"] or 0),
            "error": i["mensajeError"],
            "fecha": str(i["fechaCreacion"]),
            "channel": i["channel"],
            "tokens_in": int(i["totalInputTokens"] or 0),
            "tokens_out": int(i["totalOutputTokens"] or 0),
            "costo": round(float(i["costoUSD"] or 0), 4),
            "steps": [
                {
                    "num": int(s["stepNum"]),
                    "tipo": s["tipo"],
                    "nombre": s["nombre"],
                    "duracion_ms": int(s["duracionMs"] or 0),
                    "tokens_in": int(s["tokensIn"] or 0),
                    "tokens_out": int(s["tokensOut"] or 0),
                    "costo": round(float(s["costoUSD"] or 0), 4),
                }
                for s in steps
            ],
        })
    except Exception as e:
        logger.error(f"Dashboard /logs/{correlation_id} error: {e}")
        return jsonify({"error": str(e)}), 500


# ──────────────────────────────────────────────────────────────────────────────
# Agentes
# ──────────────────────────────────────────────────────────────────────────────

@dashboard_bp.route("/api/admin/agents")
def agents():
    try:
        db = _get_db()
        agent_rows = db.execute_query("""
            SELECT
                ad.idAgente,
                ad.nombre,
                ad.descripcion,
                ad.temperatura,
                ad.maxIteraciones,
                ad.modeloOverride,
                ad.esGeneralista,
                ad.version,
                ISNULL((
                    SELECT STRING_AGG(at2.nombreTool, ',')
                    FROM abcmasplus..BotIAv2_AgenteTools at2
                    WHERE at2.idAgente = ad.idAgente AND at2.activo = 1
                ), '') AS tools
            FROM abcmasplus..BotIAv2_AgenteDef ad
            WHERE ad.activo = 1
            ORDER BY ad.idAgente
        """)

        routing_today = db.execute_query("""
            SELECT agenteSeleccionado, COUNT(*) AS requests_hoy
            FROM abcmasplus..BotIAv2_AgentRouting
            WHERE CAST(fechaCreacion AS DATE) = CAST(GETDATE() AS DATE)
            GROUP BY agenteSeleccionado
        """)
        req_map = {r["agenteSeleccionado"]: int(r["requests_hoy"]) for r in routing_today}

        version_history = db.execute_query("""
            SELECT TOP 15
                h.idAgente,
                h.version,
                h.razonCambio,
                h.creadoPor,
                h.fechaCreacion
            FROM abcmasplus..BotIAv2_AgentePromptHistorial h
            ORDER BY h.fechaCreacion DESC
        """)
        history_map: dict[int, list] = {}
        for h in version_history:
            aid = int(h["idAgente"])
            history_map.setdefault(aid, []).append({
                "version": f"v{h['version']}",
                "razon": h["razonCambio"],
                "por": h["creadoPor"],
                "fecha": str(h["fechaCreacion"]),
            })

        return jsonify([
            {
                "id": int(r["idAgente"]),
                "nombre": r["nombre"],
                "descripcion": r["descripcion"],
                "temperatura": float(r["temperatura"] or 0),
                "max_iteraciones": int(r["maxIteraciones"] or 0),
                "modelo_override": r["modeloOverride"],
                "es_generalista": bool(r["esGeneralista"]),
                "version": int(r["version"] or 0),
                "tools": [t for t in (r["tools"] or "").split(",") if t],
                "requests_hoy": req_map.get(r["nombre"], 0),
                "historial": history_map.get(int(r["idAgente"]), []),
            }
            for r in agent_rows
        ])
    except Exception as e:
        logger.error(f"Dashboard /agents error: {e}")
        return jsonify({"error": str(e)}), 500


# ──────────────────────────────────────────────────────────────────────────────
# Knowledge
# ──────────────────────────────────────────────────────────────────────────────

@dashboard_bp.route("/api/admin/knowledge")
def knowledge():
    try:
        db = _get_db()
        cat_rows = db.execute_query("""
            SELECT
                c.id,
                c.name,
                c.display_name,
                c.icon,
                COUNT(e.id) AS entry_count
            FROM abcmasplus..BotIAv2_knowledge_categories c
            LEFT JOIN abcmasplus..BotIAv2_knowledge_entries e
                ON c.id = e.category_id AND e.active = 1
            WHERE c.active = 1
            GROUP BY c.id, c.name, c.display_name, c.icon
            ORDER BY c.display_name
        """)

        searches_today = db.execute_query("""
            SELECT COUNT(*) AS total
            FROM abcmasplus..BotIAv2_InteractionLogs
            WHERE agenteNombre LIKE '%conocimiento%'
              AND CAST(fechaCreacion AS DATE) = CAST(GETDATE() AS DATE)
        """)

        total_entries = sum(int(r["entry_count"] or 0) for r in cat_rows)
        busquedas_hoy = int((searches_today[0]["total"] if searches_today else 0) or 0)

        return jsonify({
            "total_categorias": len(cat_rows),
            "total_entradas": total_entries,
            "busquedas_hoy": busquedas_hoy,
            "categorias": [
                {
                    "id": int(r["id"]),
                    "nombre": r["display_name"] or r["name"],
                    "icono": r["icon"] or "",
                    "entradas": int(r["entry_count"] or 0),
                }
                for r in cat_rows
            ],
        })
    except Exception as e:
        logger.error(f"Dashboard /knowledge error: {e}")
        return jsonify({"error": str(e)}), 500


# ──────────────────────────────────────────────────────────────────────────────
# Usuarios
# ──────────────────────────────────────────────────────────────────────────────

@dashboard_bp.route("/api/admin/users")
def users():
    try:
        db = _get_db()
        rows = db.execute_query("""
            SELECT
                u.idUsuario,
                u.Nombre,
                u.idRol,
                r.nombre        AS rolNombre,
                ut.telegramChatId,
                ut.telegramUsername,
                ut.estado,
                ut.verificado,
                ut.fechaUltimaActividad
            FROM abcmasplus..BotIAv2_UsuariosTelegram ut
            INNER JOIN abcmasplus..Usuarios u ON ut.idUsuario = u.idUsuario
            LEFT  JOIN abcmasplus..Roles    r ON u.idRol = r.idRol
            WHERE ut.activo = 1
            ORDER BY ut.fechaUltimaActividad DESC
        """)
        return jsonify([
            {
                "id_usuario": int(r["idUsuario"] or 0),
                "nombre": r["Nombre"] or "",
                "rol": r["rolNombre"] or "",
                "chat_id": r["telegramChatId"],
                "username": r["telegramUsername"] or "",
                "estado": r["estado"] or "BLOQUEADO",
                "verificado": bool(r["verificado"]),
                "ultima_actividad": str(r["fechaUltimaActividad"] or ""),
            }
            for r in rows
        ])
    except Exception as e:
        logger.error(f"Dashboard /users error: {e}")
        return jsonify({"error": str(e)}), 500


# ──────────────────────────────────────────────────────────────────────────────
# Alertas
# ──────────────────────────────────────────────────────────────────────────────

@dashboard_bp.route("/api/admin/alerts")
def alerts():
    try:
        from src.domain.alerts.alert_repository import AlertRepository

        try:
            db_mon = _get_registry().get("monitoreo")
            repo = AlertRepository(db_manager=db_mon)
            eventos_banco, eventos_ekt = asyncio.run(repo.get_active_events_all())
            eventos = eventos_banco + eventos_ekt
        except Exception as e:
            logger.warning(f"No se pudo conectar a monitoreo: {e}")
            eventos = []

        criticos = sum(1 for e in eventos if e.prioridad >= 4)
        warnings = sum(1 for e in eventos if e.prioridad < 4)

        return jsonify({
            "criticos": criticos,
            "warnings": warnings,
            "alertas": [
                {
                    "equipo": e.equipo,
                    "ip": e.ip,
                    "sensor": e.sensor,
                    "status": e.status,
                    "mensaje": e.mensaje,
                    "prioridad": e.prioridad,
                    "origen": getattr(e, "_origen", ""),
                }
                for e in eventos[:50]
            ],
        })
    except Exception as e:
        logger.error(f"Dashboard /alerts error: {e}")
        return jsonify({"error": str(e)}), 500
