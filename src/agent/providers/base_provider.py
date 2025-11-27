"""
Interfaz abstracta para proveedores de LLM.

Define el contrato que deben cumplir todos los proveedores de LLM
para permitir la intercambiabilidad entre diferentes servicios.
"""
from abc import ABC, abstractmethod
from typing import Optional
from pydantic import BaseModel


class LLMProvider(ABC):
    """Interfaz abstracta para proveedores de LLM."""

    @abstractmethod
    async def generate(self, prompt: str, max_tokens: Optional[int] = None) -> str:
        """
        Generar texto a partir de un prompt.

        Args:
            prompt: Prompt para el modelo
            max_tokens: Número máximo de tokens a generar

        Returns:
            Texto generado por el modelo
        """
        pass

    @abstractmethod
    async def generate_structured(
        self,
        prompt: str,
        schema: type[BaseModel],
        max_tokens: Optional[int] = None
    ) -> BaseModel:
        """
        Generar salida estructurada a partir de un prompt.

        Args:
            prompt: Prompt para el modelo
            schema: Schema de Pydantic para la salida estructurada
            max_tokens: Número máximo de tokens a generar

        Returns:
            Instancia del schema con los datos generados
        """
        pass

    @abstractmethod
    def get_provider_name(self) -> str:
        """
        Obtener el nombre del proveedor.

        Returns:
            Nombre del proveedor (ej: "OpenAI", "Anthropic")
        """
        pass

    @abstractmethod
    def get_model_name(self) -> str:
        """
        Obtener el nombre del modelo.

        Returns:
            Nombre del modelo (ej: "gpt-5-nano-2025-08-07", "claude-3-5-sonnet-20241022")
        """
        pass
