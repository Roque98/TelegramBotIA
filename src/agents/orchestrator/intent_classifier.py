"""
IntentClassifier - Clasifica el intent de una consulta del usuario.

Usa un modelo barato (gpt-5.4-nano) para determinar si la consulta
involucra datos de negocio o es conversación casual, antes de rutear
al agente correcto.
"""

import logging
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)

INTENT_PROMPT = """Clasificá la siguiente consulta del usuario en UNA de estas categorías:

- business_data: el usuario pregunta por datos de la empresa (ventas, usuarios, productos, reportes, estadísticas, facturación, stock, métricas, comparaciones numéricas, análisis de datos)
- casual: saludos, agradecimientos, conversación general, preferencias personales, preguntas sobre cómo funciona el bot

Respondé ÚNICAMENTE con una de estas palabras: business_data, casual

Consulta: {query}"""


class Intent(str, Enum):
    BUSINESS_DATA = "business_data"
    CASUAL = "casual"


class IntentClassifier:
    """
    Clasifica el intent de una consulta usando un modelo nano.

    El objetivo es determinar con una llamada barata si la consulta
    requiere el modelo caro (DataAgent) o el modelo económico (CasualAgent).

    Example:
        >>> classifier = IntentClassifier(llm_provider)
        >>> intent = await classifier.classify("cuántas ventas hubo ayer?")
        >>> # Intent.BUSINESS_DATA
    """

    def __init__(self, llm: Any) -> None:
        self.llm = llm

    async def classify(self, query: str) -> Intent:
        """
        Clasifica el intent de la consulta.

        Args:
            query: Texto del mensaje del usuario

        Returns:
            Intent.BUSINESS_DATA o Intent.CASUAL
        """
        try:
            prompt = INTENT_PROMPT.format(query=query[:500])
            messages = [
                {"role": "system", "content": "Sos un clasificador de intents. Respondé solo con la categoría."},
                {"role": "user", "content": prompt},
            ]
            response = await self.llm.generate_messages(messages)
            raw = response.strip().lower()

            if "business_data" in raw:
                intent = Intent.BUSINESS_DATA
            else:
                intent = Intent.CASUAL

            logger.debug(f"Intent classified: '{query[:60]}' → {intent.value}")
            return intent

        except Exception as e:
            # En caso de error, usar el agente más capaz para no perder calidad
            logger.warning(f"Intent classification failed ({e}), defaulting to business_data")
            return Intent.BUSINESS_DATA
