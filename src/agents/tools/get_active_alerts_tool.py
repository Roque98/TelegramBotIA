"""
GetActiveAlertsTool — Lista alertas activas de PRTG con filtros.

Retorna datos estructurados (dict) — sin LLM interno.
El agente ReAct formatea la respuesta con los datos recibidos.
"""

import logging
import time
from typing import Any, Optional

from src.agents.tools.base import BaseTool, ToolCategory, ToolDefinition, ToolParameter, ToolResult
from src.domain.alerts.alert_repository import AlertRepository

logger = logging.getLogger(__name__)


class GetActiveAlertsTool(BaseTool):
    """
    Lista alertas activas de PRTG con filtros opcionales.

    Retorna un dict estructurado con el total y la lista de alertas,
    ordenadas por prioridad descendente.
    """

    is_read_only: bool = True
    is_destructive: bool = False
    is_concurrency_safe: bool = True

    def __init__(self, repo: AlertRepository) -> None:
        self._repo = repo

    @property
    def definition(self) -> ToolDefinition:
        return ToolDefinition(
            name="get_active_alerts",
            description=(
                "Lista alertas activas de monitoreo PRTG. "
                "Retorna el total y los datos de cada alerta (equipo, IP, sensor, status, prioridad, área responsable). "
                "Usar cuando el usuario pregunta si hay alertas, qué equipos están caídos o quiere ver el resumen de incidentes activos."
            ),
            category=ToolCategory.MONITORING,
            parameters=[
                ToolParameter(
                    name="ip",
                    param_type="string",
                    description="Filtrar por IP exacta del equipo (opcional)",
                    required=False,
                    default=None,
                    examples=["10.53.34.130"],
                ),
                ToolParameter(
                    name="equipo",
                    param_type="string",
                    description="Filtrar por nombre del equipo, búsqueda parcial (opcional)",
                    required=False,
                    default=None,
                    examples=["SWITCH-CORE", "FIREWALL"],
                ),
                ToolParameter(
                    name="solo_down",
                    param_type="boolean",
                    description="Si true, solo incluye equipos con status 'down' (opcional, default false)",
                    required=False,
                    default=False,
                    examples=["true", "false"],
                ),
            ],
            examples=[
                {"solo_down": "true"},
                {"ip": "10.1.2.3"},
            ],
            returns=(
                "Dict con 'total' (int) y 'alertas' (list). Cada alerta tiene: "
                "equipo, ip, sensor, status, prioridad, mensaje, area_atendedora, "
                "responsable_atendedor, area_administradora, responsable_administrador."
            ),
        )

    async def execute(self, **kwargs: Any) -> ToolResult:
        t0 = time.perf_counter()

        ip: Optional[str] = kwargs.get("ip") or None
        equipo: Optional[str] = kwargs.get("equipo") or None
        solo_down_raw = kwargs.get("solo_down", False)
        solo_down = solo_down_raw if isinstance(solo_down_raw, bool) else str(solo_down_raw).lower() == "true"

        try:
            try:
                events = await self._repo.get_active_events(
                    ip=ip, equipo=equipo, solo_down=solo_down
                )
            except ConnectionError as conn_err:
                elapsed = (time.perf_counter() - t0) * 1000
                logger.error(f"GetActiveAlertsTool: error de conectividad: {conn_err}")
                return ToolResult.error_result(
                    error=(
                        "No se pudo conectar a la instancia de monitoreo (BAZ_CDMX/EKT). "
                        f"Detalle: {conn_err}"
                    ),
                    execution_time_ms=elapsed,
                )

            elapsed = (time.perf_counter() - t0) * 1000

            if not events:
                return ToolResult.success_result(
                    data={"total": 0, "alertas": []},
                    execution_time_ms=elapsed,
                    metadata={"filtros": {"ip": ip, "equipo": equipo, "solo_down": solo_down}},
                )

            alertas = [
                {
                    "equipo": e.equipo,
                    "ip": e.ip,
                    "sensor": e.sensor,
                    "status": e.status,
                    "prioridad": e.prioridad,
                    "mensaje": e.mensaje,
                    "area_atendedora": e.area_atendedora,
                    "responsable_atendedor": e.responsable_atendedor,
                    "area_administradora": e.area_administradora,
                    "responsable_administrador": e.responsable_administrador,
                    "origen": e.origen,
                }
                for e in events
            ]

            logger.info(f"GetActiveAlertsTool: {len(alertas)} alertas encontradas en {elapsed:.0f}ms")
            return ToolResult.success_result(
                data={"total": len(alertas), "alertas": alertas},
                execution_time_ms=elapsed,
                metadata={"origen": events[0].origen if events else None},
            )

        except Exception as e:
            elapsed = (time.perf_counter() - t0) * 1000
            logger.exception(f"GetActiveAlertsTool: error inesperado: {e}")
            return ToolResult.error_result(
                error=f"Error al obtener alertas activas: {e}",
                execution_time_ms=elapsed,
            )
