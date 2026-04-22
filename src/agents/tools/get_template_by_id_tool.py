"""
GetTemplateByIdTool — Detalle completo de un template por su ID.

Llama a ABCMASplus.dbo.Template_GetById (con fallback _EKT) y retorna
los campos clave: aplicación, gerencia atendedora, gerencia de desarrollo, etc.
"""

import logging
import time
from typing import Any

from src.agents.tools.base import BaseTool, ToolCategory, ToolDefinition, ToolParameter, ToolResult
from src.domain.alerts.alert_repository import AlertRepository

logger = logging.getLogger(__name__)


class GetTemplateByIdTool(BaseTool):
    """
    Retorna los datos completos de un template dado su ID.

    Incluye la aplicación, gerencia atendedora, gerencia de desarrollo
    y otros atributos del template registrado en ABCMASplus.
    """

    is_read_only: bool = True
    is_destructive: bool = False
    is_concurrency_safe: bool = True

    def __init__(self, repo: AlertRepository) -> None:
        self._repo = repo

    @property
    def definition(self) -> ToolDefinition:
        return ToolDefinition(
            name="get_template_by_id",
            description=(
                "Retorna los datos completos de un template de monitoreo dado su ID numérico. "
                "Incluye nombre de aplicación, gerencia atendedora, gerencia de desarrollo, "
                "ambiente, negocio y otros atributos del template. "
                "Usar cuando se conoce el ID del template y se necesita obtener sus detalles."
            ),
            category=ToolCategory.MONITORING,
            parameters=[
                ToolParameter(
                    name="template_id",
                    param_type="integer",
                    description="ID numérico del template a consultar",
                    required=True,
                    examples=["15037", "1234"],
                ),
                ToolParameter(
                    name="usar_ekt",
                    param_type="boolean",
                    description="Si true, consulta la instancia EKT/COMERCIO primero (default false)",
                    required=False,
                ),
            ],
            examples=[
                {"template_id": 15037},
                {"template_id": 15037, "usar_ekt": False},
            ],
            returns=(
                "Dict con 'template_id', 'aplicacion', 'gerencia_atendedora', "
                "'id_gerencia_atendedora', 'gerencia_desarrollo', 'id_gerencia_desarrollo', "
                "'ambiente', 'negocio', 'tipo_template', 'es_aws', 'es_vertical'."
            ),
            usage_hint="Para datos de un template cuando ya tenés el ID numérico: usa `get_template_by_id`",
        )

    async def execute(self, **kwargs: Any) -> ToolResult:
        t0 = time.perf_counter()

        template_id = kwargs.get("template_id")
        usar_ekt: bool = bool(kwargs.get("usar_ekt", False))

        if template_id is None:
            return ToolResult.error_result(
                error="El parámetro 'template_id' es requerido.",
                execution_time_ms=0,
            )

        try:
            template_id = int(template_id)
        except (ValueError, TypeError):
            return ToolResult.error_result(
                error=f"'template_id' debe ser un entero, recibido: {template_id!r}",
                execution_time_ms=0,
            )

        try:
            template = await self._repo.get_template_by_id(template_id, usar_ekt=usar_ekt)
            elapsed = (time.perf_counter() - t0) * 1000

            if not template:
                return ToolResult.success_result(
                    data={
                        "template_id": template_id,
                        "mensaje": f"No se encontró template con ID {template_id}.",
                    },
                    execution_time_ms=elapsed,
                )

            logger.info(f"GetTemplateByIdTool: template_id={template_id} → {template.aplicacion} ({elapsed:.0f}ms)")

            return ToolResult.success_result(
                data={
                    "template_id": template_id,
                    "aplicacion": template.aplicacion,
                    "gerencia_atendedora": template.gerencia_atendedora,
                    "id_gerencia_atendedora": template.atendedor_id_gerencia,
                    "gerencia_desarrollo": template.gerencia_desarrollo,
                    "id_gerencia_desarrollo": template.id_gerencia_desarrollo,
                    "ambiente": template.ambiente,
                    "negocio": template.negocio,
                    "tipo_template": template.tipo_template,
                    "es_aws": template.es_aws,
                    "es_vertical": template.es_vertical,
                },
                execution_time_ms=elapsed,
            )

        except Exception as e:
            elapsed = (time.perf_counter() - t0) * 1000
            logger.exception(f"GetTemplateByIdTool: error para template_id={template_id}: {e}")
            return ToolResult.error_result(
                error=f"Error al obtener template: {e}",
                execution_time_ms=elapsed,
            )
