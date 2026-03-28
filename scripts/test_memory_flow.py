"""
Script de prueba para verificar el flujo de memoria persistente.

Este script:
1. Verifica que la tabla UserMemoryProfiles existe
2. Prueba el incremento de contador
3. Simula el flujo completo de memoria

Uso:
    python scripts/test_memory_flow.py
"""
import asyncio
import sys
import os

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.infra.database.connection import DatabaseManager
from src.agent.memory import MemoryRepository, MemoryManager
from src.agent.providers.openai_provider import OpenAIProvider
from src.config.settings import settings
from sqlalchemy import text


async def test_memory_flow():
    """Probar el flujo completo de memoria."""
    print("=" * 80)
    print("TEST DE FLUJO DE MEMORIA PERSISTENTE")
    print("=" * 80)

    # 1. Verificar conexión a BD
    print("\n1. Verificando conexión a base de datos...")
    db_manager = DatabaseManager()

    try:
        with db_manager.get_session() as session:
            result = session.execute(text("SELECT 1 as test")).fetchone()
            print(f"   ✅ Conexión exitosa: {result.test}")
    except Exception as e:
        print(f"   ❌ Error de conexión: {e}")
        return

    # 2. Verificar que tabla UserMemoryProfiles existe
    print("\n2. Verificando tabla UserMemoryProfiles...")
    try:
        with db_manager.get_session() as session:
            query = text("""
                SELECT COUNT(*) as count
                FROM INFORMATION_SCHEMA.TABLES
                WHERE TABLE_SCHEMA = 'dbo'
                  AND TABLE_NAME = 'UserMemoryProfiles'
            """)
            result = session.execute(query).fetchone()

            if result.count == 1:
                print(f"   ✅ Tabla UserMemoryProfiles existe")

                # Obtener estructura de la tabla
                structure_query = text("""
                    SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE
                    FROM INFORMATION_SCHEMA.COLUMNS
                    WHERE TABLE_NAME = 'UserMemoryProfiles'
                    ORDER BY ORDINAL_POSITION
                """)
                columns = session.execute(structure_query).fetchall()
                print(f"   📋 Columnas ({len(columns)}):")
                for col in columns:
                    print(f"      - {col.COLUMN_NAME}: {col.DATA_TYPE} (NULL: {col.IS_NULLABLE})")
            else:
                print(f"   ❌ Tabla UserMemoryProfiles NO existe")
                print(f"   💡 Ejecuta: python scripts/migrate_users_to_memory.py")
                return
    except Exception as e:
        print(f"   ❌ Error verificando tabla: {e}")
        return

    # 3. Verificar perfiles existentes
    print("\n3. Verificando perfiles existentes...")
    try:
        with db_manager.get_session() as session:
            query = text("""
                SELECT COUNT(*) as count
                FROM [dbo].[UserMemoryProfiles]
            """)
            result = session.execute(query).fetchone()
            print(f"   📊 Perfiles existentes: {result.count}")

            if result.count > 0:
                # Mostrar algunos perfiles
                sample_query = text("""
                    SELECT TOP 5
                        idUsuario,
                        numInteracciones,
                        ultimaActualizacion,
                        CASE
                            WHEN resumenContextoLaboral IS NOT NULL THEN 'SI'
                            ELSE 'NO'
                        END as tieneContexto
                    FROM [dbo].[UserMemoryProfiles]
                    ORDER BY numInteracciones DESC
                """)
                profiles = session.execute(sample_query).fetchall()
                print(f"   📋 Muestra de perfiles:")
                for p in profiles:
                    print(f"      - Usuario {p.idUsuario}: {p.numInteracciones} interacciones, contexto: {p.tieneContexto}")
    except Exception as e:
        print(f"   ❌ Error consultando perfiles: {e}")

    # 4. Probar MemoryRepository
    print("\n4. Probando MemoryRepository...")
    repository = MemoryRepository(db_manager)

    # Usar un ID de usuario de prueba (ajusta según tu BD)
    test_user_id = 1  # Cambia esto si necesitas otro ID

    print(f"   🧪 Usuario de prueba: {test_user_id}")

    try:
        # Obtener perfil actual
        profile = repository.get_user_profile(test_user_id)
        if profile:
            print(f"   ✅ Perfil encontrado: {profile.num_interacciones} interacciones")
        else:
            print(f"   ℹ️  Perfil no existe aún (se creará al incrementar)")

        # Probar incremento
        print(f"\n   🔢 Probando increment_interaction_count()...")
        new_count = repository.increment_interaction_count(test_user_id)
        print(f"   ✅ Contador incrementado: {new_count}")

        # Verificar en BD
        with db_manager.get_session() as session:
            verify_query = text("""
                SELECT numInteracciones
                FROM [dbo].[UserMemoryProfiles]
                WHERE idUsuario = :user_id
            """)
            result = session.execute(verify_query, {"user_id": test_user_id}).fetchone()

            if result:
                print(f"   ✅ Verificación en BD: contador = {result.numInteracciones}")
            else:
                print(f"   ❌ No se encontró perfil en BD después de incrementar")

    except Exception as e:
        print(f"   ❌ Error probando repository: {e}")
        import traceback
        traceback.print_exc()

    # 5. Probar MemoryManager (con LLM real)
    print("\n5. Probando MemoryManager...")

    if not settings.openai_api_key:
        print(f"   ⚠️  No hay API key de OpenAI configurada, saltando test de LLM")
    else:
        try:
            llm_provider = OpenAIProvider(
                api_key=settings.openai_api_key,
                model=settings.openai_model
            )

            memory_manager = MemoryManager(db_manager, llm_provider)

            print(f"   ✅ MemoryManager inicializado")
            print(f"   📊 Stats: {memory_manager.get_stats()}")

            # Simular llamadas a record_interaction
            print(f"\n   🔄 Simulando 3 interacciones...")
            for i in range(3):
                await memory_manager.record_interaction(test_user_id)
                print(f"      - Interacción {i+1} registrada")

            print(f"   ✅ Interacciones simuladas completadas")

            # Verificar contador final
            profile = repository.get_user_profile(test_user_id)
            if profile:
                print(f"   📊 Contador final: {profile.num_interacciones}")

        except Exception as e:
            print(f"   ❌ Error probando MemoryManager: {e}")
            import traceback
            traceback.print_exc()

    # 6. Probar obtención de contexto
    print("\n6. Probando get_memory_context()...")
    try:
        if 'memory_manager' in locals():
            context = memory_manager.get_memory_context(test_user_id)

            if context:
                print(f"   ✅ Contexto obtenido ({len(context)} chars):")
                print(f"   {'-' * 60}")
                print(f"   {context[:200]}...")
                print(f"   {'-' * 60}")
            else:
                print(f"   ℹ️  Contexto vacío (normal si no hay resúmenes generados aún)")
    except Exception as e:
        print(f"   ❌ Error obteniendo contexto: {e}")

    print("\n" + "=" * 80)
    print("TEST COMPLETADO")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(test_memory_flow())
