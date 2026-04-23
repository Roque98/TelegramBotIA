"""
DashboardService — queries async para el dashboard inline de Telegram.

Replica la lógica de dashboard_api.py pero en contexto async:
- Usa execute_query_async (ya wrappea asyncio.to_thread internamente)
- Para alertas usa await directo sobre AlertRepository, NO asyncio.run()
"""
import logging
from datetime import date, datetime, timedelta
from typing import Any, Optional

logger = logging.getLogger(__name__)

_DIAS_ES = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]


def _build_where(periodo: str) -> tuple[str, str, str]:
    """Retorna (where, where_ar, where_prev) según el período."""
    if periodo == "hoy":
        return (
            "CAST(fechaEjecucion AS DATE) = CAST(GETDATE() AS DATE)",
            "CAST(ar.fechaCreacion AS DATE) = CAST(GETDATE() AS DATE)",
            "CAST(fechaEjecucion AS DATE) = CAST(DATEADD(DAY,-1,GETDATE()) AS DATE)",
        )
    if periodo == "ayer":
        return (
            "CAST(fechaEjecucion AS DATE) = CAST(DATEADD(DAY,-1,GETDATE()) AS DATE)",
            "CAST(ar.fechaCreacion AS DATE) = CAST(DATEADD(DAY,-1,GETDATE()) AS DATE)",
            "CAST(fechaEjecucion AS DATE) = CAST(DATEADD(DAY,-2,GETDATE()) AS DATE)",
        )
    if periodo == "7d":
        return (
            "fechaEjecucion >= DATEADD(DAY,-6, CAST(GETDATE() AS DATE))",
            "ar.fechaCreacion >= DATEADD(DAY,-6, CAST(GETDATE() AS DATE))",
            "fechaEjecucion >= DATEADD(DAY,-13,CAST(GETDATE() AS DATE)) AND fechaEjecucion < DATEADD(DAY,-6,CAST(GETDATE() AS DATE))",
        )
    # 30d
    return (
        "fechaEjecucion >= DATEADD(DAY,-29,CAST(GETDATE() AS DATE))",
        "ar.fechaCreacion >= DATEADD(DAY,-29,CAST(GETDATE() AS DATE))",
        "fechaEjecucion >= DATEADD(DAY,-59,CAST(GETDATE() AS DATE)) AND fechaEjecucion < DATEADD(DAY,-29,CAST(GETDATE() AS DATE))",
    )


