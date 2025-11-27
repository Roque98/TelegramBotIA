"""
Clasificador de consultas de usuario.

Determina si una consulta requiere acceso a base de datos o es una pregunta general.
"""
import logging
from enum import Enum
from typing import Optional
from ..providers.base_provider import LLMProvider
from ..prompts import get_default_manager

logger = logging.getLogger(__name__)


class QueryType(Enum):
    """Tipos de consulta."""
    DATABASE = "database"
    GENERAL = "general"


class QueryClassifier:
    """Clasificador de consultas usando LLM."""

    def __init__(self, llm_provider: LLMProvider, prompt_version: Optional[int] = None):
        """
        Inicializar el clasificador.

        Args:
            llm_provider: Proveedor de LLM para clasificación
            prompt_version: Versión del prompt a usar (None = auto según A/B testing)
        """
        self.llm_provider = llm_provider
        self.prompt_manager = get_default_manager()
        self.prompt_version = prompt_version
        logger.info(f"Inicializado clasificador con proveedor: {llm_provider.get_provider_name()}")

    async def classify(self, user_query: str) -> QueryType:
        """
        Clasificar una consulta de usuario.

        Args:
            user_query: Consulta del usuario

        Returns:
            Tipo de consulta (DATABASE o GENERAL)
        """
        # Usar el nuevo sistema de prompts
        prompt = self.prompt_manager.get_prompt(
            'classification',
            version=self.prompt_version,
            user_query=user_query
        )

        try:
            response = await self.llm_provider.generate(prompt, max_tokens=50)
            classification = response.strip().lower()

            # Determinar tipo basado en la respuesta
            if "database" in classification:
                logger.info(f"Consulta clasificada como DATABASE: '{user_query[:50]}...'")
                return QueryType.DATABASE
            else:
                logger.info(f"Consulta clasificada como GENERAL: '{user_query[:50]}...'")
                return QueryType.GENERAL

        except Exception as e:
            logger.error(f"Error clasificando consulta: {e}")
            # En caso de error, asumir que requiere base de datos (más seguro)
            logger.warning("Asumiendo tipo DATABASE por error en clasificación")
            return QueryType.DATABASE

    async def is_database_query(self, user_query: str) -> bool:
        """
        Verificar si una consulta requiere base de datos.

        Args:
            user_query: Consulta del usuario

        Returns:
            True si requiere base de datos, False si no
        """
        query_type = await self.classify(user_query)
        return query_type == QueryType.DATABASE
