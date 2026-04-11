# Sistema de Tools

## Resumen

| Métrica | Valor |
|---------|-------|
| Tools registradas | 10 |
| Ubicación | `src/agents/tools/` |
| Patrón | BaseTool abstracta + ToolRegistry singleton |

---

## Tools Registradas

### 1. DatabaseTool — `database_query`

**Archivo**: `src/agents/tools/database_tool.py`
**Descripción**: Ejecuta consultas SQL en lenguaje natural contra SQL Server

```yaml
Nombre: "database_query"
Categoría: DATABASE
Parámetros:
  - query (string, required): Consulta en lenguaje natural
Requiere: DatabaseManager
```

**Flujo**:
```
1. LLM genera SQL desde la query de texto natural
2. SQLValidator.validate(sql) — solo SELECT/WITH/EXEC
3. DatabaseManager.execute_query(sql) → resultados
4. LLM formatea resultados como texto natural
```

---

### 2. KnowledgeTool — `knowledge_search`

**Archivo**: `src/agents/tools/knowledge_tool.py`
**Descripción**: Busca en la base de conocimiento empresarial

```yaml
Nombre: "knowledge_search"
Categoría: KNOWLEDGE
Parámetros:
  - query (string, required): Término o pregunta a buscar
Requiere: KnowledgeService
```

---

### 3. CalculateTool — `calculate`

**Archivo**: `src/agents/tools/calculate_tool.py`
**Descripción**: Evalúa expresiones matemáticas de forma segura

```yaml
Nombre: "calculate"
Categoría: CALCULATION
Parámetros:
  - expression (string, required): Expresión matemática (ej: "15 * 1.16")
```

---

### 4. DateTimeTool — `get_datetime`

**Archivo**: `src/agents/tools/datetime_tool.py`
**Descripción**: Obtiene fecha y hora actual del sistema

```yaml
Nombre: "get_datetime"
Categoría: DATETIME
Parámetros: (ninguno)
```

---

### 5. SavePreferenceTool — `save_preference`

**Archivo**: `src/agents/tools/preference_tool.py`
**Descripción**: Guarda preferencias del usuario en BD

```yaml
Nombre: "save_preference"
Categoría: UTILITY
Parámetros:
  - key (string, required): Nombre de la preferencia
  - value (string, required): Valor a guardar
Requiere: DatabaseManager
```

---

### 6. ReadAttachmentTool — `read_attachment`

**Archivo**: `src/agents/tools/read_attachment_tool.py`
**Descripción**: Lee archivos adjuntos enviados por el usuario (imágenes, PDFs, etc.)

```yaml
Nombre: "read_attachment"
Categoría: UTILITY
Parámetros:
  - file_id (string, required): ID del archivo en Telegram
```

---

### 7. AlertAnalysisTool — `alert_analysis`

**Archivo**: `src/agents/tools/alert_analysis_tool.py`
**Descripción**: Analiza alertas activas de monitoreo PRTG. Consulta eventos activos,
tickets históricos y matriz de escalamiento para generar un diagnóstico estructurado.

```yaml
Nombre: "alert_analysis"
Categoría: MONITORING
Parámetros:
  - filtro (string, optional): Equipo, IP o sensor a filtrar
Requiere: AlertRepository, OpenAIProvider (data_llm)
Requiere alias BD: "monitoreo" (DB_CONNECTIONS=core,monitoreo)
Estado: desactivada en BotIAv2_Recurso (reemplazada por FEAT-37)
```

**Flujo**:
```
1. AlertRepository.get_active_events() — BAZ_CDMX → EKT fallback
2. Seleccionar evento más crítico que coincida con filtro
3. Enriquecer: tickets históricos, template, escalamiento, contactos
4. AlertPromptBuilder.build_prompt(context) → prompt enriquecido
5. LLM (data_llm) genera análisis estructurado Markdown
6. Retorna análisis + DISCLAIMER al agente
```

---

### 8. ReloadPermissionsTool — `reload_permissions`

**Archivo**: `src/agents/tools/reload_permissions_tool.py`
**Descripción**: Invalida el cache de permisos del usuario y los recarga desde BD

```yaml
Nombre: "reload_permissions"
Categoría: UTILITY
Parámetros: (ninguno)
esPublico: true
```

---

### 9. ReloadAgentConfigTool — `reload_agent_config`

**Archivo**: `src/agents/tools/reload_agent_config_tool.py`
**Descripción**: Recarga la configuración de agentes desde BotIAv2_AgenteDef

```yaml
Nombre: "reload_agent_config"
Categoría: UTILITY
Parámetros: (ninguno)
```

---

### 10. SaveMemoryTool — `save_memory`

**Archivo**: `src/agents/tools/save_memory_tool.py`
**Descripción**: Persiste un resumen o dato importante en la memoria del usuario

