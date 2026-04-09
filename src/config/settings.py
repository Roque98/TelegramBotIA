"""
Configuración centralizada de la aplicación usando Pydantic Settings.
"""
import os
from pathlib import Path
from urllib.parse import quote_plus
from typing import Optional
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

# Obtener la ruta del directorio raíz del proyecto
PROJECT_ROOT = Path(__file__).parent.parent.parent
ENV_FILE = PROJECT_ROOT / ".env"

# Forzar carga del archivo .env con prioridad sobre variables de entorno del sistema
load_dotenv(ENV_FILE, override=True)


class DbConnectionConfig(BaseModel):
    """Configuración de una conexión a base de datos SQL Server."""

    alias: str                          # nombre lógico: "core", "ventas", etc.
    host: str = "localhost"
    port: int = 1433
    instance: str = ""                  # instancia nombrada, ej: SQLEXPRESS
    name: str = ""                      # nombre de la BD
    user: str = ""
    password: str = ""
    db_type: str = "mssql"

    @property
    def database_url(self) -> str:
        """Construye la URL de conexión SQLAlchemy."""
        if self.db_type == "sqlite":
            return f"sqlite:///{self.name}"
        elif self.db_type == "postgresql":
            return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"
        elif self.db_type == "mysql":
            return f"mysql+pymysql://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"
        elif self.db_type in ("mssql", "sqlserver"):
            driver = "ODBC Driver 17 for SQL Server"
            if self.instance:
                odbc_str = (
                    f"DRIVER={{{driver}}};"
                    f"SERVER={self.host}\\{self.instance};"
                    f"DATABASE={self.name};"
                    f"UID={self.user};"
                    f"PWD={self.password};"
                    f"Connection Timeout=15;"
                )
                return f"mssql+pyodbc:///?odbc_connect={quote_plus(odbc_str)}"
            else:
                user = quote_plus(self.user)
                password = quote_plus(self.password)
                return (
                    f"mssql+pyodbc://{user}:{password}@{self.host}:{self.port}/{self.name}"
                    f"?driver=ODBC+Driver+17+for+SQL+Server"
                )
        raise ValueError(f"db_type no soportado: {self.db_type}")

    @property
    def display_name(self) -> str:
        """Nombre legible para mostrar en usage_hints y logs."""
        return f"{self.alias} ({self.name}@{self.host})"


class Settings(BaseSettings):
    """Configuración de la aplicación."""

    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE),
        env_file_encoding="utf-8",
        case_sensitive=False
    )

    # Telegram
    telegram_bot_token: str

    # LLM Configuration
    openai_api_key: str = ""
    openai_loop_model: str = "gpt-5.4-mini"  # ReAct loop: reasoning + tool selection
    openai_data_model: str = "gpt-5.4"       # DatabaseTool: generación de SQL complejo
    anthropic_api_key: str = ""

    # Database — conexión principal "core" (backward-compat)
    db_host: str = "localhost"
    db_port: int = 1433
    db_instance: str = ""  # Para SQL Server: SQLEXPRESS, MSSQLSERVER, etc.
    db_name: str
    db_user: str
    db_password: str
    db_type: str = "mssql"

    # Multi-database: alias activos separados por coma, ej: "core,ventas,rrhh"
    # Si está vacío, solo se usa "core" (las vars DB_HOST/PORT/... de arriba)
    db_connections: str = ""

    # Application
    log_level: str = "INFO"
    environment: str = "development"

    # Retry Configuration
    retry_llm_max_attempts: int = 3
    retry_llm_min_wait: int = 2       # segundos
    retry_llm_max_wait: int = 30      # segundos
    retry_db_max_attempts: int = 3
    retry_db_min_wait: int = 1        # segundos
    retry_db_max_wait: int = 15       # segundos

    @property
    def database_url(self) -> str:
        """Construir URL de conexión a la base de datos."""
        if self.db_type == "sqlite":
            return f"sqlite:///{self.db_name}"
        elif self.db_type == "postgresql":
            return f"postgresql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"
        elif self.db_type == "mysql":
            return f"mysql+pymysql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"
        elif self.db_type == "mssql" or self.db_type == "sqlserver":
            # Para SQL Server usando pyodbc con ODBC Driver 17 for SQL Server
            driver = "ODBC Driver 17 for SQL Server"

            # Si se especifica una instancia nombrada (ej: SQLEXPRESS), usar odbc_connect
            if self.db_instance:
                # Construir connection string ODBC directa para instancia nombrada
                odbc_str = (
                    f"DRIVER={{{driver}}};"
                    f"SERVER={self.db_host}\\{self.db_instance};"
                    f"DATABASE={self.db_name};"
                    f"UID={self.db_user};"
                    f"PWD={self.db_password};"
                    f"Connection Timeout=15;"
                )
                # Usar odbc_connect permite pasar la connection string completa
                return f"mssql+pyodbc:///?odbc_connect={quote_plus(odbc_str)}"
            else:
                # Para conexión por puerto TCP/IP (sin instancia nombrada)
                user = quote_plus(self.db_user)
                password = quote_plus(self.db_password)
                driver_encoded = "ODBC+Driver+17+for+SQL+Server"
                return f"mssql+pyodbc://{user}:{password}@{self.db_host}:{self.db_port}/{self.db_name}?driver={driver_encoded}"
        else:
            raise ValueError(f"Tipo de base de datos no soportado: {self.db_type}")


    def get_db_connections(self) -> dict[str, DbConnectionConfig]:
        """
        Retorna todas las conexiones configuradas, keyed por alias.

        Lógica:
        - Siempre incluye "core" usando las vars DB_HOST/PORT/NAME/USER/PASSWORD/TYPE.
        - Si DB_CONNECTIONS tiene aliases adicionales (ej: "core,ventas"), lee sus
          vars del entorno con prefijo DB_<ALIAS>_* (ej: DB_VENTAS_HOST, DB_VENTAS_NAME…).
        - "core" en DB_CONNECTIONS se ignora (ya se agrega automáticamente).

        Ejemplo de .env para agregar "ventas":
            DB_CONNECTIONS=core,ventas
            DB_VENTAS_HOST=192.168.1.50
            DB_VENTAS_PORT=1433
            DB_VENTAS_NAME=ventas_db
            DB_VENTAS_USER=ventas_user
            DB_VENTAS_PASSWORD=secret
        """
        connections: dict[str, DbConnectionConfig] = {}

        # "core" siempre disponible usando las vars DB_* actuales
        connections["core"] = DbConnectionConfig(
            alias="core",
            host=self.db_host,
            port=self.db_port,
            instance=self.db_instance,
            name=self.db_name,
            user=self.db_user,
            password=self.db_password,
            db_type=self.db_type,
        )

        # Aliases adicionales desde DB_CONNECTIONS
        if self.db_connections:
            for alias in self.db_connections.split(","):
                alias = alias.strip().lower()
                if not alias or alias == "core":
                    continue
                prefix = f"DB_{alias.upper()}_"
                connections[alias] = DbConnectionConfig(
                    alias=alias,
                    host=os.environ.get(f"{prefix}HOST", "localhost"),
                    port=int(os.environ.get(f"{prefix}PORT", "1433")),
                    instance=os.environ.get(f"{prefix}INSTANCE", ""),
                    name=os.environ.get(f"{prefix}NAME", ""),
                    user=os.environ.get(f"{prefix}USER", ""),
                    password=os.environ.get(f"{prefix}PASSWORD", ""),
                    db_type=os.environ.get(f"{prefix}TYPE", "mssql"),
                )

        return connections


# Instancia global de configuración
settings = Settings()
