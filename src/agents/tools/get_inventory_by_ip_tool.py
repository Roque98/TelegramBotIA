import logging
import time
from typing import Any

from src.agents.tools.base import BaseTool, ToolCategory, ToolDefinition, ToolParameter, ToolResult
from src.domain.alerts.alert_repository import AlertRepository

logger = logging.getLogger(__name__)


class GetInventoryByIpTool(BaseTool):
    """
    Retorna datos de inventario para una o varias IPs.

    Busca en EquiposFisicos y MaquinasVirtuales (BAZ y EKT) usando SPs
    de lista, permitiendo consultar múltiples equipos en una sola llamada.
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
                "Busca uno o varios equipos en el inventario por dirección IP. "
                "Acepta una IP o varias separadas por coma. "
                "Retorna área atendedora, área administradora y datos técnicos "
                "(hostname, sistema operativo, ambiente, capa, impacto, urgencia, prioridad). "
                "Busca en equipos físicos y máquinas virtuales, instancias BAZ y EKT. "
                "Usar cuando se necesita saber qué área es responsable de un equipo "
                "o cuando el evento de alerta no trae las áreas completas."
            ),
            category=ToolCategory.MONITORING,
            parameters=[
                ToolParameter(
                    name="ips",
                    param_type="string",
                    description="Una o varias IPs separadas por coma",
                    required=True,
                    examples=["10.80.133.56", "10.80.133.56,10.118.57.142"],
                ),
            ],
            examples=[
                {"ips": "10.80.133.56"},
                {"ips": "10.80.133.56,10.118.57.142,192.168.1.10"},
            ],
            returns=(
                "Lista de equipos encontrados. Cada elemento contiene: 'ip', 'hostname', "
                "'area_atendedora', 'area_administradora', 'fuente' (Fisico|Virtual), "
                "'tipo_equipo', 'version_os', 'status', 'capa', 'ambiente', 'impacto', "
                "'urgencia', 'prioridad', 'negocio'. "
                "Incluye lista 'no_encontradas' con las IPs sin resultado."
            ),
            usage_hint="Para buscar datos de inventario de uno o varios equipos por IP: usa `get_inventory_by_ip`",
        )

    async def execute(self, **kwargs: Any) -> ToolResult:
        t0 = time.perf_counter()

        raw = kwargs.get("ips", "").strip()
        if not raw:
            return ToolResult.error_result(error="El parámetro 'ips' es requerido.", execution_time_ms=0)

        ips = [ip.strip() for ip in raw.split(",") if ip.strip()]
        if not ips:
            return ToolResult.error_result(error="El parámetro 'ips' no contiene IPs válidas.", execution_time_ms=0)

        try:
            items = await self._repo.get_inventory_by_ip_list(ips)
            elapsed = (time.perf_counter() - t0) * 1000

            found_ips = {item.ip for item in items}
            not_found = [ip for ip in ips if ip not in found_ips]

            logger.info(
                f"GetInventoryByIpTool: {len(items)}/{len(ips)} encontradas en {elapsed:.0f}ms"
            )

            return ToolResult.success_result(
                data={
                    "equipos": [
                        {
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
                        }
                        for item in items
                    ],
                    "no_encontradas": not_found,
                },
                execution_time_ms=elapsed,
            )

        except Exception as e:
            elapsed = (time.perf_counter() - t0) * 1000
            logger.exception(f"GetInventoryByIpTool: error para ips={raw}: {e}")
            return ToolResult.error_result(
                error=f"Error al buscar equipos en inventario: {e}",
                execution_time_ms=elapsed,
            )
