"""
Script para crear la tabla UserMemoryProfiles en la base de datos.

Este script ejecuta el archivo SQL de migración para crear la tabla
UserMemoryProfiles con todos sus índices y constraints.

Uso:
    python scripts/create_memory_table.py
"""
import logging
import sys
from pathlib import Path

# Agregar src al path para imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from src.infra.database.connection import DatabaseManager

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_memory_table():
    """
    Crear tabla UserMemoryProfiles ejecutando el script SQL.
    """
    db_manager = DatabaseManager()
    sql_file_path = Path(__file__).parent.parent / "database" / "migrations" / "002_create_user_memory_profiles.sql"

    logger.info(f"📂 Leyendo script SQL: {sql_file_path}")

    if not sql_file_path.exists():
        logger.error(f"❌ Archivo SQL no encontrado: {sql_file_path}")
        return False

    # Leer el archivo SQL
    with open(sql_file_path, 'r', encoding='utf-8') as f:
        sql_content = f.read()

    # Dividir en statements individuales (separados por GO)
    statements = [stmt.strip() for stmt in sql_content.split('GO') if stmt.strip()]

    logger.info(f"📝 Ejecutando {len(statements)} statements SQL...")

    try:
        with db_manager.get_session() as session:
            for i, statement in enumerate(statements, 1):
                # Saltar comentarios y USE statements
                if statement.startswith('--') or statement.startswith('USE') or statement.startswith('PRINT'):
                    continue

                # Saltar SELECT statements de verificación
                if statement.strip().startswith('SELECT') and 'INFORMATION_SCHEMA' in statement:
                    continue

                try:
                    logger.info(f"   Ejecutando statement {i}/{len(statements)}...")
                    session.execute(text(statement))
                    session.commit()
                except Exception as e:
                    # Si la tabla ya existe, no es un error crítico
                    if "already exists" in str(e) or "There is already an object" in str(e):
                        logger.warning(f"   ⚠️  Tabla ya existe, continuando...")
                    else:
                        logger.error(f"   ❌ Error en statement {i}: {e}")
                        raise

            logger.info("✅ Tabla UserMemoryProfiles creada exitosamente")

            # Verificar que la tabla existe
            verify_query = text("""
                SELECT COUNT(*) as count
                FROM INFORMATION_SCHEMA.TABLES
                WHERE TABLE_SCHEMA = 'dbo'
                  AND TABLE_NAME = 'UserMemoryProfiles'
            """)
            result = session.execute(verify_query).fetchone()

            if result.count == 1:
                logger.info("✅ Verificación: Tabla existe correctamente")

                # Mostrar estructura
                structure_query = text("""
                    SELECT
                        COLUMN_NAME,
                        DATA_TYPE,
                        IS_NULLABLE,
                        COLUMN_DEFAULT
                    FROM INFORMATION_SCHEMA.COLUMNS
                    WHERE TABLE_NAME = 'UserMemoryProfiles'
                    ORDER BY ORDINAL_POSITION
                """)
                columns = session.execute(structure_query).fetchall()

                logger.info(f"📋 Estructura de la tabla ({len(columns)} columnas):")
                for col in columns:
                    nullable = "NULL" if col.IS_NULLABLE == 'YES' else "NOT NULL"
                    default = f" DEFAULT {col.COLUMN_DEFAULT}" if col.COLUMN_DEFAULT else ""
                    logger.info(f"   - {col.COLUMN_NAME}: {col.DATA_TYPE} {nullable}{default}")

                # Mostrar índices
                index_query = text("""
                    SELECT
                        i.name AS index_name,
                        i.type_desc AS index_type
                    FROM sys.indexes i
                    INNER JOIN sys.tables t ON i.object_id = t.object_id
                    WHERE t.name = 'UserMemoryProfiles'
                      AND i.name IS NOT NULL
                """)
                indexes = session.execute(index_query).fetchall()

                if indexes:
                    logger.info(f"🔍 Índices creados ({len(indexes)}):")
                    for idx in indexes:
                        logger.info(f"   - {idx.index_name} ({idx.index_type})")

                return True
            else:
                logger.error("❌ Verificación falló: Tabla no encontrada después de creación")
                return False

    except Exception as e:
        logger.error(f"❌ Error creando tabla: {e}", exc_info=True)
        return False
    finally:
        db_manager.close()


if __name__ == "__main__":
    logger.info("=" * 80)
    logger.info("🚀 CREACIÓN DE TABLA UserMemoryProfiles")
    logger.info("=" * 80)

    try:
        success = create_memory_table()

        if success:
            logger.info("=" * 80)
            logger.info("✅ Tabla creada exitosamente")
            logger.info("=" * 80)
            logger.info("")
            logger.info("📌 SIGUIENTE PASO:")
            logger.info("   Ejecuta: python scripts/migrate_users_to_memory.py")
            logger.info("")
            sys.exit(0)
        else:
            logger.error("❌ Falló la creación de la tabla")
            sys.exit(1)

    except Exception as e:
        logger.error(f"❌ Error crítico: {e}")
        sys.exit(1)
