"""
GetContactoGerenciaTool — Datos de contacto de una gerencia por su ID.

Llama a ABCMASplus.dbo.Contacto_GetByIdGerencia (con variante _EKT) y retorna
el correo y extensiones del área responsable (atendedora o administradora).
"""

import logging
import time
from typing import Any

from src.agents.tools.base import BaseTool, ToolCategory, ToolDefinition, ToolParameter, ToolResult
from src.domain.alerts.alert_repository import AlertRepository

logger = logging.getLogger(__name__)


class GetContactoGerenciaTool(BaseTool):
    """
    Retorna los datos de contacto (correo y extensiones) de una gerencia dado su ID.

    Usar cuando se conoce el ID de área atendedora o administradora y se necesita
    obtener el correo electrónico y extensiones telefónicas del área responsable.
    """

    is_read_only: bool = True
    is_destructive: bool = False
    is_concurrency_safe: bool = True

    def __init__(self, repo: AlertRepository) -> None:
        self._repo = repo

    @property
    def definition(self) -> ToolDefinition:
        return ToolDefinition(
            name="get_contacto_gerencia",
            description=(
                "Retorna los datos de contacto (correo electrónico y extensiones telefónicas) "
                "de una gerencia dado su ID numérico. "
                "Usar cuando se tiene el idAreaAtendedora o idAreaAdministradora de un evento "
                "y se necesita obtener el correo y teléfono del área responsable."
            ),
            category=ToolCategory.MONITORING,
            parameters=[
                ToolParameter(
                    name="id_gerencia",
                    param_type="integer",
                    description="ID numérico de la gerencia (idAreaAtendedora o idAreaAdministradora)",
                    required=True,
                    examples=["5", "8", "42"],
                ),
                ToolParameter(
                    name="usar_ekt",
                    param_type="boolean",
                    description="Si true, consulta la instancia EKT/COMERCIO (default false)",
                    required=False,
                ),
            ],
            examples=[
                {"id_gerencia": 5},
                {"id_gerencia": 8, "usar_ekt": False},
                {"id_gerencia": 42, "usar_ekt": True},
            ],
            returns=(
                "Dict con 'id_gerencia', 'gerencia', 'responsable', 'correos', 'extensiones'. "
                "'responsable' es el nombre del gerente/responsable del área. "
                "'correos' y 'extensiones' pueden ser cadenas vacías si no hay datos."
            ),
        )

    async def execute(self, **kwargs: Any) -> ToolResult:
        t0 = time.perf_counter()

        id_gerencia = kwargs.get("id_gerencia")
        usar_ekt: bool = bool(kwargs.get("usar_ekt", False))

        if id_gerencia is None:
            return ToolResult.error_result(
                error="El parámetro 'id_gerencia' es requerido.",
                execution_time_ms=0,
            )

        try:
            id_gerencia = int(id_gerencia)
        except (ValueError, TypeError):
            return ToolResult.error_result(
                error=f"'id_gerencia' debe ser un entero, recibido: {id_gerencia!r}",
                execution_time_ms=0,
            )

        try:
            contacto = await self._repo.get_contacto_gerencia(id_gerencia, usar_ekt=usar_ekt)
            elapsed = (time.perf_counter() - t0) * 1000

            if not contacto:
                return ToolResult.success_result(
                    data={
                        "id_gerencia": id_gerencia,
                        "mensaje": f"No se encontraron datos de contacto para gerencia ID {id_gerencia}.",
                    },
                    execution_time_ms=elapsed,
                )

            logger.info(
                f"GetContactoGerenciaTool: id_gerencia={id_gerencia} → {contacto.gerencia} ({elapsed:.0f}ms)"
            )

            return ToolResult.success_result(
                data={
                    "id_gerencia": id_gerencia,
                    "gerencia": contacto.gerencia,
                    "responsable": contacto.responsable,
                    "correos": contacto.correos,
                    "extensiones": contacto.extensiones,
                },
                execution_time_ms=elapsed,
            )

        except Exception as e:
            elapsed = (time.perf_counter() - t0) * 1000
            logger.exception(f"GetContactoGerenciaTool: error para id_gerencia={id_gerencia}: {e}")
            return ToolResult.error_result(
                error=f"Error al obtener contacto de gerencia: {e}",
                execution_time_ms=elapsed,
            )
