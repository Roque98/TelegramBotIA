"""
GetEscalationMatrixTool — Matriz de escalamiento para un equipo por IP.

Retorna datos estructurados (dict) — sin LLM interno.
"""

import logging
import time
from typing import Any

from src.agents.tools.base import BaseTool, ToolCategory, ToolDefinition, ToolParameter, ToolResult
from src.domain.alerts.alert_repository import AlertRepository

logger = logging.getLogger(__name__)


class GetEscalationMatrixTool(BaseTool):
    """
    Retorna la matriz de escalamiento para un equipo dado su IP.

    Internamente busca el template asociado a la IP y luego
    obtiene los niveles de escalamiento con nombre, puesto y contacto.
    """

    is_read_only: bool = True
    is_destructive: bool = False
    is_concurrency_safe: bool = True

    def __init__(self, repo: AlertRepository) -> None:
        self._repo = repo

    @property
    def definition(self) -> ToolDefinition:
        return ToolDefinition(
            name="get_escalation_matrix",
            description=(
                "Retorna la matriz de escalamiento de un equipo dado su IP. "
                "Incluye los niveles de escalamiento con nombre, puesto, extensión, celular, correo y tiempo de respuesta. "
                "Usar cuando el usuario pregunta a quién escalar, quién atiende una alerta o "
                "necesita los contactos de escalamiento para un equipo."
            ),
            category=ToolCategory.MONITORING,
            parameters=[
                ToolParameter(
                    name="ip",
                    param_type="string",
                    description="IP del equipo para obtener su matriz de escalamiento",
                    required=True,
                    examples=["10.118.57.142", "10.53.34.130"],
                ),
            ],
            examples=[
                {"ip": "10.118.57.142"},
            ],
            returns=(
                "Dict con 'ip', 'template' (nombre de aplicación), 'gerencia_desarrollo' y "
                "'niveles' (list). Cada nivel tiene: nivel, nombre, puesto, extension, celular, "
                "correo, tiempo_escalacion."
            ),
        )

    async def execute(self, **kwargs: Any) -> ToolResult:
        t0 = time.perf_counter()

        ip: str = kwargs.get("ip", "").strip()

        if not ip:
            return ToolResult.error_result(
                error="El parámetro 'ip' es requerido.",
                execution_time_ms=0,
            )

        try:
            # Obtener template_id para la IP
            template_id_row = await self._repo.get_template_id(ip=ip)
            elapsed = (time.perf_counter() - t0) * 1000

            if not template_id_row:
                return ToolResult.success_result(
                    data={
                        "ip": ip,
                        "template": None,
                        "gerencia_desarrollo": None,
                        "niveles": [],
                        "mensaje": "No se encontró template asociado a esta IP.",
                    },
                    execution_time_ms=elapsed,
                )

            tid = template_id_row.get("idTemplate")
            instancia = template_id_row.get("instancia", "")
            usar_ekt = str(instancia).upper() == "COMERCIO"

            if not tid:
                return ToolResult.success_result(
                    data={
                        "ip": ip,
                        "template": None,
                        "gerencia_desarrollo": None,
                        "niveles": [],
                        "mensaje": "No se encontró template asociado a esta IP.",
                    },
                    execution_time_ms=elapsed,
                )

            import asyncio
            template, matriz = await asyncio.gather(
                self._repo.get_template_info(tid, usar_ekt=usar_ekt),
                self._repo.get_escalation_matrix(tid, usar_ekt=usar_ekt),
            )

            elapsed = (time.perf_counter() - t0) * 1000

            niveles = [
                {
                    "nivel": n.nivel,
                    "nombre": n.nombre,
                    "puesto": n.puesto,
                    "extension": n.extension,
                    "celular": n.celular,
                    "correo": n.correo,
                    "tiempo_escalacion": n.tiempo_escalacion,
                }
                for n in matriz
            ]

            logger.info(
                f"GetEscalationMatrixTool: {len(niveles)} niveles para {ip} "
                f"(template={template.aplicacion if template else 'N/A'}) en {elapsed:.0f}ms"
            )

            return ToolResult.success_result(
                data={
                    "ip": ip,
                    "template": template.aplicacion if template else None,
                    "gerencia_desarrollo": template.gerencia_desarrollo if template else None,
                    "niveles": niveles,
                },
                execution_time_ms=elapsed,
                metadata={"template_id": tid, "usar_ekt": usar_ekt},
            )

        except Exception as e:
            elapsed = (time.perf_counter() - t0) * 1000
            logger.exception(f"GetEscalationMatrixTool: error para {ip}: {e}")
            return ToolResult.error_result(
                error=f"Error al obtener matriz de escalamiento: {e}",
                execution_time_ms=elapsed,
            )
