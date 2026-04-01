"""
Proveedor de OpenAI para LLM.

Implementa la interfaz LLMProvider para OpenAI usando la API Responses.
"""
import logging
from typing import Optional

from openai import AsyncOpenAI
from pydantic import BaseModel

from src.config.settings import settings
from src.domain.cost.cost_tracker import get_current_tracker
from src.utils.retry import llm_retry

logger = logging.getLogger(__name__)


class OpenAIProvider:
    """Proveedor de OpenAI."""

    def __init__(self, api_key: str, model: str = "gpt-5-nano-2025-08-07"):
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = model
        logger.info(f"Inicializado proveedor OpenAI con modelo: {model}")

    @llm_retry(
        max_attempts=settings.retry_llm_max_attempts,
        min_wait=settings.retry_llm_min_wait,
        max_wait=settings.retry_llm_max_wait,
    )
    async def generate(self, prompt: str, max_tokens: Optional[int] = None) -> str:
        """Generar texto usando OpenAI Responses API (input como string)."""
        return await self._call_responses_api(prompt)

    @llm_retry(
        max_attempts=settings.retry_llm_max_attempts,
        min_wait=settings.retry_llm_min_wait,
        max_wait=settings.retry_llm_max_wait,
    )
    async def generate_messages(
        self,
        messages: list[dict],
        max_tokens: Optional[int] = None,
    ) -> str:
        """
        Generar texto pasando la lista de mensajes estructurada directamente.

        Usar en lugar de generate() cuando se tiene system+user separados,
        para que el modelo reciba el system prompt como rol de sistema real
        y no como texto de usuario.
        """
        return await self._call_responses_api(messages)

    async def _call_responses_api(self, input) -> str:
        """Llama a responses.create y extrae el texto de la respuesta."""
        try:
            response = await self.client.responses.create(
                model=self.model,
                input=input,
            )

            text = response.output_text.strip() if response.output_text else ""

            if not text:
                text = self._extract_text_from_output(response.output)

            # Registrar uso en el tracker activo (si existe)
            tracker = get_current_tracker()
            if tracker and hasattr(response, "usage"):
                tracker.add_turn(self.model, response.usage)

            if not text:
                logger.error(
                    f"LLM returned empty text. "
                    f"Output items: {[type(item).__name__ for item in response.output]}"
                )
                raise ValueError("LLM returned empty response")

            return text

        except Exception as e:
            logger.error(f"Error generando con OpenAI: {e}")
            raise

    def _extract_text_from_output(self, output: list) -> str:
        """
        Extracción de texto de fallback para modelos que no populan output_text.

        Algunos modelos (razonamiento, streaming) pueden devolver el texto
        dentro de ResponseOutputMessage en vez de como output_text directo.
        """
        for item in output:
            content = getattr(item, "content", None)
            if content:
                for part in content:
                    text = getattr(part, "text", None)
                    if text:
                        return text.strip()
            text = getattr(item, "text", None)
            if text:
                return text.strip()
        return ""

    @llm_retry(
        max_attempts=settings.retry_llm_max_attempts,
        min_wait=settings.retry_llm_min_wait,
        max_wait=settings.retry_llm_max_wait,
    )
    async def generate_structured(
        self,
        prompt: str,
        schema: type[BaseModel],
        max_tokens: Optional[int] = None,
    ) -> BaseModel:
        """Generar salida estructurada usando OpenAI Responses API."""
        try:
            response = await self.client.responses.parse(
                model=self.model,
                input=prompt,
                text_format=schema,
            )
            return response.output_parsed
        except Exception as e:
            logger.error(f"Error generando salida estructurada con OpenAI: {e}")
            raise

    def get_provider_name(self) -> str:
        return "OpenAI"

    def get_model_name(self) -> str:
        return self.model
