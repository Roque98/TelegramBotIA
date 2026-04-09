"""
IntentClassifier - Clasifica el intent de una consulta del usuario.

Usa un modelo barato (gpt-5.4-nano) para seleccionar el agente adecuado
de entre los agentes activos cargados desde BD, antes de rutear al agente correcto.

Los agentes y sus descripciones se leen dinámicamente desde BD vía AgentConfigService,
por lo que agregar un nuevo agente no requiere tocar este código.
"""

import logging
from typing import TYPE_CHECKING, Any, Optional

if TYPE_CHECKING:
    from src.domain.agent_config.agent_config_entity import AgentDefinition

logger = logging.getLogger(__name__)

_CLASSIFIER_SYSTEM = (
    "Sos un clasificador de intents. Respondé solo con el nombre de la categoría."
)


class IntentClassifier:
    """
    Clasifica el intent de una consulta usando un modelo nano.

    El objetivo es determinar con una llamada barata qué agente especializado
    debe manejar la consulta. El agente generalista actúa como fallback para
    cualquier respuesta desconocida o error del clasificador.

    Example:
        >>> classifier = IntentClassifier(llm_provider)
        >>> intent = await classifier.classify("cuántas ventas hubo ayer?", agents)
        >>> # "datos"
    """

    def __init__(self, llm: Any) -> None:
        self.llm = llm

    async def classify(
        self, query: str, agents: list["AgentDefinition"]
    ) -> str:
        """
        Clasifica el intent de la consulta y retorna el nombre del agente.

        Args:
            query: Texto del mensaje del usuario
            agents: Lista de agentes activos desde BD

        Returns:
            Nombre del agente seleccionado (str). Si el clasificador falla
            o no coincide, retorna "generalista".
        """
        # Construir opciones con los agentes especializados (no generalista)
        especialistas = [a for a in agents if not a.es_generalista]

        if not especialistas:
            logger.debug("No hay agentes especializados — usando generalista directamente")
            return "generalista"

        opciones = "\n".join(
            f"- {a.nombre}: {a.descripcion}" for a in especialistas
        )
        prompt = (
            f"Clasificá la consulta en UNA de estas categorías:\n"
            f"{opciones}\n"
            f"- generalista: si no encaja claramente en ninguna de las anteriores\n\n"
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

            # Buscar el primer nombre válido en la respuesta
            for name in valid_names:
                if name in raw:
                    logger.debug(
                        f"IntentClassifier: '{query[:60]}' → '{name}'"
                    )
                    return name

            # Sin coincidencia → fallback generalista
            logger.debug(
                f"IntentClassifier: respuesta '{raw[:40]}' no coincide con ningún agente "
                f"→ fallback 'generalista'"
            )
            return "generalista"

        except Exception as e:
            logger.warning(
                f"IntentClassifier falló ({e}), usando 'generalista'"
            )
            return "generalista"
