"""
Test de conexión a SQL Server - localhost\sqlexpress
Valida diferentes métodos de conexión y configuraciones.
"""

import sys
import time
import pyodbc
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError, SQLAlchemyError
from dotenv import load_dotenv
import os

# Cargar variables de entorno
load_dotenv()

# Configuración desde .env
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "1433")
DB_NAME = os.getenv("DB_NAME", "Pruebas")
DB_USER = os.getenv("DB_USER", "usrmon")
DB_PASSWORD = os.getenv("DB_PASSWORD", "MonAplic01@")

print("="*80)
print("TEST DE CONEXIÓN A SQL SERVER - localhost\\sqlexpress")
print("="*80)
print(f"\nConfiguración:")
print(f"  Host: {DB_HOST}")
print(f"  Puerto: {DB_PORT}")
print(f"  Base de datos: {DB_NAME}")
print(f"  Usuario: {DB_USER}")
print(f"  Password: {'*' * len(DB_PASSWORD)}")
print("="*80 + "\n")


def test_1_pyodbc_directo():
    """Test 1: Conexión directa con pyodbc (sin SQLAlchemy)"""
    print("\n[TEST 1] Conexión directa con pyodbc")
    print("-" * 80)

    # Intentar con diferentes drivers disponibles
    drivers = [
        "ODBC Driver 17 for SQL Server",
        "ODBC Driver 18 for SQL Server",
        "SQL Server Native Client 11.0",
        "SQL Server"
    ]

    for driver in drivers:
        try:
            print(f"\nIntentando con driver: {driver}")
            connection_string = (
                f"DRIVER={{{driver}}};"
                f"SERVER={DB_HOST}\\SQLEXPRESS;"
                f"DATABASE={DB_NAME};"
                f"UID={DB_USER};"
                f"PWD={DB_PASSWORD};"
                f"Connection Timeout=10;"
            )

            start_time = time.time()
            conn = pyodbc.connect(connection_string)
            elapsed = time.time() - start_time

            cursor = conn.cursor()
            cursor.execute("SELECT @@VERSION")
            version = cursor.fetchone()[0]

            print(f"  ✓ ÉXITO - Conectado en {elapsed:.2f}s")
            print(f"  Versión SQL Server: {version[:80]}...")

            cursor.close()
            conn.close()
            return True

        except pyodbc.Error as e:
            print(f"  ✗ ERROR con {driver}: {str(e)[:100]}")

    return False


def test_2_pyodbc_por_puerto():
    """Test 2: Conexión por puerto TCP/IP en lugar de instancia nombrada"""
    print("\n\n[TEST 2] Conexión por puerto TCP/IP (localhost:1433)")
    print("-" * 80)

    drivers_to_try = [
        "ODBC Driver 17 for SQL Server",
        "ODBC Driver 18 for SQL Server"
    ]

    for driver in drivers_to_try:
        try:
            print(f"\nIntentando con driver: {driver}")
            connection_string = (
                f"DRIVER={{{driver}}};"
                f"SERVER={DB_HOST},{DB_PORT};"
                f"DATABASE={DB_NAME};"
                f"UID={DB_USER};"
                f"PWD={DB_PASSWORD};"
                f"Connection Timeout=10;"
                f"TrustServerCertificate=yes;"  # Para ODBC 18
            )

            start_time = time.time()
            conn = pyodbc.connect(connection_string)
            elapsed = time.time() - start_time

            cursor = conn.cursor()
            cursor.execute("SELECT DB_NAME() as CurrentDB, @@SERVERNAME as ServerName")
            result = cursor.fetchone()

            print(f"  ✓ ÉXITO - Conectado en {elapsed:.2f}s")
            print(f"  Base de datos actual: {result[0]}")
            print(f"  Servidor: {result[1]}")

            cursor.close()
            conn.close()
            return True

        except pyodbc.Error as e:
            print(f"  ✗ ERROR con {driver}: {str(e)[:150]}")

    return False


def test_3_sqlalchemy_basico():
    """Test 3: SQLAlchemy con configuración básica (actual del proyecto)"""
    print("\n\n[TEST 3] SQLAlchemy - Configuración actual del proyecto")
    print("-" * 80)

    try:
        # Forma actual del proyecto
        database_url = f"mssql+pyodbc://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?driver=ODBC+Driver+17+for+SQL+Server"
        print(f"\nConnection String: {database_url.replace(DB_PASSWORD, '***')}")

        start_time = time.time()
        engine = create_engine(database_url, echo=False)

        with engine.connect() as connection:
            elapsed = time.time() - start_time
            result = connection.execute(text("SELECT DB_NAME() as CurrentDB"))
            db_name = result.fetchone()[0]

            print(f"  ✓ ÉXITO - Conectado en {elapsed:.2f}s")
            print(f"  Base de datos: {db_name}")

        engine.dispose()
        return True

    except SQLAlchemyError as e:
        print(f"  ✗ ERROR: {str(e)[:200]}")
        return False


