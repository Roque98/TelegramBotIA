"""
Selector automático de Tools usando LLM.

Este módulo permite que el LLM analice una consulta del usuario
y seleccione automáticamente el tool más apropiado para responderla.
"""

import logging
import json
import re
from typing import Optional, List, Dict, Any
from src.agent.prompts.prompt_manager import get_default_manager
from src.tools import get_registry, BaseTool

logger = logging.getLogger(__name__)


class ToolSelectionResult:
    """Resultado de la selección de tool."""

    def __init__(
        self,
        selected_tool: Optional[str] = None,
        confidence: float = 0.0,
        reasoning: Optional[str] = None,
        fallback_used: bool = False
    ):
        """
        Inicializar resultado de selección.

        Args:
            selected_tool: Nombre del tool seleccionado
            confidence: Confianza de la selección (0.0-1.0)
            reasoning: Razonamiento del LLM para la selección
            fallback_used: Si se usó fallback por error
        """
        self.selected_tool = selected_tool
        self.confidence = confidence
        self.reasoning = reasoning
        self.fallback_used = fallback_used

    @property
    def has_selection(self) -> bool:
        """Verificar si hay un tool seleccionado."""
        return self.selected_tool is not None

    def __repr__(self) -> str:
        return (
            f"ToolSelectionResult(tool='{self.selected_tool}', "
            f"confidence={self.confidence:.2f}, fallback={self.fallback_used})"
        )


