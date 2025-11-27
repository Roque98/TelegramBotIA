"""
Test final de validación de conexión a SQL Server.
Verifica que la configuración corregida funcione correctamente.
"""

import sys
import time
from src.config.settings import settings
from src.database.connection import DatabaseManager

print("="*80)
print("TEST FINAL DE VALIDACIÓN - SQL SERVER")
print("="*80)
print(f"\nConfiguración cargada desde .env:")
print(f"  DB_TYPE: {settings.db_type}")
print(f"  DB_HOST: {settings.db_host}")
if settings.db_instance:
    print(f"  DB_INSTANCE: {settings.db_instance}")
    print(f"  Servidor: {settings.db_host}\\{settings.db_instance}")
else:
    print(f"  DB_PORT: {settings.db_port}")
    print(f"  Servidor: {settings.db_host}:{settings.db_port}")
print(f"  DB_NAME: {settings.db_name}")
print(f"  DB_USER: {settings.db_user}")
print(f"\nConnection String generado:")
print(f"  {settings.database_url.replace(settings.db_password, '***')}")
print("="*80)


def test_connection():
    """Test 1: Verificar que se puede crear una instancia de DatabaseManager"""
    print("\n[TEST 1] Creando DatabaseManager...")
    print("-" * 80)

    try:
        start_time = time.time()
        db_manager = DatabaseManager()
        elapsed = time.time() - start_time

        print(f"  ✓ DatabaseManager creado exitosamente en {elapsed:.2f}s")
        return db_manager

    except Exception as e:
        print(f"  ✗ ERROR creando DatabaseManager: {e}")
        return None


def test_simple_query(db_manager):
    """Test 2: Ejecutar una consulta simple"""
    print("\n[TEST 2] Ejecutando consulta simple (SELECT DB_NAME())")
    print("-" * 80)

    try:
        start_time = time.time()
        result = db_manager.execute_query("SELECT DB_NAME() as DatabaseName")
        elapsed = time.time() - start_time

        if result:
            db_name = result[0]['DatabaseName']
            print(f"  ✓ Consulta ejecutada exitosamente en {elapsed:.2f}s")
            print(f"  Base de datos conectada: {db_name}")
            return True
        else:
            print(f"  ✗ La consulta no devolvió resultados")
            return False

    except Exception as e:
        print(f"  ✗ ERROR ejecutando consulta: {e}")
        return False


def test_schema(db_manager):
    """Test 3: Obtener el esquema de la base de datos"""
    print("\n[TEST 3] Obteniendo esquema de la base de datos")
    print("-" * 80)

    try:
        start_time = time.time()
        schema = db_manager.get_schema()
        elapsed = time.time() - start_time

        if schema:
            lines = schema.split('\n')
            table_count = len([l for l in lines if l.startswith('Tabla:')])

            print(f"  ✓ Esquema obtenido exitosamente en {elapsed:.2f}s")
            print(f"  Tablas encontradas: {table_count}")

            # Mostrar primeras 10 líneas
            print(f"\n  Primeras líneas del esquema:")
            for line in lines[:10]:
                print(f"    {line}")

            if len(lines) > 10:
                print(f"    ... y {len(lines) - 10} líneas más")

            return True
        else:
            print(f"  ⚠ No se encontraron tablas en la base de datos")
            return True  # No es un error, la BD puede estar vacía

    except Exception as e:
        print(f"  ✗ ERROR obteniendo esquema: {e}")
        return False


def test_connection_pool(db_manager):
    """Test 4: Verificar el pool de conexiones"""
    print("\n[TEST 4] Verificando pool de conexiones")
    print("-" * 80)

    try:
        # Crear múltiples sesiones
        sessions = []
        for i in range(3):
            session = db_manager.get_session()
            sessions.append(session)
            print(f"  ✓ Sesión {i+1} creada")

        # Cerrar todas las sesiones
        for i, session in enumerate(sessions):
            session.close()
            print(f"  ✓ Sesión {i+1} cerrada")

        print(f"  ✓ Pool de conexiones funcionando correctamente")
        return True

    except Exception as e:
        print(f"  ✗ ERROR con pool de conexiones: {e}")
        return False


def main():
    """Ejecutar todos los tests"""
    print("\nIniciando tests...\n")

    results = {}

    # Test 1: Crear DatabaseManager
    db_manager = test_connection()
    results['connection'] = db_manager is not None

    if not db_manager:
        print("\n" + "="*80)
        print("❌ NO SE PUDO CONECTAR A LA BASE DE DATOS")
        print("="*80)
        print("\nVerifica:")
        print("  1. SQL Server está ejecutándose")
        print("  2. La instancia SQLEXPRESS está activa")
        print("  3. Las credenciales en .env son correctas")
        print("  4. La base de datos 'Pruebas' existe")
        return False

    # Test 2: Consulta simple
    results['simple_query'] = test_simple_query(db_manager)

    # Test 3: Esquema
    results['schema'] = test_schema(db_manager)

    # Test 4: Pool de conexiones
    results['pool'] = test_connection_pool(db_manager)

    # Cerrar conexiones
    db_manager.close()
    print("\n[LIMPIEZA] Conexiones cerradas")

    # Resumen
    print("\n" + "="*80)
    print("RESUMEN DE TESTS")
    print("="*80)

    for test_name, result in results.items():
        status = "✓ ÉXITO" if result else "✗ FALLO"
        print(f"  {status} - {test_name}")

    successful_tests = sum(1 for r in results.values() if r)
    total_tests = len(results)

    print(f"\n  Tests exitosos: {successful_tests}/{total_tests}")

    if successful_tests == total_tests:
        print("\n" + "="*80)
        print("🎉 TODOS LOS TESTS PASARON")
        print("="*80)
        print("\n✓ La conexión a SQL Server está funcionando correctamente")
        print("✓ La configuración es correcta")
        print("✓ El pool de conexiones está operativo")
        print("\nAhora puedes ejecutar el bot con confianza:")
        print("  python main.py")
        return True
    else:
        print("\n" + "="*80)
        print("⚠ ALGUNOS TESTS FALLARON")
        print("="*80)
        print("\nRevisa los errores arriba para más detalles")
        return False


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTest interrumpido por el usuario.")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ ERROR INESPERADO: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