class DashboardService:

    def __init__(self, db_manager: Any, db_registry: Optional[Any] = None) -> None:
        self._db = db_manager
        self._registry = db_registry

    # ──────────────────────────────────────────────────────────────────────────
    # Overview
    # ──────────────────────────────────────────────────────────────────────────

    async def get_overview(self, periodo: str = "hoy") -> dict:
        if periodo not in ("hoy", "ayer", "7d", "30d"):
            periodo = "hoy"

        where, where_ar, where_prev = _build_where(periodo)

        stats, percentiles, prev, agent_rows = await _gather(
            self._db.execute_query_async(f"""
                SELECT
                    COUNT(*)                                            AS total_mensajes,
                    COUNT(DISTINCT telegramChatId)                      AS usuarios_activos,
                    SUM(CASE WHEN exitoso = 0 THEN 1 ELSE 0 END)       AS errores,
                    ISNULL(SUM(costUSD), 0)                             AS costo_total
                FROM abcmasplus..BotIAv2_InteractionLogs WHERE {where}
            """),
            self._db.execute_query_async(f"""
                SELECT TOP 1
                    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY duracionMs) OVER () AS p50_ms,
                    PERCENTILE_CONT(0.9) WITHIN GROUP (ORDER BY duracionMs) OVER () AS p90_ms
                FROM abcmasplus..BotIAv2_InteractionLogs WHERE {where}
            """),
            self._db.execute_query_async(f"""
                SELECT COUNT(*) AS total_prev
                FROM abcmasplus..BotIAv2_InteractionLogs WHERE {where_prev}
            """),
            self._db.execute_query_async(f"""
                SELECT
                    ar.agenteSeleccionado,
                    COUNT(*) AS requests,
                    SUM(CASE WHEN il.exitoso = 1 THEN 1 ELSE 0 END) AS exitosos,
                    ISNULL(SUM(il.costUSD), 0) AS costo
                FROM abcmasplus..BotIAv2_AgentRouting ar
                LEFT JOIN abcmasplus..BotIAv2_InteractionLogs il
                    ON ar.correlationId = il.correlationId
                WHERE {where_ar}
                GROUP BY ar.agenteSeleccionado
                ORDER BY requests DESC
            """),
        )

        s  = stats[0] if stats else {}
        pc = percentiles[0] if percentiles else {}
        p  = prev[0] if prev else {}

        total      = int(s.get("total_mensajes") or 0)
        total_prev = int(p.get("total_prev") or 0)
        pct = round((total - total_prev) / total_prev * 100) if total_prev else 0

        return {
            "periodo": periodo,
            "mensajes": total,
            "mensajes_pct_change": pct,
            "usuarios_activos": int(s.get("usuarios_activos") or 0),
            "errores": int(s.get("errores") or 0),
            "costo": round(float(s.get("costo_total") or 0), 4),
            "p50_s": round(float(pc.get("p50_ms") or 0) / 1000, 1),
            "p90_s": round(float(pc.get("p90_ms") or 0) / 1000, 1),
            "agentes": [
                {
                    "nombre": r["agenteSeleccionado"],
                    "requests": int(r["requests"] or 0),
                    "exito_pct": round(int(r["exitosos"] or 0) / int(r["requests"]) * 100)
                    if r["requests"] else 0,
                    "costo": round(float(r["costo"] or 0), 4),
                }
                for r in agent_rows
            ],
        }

    # ──────────────────────────────────────────────────────────────────────────
    # Alertas
    # ──────────────────────────────────────────────────────────────────────────

    async def get_alerts(self) -> dict:
        if not self._registry:
            return {"criticos": 0, "warnings": 0, "alertas": [], "error": "db_registry no disponible"}

        try:
            from src.domain.alerts.alert_repository import AlertRepository
            db_mon = self._registry.get("monitoreo")
            repo = AlertRepository(db_manager=db_mon)
            eventos_banco, eventos_ekt = await repo.get_active_events_all()
            eventos = eventos_banco + eventos_ekt
        except Exception as e:
            logger.warning(f"DashboardService.get_alerts: {e}")
            return {"criticos": 0, "warnings": 0, "alertas": [], "error": str(e)}

        criticos = sum(1 for e in eventos if e.prioridad >= 4)
        warnings = sum(1 for e in eventos if e.prioridad < 4)

        return {
            "criticos": criticos,
            "warnings": warnings,
            "alertas": [
                {
                    "equipo": e.equipo,
                    "ip": e.ip,
                    "sensor": e.sensor,
                    "status": e.status,
                    "prioridad": e.prioridad,
                    "origen": getattr(e, "_origen", ""),
                }
                for e in eventos[:20]
            ],
        }

    # ──────────────────────────────────────────────────────────────────────────
    # Logs
    # ──────────────────────────────────────────────────────────────────────────

    async def get_logs(self, page: int = 1, page_size: int = 8) -> dict:
        rows = await self._db.execute_query_async("""
            SELECT TOP 50
                il.telegramUsername,
                il.query,
                il.agenteNombre,
                il.duracionMs,
                il.exitoso,
                il.fechaEjecucion,
                il.costUSD
            FROM abcmasplus..BotIAv2_InteractionLogs il
            ORDER BY il.fechaEjecucion DESC
        """)

        total = len(rows)
        total_pages = max(1, (total + page_size - 1) // page_size)
        page = max(1, min(page, total_pages))
        start = (page - 1) * page_size
        slice_ = rows[start: start + page_size]

        return {
            "logs": [
                {
                    "username": r["telegramUsername"] or "api",
                    "query": (r["query"] or "")[:50],
                    "agente": r["agenteNombre"] or "—",
                    "duracion_ms": int(r["duracionMs"] or 0),
                    "exitoso": bool(r["exitoso"]),
                    "fecha": str(r["fechaEjecucion"] or ""),
                    "costo": round(float(r["costUSD"] or 0), 4),
                }
                for r in slice_
            ],
            "page": page,
            "total_pages": total_pages,
            "total": total,
        }

    # ──────────────────────────────────────────────────────────────────────────
    # Agentes
    # ──────────────────────────────────────────────────────────────────────────

    async def get_agents(self) -> list[dict]:
        agent_rows, routing_today = await _gather(
            self._db.execute_query_async("""
                SELECT
                    ad.idAgente, ad.nombre, ad.descripcion,
                    ad.temperatura, ad.maxIteraciones, ad.modeloOverride,
                    ad.esGeneralista, ad.version,
                    ISNULL((
                        SELECT STRING_AGG(at2.nombreTool, ',')
                        FROM abcmasplus..BotIAv2_AgenteTools at2
                        WHERE at2.idAgente = ad.idAgente AND at2.activo = 1
                    ), '') AS tools
                FROM abcmasplus..BotIAv2_AgenteDef ad
                WHERE ad.activo = 1
                ORDER BY ad.idAgente
            """),
            self._db.execute_query_async("""
                SELECT agenteSeleccionado, COUNT(*) AS requests_hoy
                FROM abcmasplus..BotIAv2_AgentRouting
                WHERE CAST(fechaCreacion AS DATE) = CAST(GETDATE() AS DATE)
                GROUP BY agenteSeleccionado
            """),
        )

        req_map = {r["agenteSeleccionado"]: int(r["requests_hoy"]) for r in routing_today}

        return [
            {
                "nombre": r["nombre"],
                "descripcion": (r["descripcion"] or "")[:80],
                "temperatura": float(r["temperatura"] or 0),
                "max_iteraciones": int(r["maxIteraciones"] or 0),
                "modelo_override": r["modeloOverride"],
                "es_generalista": bool(r["esGeneralista"]),
                "version": int(r["version"] or 0),
                "tools_count": len([t for t in (r["tools"] or "").split(",") if t]),
                "requests_hoy": req_map.get(r["nombre"], 0),
            }
            for r in agent_rows
        ]

    # ──────────────────────────────────────────────────────────────────────────
    # Usuarios
    # ──────────────────────────────────────────────────────────────────────────

    async def get_users(self) -> list[dict]:
        rows = await self._db.execute_query_async(
            "EXEC abcmasplus..BotIAv2_sp_GetAllUsuariosTelegram"
        )
        return [
            {
                "nombre": r["Nombre"] or "",
                "rol": r["rolNombre"] or "",
                "estado": r["estado"] or "BLOQUEADO",
                "verificado": bool(r["verificado"]),
                "ultima_actividad": str(r["fechaUltimaActividad"] or ""),
            }
            for r in rows[:15]  # máx 15 — decisión deliberada
        ]

    # ──────────────────────────────────────────────────────────────────────────
    # Knowledge
    # ──────────────────────────────────────────────────────────────────────────

    async def get_knowledge(self) -> dict:
        cat_rows, searches = await _gather(
            self._db.execute_query_async("""
                SELECT
                    c.display_name, c.icon,
                    COUNT(e.id) AS entry_count
                FROM abcmasplus..BotIAv2_knowledge_categories c
                LEFT JOIN abcmasplus..BotIAv2_knowledge_entries e
                    ON c.id = e.category_id AND e.active = 1
                WHERE c.active = 1
                GROUP BY c.id, c.display_name, c.icon
                ORDER BY c.display_name
            """),
            self._db.execute_query_async("""
                SELECT COUNT(*) AS total
                FROM abcmasplus..BotIAv2_InteractionLogs
                WHERE agenteNombre LIKE '%conocimiento%'
                  AND CAST(fechaEjecucion AS DATE) = CAST(GETDATE() AS DATE)
            """),
        )

        total_entries = sum(int(r["entry_count"] or 0) for r in cat_rows)
        busquedas_hoy = int((searches[0]["total"] if searches else 0) or 0)

        return {
            "total_categorias": len(cat_rows),
            "total_entradas": total_entries,
            "busquedas_hoy": busquedas_hoy,
            "categorias": [
                {
                    "nombre": r["display_name"] or "",
                    "icono": r["icon"] or "",
                    "entradas": int(r["entry_count"] or 0),
                }
                for r in cat_rows
            ],
        }


# ──────────────────────────────────────────────────────────────────────────────
# Helper
# ──────────────────────────────────────────────────────────────────────────────

async def _gather(*coros):
    import asyncio
    return await asyncio.gather(*coros)
