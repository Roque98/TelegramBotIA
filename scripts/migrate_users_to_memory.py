"""
Script de migración: Crear perfiles de memoria para usuarios existentes.

Este script crea perfiles de memoria vacíos para todos los usuarios activos
que aún no tienen un perfil en UserMemoryProfiles.

Uso:
    python scripts/migrate_users_to_memory.py
"""
import logging
import sys
from pathlib import Path

# Agregar src al path para imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from src.database.connection import DatabaseManager

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def migrate_existing_users():
    """
    Crear perfiles de memoria vacíos para usuarios existentes.

    Solo crea perfiles para usuarios activos que no tengan uno.
    """
    db_manager = DatabaseManager()

    try:
        with db_manager.get_session() as session:
            # Query para insertar perfiles vacíos
            query = text("""
                INSERT INTO [dbo].[UserMemoryProfiles]
                    ([idUsuario], [numInteracciones], [fechaCreacion], [ultimaActualizacion], [version])
                SELECT
                    u.idUsuario,
                    0 AS numInteracciones,
                    GETDATE() AS fechaCreacion,
                    GETDATE() AS ultimaActualizacion,
                    1 AS version
                FROM [dbo].[Usuarios] u
                WHERE u.activo = 1
                  AND NOT EXISTS (
                      SELECT 1
                      FROM [dbo].[UserMemoryProfiles] m
                      WHERE m.idUsuario = u.idUsuario
                  )
            """)

            result = session.execute(query)
            rows_inserted = result.rowcount
            session.commit()

            logger.info(f"✅ Migración completada: {rows_inserted} perfiles de memoria creados")

            # Mostrar estadísticas
            stats_query = text("""
                SELECT
                    COUNT(*) as total_usuarios,
                    COUNT(m.idMemoryProfile) as con_perfil,
                    COUNT(*) - COUNT(m.idMemoryProfile) as sin_perfil
                FROM [dbo].[Usuarios] u
                LEFT JOIN [dbo].[UserMemoryProfiles] m ON u.idUsuario = m.idUsuario
                WHERE u.activo = 1
            """)

            stats = session.execute(stats_query).fetchone()
            logger.info(f"📊 Estadísticas:")
            logger.info(f"   - Total usuarios activos: {stats.total_usuarios}")
            logger.info(f"   - Con perfil de memoria: {stats.con_perfil}")
            logger.info(f"   - Sin perfil de memoria: {stats.sin_perfil}")

            return rows_inserted

    except Exception as e:
        logger.error(f"❌ Error durante migración: {e}", exc_info=True)
        raise
    finally:
        db_manager.close()


if __name__ == "__main__":
    logger.info("🚀 Iniciando migración de usuarios a memoria persistente...")

    try:
        migrate_existing_users()
        logger.info("✅ Migración completada exitosamente")
        sys.exit(0)
    except Exception as e:
        logger.error("❌ Migración falló")
        sys.exit(1)
