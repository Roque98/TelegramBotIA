"""
AgentDefinition — Entidad que representa la configuración de un agente LLM.
"""
from typing import Optional
from pydantic import BaseModel


class AgentDefinition(BaseModel):
    id: int
    nombre: str
    descripcion: str
    system_prompt: str
    temperatura: float
    max_iteraciones: int
    modelo_override: Optional[str]
    es_generalista: bool
    tools: list[str]        # nombres de tools en scope; vacío para el generalista
    activo: bool
    version: int
