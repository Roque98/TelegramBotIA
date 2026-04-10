"""
Alert Repository — Acceso a datos de alertas PRTG con fallback BAZ_CDMX → EKT.

Estrategia:
  1. Intenta SP estándar contra la instancia BAZ_CDMX (alias "monitoreo")
  2. Si retorna vacío → reintenta con SP versión _EKT (OPENDATASOURCE)
  3. Marca cada AlertEvent con _origen: "BAZ_CDMX" | "EKT"

Los SPs _EKT usan OPENDATASOURCE internamente y requieren AUTOCOMMIT,
que ya está configurado globalmente en DatabaseManager.

Nunca lanza excepciones al llamador — retorna [] o None en caso de error.
"""

import logging
from typing import Optional

from src.domain.alerts.alert_entity import (
    AlertContext,
    AlertEvent,
    AreaContacto,
    EscalationLevel,
    HistoricalTicket,
    Template,
)

logger = logging.getLogger(__name__)


class AlertRepository:
    """
    Repositorio de alertas con fallback automático BAZ_CDMX → EKT.

    Recibe un DatabaseManager del alias "monitoreo" (BAZ_CDMX).
    Los SPs _EKT acceden a la instancia EKT vía OPENDATASOURCE internamente.

    Example:
        >>> repo = AlertRepository(db_manager=registry.get("monitoreo"))
        >>> events = await repo.get_active_events(solo_down=True)
    """

    def __init__(self, db_manager) -> None:
        self._db = db_manager

    # ─────────────────────────────────────────────────────────────────────────
    # Eventos activos
    # ─────────────────────────────────────────────────────────────────────────

    async def get_active_events(
        self,
        ip: Optional[str] = None,
        equipo: Optional[str] = None,
        solo_down: bool = False,
    ) -> list[AlertEvent]:
        """
        Obtiene eventos activos de monitoreo PRTG.

        Combina resultados de PrtgObtenerEventosEnriquecidos y
        PrtgObtenerEventosEnriquecidosPerformance. Intenta BAZ_CDMX primero;
        si no hay resultados, reintenta con versiones _EKT.

        Args:
            ip: Filtrar por IP exacta (opcional)
            equipo: Filtrar por nombre de equipo (case-insensitive, parcial)
            solo_down: Si True, solo retorna eventos con Status "down"

        Returns:
            Lista de AlertEvent ordenada por Prioridad desc
        """
        sps_baz = [
            "EXEC Monitoreos.dbo.PrtgObtenerEventosEnriquecidos",
            "EXEC Monitoreos.dbo.PrtgObtenerEventosEnriquecidosPerformance",
        ]
        sps_ekt = [
            "EXEC Monitoreos.dbo.PrtgObtenerEventosEnriquecidos_EKT",
            "EXEC Monitoreos.dbo.PrtgObtenerEventosEnriquecidosPerformance_EKT",
        ]

        rows, origen = await self._run_sps_with_fallback(sps_baz, sps_ekt)

        events = []
        seen = set()  # deduplicar por (IP, Sensor)
        for row in rows:
            key = (row.get("IP", ""), row.get("Sensor", ""))
            if key in seen:
                continue
            seen.add(key)
            try:
                row["_origen"] = origen
                events.append(AlertEvent.model_validate(row))
            except Exception as e:
                logger.debug(f"AlertRepository: fila inválida ignorada: {e}")

        # Filtrar
        if ip:
            events = [e for e in events if e.ip == ip]
        if equipo:
            equipo_lower = equipo.lower()
            events = [e for e in events if equipo_lower in e.equipo.lower()]
        if solo_down:
            events = [e for e in events if e.status.lower() == "down"]

        events.sort(key=lambda e: e.prioridad, reverse=True)
        logger.debug(f"AlertRepository: {len(events)} eventos activos (origen={origen})")
        return events

    # ─────────────────────────────────────────────────────────────────────────
    # Tickets históricos
    # ─────────────────────────────────────────────────────────────────────────

    async def get_historical_tickets(
        self, ip: str, sensor: str
    ) -> list[HistoricalTicket]:
        """
        Obtiene los TOP 15 tickets históricos más recientes para el IP/sensor dado.

        Fallback automático a versión EKT si BAZ no retorna resultados.
        """
        params = {"ip": ip, "sensor": sensor}
        sp_baz = "EXEC Monitoreos.dbo.IABOT_ObtenerTicketsByAlerta @ip = :ip, @sensor = :sensor"
        sp_ekt = "EXEC Monitoreos.dbo.IABOT_ObtenerTicketsByAlerta_EKT @ip = :ip, @sensor = :sensor"

        rows, _ = await self._run_sp_with_fallback(sp_baz, sp_ekt, params)

        tickets = []
        for row in rows:
            try:
                tickets.append(HistoricalTicket.model_validate(row))
            except Exception as e:
                logger.debug(f"AlertRepository: ticket inválido ignorado: {e}")
        return tickets

    # ─────────────────────────────────────────────────────────────────────────
    # Template
    # ─────────────────────────────────────────────────────────────────────────

    async def get_template_id(
        self, ip: str, url: Optional[str] = None
    ) -> Optional[dict]:
        """
        Obtiene el idTemplate y la instancia para el IP o URL dado.

        La columna 'instancia' puede venir sin nombre en algunos SPs — se normaliza.
        """
        if url:
            sp = "EXEC ABCMASplus.dbo.IDTemplateByUrl @url = :url"
            params = {"url": url}
        else:
            sp = "EXEC ABCMASplus.dbo.IDTemplateByIp @ip = :ip"
            params = {"ip": ip}

        try:
            rows = await self._db.execute_query_async(sp, params)
            if not rows:
                return None
            row = dict(rows[0])
            # Normalizar columna 'instancia' si viene sin nombre
            if "instancia" not in row:
                unnamed = row.get("") or row.get(None) or ""
                row = {
                    "idTemplate": row.get("idTemplate"),
                    "instancia": str(unnamed).strip(),
                }
            return row
        except Exception as e:
            logger.warning(f"AlertRepository.get_template_id({ip}): {e}")
            return None

    async def get_template_info(self, template_id: int, usar_ekt: bool = False) -> Optional[Template]:
        """
        Obtiene la información completa del template.

        Fallback automático a versión EKT si BAZ no retorna resultados.
        """
        params = {"id": template_id}
        sp_baz = "EXEC ABCMASplus.dbo.Template_GetById @id = :id"
        sp_ekt = "EXEC ABCMASplus.dbo.Template_GetById_EKT @id = :id"

        if usar_ekt:
            rows, _ = await self._run_sp_with_fallback(sp_ekt, sp_baz, params)
        else:
            rows, _ = await self._run_sp_with_fallback(sp_baz, sp_ekt, params)

        if not rows:
            return None
        try:
            return Template.model_validate(rows[0])
        except Exception as e:
            logger.warning(f"AlertRepository.get_template_info({template_id}): {e}")
            return None

    async def get_escalation_matrix(
        self, template_id: int, usar_ekt: bool = False
    ) -> list[EscalationLevel]:
        """
        Obtiene la matriz de escalamiento del template, ordenada por nivel.

        Fallback automático a versión EKT si BAZ no retorna resultados.
        """
        params = {"idTemplate": template_id}
        sp_baz = "EXEC ABCMASplus.dbo.ObtenerMatriz @idTemplate = :idTemplate"
        sp_ekt = "EXEC ABCMASplus.dbo.ObtenerMatriz_EKT @idTemplate = :idTemplate"

        if usar_ekt:
            rows, _ = await self._run_sp_with_fallback(sp_ekt, sp_baz, params)
        else:
            rows, _ = await self._run_sp_with_fallback(sp_baz, sp_ekt, params)

        levels = []
        for row in rows:
            try:
                levels.append(EscalationLevel.model_validate(row))
            except Exception as e:
                logger.debug(f"AlertRepository: nivel de escalamiento inválido ignorado: {e}")
        levels.sort(key=lambda l: l.nivel)
        return levels

    # ─────────────────────────────────────────────────────────────────────────
    # Contactos
    # ─────────────────────────────────────────────────────────────────────────

    async def get_contacto_gerencia(
        self, id_gerencia: int, usar_ekt: bool = False
    ) -> Optional[AreaContacto]:
        """
        Obtiene los datos de contacto de una gerencia por su ID.

        Args:
            id_gerencia: ID de la gerencia en ABCMASplus
            usar_ekt: Si True, usa la versión EKT del SP
        """
        params = {"idGerencia": id_gerencia}
        if usar_ekt:
            sp = "EXEC ABCMASplus.dbo.Contacto_GetByIdGerencia_EKT @idGerencia = :idGerencia"
        else:
            sp = "EXEC ABCMASplus.dbo.Contacto_GetByIdGerencia @idGerencia = :idGerencia"

        try:
            rows = await self._db.execute_query_async(sp, params)
            if not rows:
                return None
            return AreaContacto.model_validate(rows[0])
        except Exception as e:
            logger.warning(f"AlertRepository.get_contacto_gerencia({id_gerencia}): {e}")
            return None

    # ─────────────────────────────────────────────────────────────────────────
    # Helpers privados
    # ─────────────────────────────────────────────────────────────────────────

    async def _run_sp_with_fallback(
        self,
        sp_principal: str,
        sp_fallback: str,
        params: Optional[dict] = None,
    ) -> tuple[list[dict], str]:
        """
        Ejecuta sp_principal; si retorna vacío, ejecuta sp_fallback.

        Returns:
            (filas, origen) donde origen es "principal" o "fallback"
        """
        try:
            rows = await self._db.execute_query_async(sp_principal, params)
            if rows:
                return list(rows), "BAZ_CDMX"
        except Exception as e:
            logger.warning(f"AlertRepository SP principal falló ({sp_principal}): {e}")

        try:
            rows = await self._db.execute_query_async(sp_fallback, params)
            if rows:
                return list(rows), "EKT"
        except Exception as e:
            logger.warning(f"AlertRepository SP fallback falló ({sp_fallback}): {e}")

        return [], "BAZ_CDMX"

    async def _run_sps_with_fallback(
        self,
        sps_principal: list[str],
        sps_fallback: list[str],
    ) -> tuple[list[dict], str]:
        """
        Ejecuta múltiples SPs principales y combina resultados.
        Si el total es vacío, reintenta con los SPs de fallback.

        Returns:
            (filas_combinadas, origen)
        """
        rows_baz: list[dict] = []
        for sp in sps_principal:
            try:
                result = await self._db.execute_query_async(sp, None)
                rows_baz.extend(result or [])
            except Exception as e:
                logger.warning(f"AlertRepository SP '{sp}' falló: {e}")

        if rows_baz:
            return rows_baz, "BAZ_CDMX"

        # Fallback a EKT
        rows_ekt: list[dict] = []
        for sp in sps_fallback:
            try:
                result = await self._db.execute_query_async(sp, None)
                rows_ekt.extend(result or [])
            except Exception as e:
                logger.warning(f"AlertRepository SP EKT '{sp}' falló: {e}")

        return rows_ekt, "EKT"
