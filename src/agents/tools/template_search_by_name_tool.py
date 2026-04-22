"""
TemplateSearchByNameTool — Busca templates por nombre de aplicación en banco y EKT.

Consulta ambas instancias en paralelo y retorna resultados con campo `instancia`
para que el agente pueda usar `usar_ekt` correctamente en llamadas posteriores.
"""

import logging
import time
from typing import Any

from src.agents.tools.base import BaseTool, ToolCategory, ToolDefinition, ToolParameter, ToolResult
from src.domain.alerts.alert_repository import AlertRepository

logger = logging.getLogger(__name__)


class TemplateSearchByNameTool(BaseTool):
    """
    Busca templates cuyo nombre de aplicación coincida parcialmente con el texto dado.

    Consulta BAZ y EKT en paralelo. Usar antes de get_escalation_matrix cuando
    el usuario menciona el nombre de una app pero no tiene el ID del template.
    """

    is_read_only: bool = True
    is_destructive: bool = False
    is_concurrency_safe: bool = True

    def __init__(self, repo: AlertRepository) -> None:
        self._repo = repo

    @property
    def definition(self) -> ToolDefinition:
        return ToolDefinition(
            name="template_search_by_name",
            description=(
                "Busca templates de monitoreo cuyo nombre de aplicación coincida parcialmente "
                "con el texto dado. Consulta banco (BAZ) y EKT en paralelo. "
                "Retorna lista de templates con su ID, aplicación, gerencia atendedora, "
                "gerencia de desarrollo, ambiente, negocio e instancia de origen (BAZ o EKT). "
                "Usar cuando el usuario menciona el nombre de una aplicación y se necesita "
                "encontrar su template para obtener la matriz de escalamiento u otros datos. "
                "Mínimo 2 caracteres de búsqueda requeridos."
            ),
            category=ToolCategory.MONITORING,
            parameters=[
                ToolParameter(
                    name="nombre",
                    param_type="string",
                    description="Nombre o parte del nombre de la aplicación a buscar (mínimo 2 caracteres)",
                    required=True,
                    examples=["Servicios", "Portal", "SAP", "CORE"],
                ),
            ],
            examples=[
                {"nombre": "Servicios"},
                {"nombre": "Portal web"},
                {"nombre": "SAP"},
            ],
            returns=(
                "Dict con 'templates' (lista de resultados), 'total' y 'mensaje'. "
                "Cada template contiene: 'template_id', 'aplicacion', 'instancia' (BAZ|EKT), "
                "'gerencia_atendedora', 'id_gerencia_atendedora', 'gerencia_desarrollo', "
                "'id_gerencia_desarrollo', 'ambiente', 'negocio', 'tipo_template', "
                "'es_aws', 'es_vertical'. "
                "Usar 'instancia' para saber si llamar a otras tools con usar_ekt=true (EKT) o false (BAZ)."
            ),
            usage_hint=(
                "Para encontrar el template de una aplicación por nombre (cuando no tenés el ID): "
                "usa `template_search_by_name`. "
                "Úsala antes de `get_escalation_matrix` cuando el usuario menciona el nombre de una app."
            ),
        )

    async def execute(self, **kwargs: Any) -> ToolResult:
        t0 = time.perf_counter()

        nombre: str = kwargs.get("nombre", "").strip()

        if not nombre:
            return ToolResult.error_result(
                error="El parámetro 'nombre' es requerido.",
                execution_time_ms=0,
            )
        if len(nombre) < 2:
            return ToolResult.error_result(
                error="El nombre debe tener al menos 2 caracteres para realizar la búsqueda.",
                execution_time_ms=0,
            )

        try:
            templates = await self._repo.get_templates_by_nombre(nombre)
            elapsed = (time.perf_counter() - t0) * 1000

            logger.info(
                f"TemplateSearchByNameTool: '{nombre}' → {len(templates)} resultados en {elapsed:.0f}ms"
            )

            if not templates:
                return ToolResult.success_result(
                    data={
                        "templates": [],
                        "total": 0,
                        "truncado": False,
                        "mensaje": f"No se encontraron templates con nombre '{nombre}'.",
                    },
                    execution_time_ms=elapsed,
                )

            truncado = len(templates) == 10  # 5 BAZ + 5 EKT = 10 significa que el SP llegó al límite

            return ToolResult.success_result(
                data={
                    "templates": [
                        {
                            "template_id": t.id_template,
                            "aplicacion": t.aplicacion,
                            "instancia": t.instancia,
                            "gerencia_atendedora": t.gerencia_atendedora,
                            "id_gerencia_atendedora": t.atendedor_id_gerencia,
                            "gerencia_desarrollo": t.gerencia_desarrollo,
                            "id_gerencia_desarrollo": t.id_gerencia_desarrollo,
                            "ambiente": t.ambiente,
                            "negocio": t.negocio,
                            "tipo_template": t.tipo_template,
                            "es_aws": t.es_aws,
                            "es_vertical": t.es_vertical,
                        }
                        for t in templates
                    ],
                    "total": len(templates),
                    "truncado": truncado,
                    "mensaje": (
                        f"Se muestran los primeros {len(templates)} resultados para '{nombre}'. "
                        f"Puede haber más — refiná la búsqueda para acotar los resultados."
                        if truncado else
                        f"{len(templates)} template(s) encontrado(s) para '{nombre}'."
                    ),
                },
                execution_time_ms=elapsed,
            )

        except Exception as e:
            elapsed = (time.perf_counter() - t0) * 1000
            logger.exception(f"TemplateSearchByNameTool: error para nombre='{nombre}': {e}")
            return ToolResult.error_result(
                error=f"Error al buscar templates por nombre: {e}",
                execution_time_ms=elapsed,
            )
