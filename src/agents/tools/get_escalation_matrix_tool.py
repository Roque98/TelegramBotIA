"""
GetEscalationMatrixTool — Matriz de escalamiento + contactos de área para un equipo por IP.

Retorna datos estructurados (dict) — sin LLM interno.
"""

import asyncio
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
                "Retorna la matriz de escalamiento de un equipo dado su IP, incluyendo "
                "los contactos de las áreas responsables (atendedora y administradora). "
                "Incluye niveles de escalamiento con nombre, puesto, extensión, celular, correo y tiempo de respuesta. "
                "Usar cuando el usuario pregunta a quién escalar, con quién reportar una alerta, "
                "quién atiende un equipo o necesita los contactos de escalamiento."
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
                "Dict con 'titulo' (formato '📌 #id nombre | instancia'), 'ip', "
                "'template_id', 'template', 'instancia' (ABCEKT o ABCMASplus), "
                "'gerencia_desarrollo', 'area_atendedora', 'area_administradora' y "
                "'niveles' (list). Cada nivel tiene: nivel, nombre, puesto, extension, celular, "
                "correo, tiempo_escalacion. Usar 'titulo' como encabezado del resultado."
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
            # Obtener template_id e inventario en paralelo — el inventario es
            # la fuente de verdad para área atendedora y administradora.
            template_id_row, inventario = await asyncio.gather(
                self._repo.get_template_id(ip=ip),
                self._repo.get_inventory_by_ip(ip=ip),
            )

            if not template_id_row:
                elapsed = (time.perf_counter() - t0) * 1000
                return ToolResult.success_result(
                    data={
                        "ip": ip,
                        "template": None,
                        "gerencia_desarrollo": None,
                        "area_atendedora": None,
                        "area_administradora": None,
                        "niveles": [],
                        "mensaje": "No se encontró template asociado a esta IP.",
                    },
                    execution_time_ms=elapsed,
                )

            tid = template_id_row.get("idTemplate")
            instancia = template_id_row.get("instancia", "")
            usar_ekt = str(instancia).upper() == "COMERCIO"

            if not tid:
                elapsed = (time.perf_counter() - t0) * 1000
                return ToolResult.success_result(
                    data={
                        "ip": ip,
                        "template": None,
                        "gerencia_desarrollo": None,
                        "area_atendedora": None,
                        "area_administradora": None,
                        "niveles": [],
                        "mensaje": "No se encontró template asociado a esta IP.",
                    },
                    execution_time_ms=elapsed,
                )

            # Obtener template y matriz en paralelo
            template, matriz = await asyncio.gather(
                self._repo.get_template_info(tid, usar_ekt=usar_ekt),
                self._repo.get_escalation_matrix(tid, usar_ekt=usar_ekt),
            )

            # IDs de área desde el inventario (fuente de verdad)
            logger.info(
                f"GetEscalationMatrixTool: inventario para {ip} → "
                f"inventario={inventario!r} "
                f"id_atendedora={inventario.id_area_atendedora if inventario else None} "
                f"id_administradora={inventario.id_area_administradora if inventario else None}"
            )
            id_atendedora    = inventario.id_area_atendedora    if inventario else None
            id_administradora = inventario.id_area_administradora if inventario else None

            contacto_atendedora_task = (
                self._repo.get_contacto_gerencia(id_atendedora, usar_ekt=usar_ekt)
                if id_atendedora else asyncio.sleep(0)
            )
            contacto_administradora_task = (
                self._repo.get_contacto_gerencia(id_administradora, usar_ekt=usar_ekt)
                if id_administradora else asyncio.sleep(0)
            )

            contacto_atendedora, contacto_administradora = await asyncio.gather(
                contacto_atendedora_task,
                contacto_administradora_task,
            )

            if isinstance(contacto_atendedora, Exception):
                contacto_atendedora = None
            if isinstance(contacto_administradora, Exception):
                contacto_administradora = None

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

            def _contacto_dict(c) -> dict | None:
                if c is None or isinstance(c, type(None)):
                    return None
                try:
                    return {
                        "gerencia": c.gerencia,
                        "responsable": c.responsable,
                        "correos": c.correos,
                        "extensiones": c.extensiones,
                    }
                except AttributeError:
                    return None

            logger.info(
                f"GetEscalationMatrixTool: {len(niveles)} niveles para {ip} "
                f"(template={template.aplicacion if template else 'N/A'}) en {elapsed:.0f}ms"
            )

            etiqueta = template.etiqueta if template else ("ABCEKT" if usar_ekt else "ABCMASplus")
            nombre_template = template.aplicacion if template else None
            titulo = f"📌 #{tid} {nombre_template} | {etiqueta}" if nombre_template else f"📌 #{tid} | {etiqueta}"

            return ToolResult.success_result(
                data={
                    "titulo": titulo,
                    "ip": ip,
                    "template_id": tid,
                    "template": nombre_template,
                    "instancia": etiqueta,
                    "gerencia_desarrollo": template.gerencia_desarrollo if template else None,
                    "area_atendedora": _contacto_dict(contacto_atendedora),
                    "area_administradora": _contacto_dict(contacto_administradora),
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
