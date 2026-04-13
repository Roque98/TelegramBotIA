"""
GetInventoryByIpTool — Datos de inventario de un equipo por su IP.

Busca en EquiposFisicos y MaquinasVirtuales (BAZ y EKT) y retorna
área atendedora, área administradora y datos técnicos del equipo.
"""

import logging
import time
from typing import Any

from src.agents.tools.base import BaseTool, ToolCategory, ToolDefinition, ToolParameter, ToolResult
from src.domain.alerts.alert_repository import AlertRepository

logger = logging.getLogger(__name__)


class GetInventoryByIpTool(BaseTool):
    """
    Retorna los datos de inventario de un equipo dado su IP.

    Busca primero en EquiposFisicos (equipos físicos) y luego en
    MaquinasVirtuales (VMs), tanto en instancia BAZ como EKT.

    Útil para obtener el área atendedora y administradora real del
    inventario cuando no están disponibles en el evento de alerta.
    """

    is_read_only: bool = True
    is_destructive: bool = False
    is_concurrency_safe: bool = True

    def __init__(self, repo: AlertRepository) -> None:
        self._repo = repo

    @property
    def definition(self) -> ToolDefinition:
        return ToolDefinition(
            name="get_inventory_by_ip",
            description=(
                "Busca un equipo en el inventario por su dirección IP. "
                "Retorna el área atendedora, área administradora y datos técnicos "
                "(hostname, sistema operativo, ambiente, capa, impacto, urgencia, prioridad). "
                "Busca en equipos físicos y máquinas virtuales, instancias BAZ y EKT. "
                "Usar cuando se necesita saber qué área es responsable de un equipo "
                "o cuando el evento de alerta no trae las áreas completas."
            ),
            category=ToolCategory.MONITORING,
            parameters=[
                ToolParameter(
                    name="ip",
                    param_type="string",
                    description="Dirección IP del equipo a buscar en el inventario",
                    required=True,
                    examples=["10.80.133.56", "10.118.57.142", "192.168.1.10"],
                ),
            ],
            examples=[
                {"ip": "10.80.133.56"},
                {"ip": "10.118.57.142"},
            ],
            returns=(
                "Dict con 'ip', 'hostname', 'area_atendedora', 'area_administradora', "
                "'fuente' (Fisico|Virtual), 'tipo_equipo', 'version_os', 'status', "
                "'capa', 'ambiente', 'impacto', 'urgencia', 'prioridad', 'negocio'. "
                "Si no se encuentra, retorna 'mensaje' indicando que no existe en inventario."
            ),
        )

    async def execute(self, **kwargs: Any) -> ToolResult:
        t0 = time.perf_counter()

        ip = kwargs.get("ip", "").strip()

        if not ip:
            return ToolResult.error_result(
                error="El parámetro 'ip' es requerido.",
                execution_time_ms=0,
            )

        try:
            item = await self._repo.get_inventory_by_ip(ip)
            elapsed = (time.perf_counter() - t0) * 1000

            if not item:
                return ToolResult.success_result(
                    data={
                        "ip": ip,
                        "mensaje": f"No se encontró el equipo con IP {ip} en el inventario.",
                    },
                    execution_time_ms=elapsed,
                )

            logger.info(
                f"GetInventoryByIpTool: {ip} → {item.hostname} "
                f"({item.fuente}, atendedora={item.area_atendedora!r}) en {elapsed:.0f}ms"
            )

            return ToolResult.success_result(
                data={
                    "ip": item.ip,
                    "hostname": item.hostname,
                    "id_area_atendedora": item.id_area_atendedora,
                    "id_area_administradora": item.id_area_administradora,
                    "area_atendedora": item.area_atendedora,
                    "area_administradora": item.area_administradora,
                    "fuente": item.fuente,
                    "tipo_equipo": item.tipo_equipo,
                    "version_os": item.version_os,
                    "status": item.status,
                    "capa": item.capa,
                    "ambiente": item.ambiente,
                    "impacto": item.impacto,
                    "urgencia": item.urgencia,
                    "prioridad": item.prioridad,
                    "negocio": item.negocio,
                },
                execution_time_ms=elapsed,
            )

        except Exception as e:
            elapsed = (time.perf_counter() - t0) * 1000
            logger.exception(f"GetInventoryByIpTool: error para ip={ip}: {e}")
            return ToolResult.error_result(
                error=f"Error al buscar equipo en inventario: {e}",
                execution_time_ms=elapsed,
            )
