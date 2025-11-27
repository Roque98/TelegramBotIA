"""
Proveedor de Anthropic (Claude) para LLM.

Implementa la interfaz LLMProvider para Anthropic Claude.
"""
import logging
import json
from typing import Optional
from pydantic import BaseModel
from anthropic import AsyncAnthropic
from .base_provider import LLMProvider

logger = logging.getLogger(__name__)


class AnthropicProvider(LLMProvider):
    """Proveedor de Anthropic Claude."""

    def __init__(self, api_key: str, model: str = "claude-3-5-sonnet-20241022"):
        """
        Inicializar el proveedor de Anthropic.

        Args:
            api_key: API key de Anthropic
            model: Nombre del modelo a usar
        """
        self.client = AsyncAnthropic(api_key=api_key)
        self.model = model
        logger.info(f"Inicializado proveedor Anthropic con modelo: {model}")

    async def generate(self, prompt: str, max_tokens: Optional[int] = None) -> str:
        """
        Generar texto usando Anthropic Messages API.

        Args:
            prompt: Prompt para el modelo
            max_tokens: Número máximo de tokens a generar

        Returns:
            Texto generado
        """
        try:
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens or 1024,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text.strip()
        except Exception as e:
            logger.error(f"Error generando con Anthropic: {e}")
            raise

    async def generate_structured(
        self,
        prompt: str,
        schema: type[BaseModel],
        max_tokens: Optional[int] = None
    ) -> BaseModel:
        """
        Generar salida estructurada usando Anthropic.

        Nota: Anthropic no tiene soporte nativo de salida estructurada,
        por lo que se usa prompt engineering para forzar JSON.

        Args:
            prompt: Prompt para el modelo
            schema: Schema de Pydantic para la salida
            max_tokens: Número máximo de tokens a generar

        Returns:
            Instancia del schema con datos generados
        """
        try:
            # Obtener el schema JSON
            json_schema = schema.model_json_schema()

            # Crear prompt estructurado
            structured_prompt = f"""{prompt}

Responde ÚNICAMENTE con un objeto JSON válido que cumpla el siguiente schema:
{json.dumps(json_schema, indent=2)}

No incluyas explicaciones, solo el JSON."""

            response = await self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens or 2048,
                messages=[{"role": "user", "content": structured_prompt}]
            )

            # Parsear la respuesta como JSON
            json_text = response.content[0].text.strip()
            # Intentar extraer JSON si está entre markdown
            if "```json" in json_text:
                json_text = json_text.split("```json")[1].split("```")[0].strip()
            elif "```" in json_text:
                json_text = json_text.split("```")[1].split("```")[0].strip()

            # Parsear y validar con el schema
            data = json.loads(json_text)
            return schema.model_validate(data)

        except Exception as e:
            logger.error(f"Error generando salida estructurada con Anthropic: {e}")
            raise

    def get_provider_name(self) -> str:
        """Obtener nombre del proveedor."""
        return "Anthropic"

    def get_model_name(self) -> str:
        """Obtener nombre del modelo."""
        return self.model
