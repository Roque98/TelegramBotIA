"""
SchemaIntrospector - Introspección del esquema de base de datos.

Responsabilidad única: leer la estructura de tablas y columnas
de un engine SQLAlchemy y devolverla como texto descriptivo.
"""
import logging
from sqlalchemy import inspect
from sqlalchemy.exc import SQLAlchemyError, OperationalError
from sqlalchemy.exc import TimeoutError as SQLTimeoutError

from src.utils.retry import db_retry
from src.config.settings import settings

logger = logging.getLogger(__name__)


class SchemaIntrospector:
    """Lee el esquema (tablas y columnas) de un engine SQLAlchemy."""

    def __init__(self, engine) -> None:
        self._engine = engine

    @db_retry(
        max_attempts=settings.retry_db_max_attempts,
        min_wait=settings.retry_db_min_wait,
        max_wait=settings.retry_db_max_wait,
    )
    def get_schema(self) -> str:
        """
        Retorna el esquema de la base de datos en formato texto.

        Returns:
            Descripción de tablas y columnas.

        Raises:
            ConnectionError: Si hay error de conexión.
            TimeoutError: Si la operación tarda demasiado.
            SQLAlchemyError: Si hay error de BD.
        """
        try:
            inspector = inspect(self._engine)
            schema_description = []

            for table_name in inspector.get_table_names():
                schema_description.append(f"\nTabla: {table_name}")
                columns = inspector.get_columns(table_name)

                for column in columns:
                    col_type = str(column["type"])
                    nullable = "NULL" if column["nullable"] else "NOT NULL"
                    schema_description.append(
                        f"  - {column['name']}: {col_type} {nullable}"
                    )

            return "\n".join(schema_description)

        except OperationalError as e:
            logger.error(f"Error de conexión al obtener esquema: {e}")
            raise ConnectionError(f"No se pudo conectar a la base de datos: {e}") from e

        except SQLTimeoutError as e:
            logger.error(f"Timeout al obtener esquema: {e}")
            raise TimeoutError(f"La base de datos no respondió a tiempo: {e}") from e

        except SQLAlchemyError as e:
            logger.error(f"Error de SQLAlchemy obteniendo esquema: {e}")
            raise

        except Exception as e:
            logger.error(f"Error inesperado obteniendo esquema: {e}", exc_info=True)
            raise
