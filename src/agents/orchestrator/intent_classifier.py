"""
IntentClassifier - Clasifica el intent de una consulta del usuario.

Usa un modelo barato (gpt-5.4-nano) para seleccionar el agente adecuado
de entre los agentes activos cargados desde BD, antes de rutear al agente correcto.

Los agentes y sus descripciones se leen dinámicamente desde BD vía AgentConfigService,
por lo que agregar un nuevo agente no requiere tocar este código.
"""

import logging
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Optional

if TYPE_CHECKING:
    from src.domain.agent_config.agent_config_entity import AgentDefinition

logger = logging.getLogger(__name__)

_CLASSIFIER_SYSTEM = (
    "Sos un clasificador de intents. Respondé solo con el nombre de la categoría."
)


@dataclass
class ClassifyResult:
    """Resultado de clasificación con métricas para observabilidad."""
    agent_name: str
    confidence: Optional[float] = None
    alternatives: list[str] = field(default_factory=list)
    used_fallback: bool = False


class IntentClassifier:
    """
    Clasifica el intent de una consulta usando un modelo nano.

    El objetivo es determinar con una llamada barata qué agente especializado
    debe manejar la consulta. El agente generalista actúa como fallback para
    cualquier respuesta desconocida o error del clasificador.

    Example:
        >>> classifier = IntentClassifier(llm_provider)
        >>> result = await classifier.classify("cuántas ventas hubo ayer?", agents)
        >>> result.agent_name  # "datos"
        >>> result.confidence  # 0.95
    """

    def __init__(self, llm: Any) -> None:
        self.llm = llm

    async def classify(
        self, query: str, agents: list["AgentDefinition"]
    ) -> ClassifyResult:
        """
        Clasifica el intent de la consulta y retorna un ClassifyResult.

        Args:
            query: Texto del mensaje del usuario
            agents: Lista de agentes activos desde BD

        Returns:
            ClassifyResult con agent_name, confidence y used_fallback.
            Si el clasificador falla o no coincide, retorna agent_name="generalista"
            con used_fallback=True.
        """
        especialistas = [a for a in agents if not a.es_generalista]

        if not especialistas:
            logger.debug("No hay agentes especializados — usando generalista directamente")
            return ClassifyResult(agent_name="generalista", used_fallback=True)

        opciones = "\n".join(
            f"- {a.nombre}: {a.descripcion}" for a in especialistas
        )
        prompt = (
            f"Clasificá la consulta en UNA de estas categorías:\n"
            f"{opciones}\n"
            f"- generalista: SOLO si la consulta no tiene ninguna relación con los dominios anteriores\n\n"
            f"IMPORTANTE: Si la consulta menciona IPs, equipos, alertas, sensores, "
            f"incidentes o infraestructura, preferí el agente especializado aunque "
            f"el usuario use verbos de acción como 'solucionar', 'atender' o 'resolver'.\n\n"
            f"Respondé ÚNICAMENTE con el nombre de la categoría.\n\n"
            f"Consulta: {query[:500]}"
        )

        valid_names = {a.nombre for a in agents} | {"generalista"}

        try:
            messages = [
                {"role": "system", "content": _CLASSIFIER_SYSTEM},
                {"role": "user", "content": prompt},
            ]
            response = await self.llm.generate_messages(messages)
            raw = response.strip().lower()

            matched = [name for name in valid_names if name in raw]

            if matched:
                selected = matched[0]
                alternatives = matched[1:]
                confidence = 0.95 if len(matched) == 1 else 0.60
                logger.debug(
                    f"IntentClassifier: '{query[:60]}' → '{selected}' "
                    f"(confidence={confidence}, alternatives={alternatives})"
                )
                return ClassifyResult(
                    agent_name=selected,
                    confidence=confidence,
                    alternatives=alternatives,
                )

            logger.debug(
                f"IntentClassifier: respuesta '{raw[:40]}' no coincide con ningún agente "
                f"→ fallback 'generalista'"
            )
            return ClassifyResult(agent_name="generalista", used_fallback=True)

        except Exception as e:
            logger.warning(
                f"IntentClassifier falló ({e}), usando 'generalista'"
            )
            return ClassifyResult(agent_name="generalista", used_fallback=True)
