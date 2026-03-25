"""
Script de prueba manual para el sistema de Tools.

Este script permite probar el sistema de Tools sin necesidad de
conectarse a Telegram, útil para desarrollo y debugging.

Uso:
    python test_tools_manual.py
"""
import asyncio
import logging
from src.config.settings import settings
from src.database.connection import DatabaseManager
from src.agent.llm_agent import LLMAgent
from src.tools import (
    initialize_builtin_tools,
    get_registry,
    get_tool_summary,
    ToolOrchestrator,
    ExecutionContextBuilder
)

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_tool_initialization():
    """Test 1: Verificar inicialización de tools."""
    print("\n" + "="*60)
    print("TEST 1: Inicialización de Tools")
    print("="*60)

    # Inicializar tools
    initialize_builtin_tools()

    # Obtener resumen
    summary = get_tool_summary()

    print(f"\n✅ Tools registrados: {summary['total_tools']}")
    print(f"✅ Comandos disponibles: {', '.join(summary['commands'])}")

    print("\nDetalles de tools:")
    for tool_info in summary['tools']:
        print(f"\n  📦 {tool_info['name']} (v{tool_info['version']})")
        print(f"     Descripción: {tool_info['description']}")
        print(f"     Comandos: {', '.join(tool_info['commands'])}")
        print(f"     Categoría: {tool_info['category']}")
        print(f"     Requiere auth: {tool_info['requires_auth']}")

    return summary['total_tools'] > 0


async def test_query_tool_direct():
    """Test 2: Probar QueryTool directamente."""
    print("\n" + "="*60)
    print("TEST 2: QueryTool - Ejecución Directa")
    print("="*60)

    try:
        # Inicializar componentes
        db_manager = DatabaseManager()
        llm_agent = LLMAgent(db_manager=db_manager)

        # Obtener QueryTool del registry
        registry = get_registry()
        query_tool = registry.get_tool_by_name("query")

        if not query_tool:
            print("❌ QueryTool no encontrado en el registry")
            return False

        # Crear contexto de ejecución
        context = (
            ExecutionContextBuilder()
            .with_llm_agent(llm_agent)
            .with_db_manager(db_manager)
            .build()
        )

        # Ejecutar query de prueba
        test_query = "¿Cuántos usuarios hay registrados en el sistema?"
        print(f"\n🔍 Ejecutando query: {test_query}")

        result = await query_tool.execute(
            user_id=999,  # Usuario de prueba
            params={"query": test_query},
            context=context
        )

        # Mostrar resultado
        if result.success:
            print(f"\n✅ Query ejecutada exitosamente")
            print(f"⏱️  Tiempo de ejecución: {result.execution_time_ms:.2f}ms")
            print(f"\n📊 Respuesta:")
            print("-" * 60)
            print(result.data)
            print("-" * 60)
            return True
        else:
            print(f"\n❌ Error en query: {result.error}")
            print(f"   Mensaje usuario: {result.user_friendly_error}")
            return False

    except Exception as e:
        print(f"\n❌ Excepción durante test: {e}")
        logger.error("Error en test_query_tool_direct", exc_info=True)
        return False


async def test_orchestrator_flow():
    """Test 3: Probar flujo completo con ToolOrchestrator."""
    print("\n" + "="*60)
    print("TEST 3: ToolOrchestrator - Flujo Completo")
    print("="*60)

    try:
        # Inicializar componentes
        db_manager = DatabaseManager()
        llm_agent = LLMAgent(db_manager=db_manager)

        # Crear orquestador
        registry = get_registry()
        orchestrator = ToolOrchestrator(registry)

        # Crear contexto
        context = (
            ExecutionContextBuilder()
            .with_llm_agent(llm_agent)
            .with_db_manager(db_manager)
            .build()
        )

        # Ejecutar varias queries de prueba
        test_queries = [
            "¿Cuántos usuarios hay?",
            "¿Qué tablas tiene la base de datos?",
            "Dame un resumen del sistema"
        ]

        success_count = 0
        for i, query in enumerate(test_queries, 1):
            print(f"\n📝 Query {i}/{len(test_queries)}: {query}")

            result = await orchestrator.execute_command(
                user_id=999,
                command="/ia",
                params={"query": query},
                context=context
            )

            if result.success:
                print(f"   ✅ Exitosa ({result.execution_time_ms:.2f}ms)")
                success_count += 1
            else:
                print(f"   ❌ Fallida: {result.error}")

        # Mostrar estadísticas del orquestador
        print("\n📊 Estadísticas del Orquestador:")
        stats = orchestrator.get_stats()
        print(f"   Total ejecuciones: {stats['total_executions']}")
        print(f"   Total errores: {stats['total_errors']}")
        print(f"   Tasa de éxito: {stats['success_rate']:.1f}%")

        return success_count == len(test_queries)

    except Exception as e:
        print(f"\n❌ Excepción durante test: {e}")
        logger.error("Error en test_orchestrator_flow", exc_info=True)
        return False


