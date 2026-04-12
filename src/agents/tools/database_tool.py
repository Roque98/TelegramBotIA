"""
Database Tool - Herramienta para consultas de datos de negocio.

El agente describe en lenguaje natural qué datos necesita.
DatabaseTool genera el SQL internamente usando gpt-5.4 y lo ejecuta.
El loop ReAct (mini) nunca necesita escribir SQL.

Soporta múltiples bases de datos vía DatabaseRegistry (DB-37).
El agente puede indicar el alias de conexión con el parámetro `db`.
"""

import logging
import re
import time
from typing import TYPE_CHECKING, Any, Optional, Union

from .base import BaseTool, ToolCategory, ToolDefinition, ToolParameter, ToolResult

if TYPE_CHECKING:
    from src.infra.database.registry import DatabaseRegistry
    from src.infra.database.connection import DatabaseManager

logger = logging.getLogger(__name__)

SQL_GENERATION_PROMPT = """Eres un experto en SQL Server (T-SQL). Genera UNA consulta SELECT para responder la solicitud del usuario.

REGLAS:
- Solo SELECT, nunca INSERT/UPDATE/DELETE/DROP
- Usa TOP para limitar resultados cuando sea apropiado
- Usa alias descriptivos en español (AS total, AS nombre, etc.)
- La base de datos destino es: {db_name}
- Si no tienes suficiente contexto del esquema, genera la consulta más razonable posible

SOLICITUD: {description}

Responde ÚNICAMENTE con la consulta SQL, sin explicaciones ni markdown."""


