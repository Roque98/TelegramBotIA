"""
Validador de consultas SQL.

Proporciona validaciones de seguridad para consultas SQL antes de ejecutarlas.
"""
import logging
import re
from typing import Tuple

logger = logging.getLogger(__name__)


class SQLValidator:
    """Validador de consultas SQL."""

    # Keywords prohibidos que no deben aparecer en las consultas
    FORBIDDEN_KEYWORDS = [
        "DROP", "DELETE", "UPDATE", "INSERT", "ALTER", "TRUNCATE",
        "CREATE", "REPLACE", "EXEC", "EXECUTE", "GRANT", "REVOKE"
    ]

    # Comandos de sistema prohibidos
    FORBIDDEN_SYSTEM_COMMANDS = [
        "xp_cmdshell", "sp_executesql", "openrowset", "opendatasource"
    ]

    def __init__(self):
        """Inicializar el validador."""
        logger.info("Inicializado validador de SQL")

    def validate(self, sql_query: str) -> Tuple[bool, str]:
        """
        Validar una consulta SQL.

        Args:
            sql_query: Consulta SQL a validar

        Returns:
            Tupla (es_valida, mensaje_error)
            - es_valida: True si la consulta es válida, False si no
            - mensaje_error: Mensaje de error si no es válida, vacío si es válida
        """
        # 1. Verificar que no esté vacía
        if not sql_query or not sql_query.strip():
            return False, "La consulta SQL está vacía"

        # 2. Normalizar la consulta
        normalized_query = sql_query.strip().upper()

        # 3. Verificar que comience con SELECT
        if not normalized_query.startswith("SELECT"):
            return False, "Solo se permiten consultas SELECT"

        # 4. Verificar keywords prohibidos
        for keyword in self.FORBIDDEN_KEYWORDS:
            if self._contains_keyword(normalized_query, keyword):
                logger.warning(f"Keyword prohibido detectado: {keyword}")
                return False, f"Keyword prohibido detectado: {keyword}"

        # 5. Verificar comandos de sistema
        for command in self.FORBIDDEN_SYSTEM_COMMANDS:
            if command.upper() in normalized_query:
                logger.warning(f"Comando de sistema prohibido detectado: {command}")
                return False, f"Comando de sistema prohibido detectado: {command}"

        # 6. Verificar múltiples statements (detectar ;)
        if self._has_multiple_statements(sql_query):
            logger.warning("Múltiples statements detectados")
            return False, "No se permiten múltiples consultas SQL"

        # 7. Verificar comentarios sospechosos que puedan ocultar código
        if self._has_suspicious_comments(sql_query):
            logger.warning("Comentarios sospechosos detectados")
            return False, "La consulta contiene comentarios sospechosos"

        logger.info("Consulta SQL validada exitosamente")
        return True, ""

    def _contains_keyword(self, normalized_query: str, keyword: str) -> bool:
        """
        Verificar si una consulta contiene un keyword prohibido.

        Usa word boundaries para evitar falsos positivos (ej: 'SELECT' en 'SELECTED').

        Args:
            normalized_query: Consulta normalizada (uppercase)
            keyword: Keyword a buscar

        Returns:
            True si contiene el keyword, False si no
        """
        pattern = r'\b' + keyword + r'\b'
        return bool(re.search(pattern, normalized_query))

    def _has_multiple_statements(self, sql_query: str) -> bool:
        """
        Verificar si la consulta contiene múltiples statements.

        Args:
            sql_query: Consulta SQL

        Returns:
            True si tiene múltiples statements, False si no
        """
        # Remover strings literales para evitar falsos positivos
        cleaned_query = re.sub(r"'[^']*'", "", sql_query)

        # Buscar punto y coma que no esté al final
        semicolons = cleaned_query.count(';')

        if semicolons == 0:
            return False
        elif semicolons == 1 and cleaned_query.strip().endswith(';'):
            return False
        else:
            return True

    def _has_suspicious_comments(self, sql_query: str) -> bool:
        """
        Verificar si la consulta tiene comentarios sospechosos.

        Args:
            sql_query: Consulta SQL

        Returns:
            True si tiene comentarios sospechosos, False si no
        """
        # Buscar comentarios de bloque /* */ que puedan ocultar código
        if "/*" in sql_query and "*/" in sql_query:
            comment_content = re.findall(r'/\*(.*?)\*/', sql_query, re.DOTALL)
            for comment in comment_content:
                # Verificar si el comentario contiene keywords prohibidos
                comment_upper = comment.upper()
                for keyword in self.FORBIDDEN_KEYWORDS:
                    if keyword in comment_upper:
                        return True

        return False

    def is_safe_query(self, sql_query: str) -> bool:
        """
        Verificar si una consulta es segura.

        Args:
            sql_query: Consulta SQL

        Returns:
            True si es segura, False si no
        """
        is_valid, _ = self.validate(sql_query)
        return is_valid
