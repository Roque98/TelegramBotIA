"""
test_orchestrator.py — Test de integración del Orchestrator dinámico ARQ-35.

Verifica que cada tipo de consulta se rutea al agente correcto.

Uso:
    python scripts/test_orchestrator.py
    python scripts/test_orchestrator.py --verbose
"""
import asyncio
import argparse
import sys
import logging
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Forzar UTF-8 en stdout
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout = open(sys.stdout.fileno(), mode="w", encoding="utf-8", buffering=1)

from src.infra.database.connection import DatabaseManager
from src.domain.agent_config.agent_config_repository import AgentConfigRepository
from src.domain.agent_config.agent_config_service import AgentConfigService
from src.agents.orchestrator.intent_classifier import IntentClassifier
from src.agents.orchestrator.orchestrator import AgentOrchestrator


async def test_config_load():
    """Test 1: Verificar carga de agentes desde BD."""
    print("\n[TEST 1] Carga de configuración desde BD")
    db = DatabaseManager()
    repo = AgentConfigRepository(db_manager=db)
    service = AgentConfigService(repository=repo)
    agents = service.get_active_agents()

    print(f"  Agentes activos: {len(agents)}")
    for a in agents:
        print(f"  - '{a.nombre}' | generalista={a.es_generalista} | "
              f"tools={a.tools} | version={a.version}")

    assert len(agents) > 0, "ERROR: No hay agentes activos en BD"
    assert any(a.es_generalista for a in agents), "ERROR: No hay agente generalista"
    has_datos = any(a.nombre == "datos" for a in agents)
    has_conocimiento = any(a.nombre == "conocimiento" for a in agents)
    has_casual = any(a.nombre == "casual" for a in agents)
    assert has_datos, "ERROR: Falta agente 'datos'"
    assert has_conocimiento, "ERROR: Falta agente 'conocimiento'"
    assert has_casual, "ERROR: Falta agente 'casual'"

    print("  [OK] Configuración cargada correctamente")
    return service, agents


async def test_placeholder_validation(service, agents):
    """Test 2: Verificar que los prompts tienen los placeholders requeridos."""
    print("\n[TEST 2] Validación de placeholders en prompts")
    for a in agents:
        has_td = "{tools_description}" in a.system_prompt
        has_uh = "{usage_hints}" in a.system_prompt
        status = "OK" if (has_td and has_uh) else "WARN (excluido)"
        print(f"  - '{a.nombre}' | {{tools_description}}={has_td} | {{usage_hints}}={has_uh} | {status}")

    print("  [OK] Validación de placeholders completada")


async def test_intent_classifier(agents):
    """Test 3: Verificar routing del IntentClassifier."""
    print("\n[TEST 3] Intent Classification (necesita conexión a OpenAI)")
    from src.config.settings import settings
    from src.agents.providers.openai_provider import OpenAIProvider

    if not settings.openai_api_key:
        print("  [SKIP] Sin OPENAI_API_KEY — omitiendo test de clasificación LLM")
        return

    llm = OpenAIProvider(api_key=settings.openai_api_key, model=settings.openai_loop_model)
    classifier = IntentClassifier(llm=llm)

    test_cases = [
        ("¿cuántas ventas hubo ayer?", "datos"),
        ("¿cuál es la política de vacaciones?", "conocimiento"),
        ("hola, ¿cómo estás?", "casual"),
        ("necesito analizar datos de ventas y también entender la política de comisiones", "generalista"),
    ]

    passed = 0
    for query, expected in test_cases:
        result = await classifier.classify(query, agents)
        status = "OK" if result == expected else f"WARN (got '{result}', expected '{expected}')"
        print(f"  [{status}] '{query[:50]}' → '{result}'")
        if result == expected:
            passed += 1

    print(f"  {passed}/{len(test_cases)} tests passed")


async def test_agent_builder(agents):
    """Test 4: Verificar construcción de agentes."""
    print("\n[TEST 4] AgentBuilder — construcción de instancias")
    from src.config.settings import settings
    from src.agents.tools.registry import ToolRegistry
    from src.agents.factory.agent_builder import AgentBuilder

    if not settings.openai_api_key:
        print("  [SKIP] Sin OPENAI_API_KEY — omitiendo test de construcción")
        return

    # Crear un registry mínimo (sin tools reales para este test)
    ToolRegistry.reset()
    registry = ToolRegistry()

    builder = AgentBuilder(
        tool_registry=registry,
        openai_api_key=settings.openai_api_key,
    )

    for a in agents:
        agent = builder.build(a)
        expected_scope = None if a.es_generalista else set(a.tools)
        print(f"  - '{a.nombre}' | tool_scope={agent.tool_scope} | "
              f"temp={agent.temperature} | max_iter={agent.max_iterations} | "
              f"override={'yes' if agent.system_prompt_override else 'no'}")
        assert agent.tool_scope == expected_scope, (
            f"ERROR: scope incorrecto para '{a.nombre}': "
            f"got {agent.tool_scope}, expected {expected_scope}"
        )

    # Test cache: build dos veces el mismo agente debe retornar la misma instancia
    a0 = agents[0]
    inst1 = builder.build(a0)
    inst2 = builder.build(a0)
    assert inst1 is inst2, "ERROR: cache no funciona (instancias distintas)"
    print(f"  [OK] Cache funciona: mismo agente retorna misma instancia")

    # Test clear_instance_cache
    builder.clear_instance_cache()
    inst3 = builder.build(a0)
    assert inst3 is not inst1, "ERROR: clear_instance_cache no limpió el cache"
    print(f"  [OK] clear_instance_cache funciona correctamente")

    ToolRegistry.reset()
    print("  [OK] AgentBuilder funciona correctamente")


async def test_cache_invalidation():
    """Test 5: Verificar invalidación de cache."""
    print("\n[TEST 5] Cache invalidation")
    db = DatabaseManager()
    repo = AgentConfigRepository(db_manager=db)
    service = AgentConfigService(repository=repo)

    # Cargar por primera vez
    agents1 = service.get_active_agents()
    # Segunda carga debe venir del cache
    agents2 = service.get_active_agents()
    assert agents1 == agents2, "ERROR: cache retorna resultados inconsistentes"
    print(f"  [OK] Cache LRU: dos cargas retornan resultados consistentes ({len(agents1)} agentes)")

    # Invalidar
    service.invalidate_cache()
    agents3 = service.get_active_agents()
    assert len(agents3) > 0, "ERROR: tras invalidar, no se cargaron agentes"
    print(f"  [OK] Cache invalidado y recargado: {len(agents3)} agentes")


async def main(verbose: bool = False):
    if verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.WARNING)

    print("=" * 60)
    print("ARQ-35 Integration Test — Dynamic Orchestrator")
    print("=" * 60)

    try:
        service, agents = await test_config_load()
        await test_placeholder_validation(service, agents)
        await test_agent_builder(agents)
        await test_cache_invalidation()
        await test_intent_classifier(agents)

        print("\n" + "=" * 60)
        print("Todos los tests completados.")
        print("=" * 60)

    except AssertionError as e:
        print(f"\n[FAIL] {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] {e}", file=sys.stderr)
        if verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test de integración ARQ-35")
    parser.add_argument("--verbose", "-v", action="store_true")
    args = parser.parse_args()
    asyncio.run(main(verbose=args.verbose))
