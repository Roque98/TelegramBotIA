"""
AlertAnalysisTool — Herramienta de análisis de alertas PRTG.

Flujo interno:
  1. Obtener eventos activos del repositorio (BAZ_CDMX → EKT fallback)
  2. Seleccionar el evento más crítico que coincida con el filtro
  3. Enriquecer: tickets históricos, template, matriz de escalamiento, contactos
  4. Construir prompt con AlertPromptBuilder
  5. Llamar al LLM (data_llm) para generar el análisis estructurado
  6. Retornar texto Markdown con DISCLAIMER

La tool devuelve la respuesta completa al ReActAgent como observación.
El agente la presenta al usuario sin modificaciones adicionales.
"""

import logging
import time
from typing import Any, Optional

from src.agents.tools.base import BaseTool, ToolCategory, ToolDefinition, ToolParameter, ToolResult
from src.domain.alerts.alert_entity import AlertContext
from src.domain.alerts.alert_repository import AlertRepository
from src.domain.alerts.alert_prompt_builder import AlertPromptBuilder

logger = logging.getLogger(__name__)


class AlertAnalysisTool(BaseTool):
    """
    Analiza alertas activas de PRTG consultando datos de monitoreo y generando
    un diagnóstico estructurado con acciones recomendadas y matriz de escalamiento.

    Requiere que la conexión 'monitoreo' esté configurada en DB_CONNECTIONS.
    """

    is_read_only: bool = True
    is_destructive: bool = False
    is_concurrency_safe: bool = True

    def __init__(self, repo: AlertRepository, llm) -> None:
        """
        Args:
            repo: AlertRepository con conexión a instancia monitoreo (BAZ_CDMX)
            llm: OpenAIProvider (data_llm) para generación del análisis
        """
        self._repo = repo
        self._llm = llm
        self._builder = AlertPromptBuilder()

    @property
    def definition(self) -> ToolDefinition:
        return ToolDefinition(
            name="alert_analysis",
            description=(
                "Analiza alertas activas de monitoreo PRTG. "
                "Consulta eventos activos, tickets históricos y matriz de escalamiento "
                "para generar un diagnóstico estructurado con acciones recomendadas. "
                "Usar cuando el usuario pregunta por alertas, equipos caídos o problemas de red/infraestructura."
            ),
            category=ToolCategory.MONITORING,
            parameters=[
                ToolParameter(
                    name="query",
                    param_type="string",
                    description="Consulta del operador: qué quiere saber sobre las alertas",
                    required=True,
                    examples=["¿qué alertas hay activas?", "analiza el servidor 10.1.2.3", "equipos caídos en producción"],
                ),
                ToolParameter(
                    name="ip",
                    param_type="string",
                    description="Filtrar por IP exacta del equipo (opcional)",
                    required=False,
                    default=None,
                    examples=["10.53.34.130", "192.168.1.1"],
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
                {"query": "¿qué alertas críticas hay activas?", "solo_down": "true"},
                {"query": "analiza el equipo 10.1.2.3", "ip": "10.1.2.3"},
            ],
            returns=(
                "Análisis estructurado en Markdown con: equipo afectado, área responsable, "
                "matriz de escalamiento, acciones recomendadas y posible causa raíz."
            ),
        )

    async def execute(self, **kwargs: Any) -> ToolResult:
        """
        Ejecuta el flujo completo de análisis de alerta.

        Args:
            query: Texto de la consulta del operador
            ip: IP exacta para filtrar (opcional)
            equipo: Nombre parcial para filtrar (opcional)
            solo_down: Solo equipos down (opcional)

        Returns:
            ToolResult con el análisis Markdown como data (string)
        """
        t0 = time.perf_counter()

        query: str = kwargs.get("query", "")
        ip: Optional[str] = kwargs.get("ip") or None
        equipo: Optional[str] = kwargs.get("equipo") or None
        solo_down_raw = kwargs.get("solo_down", False)
        solo_down = solo_down_raw if isinstance(solo_down_raw, bool) else str(solo_down_raw).lower() == "true"

        try:
            # ── 1. Obtener eventos activos ─────────────────────────────────
            try:
                events = await self._repo.get_active_events(
                    ip=ip,
                    equipo=equipo,
                    solo_down=solo_down,
                )
            except ConnectionError as conn_err:
                elapsed = (time.perf_counter() - t0) * 1000
                logger.error(f"AlertAnalysisTool: error de conectividad con monitoreo: {conn_err}")
                return ToolResult.error_result(
                    error=(
                        "⚠️ No se pudo conectar a la instancia de monitoreo (BAZ_CDMX/EKT). "
                        "Verifica que el servidor está accesible y las credenciales en .env son correctas.\n"
                        f"Detalle técnico: {conn_err}"
                    ),
                    execution_time_ms=elapsed,
                )

            if not events:
                elapsed = (time.perf_counter() - t0) * 1000
                msg = "No se encontraron alertas activas con los filtros indicados."
                return ToolResult.success_result(data=msg, execution_time_ms=elapsed)

            # ── 2. Tomar el evento más crítico ─────────────────────────────
            evento = events[0]
            logger.info(
                f"AlertAnalysisTool: analizando {evento.equipo} ({evento.ip}) "
                f"— prioridad={evento.prioridad} origen={evento.origen}"
            )

            # ── 3. Enriquecimiento en paralelo ─────────────────────────────
            import asyncio as _asyncio

            tickets_task = _asyncio.create_task(
                self._repo.get_historical_tickets(ip=evento.ip, sensor=evento.sensor)
            )
            template_id_task = _asyncio.create_task(
                self._repo.get_template_id(
                    ip=evento.ip,
                    url=evento.sensor if evento.es_url_sensor else None,
                )
            )

            tickets, template_id_row = await _asyncio.gather(tickets_task, template_id_task)

            # Template e info dependiente
            template = None
            matriz = []
            contacto_atendedora = None
            contacto_administradora = None

            if template_id_row:
                tid = template_id_row.get("idTemplate")
                usar_ekt = evento.es_ekt

                if tid:
                    template, matriz = await _asyncio.gather(
                        self._repo.get_template_info(tid, usar_ekt=usar_ekt),
                        self._repo.get_escalation_matrix(tid, usar_ekt=usar_ekt),
                    )

            # Contactos de área (si tienen ID de gerencia)
            contacto_tasks = []
            if evento.id_area_atendedora:
                contacto_tasks.append(
                    self._repo.get_contacto_gerencia(evento.id_area_atendedora, usar_ekt=evento.es_ekt)
                )
            else:
                contacto_tasks.append(_asyncio.sleep(0))  # placeholder

            if evento.id_area_administradora:
                contacto_tasks.append(
                    self._repo.get_contacto_gerencia(evento.id_area_administradora, usar_ekt=evento.es_ekt)
                )
            else:
                contacto_tasks.append(_asyncio.sleep(0))  # placeholder

            results_contacto = await _asyncio.gather(*contacto_tasks, return_exceptions=True)
            contacto_atendedora = results_contacto[0] if not isinstance(results_contacto[0], (Exception, type(None))) else None
            contacto_administradora = results_contacto[1] if not isinstance(results_contacto[1], (Exception, type(None))) else None

            # ── 4. Construir contexto y prompt ─────────────────────────────
            context = AlertContext(
                evento=evento,
                tickets=tickets[:15],  # TOP 15
                template=template,
                matriz=matriz,
                contacto_atendedora=contacto_atendedora,
                contacto_administradora=contacto_administradora,
                query_usuario=query,
            )

            system_prompt, user_prompt = self._builder.build(context)

            # ── 5. Llamar al LLM para análisis ─────────────────────────────
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ]

            llm_response = await self._llm.generate_messages(
                messages=messages,
                max_tokens=2048,
            )

            analysis_text = str(llm_response)

            # ── 6. Retornar análisis ───────────────────────────────────────
            instancia = "ABCMASplus (Banco)" if evento.origen == "BAZ_CDMX" else "ABCEKT (EKT)"
            final_text = f"**Instancia:** {instancia}\n\n{analysis_text}"

            elapsed = (time.perf_counter() - t0) * 1000
            logger.info(
                f"AlertAnalysisTool: análisis completado en {elapsed:.0f}ms "
                f"({len(tickets)} tickets, template={'sí' if template else 'no'}, "
                f"escalamiento={len(matriz)} niveles)"
            )

            return ToolResult.success_result(
                data=final_text,
                execution_time_ms=elapsed,
                metadata={
                    "equipo": evento.equipo,
                    "ip": evento.ip,
                    "origen": evento.origen,
                    "tickets_count": len(tickets),
                    "total_eventos": len(events),
                },
            )

        except Exception as e:
            elapsed = (time.perf_counter() - t0) * 1000
            logger.exception(f"AlertAnalysisTool: error en ejecución: {e}")
            return ToolResult.error_result(
                error=f"Error al analizar alertas: {e}",
                execution_time_ms=elapsed,
            )
