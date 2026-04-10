"""
GetAlertDetailTool — Contexto completo de una alerta por IP.

Combina en paralelo: tickets históricos, template, matriz de
escalamiento y contactos de área. Retorna datos estructurados (dict).
"""

import asyncio
import logging
import time
from typing import Any

from src.agents.tools.base import BaseTool, ToolCategory, ToolDefinition, ToolParameter, ToolResult
from src.domain.alerts.alert_repository import AlertRepository

logger = logging.getLogger(__name__)


class GetAlertDetailTool(BaseTool):
    """
    Retorna el contexto completo de una alerta dado su IP.

    Enriquece con tickets históricos, template, matriz de escalamiento
    y datos de contacto de las áreas responsables, todo en paralelo.

    Usar cuando el usuario quiere el análisis completo de un equipo
    específico, no solo el resumen de la alerta.
    """

    is_read_only: bool = True
    is_destructive: bool = False
    is_concurrency_safe: bool = True

    def __init__(self, repo: AlertRepository) -> None:
        self._repo = repo

    @property
    def definition(self) -> ToolDefinition:
        return ToolDefinition(
            name="get_alert_detail",
            description=(
                "Retorna el contexto completo de una alerta dado su IP: "
                "estado actual del sensor, tickets históricos, template de aplicación, "
                "matriz de escalamiento completa y contactos de las áreas responsables. "
                "Usar cuando el usuario pide el detalle completo de una alerta específica o "
                "quiere saber todo sobre un equipo: quién atiende, historial y a quién escalar."
            ),
            category=ToolCategory.MONITORING,
            parameters=[
                ToolParameter(
                    name="ip",
                    param_type="string",
                    description="IP del equipo a analizar",
                    required=True,
                    examples=["10.118.57.142", "10.53.34.130"],
                ),
                ToolParameter(
                    name="sensor",
                    param_type="string",
                    description="Nombre del sensor para filtrar tickets históricos (opcional)",
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
                "Dict completo con: evento (estado actual), tickets (historial), "
                "template, matriz de escalamiento (niveles) y contactos de áreas."
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
            # ── 1. Obtener evento activo para la IP ────────────────────────
            events = await self._repo.get_active_events(ip=ip)
            evento = events[0] if events else None

            # ── 2. Enriquecimiento en paralelo ─────────────────────────────
            sensor_key = sensor or (evento.sensor if evento else "")

            tickets_task = asyncio.create_task(
                self._repo.get_historical_tickets(ip=ip, sensor=sensor_key)
            )
            template_id_task = asyncio.create_task(
                self._repo.get_template_id(ip=ip)
            )

            tickets, template_id_row = await asyncio.gather(tickets_task, template_id_task)

            template = None
            matriz = []
            contacto_atendedora = None
            contacto_administradora = None

            if template_id_row:
                tid = template_id_row.get("idTemplate")
                instancia = template_id_row.get("instancia", "")
                usar_ekt = str(instancia).upper() == "COMERCIO"

                if tid:
                    template, matriz = await asyncio.gather(
                        self._repo.get_template_info(tid, usar_ekt=usar_ekt),
                        self._repo.get_escalation_matrix(tid, usar_ekt=usar_ekt),
                    )

            # Contactos de área (si el evento tiene IDs de gerencia)
            if evento:
                contacto_tasks = []
                usar_ekt = evento.es_ekt

                contacto_tasks.append(
                    self._repo.get_contacto_gerencia(evento.id_area_atendedora, usar_ekt=usar_ekt)
                    if evento.id_area_atendedora else asyncio.sleep(0)
                )
                contacto_tasks.append(
                    self._repo.get_contacto_gerencia(evento.id_area_administradora, usar_ekt=usar_ekt)
                    if evento.id_area_administradora else asyncio.sleep(0)
                )

                results = await asyncio.gather(*contacto_tasks, return_exceptions=True)
                contacto_atendedora = results[0] if not isinstance(results[0], (Exception, type(None))) else None
                contacto_administradora = results[1] if not isinstance(results[1], (Exception, type(None))) else None

            elapsed = (time.perf_counter() - t0) * 1000

            # ── 3. Serializar a dict ───────────────────────────────────────
            data = {
                "ip": ip,
                "evento": {
                    "equipo": evento.equipo,
                    "ip": evento.ip,
                    "sensor": evento.sensor,
                    "status": evento.status,
                    "prioridad": evento.prioridad,
                    "mensaje": evento.mensaje,
                    "area_atendedora": evento.area_atendedora,
                    "responsable_atendedor": evento.responsable_atendedor,
                    "area_administradora": evento.area_administradora,
                    "responsable_administrador": evento.responsable_administrador,
                } if evento else None,
                "tickets": [
                    {
                        "ticket": t.ticket,
                        "alerta": t.alerta,
                        "detalle": t.detalle,
                        "accion_correctiva": t.accion_formateada,
                    }
                    for t in tickets[:15]
                ],
                "total_tickets": len(tickets),
                "template": {
                    "aplicacion": template.aplicacion,
                    "gerencia_desarrollo": template.gerencia_desarrollo,
                } if template else None,
                "escalamiento": [
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
                ],
                "contacto_atendedora": {
                    "gerencia": contacto_atendedora.gerencia,
                    "responsable": evento.responsable_atendedor if evento else "",
                    "correos": contacto_atendedora.correos,
                    "extensiones": contacto_atendedora.extensiones,
                } if contacto_atendedora else None,
                "contacto_administradora": {
                    "gerencia": contacto_administradora.gerencia,
                    "responsable": evento.responsable_administrador if evento else "",
                    "correos": contacto_administradora.correos,
                    "extensiones": contacto_administradora.extensiones,
                } if contacto_administradora else None,
            }

            logger.info(
                f"GetAlertDetailTool: {ip} — {len(tickets)} tickets, "
                f"template={'sí' if template else 'no'}, "
                f"escalamiento={len(matriz)} niveles en {elapsed:.0f}ms"
            )

            return ToolResult.success_result(
                data=data,
                execution_time_ms=elapsed,
                metadata={
                    "tickets_count": len(tickets),
                    "escalamiento_niveles": len(matriz),
                    "tiene_template": template is not None,
                },
            )

        except Exception as e:
            elapsed = (time.perf_counter() - t0) * 1000
            logger.exception(f"GetAlertDetailTool: error para {ip}: {e}")
            return ToolResult.error_result(
                error=f"Error al obtener detalle de alerta: {e}",
                execution_time_ms=elapsed,
            )
