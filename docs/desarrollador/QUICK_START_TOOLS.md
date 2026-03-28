# Quick Start — Sistema de Tools

> **Última actualización:** 2026-03-28
> **Ubicación del código:** `src/agents/tools/`

Guía rápida para entender, usar y extender el sistema de tools del ReActAgent.

---

## Las 5 Tools disponibles

| Tool | Nombre | Cuándo la usa el agente |
|------|--------|------------------------|
| `DatabaseTool` | `database_query` | Consultas de datos en lenguaje natural |
| `KnowledgeTool` | `knowledge_search` | Políticas, procesos, FAQs |
| `CalculateTool` | `calculate` | Expresiones matemáticas |
| `DateTimeTool` | `get_datetime` | Fecha y hora actual del sistema |
| `SavePreferenceTool` | `save_preference` | Guardar preferencias del usuario |

---

## Probar con el bot de Telegram

```bash
# 1. Configurar .env
cp .env.example .env
# Editar .env con TELEGRAM_BOT_TOKEN, OPENAI_API_KEY, DB_*

# 2. Arrancar
python main.py

# 3. En Telegram
/ia ¿Cuántas ventas hubo ayer?          → database_query
/ia ¿Cómo solicito vacaciones?          → knowledge_search
/ia ¿Cuánto es 15 * 1.16?               → calculate
/ia ¿Qué día es hoy?                    → get_datetime
```

---

## Probar con la API REST

```bash
# 1. Arrancar el API
python src/api/chat_endpoint.py

# 2. Generar token de prueba
python scripts/generar_token.py 12345

# 3. Enviar request
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"token": "<token>", "message": "¿Cuántas ventas hubo ayer?"}'
```

---

## Crear una nueva tool

```python
# src/agents/tools/mi_tool.py
from src.agents.tools.base import BaseTool, ToolParameter, ToolResult, ToolCategory

class MiTool(BaseTool):
    @property
    def name(self) -> str:
        return "mi_tool"

    @property
    def description(self) -> str:
        return "Descripción que verá el LLM — sé específico sobre cuándo usarla"

    def get_parameters(self) -> list[ToolParameter]:
        return [
            ToolParameter(
                name="param1",
                param_type="string",
                description="Descripción del parámetro",
                required=True,
            )
        ]

    async def execute(self, param1: str, **kwargs) -> ToolResult:
        try:
            resultado = await self._hacer_algo(param1)
            return ToolResult(success=True, observation=str(resultado))
        except Exception as e:
            return ToolResult(success=False, observation="Error al ejecutar", error=str(e))
```

Registrar en `src/pipeline/factory.py`:

```python
def create_tool_registry(db_manager=None, knowledge_manager=None) -> ToolRegistry:
    registry = ToolRegistry()
    # ... tools existentes ...
    registry.register(MiTool())  # ← agregar aquí
    return registry
```

---

## Ejecutar tests de tools

```bash
# Tests del sistema de tools
python -m pytest tests/agents/test_tools.py -v

# Tests del ReActAgent completo
python -m pytest tests/agents/test_react_agent.py -v

# Todos los tests
python -m pytest tests/ -v
```

---

## Estructura del código

```
src/agents/tools/
├── base.py           ← BaseTool, ToolResult, ToolParameter, ToolCategory
├── registry.py       ← ToolRegistry (singleton, thread-safe)
├── database_tool.py  ← database_query
├── knowledge_tool.py ← knowledge_search
├── calculate_tool.py ← calculate
├── datetime_tool.py  ← get_datetime
└── preference_tool.py← save_preference
```

Ver documentación completa en `.claude/context/TOOLS.md`.
