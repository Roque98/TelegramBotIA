"""
Gestión de conexiones a la base de datos.
"""
import logging
from typing import List, Dict, Any
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from src.config.settings import settings

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Gestor de conexiones y operaciones de base de datos."""

    def __init__(self):
        """Inicializar el gestor de base de datos."""
        self.database_url = settings.database_url

        # Para operaciones síncronas con configuración optimizada
        self.engine = create_engine(
            self.database_url,
            echo=False,
            pool_size=5,              # Número de conexiones permanentes en el pool
            max_overflow=10,          # Conexiones adicionales permitidas
            pool_timeout=20,          # Segundos esperando conexión del pool
            pool_recycle=3600,        # Reciclar conexiones cada hora (evita timeouts)
            pool_pre_ping=True,       # Verificar conexión antes de usar (previene errores)
            connect_args={
                "timeout": 15,        # Timeout de conexión inicial (segundos)
            }
        )
        self.SessionLocal = sessionmaker(bind=self.engine)

        logger.info(f"Conectado a base de datos: {settings.db_type} en {settings.db_host}")

    def get_session(self) -> Session:
        """Obtener una sesión de base de datos."""
        return self.SessionLocal()

    def get_schema(self) -> str:
        """
        Obtener el esquema de la base de datos en formato texto.

        Returns:
            Descripción del esquema de la base de datos
        """
        try:
            inspector = inspect(self.engine)
            schema_description = []

            for table_name in inspector.get_table_names():
                schema_description.append(f"\nTabla: {table_name}")
                columns = inspector.get_columns(table_name)

                for column in columns:
                    col_type = str(column['type'])
                    nullable = "NULL" if column['nullable'] else "NOT NULL"
                    schema_description.append(
                        f"  - {column['name']}: {col_type} {nullable}"
                    )

            return "\n".join(schema_description)

        except Exception as e:
            logger.error(f"Error obteniendo esquema: {e}")
            raise

    def execute_query(self, sql_query: str) -> List[Dict[str, Any]]:
        """
        Ejecutar una consulta SQL de solo lectura.

        Args:
            sql_query: Consulta SQL a ejecutar

        Returns:
            Lista de diccionarios con los resultados

        Raises:
            ValueError: Si la consulta no es de solo lectura
        """
        # Validar que sea solo SELECT
        query_upper = sql_query.strip().upper()
        if not query_upper.startswith("SELECT"):
            raise ValueError("Solo se permiten consultas SELECT")

        try:
            with self.get_session() as session:
                result = session.execute(text(sql_query))
                rows = result.fetchall()

                # Convertir a lista de diccionarios
                if rows:
                    columns = result.keys()
                    return [dict(zip(columns, row)) for row in rows]
                return []

        except Exception as e:
            logger.error(f"Error ejecutando consulta: {e}")
            raise

    def close(self):
        """Cerrar las conexiones de base de datos."""
        self.engine.dispose()
        logger.info("Conexiones de base de datos cerradas")
