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

## Tests de integración

Para tests que requieren base de datos real, usar la instancia de desarrollo.
Los tests de integración están marcados con `@pytest.mark.integration` y se
excluyen por defecto:

```bash
# Solo tests unitarios (default)
pytest -m "not integration"

# Incluir tests de integración
pytest -m integration
```

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