async def test_parameter_validation():
    """Test 4: Probar validación de parámetros."""
    print("\n" + "="*60)
    print("TEST 4: Validación de Parámetros")
    print("="*60)

    try:
        db_manager = DatabaseManager()
        llm_agent = LLMAgent(db_manager=db_manager)

        registry = get_registry()
        orchestrator = ToolOrchestrator(registry)

        context = (
            ExecutionContextBuilder()
            .with_llm_agent(llm_agent)
            .with_db_manager(db_manager)
            .build()
        )

        # Test con parámetros inválidos
        test_cases = [
            ("Query muy corta", "ab", False),
            ("Query válida", "¿Cuántos usuarios hay?", True),
            ("Query muy larga", "a" * 1001, False),
        ]

        success_count = 0
        for name, query, should_succeed in test_cases:
            print(f"\n🧪 {name}: '{query[:50]}...' (esperado: {'✅' if should_succeed else '❌'})")

            result = await orchestrator.execute_command(
                user_id=999,
                command="/ia",
                params={"query": query},
                context=context
            )

            if result.success == should_succeed:
                print(f"   ✅ Comportamiento correcto")
                success_count += 1
            else:
                print(f"   ❌ Comportamiento inesperado")
                if not result.success:
                    print(f"      Error: {result.user_friendly_error}")

        return success_count == len(test_cases)

    except Exception as e:
        print(f"\n❌ Excepción durante test: {e}")
        logger.error("Error en test_parameter_validation", exc_info=True)
        return False


async def test_error_handling():
    """Test 5: Probar manejo de errores."""
    print("\n" + "="*60)
    print("TEST 5: Manejo de Errores")
    print("="*60)

    try:
        # Test 1: Context sin LLMAgent
        print("\n🧪 Test: Context sin LLMAgent")
        registry = get_registry()
        orchestrator = ToolOrchestrator(registry)

        context_without_llm = ExecutionContextBuilder().build()

        result = await orchestrator.execute_command(
            user_id=999,
            command="/ia",
            params={"query": "test"},
            context=context_without_llm
        )

        if not result.success and "no disponible" in result.user_friendly_error.lower():
            print("   ✅ Error manejado correctamente")
            test1_pass = True
        else:
            print("   ❌ Error no manejado correctamente")
            test1_pass = False

        # Test 2: Comando inexistente
        print("\n🧪 Test: Comando inexistente")
        db_manager = DatabaseManager()
        llm_agent = LLMAgent(db_manager=db_manager)

        context = (
            ExecutionContextBuilder()
            .with_llm_agent(llm_agent)
            .build()
        )

        result = await orchestrator.execute_command(
            user_id=999,
            command="/comando_que_no_existe",
            params={},
            context=context
        )

        if not result.success and "no encontrado" in result.error.lower():
            print("   ✅ Error manejado correctamente")
            test2_pass = True
        else:
            print("   ❌ Error no manejado correctamente")
            test2_pass = False

        return test1_pass and test2_pass

    except Exception as e:
        print(f"\n❌ Excepción durante test: {e}")
        logger.error("Error en test_error_handling", exc_info=True)
        return False


async def run_all_tests():
    """Ejecutar todos los tests."""
    print("\n" + "="*60)
    print("🧪 SUITE DE PRUEBAS MANUALES - SISTEMA DE TOOLS")
    print("="*60)
    print(f"Provider LLM: {settings.openai_model if settings.openai_api_key else 'Anthropic'}")
    print(f"Base de datos: {settings.database_url[:30]}...")
    print("="*60)

    results = []

    # Ejecutar tests en orden
    tests = [
        ("Inicialización de Tools", test_tool_initialization),
        ("QueryTool Directo", test_query_tool_direct),
        ("Flujo con Orquestador", test_orchestrator_flow),
        ("Validación de Parámetros", test_parameter_validation),
        ("Manejo de Errores", test_error_handling)
    ]

    for name, test_func in tests:
        try:
            result = await test_func()
            results.append((name, result))
        except Exception as e:
            logger.error(f"Error ejecutando {name}: {e}", exc_info=True)
            results.append((name, False))

    # Mostrar resumen
    print("\n" + "="*60)
    print("📊 RESUMEN DE PRUEBAS")
    print("="*60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✅ PASÓ" if result else "❌ FALLÓ"
        print(f"{status} - {name}")

    print("="*60)
    print(f"\nResultado final: {passed}/{total} tests pasaron")
    print(f"Tasa de éxito: {passed/total*100:.1f}%")

    if passed == total:
        print("\n🎉 ¡Todos los tests pasaron exitosamente!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) fallaron")
        return 1


if __name__ == "__main__":
    print("\n🚀 Iniciando pruebas del sistema de Tools...")
    print("⚠️  Asegúrate de tener configuradas las variables de entorno (.env)")
    print("⚠️  Se realizarán consultas reales al LLM y a la base de datos\n")

    input("Presiona ENTER para continuar o Ctrl+C para cancelar...")

    exit_code = asyncio.run(run_all_tests())
    exit(exit_code)
