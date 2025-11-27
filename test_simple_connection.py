"""
Test simple de conexion - sin caracteres especiales Unicode
"""
import sys
from src.config.settings import settings
from src.database.connection import DatabaseManager

print("="*80)
print("TEST SIMPLE DE CONEXION")
print("="*80)

try:
    # Test 1: Crear DatabaseManager
    print("\n[1] Creando DatabaseManager...")
    db = DatabaseManager()
    print("[OK] DatabaseManager creado")

    # Test 2: Consulta simple
    print("\n[2] Ejecutando SELECT DB_NAME()...")
    result = db.execute_query("SELECT DB_NAME() as DatabaseName")
    print(f"[OK] Resultado: {result}")

    # Test 3: Obtener esquema
    print("\n[3] Obteniendo esquema...")
    schema = db.get_schema()
    lines = schema.split('\n')
    table_count = len([l for l in lines if l.startswith('Tabla:')])
    print(f"[OK] Tablas encontradas: {table_count}")
    print(f"[OK] Primeras 5 lineas:\n{chr(10).join(lines[:5])}")

    # Test 4: Pool de conexiones
    print("\n[4] Verificando pool...")
    session1 = db.get_session()
    session2 = db.get_session()
    session1.close()
    session2.close()
    print("[OK] Pool funciona correctamente")

    # Cerrar
    db.close()

    print("\n" + "="*80)
    print("TODOS LOS TESTS PASARON!")
    print("="*80)
    sys.exit(0)

except Exception as e:
    print(f"\n[ERROR] {type(e).__name__}: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
