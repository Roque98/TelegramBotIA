"""Probar directamente el incremento de contador."""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy import text
from src.database.connection import DatabaseManager
from src.agent.memory import MemoryRepository

db_manager = DatabaseManager()

print("=" * 80)
print("PRUEBA DE INCREMENTO DE CONTADOR")
print("=" * 80)

# 1. Verificar tabla existe con SELECT directo
print("\n1. Verificando tabla con SELECT directo...")
try:
    with db_manager.get_session() as session:
        result = session.execute(text("""
            SELECT COUNT(*) as count
            FROM [abcmasplus].[dbo].[UserMemoryProfiles]
        """)).fetchone()
        print(f"   OK - Tabla existe, {result.count} registros")
except Exception as e:
    print(f"   ERROR - {e}")
    db_manager.close()
    sys.exit(1)

# 2. Obtener un usuario de LogOperaciones
print("\n2. Obteniendo usuario de prueba de LogOperaciones...")
try:
    with db_manager.get_session() as session:
        result = session.execute(text("""
            SELECT TOP 1 l.idUsuario
            FROM [abcmasplus].[dbo].[LogOperaciones] l
            INNER JOIN [abcmasplus].[dbo].[Operaciones] o ON l.idOperacion = o.idOperacion
            WHERE o.comando = '/ia' AND l.resultado = 'EXITOSO'
            ORDER BY l.fechaEjecucion DESC
        """)).fetchone()

        if result:
            test_user_id = result.idUsuario
            print(f"   Usuario: {test_user_id}")
        else:
            print("   No hay operaciones /ia, usando usuario 1")
            test_user_id = 1
except Exception as e:
    print(f"   ERROR - {e}")
    test_user_id = 1

# 3. Probar increment_interaction_count
print(f"\n3. Probando increment_interaction_count({test_user_id})...")
repository = MemoryRepository(db_manager)

try:
    print("   Antes del incremento:")
    with db_manager.get_session() as session:
        before = session.execute(text("""
            SELECT numInteracciones
            FROM [abcmasplus].[dbo].[UserMemoryProfiles]
            WHERE idUsuario = :uid
        """), {"uid": test_user_id}).fetchone()

        if before:
            print(f"      Contador actual: {before.numInteracciones}")
        else:
            print(f"      Perfil no existe aun")

    print(f"   Llamando a increment_interaction_count...")
    new_count = repository.increment_interaction_count(test_user_id)
    print(f"   Retorno: {new_count}")

    print("   Despues del incremento:")
    with db_manager.get_session() as session:
        after = session.execute(text("""
            SELECT numInteracciones, fechaCreacion, ultimaActualizacion
            FROM [abcmasplus].[dbo].[UserMemoryProfiles]
            WHERE idUsuario = :uid
        """), {"uid": test_user_id}).fetchone()

        if after:
            print(f"      Contador: {after.numInteracciones}")
            print(f"      Creado: {after.fechaCreacion}")
            print(f"      Actualizado: {after.ultimaActualizacion}")
        else:
            print(f"      ERROR - Perfil NO encontrado despues de incrementar")

    print("   OK - Incremento funciono correctamente")

except Exception as e:
    print(f"   ERROR - {e}")
    import traceback
    traceback.print_exc()

# 4. Verificar total de registros
print("\n4. Verificando total de registros...")
try:
    with db_manager.get_session() as session:
        result = session.execute(text("""
            SELECT COUNT(*) as count
            FROM [abcmasplus].[dbo].[UserMemoryProfiles]
        """)).fetchone()
        print(f"   Total registros: {result.count}")

        if result.count > 0:
            top5 = session.execute(text("""
                SELECT TOP 5 idUsuario, numInteracciones, fechaCreacion
                FROM [abcmasplus].[dbo].[UserMemoryProfiles]
                ORDER BY fechaCreacion DESC
            """)).fetchall()
            print(f"   Ultimos 5 perfiles:")
            for row in top5:
                print(f"      Usuario {row.idUsuario}: {row.numInteracciones} interacciones (creado: {row.fechaCreacion})")
except Exception as e:
    print(f"   ERROR - {e}")

db_manager.close()
print("\n" + "=" * 80)
print("FIN DE PRUEBA")
print("=" * 80)
