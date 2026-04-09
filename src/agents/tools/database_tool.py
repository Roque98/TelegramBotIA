"""
Database Tool - Herramienta para consultas de datos de negocio.

El agente describe en lenguaje natural qué datos necesita.
DatabaseTool genera el SQL internamente usando gpt-5.4 y lo ejecuta.
El loop ReAct (mini) nunca necesita escribir SQL.
"""

import logging
import re
import time
from typing import Any, Optional

from .base import BaseTool, ToolCategory, ToolDefinition, ToolParameter, ToolResult

logger = logging.getLogger(__name__)

SQL_GENERATION_PROMPT = """Eres un experto en SQL Server (T-SQL). Genera UNA consulta SELECT para responder la solicitud del usuario.

REGLAS:
- Solo SELECT, nunca INSERT/UPDATE/DELETE/DROP
- Usa TOP para limitar resultados cuando sea apropiado
- Usa alias descriptivos en español (AS total, AS nombre, etc.)
- La base de datos es: abcmasplus
- Si no tienes suficiente contexto del esquema, genera la consulta más razonable posible

SOLICITUD: {description}

Responde ÚNICAMENTE con la consulta SQL, sin explicaciones ni markdown."""


class DatabaseTool(BaseTool):
    """
    Herramienta para consultar datos de negocio desde lenguaje natural.

    El agente describe qué datos necesita en lenguaje natural.
    DatabaseTool usa gpt-5.4 para generar el SQL y lo ejecuta.

    Example:
        >>> tool = DatabaseTool(db_manager, llm_provider)
        >>> result = await tool.execute(description="cuántas ventas hubo ayer")
        >>> print(result.to_observation())
    """

    def __init__(
        self,
        db_manager: Any,
        llm_provider: Any,
        sql_validator: Optional[Any] = None,
        max_results: int = 100,
    ):
        self.db_manager = db_manager
        self.llm_provider = llm_provider
        self.max_results = max_results

        if sql_validator:
            self.sql_validator = sql_validator
        else:
            from src.infra.database.sql_validator import SQLValidator
            self.sql_validator = SQLValidator()

        logger.info(f"DatabaseTool inicializado (model={llm_provider.model}, max_results={max_results})")

    @property
    def definition(self) -> ToolDefinition:
        return ToolDefinition(
            name="database_query",
            description=(
                "Consulta datos de negocio de la base de datos. "
                "Describe en lenguaje natural qué datos necesitas: ventas, usuarios, productos, "
                "reportes, estadísticas, facturación, stock o cualquier dato empresarial."
            ),
            category=ToolCategory.DATABASE,
            parameters=[
                ToolParameter(
                    name="description",
                    param_type="string",
                    description="Descripción en lenguaje natural de los datos que necesitas",
                    required=True,
                    examples=[
                        "total de ventas de los últimos 7 días",
                        "top 5 vendedores por monto este mes",
                        "cantidad de usuarios activos por gerencia",
                    ],
                ),
            ],
            examples=[
                {"description": "total de ventas de hoy comparado con ayer"},
                {"description": "top 10 productos más vendidos este mes"},
            ],
            returns="Resultados de la consulta como lista de registros",
            usage_hint=(
                "Para datos de negocio (ventas, reportes, usuarios, productos, stock, facturación): "
                "usa `database_query`. **Obligatorio** antes de responder con cualquier cifra — "
                "está PROHIBIDO inventar o asumir datos numéricos sin consultar la base de datos."
            ),
        )

    async def execute(self, **kwargs: Any) -> ToolResult:
        start_time = time.perf_counter()
        description = kwargs.get("description", "").strip()

        if not description:
            return ToolResult.error_result("Se requiere una descripción de los datos a consultar")

        try:
            # 1. Generar SQL con gpt-5.4
            sql = await self._generate_sql(description)
            if not sql:
                return ToolResult.error_result("No se pudo generar una consulta SQL válida")

            logger.info(f"SQL generado: {sql[:120]}...")

            # 2. Validar seguridad
            is_safe, validation_error = self.sql_validator.validate(sql)
            if not is_safe:
                logger.warning(f"SQL validation failed: {validation_error}")
                return ToolResult.error_result(
                    f"La consulta generada no pasó validación de seguridad: {validation_error}",
                    metadata={"sql": sql[:200]},
                )

            # 3. Ejecutar
            results = await self._execute_query(sql)

            if isinstance(results, list) and len(results) > self.max_results:
                results = results[:self.max_results]

            elapsed_ms = (time.perf_counter() - start_time) * 1000
            logger.info(f"database_query: {elapsed_ms:.0f}ms, {len(results) if isinstance(results, list) else 1} resultados")

            return ToolResult.success_result(
                data=results,
                execution_time_ms=elapsed_ms,
                metadata={
                    "sql": sql[:200],
                    "result_count": len(results) if isinstance(results, list) else 1,
                },
            )

        except Exception as e:
            elapsed_ms = (time.perf_counter() - start_time) * 1000
            logger.error(f"DatabaseTool error: {e}")
            return ToolResult.error_result(
                error=f"Error consultando datos: {str(e)}",
                execution_time_ms=elapsed_ms,
            )

    async def _generate_sql(self, description: str) -> Optional[str]:
        """Genera SQL T-SQL a partir de una descripción en lenguaje natural."""
        try:
            messages = [
                {"role": "system", "content": "Eres un experto en T-SQL para SQL Server. Solo respondes con SQL válido."},
                {"role": "user", "content": SQL_GENERATION_PROMPT.format(description=description)},
            ]
            raw = await self.llm_provider.generate_messages(messages)
            sql = self._extract_sql(raw.strip())
            return sql
        except Exception as e:
            logger.error(f"SQL generation failed: {e}")
            return None

    def _extract_sql(self, text: str) -> str:
        """Extrae el SQL limpio de la respuesta del LLM."""
        # Quitar bloques markdown ```sql ... ```
        match = re.search(r"```(?:sql)?\s*([\s\S]+?)```", text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
        return text.strip()

    async def _execute_query(self, query: str) -> list[dict[str, Any]]:
        """
        Ejecuta la query contra la base de datos.

        Args:
            query: Consulta SQL validada

        Returns:
            Lista de resultados como diccionarios
        """
        if not hasattr(self.db_manager, "execute_query_async"):
            raise ValueError("DatabaseManager does not have execute_query_async method")

        results = await self.db_manager.execute_query_async(query)

        # Convertir a lista de dicts si es necesario
        if results is None:
            return []

        if isinstance(results, list):
            # Si ya es lista de dicts, retornar
            if results and isinstance(results[0], dict):
                return results
            # Si es lista de tuples/rows, convertir
            return [dict(row) if hasattr(row, "_asdict") else row for row in results]

        return [results]
