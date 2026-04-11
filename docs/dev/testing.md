# Testing

---

## Tests unitarios

El proyecto usa `pytest`. Los tests están en `tests/`.

```bash
# Activar virtualenv primero
source ~/.virtualenvs/GPT5-Cxk5mELR/Scripts/activate  # Windows

# Correr todos los tests
pytest

# Con verbose
pytest -v

# Un módulo específico
pytest tests/test_tools.py -v

# Un test específico
pytest tests/test_tools.py::test_calculate_tool -v

# Con cobertura
pytest --cov=src --cov-report=term-missing
```

La configuración de pytest está en `pytest.ini`.

---

## Prueba manual de una consulta

El script `scripts/test_message.py` envía una consulta al agente directamente
(sin Telegram) y muestra el resultado con detalle de pasos:

```bash
python scripts/test_message.py "cuanto es el 20% de 3500"
```

Salida esperada:

```
Respuesta: El 20% de 3500 es *700* 🧮
Success: True
Steps: 2
Tools used: ['calculate']
```

Para probar con un usuario específico:

```bash
python scripts/test_message.py "ventas de ayer" --user-id 12345
```

---

## Verificar observabilidad después de una prueba

Después de correr `test_message.py`, verificar en BD:

```sql
-- Ver la última interacción
SELECT TOP 1 *
FROM abcmasplus..BotIAv2_InteractionLogs
ORDER BY fechaInteraccion DESC;

-- Ver sus pasos
SELECT *
FROM abcmasplus..BotIAv2_InteractionSteps
WHERE correlationId = '<correlation_id_de_arriba>'
ORDER BY stepNumber;

-- Verificar que no hubo errores
SELECT COUNT(*) AS errores
FROM abcmasplus..BotIAv2_ApplicationLogs
WHERE nivel IN ('ERROR', 'CRITICAL')
  AND timestamp > DATEADD(MINUTE, -5, GETDATE());
```

---

## Validar ARQ-33 (filtrado de tools por permisos)

```python
# Ejemplo de test unitario para verificar que el filtrado funciona
from src.agents.tools.registry import ToolRegistry
from src.agents.base.events import UserContext

# Setup: user con solo calculate habilitado
user_context = UserContext(
    user_id="test",
    display_name="Test",
    roles=[],
    preferences={},
    working_memory=[],
    long_term_summary=None,
    permisos={"tool:calculate": True, "tool:datetime": True},
    permisos_loaded=True,
)

hints = registry.get_usage_hints(user_context)
assert "database_query" not in hints
assert "knowledge_search" not in hints
assert "calculate" in hints
```

---

## Tests del orquestador dinámico (ARQ-35)

Los tests de `AgentOrchestrator` e `IntentClassifier` están en `tests/agents/test_orchestrator.py`.

```bash
pytest tests/agents/test_orchestrator.py -v
```

Clases de test principales:

- `TestIntentClassifier` — verifica el ruteo de mensajes al agente correcto (`datos`, `casual`, `conocimiento`) y el fallback a `generalista` en caso de error o respuesta desconocida del LLM.
- `TestAgentOrchestrator` — verifica que el orquestador construye y ejecuta el agente seleccionado, propaga el `event_callback` y retorna error gracioso si no hay agente `generalista`.
- `TestAgentBuilder` — verifica que `AgentBuilder` asigna `tool_scope` a agentes especializados, `None` al generalista, y que el cache por `(id, version)` evita reconstruir instancias duplicadas.

---

## Tests de permisos de tools (SEC-01)

Los tests de filtrado en `ToolRegistry` están en `tests/agents/test_tool_permissions.py`.

```bash
pytest tests/agents/test_tool_permissions.py -v
```

Escenarios cubiertos:

| Test | Qué verifica |
|------|-------------|
| `test_prompt_sin_permisos_incluye_todas` | Sin `UserContext` → backward compat, todas visibles |
| `test_prompt_filtra_tool_no_permitida` | Tool ausente en `permisos` no aparece en el prompt |
| `test_prompt_tool_denegada_no_aparece` | `permitido=False` excluye la tool del prompt |
| `test_execute_tool_denegada_retorna_error` | Segunda línea de defensa: ejecución retorna error sin ejecutar |
| `test_execute_sin_permisos_ejecuta` | `permisos={}` → backward compat, ejecuta sin restricción |

---

## Tests del catálogo de tools (pipeline)

Los tests de `create_tool_registry` y `_build_tool_catalog` están en `tests/pipeline/test_tool_catalog.py`.

```bash
pytest tests/pipeline/test_tool_catalog.py -v
```

Grupos de test:

- `TestBuildToolCatalog` — verifica que el catálogo contiene exactamente las 9 tools conocidas y que cada entrada es callable.
- `TestCreateToolRegistryFromDB` — verifica el registro BD-driven: solo se registran las tools en `active_tool_names`, las que no tienen código se descartan silenciosamente, y las que tienen dependencia faltante (ej. `knowledge_search` sin `knowledge_manager`) se omiten.
- `TestCreateToolRegistryFallback` — verifica que `active_tool_names=None` registra todo el catálogo disponible (fallback cuando la BD no está disponible).
- `TestGetActiveToolNames` — verifica que `PermissionRepository.get_active_tool_names()` filtra por prefijo `tool:`, retorna solo el sufijo, e ignora recursos de tipo `cmd:` u otros.

---

## Tests de integración

Para tests que requieren base de datos real, usar la instancia de desarrollo.
Los tests de integración están marcados con `@pytest.mark.integration` y se
excluyen por defecto:

```bash
# Solo tests unitarios (default)
pytest -m "not integration"

# Incluir tests de integración
pytest -m integration

# Correr solo los tests de integración de permisos
pytest tests/integration/test_permission_flow.py -v
```

El archivo `tests/integration/test_permission_flow.py` verifica el flujo completo
`PermissionService → UserContext.permisos → ToolRegistry` sin BD real (usa mocks).
Cubre el deny definitivo de usuario que pisa permisos de rol, el cache de permisos y
la invalidación manual, y el comportamiento de recursos públicos (`esPublico=1`).

---

## Depuración

### Ver logs en tiempo real

```bash
# Activar DEBUG para ver detalle del loop ReAct
LOG_LEVEL=DEBUG python main.py
```

### Ver qué tools están registradas

```python
from src.agents.tools.registry import ToolRegistry
registry = ToolRegistry()
for name, tool in registry._tools.items():
    print(f"{name}: {tool.definition.description[:60]}")
```

### Verificar configuración de BD

```bash
python check_config.py
```

---

**← Anterior** [GitFlow del proyecto](gitflow.md) · [Índice](README.md)