class ToolSelector:
    """
    Selector inteligente de Tools usando LLM.

    Analiza las consultas del usuario y selecciona automáticamente
    el tool más apropiado para responderlas.

    Examples:
        >>> selector = ToolSelector(llm_provider)
        >>> result = await selector.select_tool("¿Cuántos usuarios hay?")
        >>> print(result.selected_tool)  # "query"
    """

    def __init__(self, llm_provider):
        """
        Inicializar el selector de tools.

        Args:
            llm_provider: Proveedor de LLM para hacer la selección
        """
        self.llm_provider = llm_provider
        self.prompt_manager = get_default_manager()
        self.registry = get_registry()
        logger.info("ToolSelector inicializado")

    async def select_tool(
        self,
        user_query: str,
        available_tools: Optional[List[str]] = None
    ) -> ToolSelectionResult:
        """
        Seleccionar el tool más apropiado para una consulta.

        Args:
            user_query: Consulta del usuario
            available_tools: Lista de tools disponibles (None = todos los del registry)

        Returns:
            ToolSelectionResult con el tool seleccionado

        Example:
            >>> result = await selector.select_tool("¿Cuántos usuarios hay?")
            >>> if result.has_selection:
            ...     print(f"Tool: {result.selected_tool}")
        """
        try:
            # Obtener tools disponibles
            tools = self._get_available_tools(available_tools)

            if not tools:
                logger.warning("No hay tools disponibles para selección")
                return ToolSelectionResult(
                    selected_tool=None,
                    confidence=0.0,
                    reasoning="No hay tools disponibles"
                )

            # Generar descripción de tools para el prompt
            tools_description = self._generate_tools_description(tools)

            # Obtener prompt de selección
            prompt = self.prompt_manager.get_prompt(
                'tool_selection',
                user_query=user_query,
                tools_description=tools_description
            )

            logger.debug(f"Prompt de selección generado ({len(prompt)} chars)")

            # Llamar al LLM para selección
            llm_response = await self.llm_provider.generate(
                prompt=prompt,
                temperature=0.1,  # Baja temperatura para más determinismo
                max_tokens=200
            )

            logger.debug(f"Respuesta del LLM: {llm_response[:200]}...")

            # Parsear respuesta del LLM
            result = self._parse_llm_response(llm_response, tools)

            logger.info(
                f"Tool seleccionado: {result.selected_tool} "
                f"(confidence: {result.confidence:.2f})"
            )

            return result

        except Exception as e:
            logger.error(f"Error en selección de tool: {e}", exc_info=True)
            return self._get_fallback_tool(user_query)

    def _get_available_tools(self, tool_names: Optional[List[str]] = None) -> List[BaseTool]:
        """
        Obtener lista de tools disponibles.

        Args:
            tool_names: Nombres de tools específicos (None = todos)

        Returns:
            Lista de tools disponibles
        """
        if tool_names:
            tools = []
            for name in tool_names:
                tool = self.registry.get_tool_by_name(name)
                if tool:
                    tools.append(tool)
            return tools

        # Obtener todos los tools del registry
        return self.registry.get_all_tools()

    def _generate_tools_description(self, tools: List[BaseTool]) -> str:
        """
        Generar descripción formateada de tools para el prompt.

        Args:
            tools: Lista de tools disponibles

        Returns:
            Descripción formateada en markdown
        """
        descriptions = []

        for tool in tools:
            metadata = tool.get_metadata()

            # Formatear comandos
            commands = ", ".join(metadata.commands)

            # Formatear parámetros
            params_desc = []
            for param in metadata.parameters.values():
                required = "requerido" if param.required else "opcional"
                params_desc.append(f"  - {param.name} ({param.type}): {param.description} [{required}]")

            params_text = "\n".join(params_desc) if params_desc else "  Sin parámetros"

            # Construir descripción del tool
            tool_desc = f"""
**{metadata.name}**
- Comandos: {commands}
- Descripción: {metadata.description}
- Categoría: {metadata.category}
- Parámetros:
{params_text}
"""
            descriptions.append(tool_desc.strip())

        return "\n\n".join(descriptions)

    def _parse_llm_response(
        self,
        llm_response: str,
        available_tools: List[BaseTool]
    ) -> ToolSelectionResult:
        """
        Parsear la respuesta del LLM para extraer el tool seleccionado.

        Espera formato JSON:
        {
            "tool": "nombre_del_tool",
            "confidence": 0.9,
            "reasoning": "explicación..."
        }

        Args:
            llm_response: Respuesta del LLM
            available_tools: Tools disponibles para validar

        Returns:
            ToolSelectionResult parseado
        """
        try:
            # Intentar extraer JSON de la respuesta
            json_match = re.search(r'\{[^}]+\}', llm_response, re.DOTALL)

            if json_match:
                json_str = json_match.group(0)
                data = json.loads(json_str)

                tool_name = data.get('tool', '').lower()
                confidence = float(data.get('confidence', 0.0))
                reasoning = data.get('reasoning', '')

                # Validar que el tool existe
                tool_names = [t.name.lower() for t in available_tools]

                if tool_name in tool_names:
                    # Obtener el nombre real del tool (con capitalización correcta)
                    actual_tool = next(
                        (t.name for t in available_tools if t.name.lower() == tool_name),
                        tool_name
                    )

                    return ToolSelectionResult(
                        selected_tool=actual_tool,
                        confidence=confidence,
                        reasoning=reasoning,
                        fallback_used=False
                    )

                logger.warning(f"Tool '{tool_name}' no encontrado en disponibles: {tool_names}")

            # Si no se pudo parsear JSON, intentar extracción simple
            return self._simple_parse(llm_response, available_tools)

        except Exception as e:
            logger.warning(f"Error parseando respuesta LLM: {e}")
            return self._simple_parse(llm_response, available_tools)

    def _simple_parse(
        self,
        llm_response: str,
        available_tools: List[BaseTool]
    ) -> ToolSelectionResult:
        """
        Parseo simple si falla el JSON.

        Busca el nombre del tool en la respuesta.

        Args:
            llm_response: Respuesta del LLM
            available_tools: Tools disponibles

        Returns:
            ToolSelectionResult con mejor match
        """
        llm_response_lower = llm_response.lower()

        # Buscar menciones de tools en la respuesta
        for tool in available_tools:
            if tool.name.lower() in llm_response_lower:
                return ToolSelectionResult(
                    selected_tool=tool.name,
                    confidence=0.5,  # Confianza media
                    reasoning="Detectado por coincidencia de nombre",
                    fallback_used=True
                )

        # No se encontró ningún tool
        return ToolSelectionResult(
            selected_tool=None,
            confidence=0.0,
            reasoning="No se pudo identificar un tool apropiado",
            fallback_used=True
        )

    def _get_fallback_tool(self, user_query: str) -> ToolSelectionResult:
        """
        Obtener tool de fallback cuando falla la selección.

        Por ahora usa QueryTool como fallback por defecto.

        Args:
            user_query: Consulta del usuario

        Returns:
            ToolSelectionResult con tool de fallback
        """
        logger.warning("Usando fallback tool: query")

        return ToolSelectionResult(
            selected_tool="query",
            confidence=0.3,
            reasoning="Fallback automático por error en selección",
            fallback_used=True
        )

    def get_stats(self) -> Dict[str, Any]:
        """
        Obtener estadísticas del selector.

        Returns:
            Diccionario con estadísticas
        """
        return {
            "tools_available": len(self.registry.get_all_tools()),
            "prompt_stats": self.prompt_manager.get_metrics('tool_selection')
        }
