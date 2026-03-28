# Guía de Testing

> **Última actualización:** 2026-03-28
> **Framework:** pytest + pytest-asyncio
> **Estructura de tests:** `tests/`

---

## Estructura de tests

```
tests/
├── agents/
│   ├── test_react_agent.py     ← ReActAgent, loop, scratchpad
│   └── test_tools.py           ← BaseTool, ToolRegistry, tools individuales
├── auth/
│   └── test_auth_middleware.py ← AuthMiddleware, TokenMiddleware
├── gateway/
│   └── test_gateway.py         ← MessageGateway, MainHandler, factory
├── handlers/
│   └── test_tools_handlers.py  ← Handlers de Telegram
├── memory/                     ← MemoryService, MemoryRepository
├── observability/              ← Tracer, MetricsCollector
└── utils/
    └── test_retry.py           ← Decorador retry
```

---

## Ejecutar tests

```bash
# Todos los tests
python -m pytest tests/ -v

# Por módulo
python -m pytest tests/agents/ -v
python -m pytest tests/agents/test_tools.py -v

# Con coverage
python -m pytest tests/ --cov=src --cov-report=html
# Ver reporte en htmlcov/index.html

# Un test específico
python -m pytest tests/agents/test_tools.py::TestToolRegistry::test_register -v

# Solo tests rápidos (sin BD)
python -m pytest tests/ -v -m "not integration"
```

---

## Escribir tests para una nueva tool

```python
# tests/agents/test_tools.py (agregar en este archivo)
import pytest
from src.agents.tools.mi_tool import MiTool

class TestMiTool:
    def setup_method(self):
        self.tool = MiTool()

    def test_name(self):
        assert self.tool.name == "mi_tool"

    def test_parameters(self):
        params = self.tool.get_parameters()
        assert len(params) == 1
        assert params[0].name == "param1"
        assert params[0].required is True

    @pytest.mark.asyncio
    async def test_execute_success(self):
        result = await self.tool.execute(param1="valor_valido")
        assert result.success is True
        assert result.observation != ""

    @pytest.mark.asyncio
    async def test_execute_error(self):
        result = await self.tool.execute(param1="")
        assert result.success is False
        assert result.error is not None
```

---

## Mocks recomendados

### Mockear DatabaseManager
```python
from unittest.mock import AsyncMock, MagicMock

@pytest.fixture
def mock_db():
    db = MagicMock()
    db.execute_query = AsyncMock(return_value=[{"count": 42}])
    return db
```

### Mockear OpenAIProvider
```python
from unittest.mock import AsyncMock
from src.agents.react.schemas import ReActResponse

@pytest.fixture
def mock_provider():
    provider = AsyncMock()
    provider.generate_structured.return_value = ReActResponse(
        thought="Tengo la respuesta",
        action="finish",
        action_input={},
        final_answer="La respuesta es 42",
    )
    return provider
```

### Mockear ToolRegistry limpio (para tests aislados)
```python
from src.agents.tools.registry import ToolRegistry

@pytest.fixture(autouse=True)
def reset_registry():
    ToolRegistry.reset()
    yield
    ToolRegistry.reset()
```

---

## Tests de integración con BD

Los tests que necesitan BD real deben marcarse con `@pytest.mark.integration` y configurarse para saltar si no hay conexión:

```python
import pytest
from src.infra.database.connection import DatabaseManager

@pytest.mark.integration
@pytest.mark.asyncio
async def test_database_tool_real():
    db = DatabaseManager()
    if not await db.health_check():
        pytest.skip("Base de datos no disponible")

    tool = DatabaseTool(db_manager=db)
    result = await tool.execute(query="cuántos registros hay")
    assert result.success is True
```

---

## Convenciones

- Un archivo de test por módulo de producción
- Clases de test agrupan por componente: `TestReActAgent`, `TestToolRegistry`, etc.
- Fixtures en `conftest.py` para mocks reutilizables
- Tests unitarios no deben tocar BD, red ni filesystem
- Nombres descriptivos: `test_<qué>_cuando_<condición>_devuelve_<resultado>`