class DatabaseTool(BaseTool):
    """
    Herramienta para consultar datos de negocio desde lenguaje natural.

    El agente describe qué datos necesita en lenguaje natural.
    DatabaseTool usa gpt-5.4 para generar el SQL y lo ejecuta.

    Acepta tanto un DatabaseRegistry (multi-DB, DB-37) como un DatabaseManager
    legacy (single-DB), para backward-compat total.

    Example:
        >>> tool = DatabaseTool(db_manager=registry, llm_provider=llm)
        >>> result = await tool.execute(description="cuántas ventas hubo ayer", db="ventas")
        >>> print(result.to_observation())
    """

    def __init__(
        self,
        db_manager: Union["DatabaseRegistry", "DatabaseManager", Any],
        llm_provider: Any,
        sql_validator: Optional[Any] = None,
        max_results: int = 100,
    ):
        self._db_source = db_manager   # DatabaseRegistry o DatabaseManager legacy
        self.llm_provider = llm_provider
        self.max_results = max_results

        if sql_validator:
            self.sql_validator = sql_validator
        else:
            from src.infra.database.sql_validator import SQLValidator
            self.sql_validator = SQLValidator()

        # Detectar modo para logging
        from src.infra.database.registry import DatabaseRegistry
        is_registry = isinstance(db_manager, DatabaseRegistry)
        logger.info(
            f"DatabaseTool inicializado "
            f"(model={llm_provider.model}, max_results={max_results}, "
            f"mode={'registry' if is_registry else 'legacy'})"
        )

    def _get_available_dbs(self) -> list[str]:
        """Retorna los alias de conexión disponibles."""
        from src.infra.database.registry import DatabaseRegistry
        if isinstance(self._db_source, DatabaseRegistry):
            return self._db_source.get_aliases()
        return ["core"]

    def _resolve_manager(self, db_alias: str) -> Any:
        """
        Resuelve el DatabaseManager para el alias pedido.

        Acepta DatabaseRegistry (multi-DB) o DatabaseManager legacy.
        """
        from src.infra.database.registry import DatabaseRegistry
        if isinstance(self._db_source, DatabaseRegistry):
            return self._db_source.get(db_alias)
        # Legacy: siempre usa el manager único
        return self._db_source

    @property
    def definition(self) -> ToolDefinition:
        available = self._get_available_dbs()
        db_hint = ""
        if len(available) > 1:
            db_hint = f" Bases de datos disponibles: {', '.join(available)} (default: core)."

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
                ToolParameter(
                    name="db",
                    param_type="string",
                    description=(
                        f"Alias de la base de datos a consultar.{db_hint}"
                    ),
                    required=False,
                    examples=available,
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
                f"está PROHIBIDO inventar o asumir datos numéricos sin consultar la base de datos."
                + (f" Conexiones disponibles: {', '.join(available)}." if len(available) > 1 else "")
            ),
        )

    async def execute(self, **kwargs: Any) -> ToolResult:
        start_time = time.perf_counter()
        description = kwargs.get("description", "").strip()
        db_alias = (kwargs.get("db") or "core").strip().lower()

        if not description:
            return ToolResult.error_result("Se requiere una descripción de los datos a consultar")

        # Validar alias antes de generar SQL
        available = self._get_available_dbs()
        if db_alias not in available:
            return ToolResult.error_result(
                f"Base de datos '{db_alias}' no disponible. "
                f"Opciones: {', '.join(available)}"
            )

        try:
            # Resolver el manager para este alias
            manager = self._resolve_manager(db_alias)

            db_name = self._get_db_name(db_alias)
            sql = await self._generate_sql(description, db_name=db_name)
            if not sql:
                return ToolResult.error_result("No se pudo generar una consulta SQL válida")

            logger.info(f"SQL generado [{db_alias}]: {sql[:120]}...")

            is_safe, validation_error = self.sql_validator.validate(sql)
            if not is_safe:
                logger.warning(f"SQL validation failed: {validation_error}")
                return ToolResult.error_result(
                    f"La consulta generada no pasó validación de seguridad: {validation_error}",
                    metadata={"sql": sql[:200]},
                )

            results = await self._execute_query(sql, manager=manager)

            if isinstance(results, list) and len(results) > self.max_results:
                results = results[:self.max_results]

            elapsed_ms = (time.perf_counter() - start_time) * 1000
            logger.info(
                f"database_query [{db_alias}]: {elapsed_ms:.0f}ms, "
                f"{len(results) if isinstance(results, list) else 1} resultados"
            )

            return ToolResult.success_result(
                data=results,
                execution_time_ms=elapsed_ms,
                metadata={
                    "sql": sql[:200],
                    "db": db_alias,
                    "result_count": len(results) if isinstance(results, list) else 1,
                },
            )

        except KeyError as e:
            elapsed_ms = (time.perf_counter() - start_time) * 1000
            return ToolResult.error_result(
                error=str(e),
                execution_time_ms=elapsed_ms,
            )
        except Exception as e:
            elapsed_ms = (time.perf_counter() - start_time) * 1000
            logger.error(f"DatabaseTool error [{db_alias}]: {e}")
            return ToolResult.error_result(
                error=f"Error consultando datos: {str(e)}",
                execution_time_ms=elapsed_ms,
            )

    def _get_db_name(self, alias: str) -> str:
        """Retorna el nombre de la BD para el alias (para inyectar en el prompt SQL)."""
        from src.infra.database.registry import DatabaseRegistry
        if isinstance(self._db_source, DatabaseRegistry):
            configs = self._db_source._configs
            if alias in configs:
                return configs[alias].name or alias
        return alias

    async def _generate_sql(self, description: str, db_name: str = "abcmasplus") -> Optional[str]:
        """Genera SQL T-SQL a partir de una descripción en lenguaje natural."""
        try:
            messages = [
                {"role": "system", "content": "Eres un experto en T-SQL para SQL Server. Solo respondes con SQL válido."},
                {"role": "user", "content": SQL_GENERATION_PROMPT.format(
                    description=description,
                    db_name=db_name,
                )},
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

    async def _execute_query(self, query: str, manager: Any = None) -> list[dict[str, Any]]:
        """
        Ejecuta la query contra el manager indicado (o el legacy si no se pasa).

        Args:
            query: Consulta SQL validada
            manager: DatabaseManager a usar. Si es None, usa self._db_source (legacy).

        Returns:
            Lista de resultados como diccionarios
        """
        target = manager if manager is not None else self._db_source
        if not hasattr(target, "execute_query_async"):
            raise ValueError("DatabaseManager does not have execute_query_async method")

        results = await target.execute_query_async(query)

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