```yaml
Nombre: "save_memory"
Categoría: UTILITY
Parámetros:
  - content (string, required): Dato a memorizar
Requiere: MemoryRepository
```

---

## Estructura del Sistema

### Archivos

```
src/agents/tools/
├── base.py                    ← BaseTool, ToolResult, ToolDefinition, ToolCategory
├── registry.py                ← ToolRegistry (singleton, thread-safe)
├── database_tool.py           ← DatabaseTool
├── knowledge_tool.py          ← KnowledgeTool
├── calculate_tool.py          ← CalculateTool
├── datetime_tool.py           ← DateTimeTool
├── preference_tool.py         ← SavePreferenceTool
├── read_attachment_tool.py    ← ReadAttachmentTool
├── alert_analysis_tool.py     ← AlertAnalysisTool (FEAT-36/37)
├── reload_permissions_tool.py ← ReloadPermissionsTool
├── reload_agent_config_tool.py← ReloadAgentConfigTool
└── save_memory_tool.py        ← SaveMemoryTool
```

---

## BaseTool (Contrato)

**Archivo**: `src/agents/tools/base.py`

```python
class BaseTool(ABC):
    @property
    @abstractmethod
    def name(self) -> str: ...

    @property
    @abstractmethod
    def description(self) -> str: ...

    @abstractmethod
    def get_parameters(self) -> list[ToolParameter]: ...

    @abstractmethod
    async def execute(self, **kwargs: Any) -> ToolResult: ...

    def get_definition(self) -> ToolDefinition:
        """Genera metadata para el prompt del LLM."""

    def to_prompt_format(self) -> str:
        """Genera descripción legible para incluir en system prompt."""
```

```python
class ToolResult(BaseModel):
    success: bool
    observation: str              # Lo que el agente "observa" como resultado
    data: Optional[Any] = None
    error: Optional[str] = None
    execution_time_ms: float = 0.0
```

```python
class ToolCategory(str, Enum):
    DATABASE    = "database"
    KNOWLEDGE   = "knowledge"
    CALCULATION = "calculation"
    DATETIME    = "datetime"
    UTILITY     = "utility"
```

---

## ToolRegistry (Singleton)

**Archivo**: `src/agents/tools/registry.py`

```python
registry = ToolRegistry()

# Registrar tool
registry.register(DatabaseTool(db_manager=db))

# Obtener tool por nombre
tool = registry.get("database_query")       # Optional[BaseTool]

# Listar todas
tools = registry.get_all()                  # list[BaseTool]

# Generar descripción para el prompt
prompt_text = registry.get_tools_prompt()   # str con todas las tools formateadas

# Resetear (para tests)
ToolRegistry.reset()
```

**Thread-safety**: usa `threading.Lock` con double-checked locking.

---

## Cómo Crear una Nueva Tool

```python
# src/agents/tools/mi_tool.py
from src.agents.tools.base import BaseTool, ToolParameter, ToolResult, ToolCategory

class MiTool(BaseTool):
    @property
    def name(self) -> str:
        return "mi_tool"

    @property
    def description(self) -> str:
        return "Descripción que verá el LLM"

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
            return ToolResult(success=False, observation="Error", error=str(e))
```

**Registrar en la factory** (`src/pipeline/factory.py`):
```python
def create_tool_registry(db_manager=None, knowledge_manager=None) -> ToolRegistry:
    registry = ToolRegistry()
    registry.register(DatabaseTool(db_manager=db_manager))
    registry.register(KnowledgeTool(knowledge_manager=knowledge_manager))
    registry.register(CalculateTool())
    registry.register(DateTimeTool())
    registry.register(SavePreferenceTool(db_manager=db_manager))
    registry.register(MiTool())  # ← agregar aquí
    return registry
```

---

## Flujo Completo Tool en ReAct Loop

```
ReActAgent recibe query: "¿Cuántas ventas hubo ayer?"
        │
        ▼
LLM (con system_prompt que incluye tools_description):
{
    "thought": "Necesito consultar la base de datos",
    "action": "database_query",
    "action_input": {"query": "ventas de ayer"},
    "final_answer": null
}
        │
        ▼
registry.get("database_query") → DatabaseTool
        │
        ▼
DatabaseTool.execute(query="ventas de ayer")
        │
        ├── SQLValidator → "SELECT COUNT(*) FROM ventas WHERE ..."
        ├── DatabaseManager.execute_query(sql) → [{"count": 45}]
        └── LLM formatea → "Ayer se registraron 45 ventas"
        │
        ▼
ToolResult(success=True, observation="Ayer se registraron 45 ventas")
        │
        ▼
scratchpad.add_step(thought, "database_query", observation)
        │
        ▼ (siguiente iteración del loop)
LLM:
{
    "thought": "Ya tengo la información",
    "action": "finish",
    "final_answer": "Ayer se registraron 45 ventas."
}
        │
        ▼
AgentResponse(success=True, message="Ayer se registraron 45 ventas.")
```
