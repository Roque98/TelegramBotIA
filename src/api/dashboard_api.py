"""
Dashboard API — endpoints de solo lectura para el panel de administración.

Todos los endpoints son síncronos (Flask) excepto alertas que usa asyncio.run().
No requiere autenticación adicional al estar dentro de la red.
"""
import asyncio
import logging
import os
from datetime import date, datetime, timedelta

from flask import Blueprint, jsonify, request, send_from_directory

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


@dashboard_bp.route("/admin/<path:filename>")
def admin_static(filename):
    return send_from_directory(os.path.abspath(_WWWROOT), filename)


# ──────────────────────────────────────────────────────────────────────────────
# Overview
# ──────────────────────────────────────────────────────────────────────────────

@dashboard_bp.route("/api/admin/overview")
def overview():
    try:
        db = _get_db()

        periodo = request.args.get("periodo", "hoy")
        if periodo not in ("hoy", "ayer", "7d", "30d"):
            periodo = "hoy"

        if periodo == "hoy":
            where     = "CAST(fechaEjecucion AS DATE) = CAST(GETDATE() AS DATE)"
            where_ar  = "CAST(ar.fechaCreacion AS DATE) = CAST(GETDATE() AS DATE)"
            where_prev = "CAST(fechaEjecucion AS DATE) = CAST(DATEADD(DAY,-1,GETDATE()) AS DATE)"
        elif periodo == "ayer":
            where     = "CAST(fechaEjecucion AS DATE) = CAST(DATEADD(DAY,-1,GETDATE()) AS DATE)"
            where_ar  = "CAST(ar.fechaCreacion AS DATE) = CAST(DATEADD(DAY,-1,GETDATE()) AS DATE)"
            where_prev = "CAST(fechaEjecucion AS DATE) = CAST(DATEADD(DAY,-2,GETDATE()) AS DATE)"
        elif periodo == "7d":
            where     = "fechaEjecucion >= DATEADD(DAY,-6, CAST(GETDATE() AS DATE))"
            where_ar  = "ar.fechaCreacion >= DATEADD(DAY,-6, CAST(GETDATE() AS DATE))"
            where_prev = "fechaEjecucion >= DATEADD(DAY,-13,CAST(GETDATE() AS DATE)) AND fechaEjecucion < DATEADD(DAY,-6,CAST(GETDATE() AS DATE))"
        else:  # 30d
            where     = "fechaEjecucion >= DATEADD(DAY,-29,CAST(GETDATE() AS DATE))"
            where_ar  = "ar.fechaCreacion >= DATEADD(DAY,-29,CAST(GETDATE() AS DATE))"
            where_prev = "fechaEjecucion >= DATEADD(DAY,-59,CAST(GETDATE() AS DATE)) AND fechaEjecucion < DATEADD(DAY,-29,CAST(GETDATE() AS DATE))"

        stats = db.execute_query(f"""
            SELECT
                COUNT(*)                                              AS total_mensajes,
                COUNT(DISTINCT telegramChatId)                        AS usuarios_activos,
                SUM(CASE WHEN exitoso = 0 THEN 1 ELSE 0 END)         AS errores,
                ISNULL(SUM(costUSD), 0)                               AS costo_total
            FROM abcmasplus..BotIAv2_InteractionLogs
            WHERE {where}
        """)

        percentiles = db.execute_query(f"""
            SELECT TOP 1
                PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY duracionMs) OVER () AS p50_ms,
                PERCENTILE_CONT(0.9) WITHIN GROUP (ORDER BY duracionMs) OVER () AS p90_ms
            FROM abcmasplus..BotIAv2_InteractionLogs
            WHERE {where}
        """)

        prev = db.execute_query(f"""
            SELECT COUNT(*) AS total_prev
            FROM abcmasplus..BotIAv2_InteractionLogs
            WHERE {where_prev}
        """)

        agent_rows = db.execute_query(f"""
            SELECT
                ar.agenteSeleccionado,
                COUNT(*)                                                          AS requests,
                SUM(CASE WHEN il.exitoso = 1 THEN 1 ELSE 0 END)                  AS exitosos,
                ISNULL(AVG(il.duracionMs), 0)                                     AS avg_ms,
                ISNULL(SUM(il.totalInputTokens + il.totalOutputTokens), 0)        AS total_tokens,
                ISNULL(SUM(il.costUSD), 0)                                        AS costo
            FROM abcmasplus..BotIAv2_AgentRouting ar
            LEFT JOIN abcmasplus..BotIAv2_InteractionLogs il
                ON ar.correlationId = il.correlationId
            WHERE {where_ar}
            GROUP BY ar.agenteSeleccionado
            ORDER BY requests DESC
        """)

        # Actividad horaria para hoy/ayer, diaria para 7d/30d.
        # Se rellenan con 0 los slots sin datos para mostrar el período completo.
        dias_es = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]
        if periodo in ("hoy", "ayer"):
            act_rows = db.execute_query(f"""
                SELECT DATEPART(HOUR, fechaEjecucion) AS slot, COUNT(*) AS mensajes
                FROM abcmasplus..BotIAv2_InteractionLogs
                WHERE {where}
                GROUP BY DATEPART(HOUR, fechaEjecucion)
                ORDER BY slot
            """)
            data_map = {int(r["slot"]): int(r["mensajes"]) for r in act_rows}
            hora_fin = datetime.now().hour if periodo == "hoy" else 23
            actividad = [
                {"label": f"{h}h", "mensajes": data_map.get(h, 0)}
                for h in range(0, hora_fin + 1)
            ]
        else:
            act_rows = db.execute_query(f"""
                SELECT CAST(fechaEjecucion AS DATE) AS slot, COUNT(*) AS mensajes
                FROM abcmasplus..BotIAv2_InteractionLogs
                WHERE {where}
                GROUP BY CAST(fechaEjecucion AS DATE)
                ORDER BY slot
            """)
            data_map = {r["slot"]: int(r["mensajes"]) for r in act_rows}
            dias_atras = 6 if periodo == "7d" else 29
            today = date.today()
            all_days = [today - timedelta(days=i) for i in range(dias_atras, -1, -1)]
            actividad = [
                {"label": f"{dias_es[d.weekday()]} {d.day}", "mensajes": data_map.get(d, 0)}
                for d in all_days
            ]

        s  = stats[0] if stats else {}
        pc = percentiles[0] if percentiles else {}
        p  = prev[0] if prev else {}

        total     = int(s.get("total_mensajes") or 0)
        total_prev = int(p.get("total_prev") or 0)
        pct = round((total - total_prev) / total_prev * 100) if total_prev else 0

        return jsonify({
            "periodo": periodo,
            "mensajes": total,
            "mensajes_pct_change": pct,
            "usuarios_activos": int(s.get("usuarios_activos") or 0),
            "errores": int(s.get("errores") or 0),
            "costo": round(float(s.get("costo_total") or 0), 2),
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
            "actividad": actividad,
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
                il.correlationId,
                il.telegramUsername,
                il.query,
                il.agenteNombre,
                il.duracionMs,
                il.exitoso,
                il.fechaEjecucion,
                il.channel,
                il.stepsTomados,
                il.totalInputTokens,
                il.totalOutputTokens,
                il.costUSD,
                (
                    SELECT TOP 1 al.level
                    FROM abcmasplus..BotIAv2_ApplicationLogs al
                    WHERE al.correlationId = il.correlationId
                    ORDER BY CASE al.level WHEN 'CRITICAL' THEN 3 WHEN 'ERROR' THEN 2 WHEN 'WARNING' THEN 1 ELSE 0 END DESC
                ) AS app_log_level
            FROM abcmasplus..BotIAv2_InteractionLogs il
            ORDER BY il.fechaEjecucion DESC
        """)
        return jsonify([
            {
                "correlation_id": r["correlationId"],
                "username": r["telegramUsername"] or "api",
                "query": (r["query"] or "")[:120],
                "agente": r["agenteNombre"],
                "duracion_ms": int(r["duracionMs"] or 0),
                "error": not bool(r["exitoso"]),
                "fecha": str(r["fechaEjecucion"]),
                "channel": r["channel"],
                "steps": int(r["stepsTomados"] or 0),
                "tokens_in": int(r["totalInputTokens"] or 0),
                "tokens_out": int(r["totalOutputTokens"] or 0),
                "costo": round(float(r["costUSD"] or 0), 4),
                "has_app_logs": r["app_log_level"] is not None,
                "app_log_level": r["app_log_level"],
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
                   duracionMs, exitoso, mensajeError, fechaEjecucion, channel, stepsTomados,
                   memoryMs, reactMs, classifyMs, totalInputTokens, totalOutputTokens, costUSD
            FROM abcmasplus..BotIAv2_InteractionLogs
            WHERE correlationId = :cid
            """,
            {"cid": correlation_id},
        )
        if not interaction:
            return jsonify({"error": "not found"}), 404

        steps = db.execute_query(
            """
            SELECT stepNum, tipo, nombre, duracionMs, tokensIn, tokensOut, costoUSD, fechaInicio,
                   entrada, salida
            FROM abcmasplus..BotIAv2_InteractionSteps
            WHERE correlationId = :cid
            ORDER BY stepNum
            """,
            {"cid": correlation_id},
        )

        app_logs_rows = db.execute_query(
            """
            SELECT id, level, event, message, module, durationMs, extra, createdAt
            FROM abcmasplus..BotIAv2_ApplicationLogs
            WHERE correlationId = :cid
            ORDER BY createdAt
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
            "fecha": str(i["fechaEjecucion"]),
            "channel": i["channel"],
            "tokens_in": int(i["totalInputTokens"] or 0),
            "tokens_out": int(i["totalOutputTokens"] or 0),
            "costo": round(float(i["costUSD"] or 0), 4),
            "steps": [
                {
                    "num": int(s["stepNum"]),
                    "tipo": s["tipo"],
                    "nombre": s["nombre"],
                    "duracion_ms": int(s["duracionMs"] or 0),
                    "tokens_in": int(s["tokensIn"] or 0),
                    "tokens_out": int(s["tokensOut"] or 0),
                    "costo": round(float(s["costoUSD"] or 0), 4),
                    "entrada": s["entrada"] or "",
                    "salida": s["salida"] or "",
                }
                for s in steps
            ],
            "app_logs": [
                {
                    "id": al["id"],
                    "level": al["level"],
                    "event": al["event"] or "",
                    "message": al["message"] or "",
                    "module": al["module"] or "",
                    "duration_ms": al["durationMs"],
                    "extra": al["extra"] or "",
                    "fecha": al["createdAt"].strftime("%Y-%m-%d %H:%M:%S") if al.get("createdAt") else None,
                }
                for al in app_logs_rows
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
                ad.systemPrompt,
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
                h.modificadoPor,
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
                "por": h["modificadoPor"],
                "fecha": str(h["fechaCreacion"]),
            })

        return jsonify([
            {
                "id": int(r["idAgente"]),
                "nombre": r["nombre"],
                "descripcion": r["descripcion"],
                "prompt": r["systemPrompt"] or "",
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


@dashboard_bp.route("/api/admin/agents/<int:agent_id>/prompt", methods=["PUT"])
def update_agent_prompt(agent_id: int):
    try:
        body = request.get_json(silent=True) or {}
        new_prompt = body.get("prompt", "").strip()
        razon = body.get("razon", "Edición manual desde dashboard").strip() or "Edición manual desde dashboard"
        por = body.get("por", "admin").strip() or "admin"
        if not new_prompt:
            return jsonify({"error": "prompt requerido"}), 400

        db = _get_db()
        rows = db.execute_non_query(
            "UPDATE abcmasplus..BotIAv2_AgenteDef SET systemPrompt = :prompt WHERE idAgente = :id AND activo = 1",
            {"prompt": new_prompt, "id": agent_id},
        )
        if rows == 0:
            return jsonify({"error": "Agente no encontrado"}), 404

        version_row = db.execute_query(
            "SELECT version FROM abcmasplus..BotIAv2_AgenteDef WHERE idAgente = :id",
            {"id": agent_id},
        )
        new_version = int(version_row[0]["version"]) if version_row else 1

        db.execute_non_query(
            """
            INSERT INTO abcmasplus..BotIAv2_AgentePromptHistorial
                (idAgente, systemPrompt, version, razonCambio, modificadoPor, fechaCreacion)
            VALUES (:id, :prompt, :version, :razon, :por, GETDATE())
            """,
            {"id": agent_id, "prompt": new_prompt, "version": new_version, "razon": razon, "por": por},
        )

        return jsonify({"ok": True, "version": new_version})
    except Exception as e:
        logger.error(f"Dashboard PUT /agents/{agent_id}/prompt error: {e}")
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
              AND CAST(fechaEjecucion AS DATE) = CAST(GETDATE() AS DATE)
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
        rows = db.execute_query("EXEC abcmasplus..BotIAv2_sp_GetAllUsuariosTelegram")
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
# Chats
# ──────────────────────────────────────────────────────────────────────────────

@dashboard_bp.route("/api/admin/chats")
def chats():
    try:
        db = _get_db()
        rows = db.execute_query("""
            SELECT TOP 150
                il.telegramChatId,
                ISNULL(
                    u.alias,
                    ISNULL(
                        NULLIF(LTRIM(
                            ISNULL(u.telegramFirstName,'') + ' ' + ISNULL(u.telegramLastName,'')
                        ), ''),
                        il.telegramUsername
                    )
                )                                         AS nombre,
                ISNULL(u.telegramUsername, il.telegramUsername) AS username,
                COUNT(*)                                  AS total_mensajes,
                SUM(CASE WHEN il.exitoso = 1 THEN 1 ELSE 0 END) AS exitosos,
                SUM(CASE WHEN il.exitoso = 0 THEN 1 ELSE 0 END) AS errores,
                MAX(il.fechaEjecucion)                    AS ultima_actividad,
                MIN(il.fechaEjecucion)                    AS primera_actividad,
                (
                    SELECT TOP 1 query
                    FROM abcmasplus..BotIAv2_InteractionLogs sub
                    WHERE sub.telegramChatId = il.telegramChatId
                    ORDER BY sub.fechaEjecucion DESC
                ) AS ultimo_query
            FROM abcmasplus..BotIAv2_InteractionLogs il
            LEFT JOIN abcmasplus..BotIAv2_UsuariosTelegram u
                ON il.telegramChatId = u.telegramChatId
            WHERE il.telegramChatId IS NOT NULL
            GROUP BY
                il.telegramChatId,
                il.telegramUsername,
                u.alias,
                u.telegramFirstName,
                u.telegramLastName,
                u.telegramUsername
            ORDER BY MAX(il.fechaEjecucion) DESC
        """)
        return jsonify([
            {
                "chat_id": str(r["telegramChatId"]),
                "nombre": r["nombre"] or r["username"] or "Desconocido",
                "username": r["username"] or "",
                "total": int(r["total_mensajes"] or 0),
                "exitosos": int(r["exitosos"] or 0),
                "errores": int(r["errores"] or 0),
                "ultima_actividad": str(r["ultima_actividad"] or ""),
                "primera_actividad": str(r["primera_actividad"] or ""),
                "ultimo_query": (r["ultimo_query"] or "")[:100],
            }
            for r in rows
        ])
    except Exception as e:
        logger.error(f"Dashboard /chats error: {e}")
        return jsonify({"error": str(e)}), 500


@dashboard_bp.route("/api/admin/chats/<chat_id>")
def chat_history(chat_id: str):
    try:
        db = _get_db()

        messages = db.execute_query(
            """
            SELECT TOP 300
                il.correlationId, il.query, il.respuesta, il.agenteNombre,
                il.fechaEjecucion, il.exitoso, il.duracionMs, il.costUSD,
                il.mensajeError, il.channel, il.stepsTomados,
                il.totalInputTokens, il.totalOutputTokens, il.memoryMs, il.reactMs,
                (
                    SELECT TOP 1 al.level
                    FROM abcmasplus..BotIAv2_ApplicationLogs al
                    WHERE al.correlationId = il.correlationId
                    ORDER BY CASE al.level WHEN 'CRITICAL' THEN 3 WHEN 'ERROR' THEN 2 WHEN 'WARNING' THEN 1 ELSE 0 END DESC
                ) AS app_log_level
            FROM abcmasplus..BotIAv2_InteractionLogs il
            WHERE il.telegramChatId = :cid
            ORDER BY il.fechaEjecucion ASC
            """,
            {"cid": chat_id},
        )

        try:
            profile_rows = db.execute_query(
                "EXEC abcmasplus..BotIAv2_sp_GetPerfilMemoria @telegramChatId = :cid",
                {"cid": chat_id},
            )
            profile = dict(profile_rows[0]) if profile_rows else None
            if profile:
                for k, v in profile.items():
                    if hasattr(v, "isoformat"):
                        profile[k] = v.isoformat()
        except Exception:
            profile = None

        try:
            stats_rows = db.execute_query(
                "EXEC abcmasplus..BotIAv2_sp_GetEstadisticasUsuario @telegramChatId = :cid",
                {"cid": chat_id},
            )
            stats = dict(stats_rows[0]) if stats_rows else None
            if stats:
                for k, v in stats.items():
                    if hasattr(v, "isoformat"):
                        stats[k] = v.isoformat()
        except Exception:
            stats = None

        return jsonify({
            "messages": [
                {
                    "correlation_id": m["correlationId"],
                    "query": m["query"] or "",
                    "respuesta": m["respuesta"] or "",
                    "agente": m["agenteNombre"] or "",
                    "fecha": str(m["fechaEjecucion"] or ""),
                    "exitoso": bool(m["exitoso"]),
                    "duracion_ms": int(m["duracionMs"] or 0),
                    "costo": round(float(m["costUSD"] or 0), 4),
                    "error": m["mensajeError"] or "",
                    "channel": m["channel"] or "",
                    "steps": int(m["stepsTomados"] or 0),
                    "tokens_in": int(m["totalInputTokens"] or 0),
                    "tokens_out": int(m["totalOutputTokens"] or 0),
                    "memory_ms": int(m["memoryMs"] or 0),
                    "react_ms": int(m["reactMs"] or 0),
                    "has_app_logs": m["app_log_level"] is not None,
                    "app_log_level": m["app_log_level"],
                }
                for m in messages
            ],
            "profile": profile,
            "stats": stats,
        })
    except Exception as e:
        logger.error(f"Dashboard /chats/{chat_id} error: {e}")
        return jsonify({"error": str(e)}), 500


# ──────────────────────────────────────────────────────────────────────────────
# Application Logs
# ──────────────────────────────────────────────────────────────────────────────

@dashboard_bp.route("/api/admin/app-logs")
def app_logs():
    try:
        db = _get_db()
        level          = request.args.get("level", "")        # WARNING, ERROR, CRITICAL
        module         = request.args.get("module", "")
        search         = request.args.get("search", "")
        correlation_id = request.args.get("correlation_id", "")
        limit   = min(int(request.args.get("limit", 100)), 500)
        offset  = int(request.args.get("offset", 0))

        where = ["1=1"]
        params: dict = {}

        if level:
            where.append("level = :level")
            params["level"] = level
        if module:
            where.append("module LIKE :module")
            params["module"] = f"%{module}%"
        if search:
            where.append("(message LIKE :search OR event LIKE :search)")
            params["search"] = f"%{search}%"
        if correlation_id:
            where.append("correlationId = :correlation_id")
            params["correlation_id"] = correlation_id

        where_sql = " AND ".join(where)

        rows = db.execute_query(f"""
            SELECT
                id,
                correlationId,
                userId,
                level,
                event,
                message,
                module,
                durationMs,
                extra,
                createdAt
            FROM abcmasplus..BotIAv2_ApplicationLogs
            WHERE {where_sql}
            ORDER BY createdAt DESC
            OFFSET {offset} ROWS FETCH NEXT {limit} ROWS ONLY
        """, params if params else None)

        total_row = db.execute_query(f"""
            SELECT COUNT(*) AS total
            FROM abcmasplus..BotIAv2_ApplicationLogs
            WHERE {where_sql}
        """, params if params else None)

        total = int((total_row[0].get("total") or 0)) if total_row else 0

        return jsonify({
            "total": total,
            "offset": offset,
            "limit": limit,
            "logs": [
                {
                    "id":             r.get("id"),
                    "correlationId":  r.get("correlationId"),
                    "userId":         r.get("userId"),
                    "level":          r.get("level"),
                    "event":          r.get("event"),
                    "message":        r.get("message"),
                    "module":         r.get("module"),
                    "durationMs":     r.get("durationMs"),
                    "extra":          r.get("extra"),
                    "fecha":          r["createdAt"].strftime("%Y-%m-%d %H:%M:%S") if r.get("createdAt") else None,
                }
                for r in rows
            ],
        })
    except Exception as e:
        logger.error(f"Dashboard /app-logs error: {e}")
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
