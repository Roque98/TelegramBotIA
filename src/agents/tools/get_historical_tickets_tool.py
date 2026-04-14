"""
GetHistoricalTicketsTool — Tickets históricos de un nodo/IP de PRTG.

Retorna datos estructurados (dict) — sin LLM interno.
"""

import logging
import time
from typing import Any

from src.agents.tools.base import BaseTool, ToolCategory, ToolDefinition, ToolParameter, ToolResult
from src.domain.alerts.alert_repository import AlertRepository

logger = logging.getLogger(__name__)


class GetHistoricalTicketsTool(BaseTool):
    """
    Retorna tickets históricos de un nodo/IP de monitoreo PRTG.

    Útil cuando el usuario quiere saber qué incidentes ha tenido
    un equipo en el pasado y cuál fue la acción correctiva.
    """

    is_read_only: bool = True
    is_destructive: bool = False
    is_concurrency_safe: bool = True

    def __init__(self, repo: AlertRepository) -> None:
        self._repo = repo

    @property
    def definition(self) -> ToolDefinition:
        return ToolDefinition(
            name="get_historical_tickets",
            description=(
                "Retorna los tickets históricos de un equipo/IP de PRTG. "
                "Incluye descripción de la alerta, detalle y acción correctiva de cada ticket. "
                "Usar cuando el usuario pregunta por el historial de incidentes, tickets previos o "
                "qué pasó antes con un equipo específico."
            ),
            category=ToolCategory.MONITORING,
            parameters=[
                ToolParameter(
                    name="ip",
                    param_type="string",
                    description="IP del equipo a consultar",
                    required=True,
                    examples=["10.118.57.142", "10.53.34.130"],
                ),
                ToolParameter(
                    name="sensor",
                    param_type="string",
                    description="Nombre del sensor para filtrar tickets (opcional)",
                    required=False,
                    default="",
                    examples=["Memoria", "CPU", "Ping"],
                ),
            ],
            examples=[
                {"ip": "10.118.57.142", "sensor": "Memoria"},
                {"ip": "10.53.34.130"},
            ],
            returns=(
                "Texto formateado con cada ticket en líneas separadas. "
                "Cada ticket incluye: ID, alerta, detalle y acción correctiva."
            ),
        )

    async def execute(self, **kwargs: Any) -> ToolResult:
        t0 = time.perf_counter()

        ip: str = kwargs.get("ip", "").strip()
        sensor: str = kwargs.get("sensor", "").strip()

        if not ip:
            return ToolResult.error_result(
                error="El parámetro 'ip' es requerido.",
                execution_time_ms=0,
            )

        try:
            # Si no viene sensor, intentar resolverlo
            if not sensor:
                # 1. Buscar en alertas activas
                events = await self._repo.get_active_events(ip=ip)
                if events:
                    sensor = events[0].sensor or ""
                    logger.debug(f"GetHistoricalTicketsTool: sensor resuelto desde alerta activa → '{sensor}'")

                # 2. Sin alerta activa: buscar sensores recientes en el historial PRTG
                if not sensor:
                    sensores_recientes = await self._repo.get_recent_sensors_by_ip(ip=ip)
                    if len(sensores_recientes) == 1:
                        # Solo un sensor → usarlo automáticamente
                        sensor = sensores_recientes[0]["sensor"]
                        logger.debug(f"GetHistoricalTicketsTool: sensor único en historial → '{sensor}'")
                    elif len(sensores_recientes) > 1:
                        # Varios sensores → preguntar al usuario
                        elapsed = (time.perf_counter() - t0) * 1000
                        lista = "\n".join(
                            f"- {s['sensor']} (última vez: {s['ultima_fecha'][:10]})"
                            for s in sensores_recientes
                        )
                        return ToolResult.success_result(
                            data=(
                                f"El equipo {ip} no tiene alerta activa, pero tiene varios sensores "
                                f"en el historial. ¿Sobre cuál querés buscar el historial de tickets?\n\n"
                                f"{lista}"
                            ),
                            execution_time_ms=elapsed,
                            metadata={"total_tickets": 0, "sensores_disponibles": [s["sensor"] for s in sensores_recientes]},
                        )

            tickets = await self._repo.get_historical_tickets(ip=ip, sensor=sensor)
            elapsed = (time.perf_counter() - t0) * 1000

            logger.info(f"GetHistoricalTicketsTool: {len(tickets)} tickets para {ip} (sensor='{sensor}') en {elapsed:.0f}ms")

            if not tickets:
                # Fallback: si no hay tickets de mesa de ayuda, mostrar historial PRTG
                prtg_events = await self._repo.get_prtg_history_by_ip(ip=ip)
                elapsed = (time.perf_counter() - t0) * 1000

                if not prtg_events:
                    sensor_info = f" (sensor: {sensor})" if sensor else ""
                    return ToolResult.success_result(
                        data=f"Sin historial de incidentes para {ip}{sensor_info}.",
                        execution_time_ms=elapsed,
                        metadata={"total_tickets": 0, "total_prtg_events": 0},
                    )

                equipo = prtg_events[0].get("equipo", ip)
                lines = [f"Sin tickets de mesa de ayuda para {ip}. Historial PRTG de {equipo}:\n"]
                for ev in prtg_events:
                    fecha = ev["fecha_insercion"][:10] if ev["fecha_insercion"] else "?"
                    sensor_ev = ev["sensor"] or "?"
                    status_ev = ev["status"] or "?"
                    downtime = f" | Duración: {ev['down_time']}" if ev["down_time"] else ""
                    mensaje = ev["mensaje"][:80] + "..." if len(ev.get("mensaje", "")) > 80 else ev.get("mensaje", "")
                    lines.append(f"- {fecha} | {sensor_ev} | {status_ev}{downtime}")
                    if mensaje:
                        lines.append(f"  {mensaje}")

                lines.append(f"\n_Total: {len(prtg_events)} eventos PRTG_")

                return ToolResult.success_result(
                    data="\n".join(lines),
                    execution_time_ms=elapsed,
                    metadata={"total_tickets": 0, "total_prtg_events": len(prtg_events)},
                )

            sensor_info = f" (sensor: {sensor})" if sensor else ""
            lines = [f"{len(tickets)} ticket(s) histórico(s) para {ip}{sensor_info}:\n"]
            for t in tickets:
                lines.append(f"#{t.ticket} — {t.alerta}")
                if t.detalle:
                    lines.append(f"  Detalle: {t.detalle}")
                if t.accion_formateada:
                    lines.append(f"  Acción correctiva: {t.accion_formateada}")
                lines.append("")

            return ToolResult.success_result(
                data="\n".join(lines),
                execution_time_ms=elapsed,
                metadata={"total_tickets": len(tickets)},
            )

        except Exception as e:
            elapsed = (time.perf_counter() - t0) * 1000
            logger.exception(f"GetHistoricalTicketsTool: error para {ip}: {e}")
            return ToolResult.error_result(
                error=f"Error al obtener tickets históricos: {e}",
                execution_time_ms=elapsed,
            )
