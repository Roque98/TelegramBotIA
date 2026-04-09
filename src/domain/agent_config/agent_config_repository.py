"""
AgentConfigRepository — Acceso a BotIAv2_AgenteDef y BotIAv2_AgenteTools.
"""
import logging
from typing import Any, Optional

from .agent_config_entity import AgentDefinition

logger = logging.getLogger(__name__)


class AgentConfigRepository:
    def __init__(self, db_manager: Any) -> None:
        self.db = db_manager

    def get_all_active(self) -> list[AgentDefinition]:
        """Retorna todos los agentes activos con sus tools."""
        rows = self.db.execute_query(
            """
            SELECT
                ad.idAgente,
                ad.nombre,
                ad.descripcion,
                ad.systemPrompt,
                ad.temperatura,
                ad.maxIteraciones,
                ad.modeloOverride,
                ad.esGeneralista,
                ad.activo,
                ad.version,
                ISNULL(
                    (
                        SELECT STRING_AGG(at2.nombreTool, ',')
                        FROM abcmasplus..BotIAv2_AgenteTools at2
                        WHERE at2.idAgente = ad.idAgente
                          AND at2.activo = 1
                    ), ''
                ) AS tools
            FROM abcmasplus..BotIAv2_AgenteDef ad
            WHERE ad.activo = 1
            ORDER BY ad.idAgente
            """
        )
        return [self._row_to_entity(r) for r in rows]

    def get_by_nombre(self, nombre: str) -> Optional[AgentDefinition]:
        rows = self.db.execute_query(
            """
            SELECT
                ad.idAgente,
                ad.nombre,
                ad.descripcion,
                ad.systemPrompt,
                ad.temperatura,
                ad.maxIteraciones,
                ad.modeloOverride,
                ad.esGeneralista,
                ad.activo,
                ad.version,
                ISNULL(
                    (
                        SELECT STRING_AGG(at2.nombreTool, ',')
                        FROM abcmasplus..BotIAv2_AgenteTools at2
                        WHERE at2.idAgente = ad.idAgente
                          AND at2.activo = 1
                    ), ''
                ) AS tools
            FROM abcmasplus..BotIAv2_AgenteDef ad
            WHERE ad.nombre = :nombre
              AND ad.activo = 1
            """,
            {"nombre": nombre},
        )
        return self._row_to_entity(rows[0]) if rows else None

    def get_generalista(self) -> Optional[AgentDefinition]:
        rows = self.db.execute_query(
            """
            SELECT
                ad.idAgente,
                ad.nombre,
                ad.descripcion,
                ad.systemPrompt,
                ad.temperatura,
                ad.maxIteraciones,
                ad.modeloOverride,
                ad.esGeneralista,
                ad.activo,
                ad.version,
                '' AS tools
            FROM abcmasplus..BotIAv2_AgenteDef ad
            WHERE ad.esGeneralista = 1
              AND ad.activo = 1
            """
        )
        return self._row_to_entity(rows[0]) if rows else None

    @staticmethod
    def _row_to_entity(row: dict) -> AgentDefinition:
        tools_str: str = row.get("tools") or ""
        tools = [t.strip() for t in tools_str.split(",") if t.strip()]
        return AgentDefinition(
            id=row["idAgente"],
            nombre=row["nombre"],
            descripcion=row["descripcion"],
            system_prompt=row["systemPrompt"],
            temperatura=float(row["temperatura"]),
            max_iteraciones=int(row["maxIteraciones"]),
            modelo_override=row.get("modeloOverride"),
            es_generalista=bool(row["esGeneralista"]),
            tools=tools,
            activo=bool(row["activo"]),
            version=int(row["version"]),
        )
