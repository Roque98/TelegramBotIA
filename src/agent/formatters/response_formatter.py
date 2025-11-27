"""
Formateador de respuestas para el usuario.

Formatea los resultados de consultas SQL en texto legible para el usuario.
"""
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


class ResponseFormatter:
    """Formateador de respuestas."""

    def __init__(self, max_results_display: int = 10):
        """
        Inicializar el formateador.

        Args:
            max_results_display: Número máximo de resultados a mostrar
        """
        self.max_results_display = max_results_display
        logger.info(f"Inicializado formateador de respuestas (max display: {max_results_display})")

    def format_query_results(
        self,
        user_query: str,
        sql_query: str,
        results: List[Dict[str, Any]],
        include_sql: bool = False
    ) -> str:
        """
        Formatear resultados de una consulta SQL.

        Args:
            user_query: Consulta original del usuario
            sql_query: Consulta SQL ejecutada
            results: Resultados de la consulta
            include_sql: Si se debe incluir el SQL en la respuesta

        Returns:
            Respuesta formateada
        """
        if not results:
            return self._format_empty_results(user_query)

        # Construir respuesta
        response_parts = []

        # Opcional: Incluir SQL ejecutado
        if include_sql:
            response_parts.append(f"**SQL ejecutado:**\n```sql\n{sql_query}\n```\n")

        # Información de resultados
        total_count = len(results)
        response_parts.append(f"**Resultados encontrados:** {total_count}\n")

        # Formatear resultados
        if total_count == 1:
            # Un solo resultado - formato detallado
            response_parts.append(self._format_single_result(results[0]))
        else:
            # Múltiples resultados - formato de lista
            response_parts.append(self._format_multiple_results(results))

        # Indicar si hay más resultados
        if total_count > self.max_results_display:
            hidden_count = total_count - self.max_results_display
            response_parts.append(f"\n... y {hidden_count} resultado(s) más.")

        return "\n".join(response_parts)

    def format_general_response(self, response_text: str) -> str:
        """
        Formatear una respuesta general (no de BD).

        Args:
            response_text: Texto de respuesta del LLM

        Returns:
            Respuesta formateada
        """
        return response_text

    def format_error(self, error_message: str, user_friendly: bool = True) -> str:
        """
        Formatear un mensaje de error.

        Args:
            error_message: Mensaje de error técnico
            user_friendly: Si se debe mostrar mensaje amigable

        Returns:
            Mensaje de error formateado
        """
        if user_friendly:
            return (
                "Lo siento, ocurrió un error al procesar tu consulta. "
                "Por favor, intenta de nuevo o reformula tu pregunta."
            )
        else:
            return f"**Error:** {error_message}"

    def _format_empty_results(self, user_query: str) -> str:
        """
        Formatear respuesta cuando no hay resultados.

        Args:
            user_query: Consulta del usuario

        Returns:
            Mensaje formateado
        """
        return "No encontré resultados para tu consulta."

    def _format_single_result(self, result: Dict[str, Any]) -> str:
        """
        Formatear un solo resultado en formato detallado.

        Args:
            result: Diccionario con el resultado

        Returns:
            Resultado formateado
        """
        lines = []

        for key, value in result.items():
            # Formatear valores None
            if value is None:
                value = "(vacío)"

            lines.append(f"**{key}:** {value}")

        return "\n".join(lines)

    def _format_multiple_results(self, results: List[Dict[str, Any]]) -> str:
        """
        Formatear múltiples resultados en formato de lista.

        Args:
            results: Lista de diccionarios con resultados

        Returns:
            Resultados formateados
        """
        lines = []

        # Limitar cantidad de resultados mostrados
        display_results = results[:self.max_results_display]

        for i, row in enumerate(display_results, 1):
            # Formatear cada fila
            row_text = self._format_row_inline(row)
            lines.append(f"{i}. {row_text}")

        return "\n".join(lines)

    def _format_row_inline(self, row: Dict[str, Any]) -> str:
        """
        Formatear una fila en formato inline (una línea).

        Args:
            row: Diccionario con los datos de la fila

        Returns:
            Fila formateada
        """
        parts = []

        for key, value in row.items():
            if value is None:
                value = "(vacío)"

            parts.append(f"{key}: {value}")

        return " | ".join(parts)

    def _format_row_table(self, row: Dict[str, Any]) -> str:
        """
        Formatear una fila en formato de tabla.

        Args:
            row: Diccionario con los datos de la fila

        Returns:
            Fila formateada
        """
        # TODO: Implementar formato de tabla con Unicode box drawing
        # Para una futura mejora con mejores tablas visuales
        return self._format_row_inline(row)
