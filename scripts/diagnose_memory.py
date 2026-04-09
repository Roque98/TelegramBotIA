"""
Script de diagnóstico simple para verificar por qué UserMemoryProfiles está vacío.
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.infra.database.connection import DatabaseManager
from src.agent.memory import MemoryRepository
from sqlalchemy import text


async def diagnose():
    """Diagnosticar el problema de memoria."""
    print("=" * 80)
    print("DIAGNOSTICO DE MEMORIA PERSISTENTE")
    print("=" * 80)

    db_manager = DatabaseManager()

    # 1. Verificar conexión
    print("\n1. Verificando conexión a BD...")
    try:
        with db_manager.get_session() as session:
            result = session.execute(text("SELECT 1 as test")).fetchone()
            print(f"   OK - Conexion exitosa")
    except Exception as e:
        print(f"   ERROR - {e}")
        return

    # 2. Verificar tabla existe
    print("\n2. Verificando tabla UserMemoryProfiles...")
    try:
        with db_manager.get_session() as session:
            # Verificar directamente con SELECT COUNT
            query = text("""
                SELECT COUNT(*) as count
                FROM [abcmasplus].[dbo].[UserMemoryProfiles]
            """)
            result = session.execute(query).fetchone()
            print(f"   OK - Tabla existe con {result.count} registros")
    except Exception as e:
        print(f"   ERROR - {e}")
        return

    # 3. Contar perfiles
    print("\n3. Contando perfiles existentes...")
    try:
        with db_manager.get_session() as session:
            query = text("SELECT COUNT(*) as count FROM [abcmasplus].[dbo].[UserMemoryProfiles]")
            result = session.execute(query).fetchone()
            print(f"   Total de perfiles: {result.count}")

            if result.count > 0:
                sample = session.execute(text("""
                    SELECT TOP 3 idUsuario, numInteracciones, ultimaActualizacion
                    FROM [abcmasplus].[dbo].[UserMemoryProfiles]
                """)).fetchall()
                print(f"   Muestra:")
                for p in sample:
                    print(f"      Usuario {p.idUsuario}: {p.numInteracciones} interacciones")
    except Exception as e:
        print(f"   ERROR - {e}")

    # 4. Verificar LogOperaciones
    print("\n4. Verificando LogOperaciones con comando '/ia'...")
    try:
        with db_manager.get_session() as session:
            query = text("""
                SELECT COUNT(*) as count
                FROM [abcmasplus].[dbo].[LogOperaciones] l
                INNER JOIN [abcmasplus].[dbo].[Operaciones] o ON l.idOperacion = o.idOperacion
                WHERE o.comando = '/ia' AND l.resultado = 'EXITOSO'
            """)
            result = session.execute(query).fetchone()
            print(f"   Total operaciones /ia exitosas: {result.count}")

            if result.count > 0:
                # Mostrar usuarios con operaciones
                query2 = text("""
                    SELECT TOP 5 l.idUsuario, COUNT(*) as total
                    FROM [abcmasplus].[dbo].[LogOperaciones] l
                    INNER JOIN [abcmasplus].[dbo].[Operaciones] o ON l.idOperacion = o.idOperacion
                    WHERE o.comando = '/ia' AND l.resultado = 'EXITOSO'
                    GROUP BY l.idUsuario
                    ORDER BY total DESC
                """)
                users = session.execute(query2).fetchall()
                print(f"   Usuarios con mas operaciones:")
                for u in users:
                    print(f"      Usuario {u.idUsuario}: {u.total} operaciones")
    except Exception as e:
        print(f"   ERROR - {e}")

    # 5. Probar increment_interaction_count manualmente
    print("\n5. Probando increment_interaction_count()...")
    repository = MemoryRepository(db_manager)

    # Obtener un usuario que tenga operaciones
    with db_manager.get_session() as session:
        query = text("""
            SELECT TOP 1 l.idUsuario
            FROM [abcmasplus].[dbo].[LogOperaciones] l
            INNER JOIN [abcmasplus].[dbo].[Operaciones] o ON l.idOperacion = o.idOperacion
            WHERE o.comando = '/ia' AND l.resultado = 'EXITOSO'
        """)
        user_row = session.execute(query).fetchone()

        if not user_row:
            print("   ERROR - No hay usuarios con operaciones /ia")
            return

        test_user_id = user_row.idUsuario
        print(f"   Usando usuario de prueba: {test_user_id}")

    try:
        # Intentar incrementar
        print(f"   Intentando incrementar contador...")
        new_count = repository.increment_interaction_count(test_user_id)
        print(f"   OK - Contador incrementado a: {new_count}")

        # Verificar en BD
        with db_manager.get_session() as session:
            query = text("""
                SELECT numInteracciones
                FROM [abcmasplus].[dbo].[UserMemoryProfiles]
                WHERE idUsuario = :user_id
            """)
            result = session.execute(query, {"user_id": test_user_id}).fetchone()

            if result:
                print(f"   OK - Verificado en BD: {result.numInteracciones}")
            else:
                print(f"   ERROR - No se encontro perfil despues de incrementar")

    except Exception as e:
        print(f"   ERROR - {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "=" * 80)
    print("DIAGNOSTICO COMPLETADO")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(diagnose())
