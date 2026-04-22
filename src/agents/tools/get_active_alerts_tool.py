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
                "Dict con banco_total, ekt_total, banco (lista de {ip, sensor}) "
                "y ekt (lista de {ip, sensor})."
            ),
            usage_hint="Para alertas activas o equipos caídos/en warning: usa `get_active_alerts`",
        )

    async def execute(self, **kwargs: Any) -> ToolResult:
        t0 = time.perf_counter()

        ip: Optional[str] = kwargs.get("ip") or None
        equipo: Optional[str] = kwargs.get("equipo") or None
        solo_down_raw = kwargs.get("solo_down", False)
        solo_down = solo_down_raw if isinstance(solo_down_raw, bool) else str(solo_down_raw).lower() == "true"

        try:
            try:
                eventos_banco, eventos_ekt = await self._repo.get_active_events_all(
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
            total = len(eventos_banco) + len(eventos_ekt)

            if total == 0:
                return ToolResult.success_result(
                    data="Sin alertas activas para los filtros indicados.",
                    execution_time_ms=elapsed,
                    metadata={"total": 0},
                )

            logger.info(f"GetActiveAlertsTool: {total} alertas (Banco={len(eventos_banco)}, EKT={len(eventos_ekt)}) en {elapsed:.0f}ms")
            return ToolResult.success_result(
                data={
                    "banco_total": len(eventos_banco),
                    "ekt_total": len(eventos_ekt),
                    "banco": [{"ip": e.ip, "sensor": e.sensor} for e in eventos_banco],
                    "ekt": [{"ip": e.ip, "sensor": e.sensor} for e in eventos_ekt],
                },
                execution_time_ms=elapsed,
                metadata={"total": total},
            )

        except Exception as e:
            elapsed = (time.perf_counter() - t0) * 1000
            logger.exception(f"GetActiveAlertsTool: error inesperado: {e}")
            return ToolResult.error_result(
                error=f"Error al obtener alertas activas: {e}",
                execution_time_ms=elapsed,
            )
