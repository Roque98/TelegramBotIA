"""
Proveedor de OpenAI para LLM.

Implementa la interfaz LLMProvider para OpenAI usando la API Responses.
"""
import logging
from typing import Optional
from pydantic import BaseModel
from openai import AsyncOpenAI
from .base_provider import LLMProvider

logger = logging.getLogger(__name__)


class OpenAIProvider(LLMProvider):
    """Proveedor de OpenAI."""

    def __init__(self, api_key: str, model: str = "gpt-5-nano-2025-08-07"):
        """
        Inicializar el proveedor de OpenAI.

        Args:
            api_key: API key de OpenAI
            model: Nombre del modelo a usar
        """
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = model
        logger.info(f"Inicializado proveedor OpenAI con modelo: {model}")

    async def generate(self, prompt: str, max_tokens: Optional[int] = None) -> str:
        """
        Generar texto usando OpenAI Responses API.

        Args:
            prompt: Prompt para el modelo
            max_tokens: Número máximo de tokens (no usado en Responses API)

        Returns:
            Texto generado
        """
        try:
            response = await self.client.responses.create(
                model=self.model,
                input=prompt
            )
            return response.output_text.strip()
        except Exception as e:
            logger.error(f"Error generando con OpenAI: {e}")
            raise

    async def generate_structured(
        self,
        prompt: str,
        schema: type[BaseModel],
        max_tokens: Optional[int] = None
    ) -> BaseModel:
        """
        Generar salida estructurada usando OpenAI Responses API.

        Args:
            prompt: Prompt para el modelo
            schema: Schema de Pydantic para la salida
            max_tokens: Número máximo de tokens (no usado en Responses API)

        Returns:
            Instancia del schema con datos generados
        """
        try:
            response = await self.client.responses.parse(
                model=self.model,
                input=prompt,
                text_format=schema
            )
            return response.output_parsed
        except Exception as e:
            logger.error(f"Error generando salida estructurada con OpenAI: {e}")
            raise

    def get_provider_name(self) -> str:
        """Obtener nombre del proveedor."""
        return "OpenAI"

    def get_model_name(self) -> str:
        """Obtener nombre del modelo."""
        return self.model