def test_4_sqlalchemy_optimizado():
    """Test 4: SQLAlchemy con configuración optimizada (recomendada)"""
    print("\n\n[TEST 4] SQLAlchemy - Configuración optimizada con timeouts y pool")
    print("-" * 80)

    try:
        # Probar con ODBC 17
        database_url = f"mssql+pyodbc://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?driver=ODBC+Driver+17+for+SQL+Server"
        print(f"\nConnection String: {database_url.replace(DB_PASSWORD, '***')}")

        start_time = time.time()
        engine = create_engine(
            database_url,
            echo=False,
            pool_size=5,              # Número de conexiones en el pool
            max_overflow=10,          # Conexiones adicionales permitidas
            pool_timeout=20,          # Timeout esperando conexión del pool
            pool_recycle=3600,        # Reciclar conexiones cada hora
            pool_pre_ping=True,       # Verificar conexión antes de usar
            connect_args={
                "timeout": 15,        # Timeout de conexión (segundos)
            }
        )

        with engine.connect() as connection:
            elapsed = time.time() - start_time
            result = connection.execute(text("SELECT DB_NAME() as CurrentDB, @@VERSION as Version"))
            row = result.fetchone()

            print(f"  ✓ ÉXITO - Conectado en {elapsed:.2f}s")
            print(f"  Base de datos: {row[0]}")
            print(f"  SQL Server: {row[1][:100]}...")

        engine.dispose()
        return True

    except SQLAlchemyError as e:
        print(f"  ✗ ERROR: {str(e)[:200]}")

        # Intentar con ODBC 18 y TrustServerCertificate
        print(f"\n  Reintentando con ODBC Driver 18...")
        try:
            database_url = f"mssql+pyodbc://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?driver=ODBC+Driver+18+for+SQL+Server&TrustServerCertificate=yes"

            engine = create_engine(
                database_url,
                echo=False,
                pool_size=5,
                max_overflow=10,
                pool_timeout=20,
                pool_recycle=3600,
                pool_pre_ping=True,
                connect_args={"timeout": 15}
            )

            with engine.connect() as connection:
                elapsed = time.time() - start_time
                result = connection.execute(text("SELECT DB_NAME()"))
                db_name = result.fetchone()[0]

                print(f"  ✓ ÉXITO con ODBC 18 - Conectado en {elapsed:.2f}s")
                print(f"  Base de datos: {db_name}")

            engine.dispose()
            return True

        except SQLAlchemyError as e2:
            print(f"  ✗ ERROR con ODBC 18: {str(e2)[:200]}")
            return False


def test_5_verificar_sql_server():
    """Test 5: Verificaciones del servidor SQL Server"""
    print("\n\n[TEST 5] Verificaciones del servidor SQL Server")
    print("-" * 80)

    # Listar drivers ODBC disponibles
    print("\nDrivers ODBC instalados:")
    drivers = pyodbc.drivers()
    for driver in drivers:
        print(f"  - {driver}")

    if not drivers:
        print("  ✗ No hay drivers ODBC instalados")
        return False

    # Verificar si hay algún driver de SQL Server
    sql_drivers = [d for d in drivers if "SQL Server" in d]
    if sql_drivers:
        print(f"\n  ✓ Drivers de SQL Server encontrados: {len(sql_drivers)}")
        return True
    else:
        print("\n  ✗ No se encontraron drivers de SQL Server")
        return False


def main():
    """Ejecutar todos los tests"""
    tests = [
        test_5_verificar_sql_server,  # Primero verificar drivers
        test_1_pyodbc_directo,
        test_2_pyodbc_por_puerto,
        test_3_sqlalchemy_basico,
        test_4_sqlalchemy_optimizado,
    ]

    results = {}

    for test_func in tests:
        try:
            result = test_func()
            results[test_func.__name__] = result
        except Exception as e:
            print(f"\n  ✗ EXCEPCIÓN NO CONTROLADA: {e}")
            results[test_func.__name__] = False

    # Resumen
    print("\n\n" + "="*80)
    print("RESUMEN DE TESTS")
    print("="*80)

    for test_name, result in results.items():
        status = "✓ ÉXITO" if result else "✗ FALLO"
        print(f"{status} - {test_name}")

    successful_tests = sum(1 for r in results.values() if r)
    total_tests = len(results)

    print(f"\nTests exitosos: {successful_tests}/{total_tests}")

    if successful_tests > 0:
        print("\n" + "="*80)
        print("RECOMENDACIONES")
        print("="*80)
        print("\nSi algún test fue exitoso, usa esa configuración en tu código.")
        print("\nPasos siguientes:")
        print("1. Verifica que SQL Server esté ejecutándose (services.msc)")
        print("2. Verifica que TCP/IP esté habilitado en SQL Server Configuration Manager")
        print("3. Verifica el puerto 1433 esté abierto en el firewall")
        print("4. Si usas instancia nombrada (SQLEXPRESS), verifica SQL Server Browser")
        print("5. Actualiza /src/database/connection.py con la configuración que funcionó")
    else:
        print("\n" + "="*80)
        print("PROBLEMAS DETECTADOS")
        print("="*80)
        print("\nNingún test fue exitoso. Posibles causas:")
        print("  1. SQL Server no está ejecutándose")
        print("  2. TCP/IP no está habilitado en la configuración de SQL Server")
        print("  3. Firewall bloqueando puerto 1433")
        print("  4. Credenciales incorrectas")
        print("  5. Base de datos 'Pruebas' no existe")
        print("\nVerifica estos puntos y vuelve a ejecutar el test.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nTest interrumpido por el usuario.")
        sys.exit(0)
