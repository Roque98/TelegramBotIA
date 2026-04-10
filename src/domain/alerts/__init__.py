"""
Dominio de Alertas — Entidades y repositorio para análisis de alertas PRTG.

Módulos:
- alert_entity: Modelos Pydantic (AlertEvent, HistoricalTicket, Template, etc.)
- alert_repository: Acceso a BD con fallback automático BAZ_CDMX → EKT
- alert_prompt_builder: Construcción del prompt enriquecido para el LLM
"""

from .alert_entity import (
    AlertContext,
    AlertEvent,
    AreaContacto,
    EscalationLevel,
    HistoricalTicket,
    Template,
)
from .alert_repository import AlertRepository
from .alert_prompt_builder import AlertPromptBuilder

__all__ = [
    "AlertEvent",
    "HistoricalTicket",
    "Template",
    "EscalationLevel",
    "AreaContacto",
    "AlertContext",
    "AlertRepository",
    "AlertPromptBuilder",
]
