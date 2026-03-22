# Agentes LLM

## Estado Actual

### ReActAgent (Nuevo Orquestador Principal)

**Archivo**: `src/agents/react/agent.py`
**Estado**: ACTIVO - Arquitectura principal

```python
class ReActAgent(BaseAgent):
    def __init__(
        self,
        llm: LLMProvider,
        tool_registry: ToolRegistry,
        max_iterations: int = 10,
        temperature: float = 0.1,
    )

    async def execute(
        self,
        query: str,
        context: UserContext,
        **kwargs: Any,
    ) -> AgentResponse
```

**Componentes**:
- `llm`: Proveedor LLM (OpenAI, Anthropic)
- `tools`: ToolRegistry con herramientas disponibles
- `scratchpad`: Historial de pasos (thought/action/observation)

**Flujo de execute()**:
```
1. Iniciar tracing (si observability disponible)
2. Construir system_prompt con tools disponibles
3. Loop ReAct (max_iterations):
   │
   ├─ THOUGHT: ¿Qué necesito hacer?
   │  └── LLM genera ReActResponse (JSON)
   │
   ├─ Si action == FINISH:
   │  └── return AgentResponse.success(final_answer)
   │
   ├─ ACTION: Ejecutar tool
   │  └── observation = tool.execute(**action_input)
   │
   └─ OBSERVE: Agregar al scratchpad
      └── scratchpad.add_step(thought, action, observation)
   │
4. Si max_iterations: synthesize_partial()
5. Registrar métricas y finalizar trace
6. return AgentResponse
```

---

### LLMAgent (Legacy - Fallback)

**Archivo**: `src/agent/llm_agent.py`
**Líneas**: ~544
**Estado**: LEGACY - Usado como fallback cuando ReAct falla

```python
class LLMAgent:
    def __init__(
        self,
        db_manager: DatabaseManager,
        llm_provider: str = "openai",
        model: str = "gpt-4"
    )

    async def process_query(
        self,
        user_id: int,
        query: str
    ) -> str
```

**Componentes internos**:
- `llm_provider`: OpenAIProvider | AnthropicProvider
- `query_classifier`: QueryClassifier
- `sql_generator`: SQLGenerator
- `sql_validator`: SQLValidator
- `response_formatter`: ResponseFormatter
- `memory_manager`: MemoryManager
- `conversation_history`: ConversationHistory
- `prompt_manager`: PromptManager

**Flujo de process_query()**:
```
1. conversation_history.add_message(query)
2. memory_context = memory_manager.get_memory_context()
3. classification = query_classifier.classify(query)
   │
   ├─ DATABASE
   │  ├── sql = sql_generator.generate(query)
   │  ├── sql_validator.validate(sql)
   │  ├── results = db_manager.execute_query(sql)
   │  └── response = response_formatter.format(results)
   │
   ├─ KNOWLEDGE
   │  ├── context = query_classifier.get_knowledge_context()
   │  └── response = llm.generate(prompt + context)
   │
   └─ GENERAL
      └── response = llm.generate(prompt) | saludo dinámico
   │
4. memory_manager.record_interaction() [async]
5. conversation_history.add_response(response)
6. return response
```

---

## Clasificación de Queries

### QueryClassifier

**Archivo**: `src/agent/classifiers/query_classifier.py`

```python
class QueryType(Enum):
    DATABASE = "database"    # Requiere SQL
    KNOWLEDGE = "knowledge"  # Buscar en KB
    GENERAL = "general"      # Conversación general

class QueryClassifier:
    async def classify(self, query: str, context: str = "") -> QueryType
    def get_knowledge_context(self) -> str  # Cached
```

**Lógica de clasificación**:
1. Busca en KnowledgeManager si hay entradas relevantes
2. Si hay match con score alto → KNOWLEDGE
3. Si parece query de datos (ventas, usuarios, etc.) → DATABASE
4. Si es saludo, despedida, pregunta sobre el bot → GENERAL

---

## Generación SQL

### SQLGenerator

**Archivo**: `src/agent/sql/sql_generator.py`

```python
class SQLGenerator:
    async def generate_sql(
        self,
        query: str,
        schema: dict = None
    ) -> str
```

**Prompt incluye**:
- Schema de la BD (tablas, columnas, tipos)
- Ejemplos few-shot
- Restricciones (solo SELECT)

### SQLValidator

**Archivo**: `src/agent/sql/sql_validator.py`

```python
class SQLValidator:
    def validate(self, sql: str) -> ValidationResult
    # Solo SELECT, EXEC, WITH
    # Rechaza modificaciones y injection
```

---

## Formateo de Respuestas

### ResponseFormatter

**Archivo**: `src/agent/formatters/response_formatter.py`

```python
class ResponseFormatter:
    async def format_query_results(
        self,
        query: str,
        results: list[dict],
        use_natural_language: bool = True
    ) -> str
```

**Modos**:
- `use_natural_language=True`: LLM convierte resultados a texto
- `use_natural_language=False`: Formato estructurado/tabla

---

## Proveedores LLM

### OpenAIProvider

**Archivo**: `src/agent/providers/openai_provider.py`

```python
class OpenAIProvider(LLMProvider):
    async def generate(self, prompt: str, max_tokens: int = 1000) -> str
    async def generate_structured(self, prompt: str, schema: Type[BaseModel]) -> T
```

### AnthropicProvider

**Archivo**: `src/agent/providers/anthropic_provider.py`

```python
class AnthropicProvider(LLMProvider):
    async def generate(self, prompt: str, max_tokens: int = 1000) -> str
    async def generate_structured(self, prompt: str, schema: Type[BaseModel]) -> T
```

---

## Arquitectura ReAct (Implementada)

### Estructura Actual

```
src/agents/
├── base/
│   ├── agent.py           # BaseAgent, AgentResponse
│   ├── events.py          # ConversationEvent, UserContext
│   └── exceptions.py      # LLMException, ToolException, etc.
│
├── react/
│   ├── agent.py           # ReActAgent
│   ├── scratchpad.py      # Historial de pasos
│   ├── schemas.py         # ReActStep, ReActResponse, ActionType
│   └── prompts.py         # Prompts del sistema
│
└── tools/
    ├── base.py            # BaseTool, ToolResult
    ├── registry.py        # ToolRegistry (singleton)
    ├── database_tool.py   # Consultas SQL
    ├── knowledge_tool.py  # Base de conocimiento
    └── calculate_tool.py  # Cálculos
```

### Gateway (Integración)

```
src/gateway/
├── __init__.py            # Lazy imports
├── message_gateway.py     # Normaliza Telegram/API/WebSocket → ConversationEvent
├── handler.py             # MainHandler (orquesta ReAct + Memory + Fallback)
└── factory.py             # Factories para crear componentes
```

### Memory Service

```
src/memory/
├── __init__.py
├── service.py             # MemoryService (cache + repository + context)
├── repository.py          # MemoryRepository (DB)
└── context_builder.py     # UserContextBuilder
```

### Observability

```
src/observability/
├── __init__.py
├── tracing.py             # TraceSpan, TraceContext, Tracer
└── metrics.py             # MetricsCollector, LatencyStats, Counter
```

### Contratos Base

```python
class AgentType(str, Enum):
    SINGLE_STEP = "single_step"
    REACT = "react"

class AgentResponse(BaseModel):
    success: bool
    message: Optional[str]
    data: Optional[dict]
    error: Optional[str]
    agent_name: str
    agent_type: AgentType
    execution_time_ms: float
    steps_taken: int = 1

class UserContext(BaseModel):
    user_id: str
    display_name: str
    roles: list[str]
    preferences: dict
    working_memory: list[MemoryEntry]
    long_term_summary: Optional[str]

class BaseAgent(ABC):
    name: str
    agent_type: AgentType

    @abstractmethod
    async def execute(
        self,
        query: str,
        context: UserContext
    ) -> AgentResponse
```

### Feature Flags

```python
# src/config/settings.py
use_react_agent: bool = False          # Habilitar ReAct
react_fallback_on_error: bool = True   # Usar LLMAgent como fallback
```

---

## Observabilidad

### Tracing

```python
from src.observability import get_tracer

tracer = get_tracer()
tracer.start_trace(user_id="123", channel="telegram")

with tracer.span("database_query", {"table": "users"}):
    # operación...
    pass

result = tracer.end_trace()  # dict con trace_id, spans, duration
```

### Métricas

```python
from src.observability import get_metrics

metrics = get_metrics()
metrics.record_request(
    channel="telegram",
    duration_ms=150.0,
    steps=2,
    success=True,
)
metrics.record_tool_usage("database_query")

stats = metrics.get_stats()  # dict con counters, latencias, etc.
```

---

## Flujo de Integración

```
Telegram/API/WebSocket
        │
        ▼
  MessageGateway.from_*()
        │
        ▼
  ConversationEvent
        │
        ▼
  MainHandler._process_event()
        │
        ├─ MemoryService.get_context()
        │
        ▼
  ReActAgent.execute()
        │
        ├─ Tracer.start_trace()
        │
        ▼
  [ReAct Loop]
        │
        ├─ Tool.execute()
        │
        ▼
  AgentResponse
        │
        ├─ MemoryService.record_interaction()
        ├─ MetricsCollector.record_request()
        │
        ▼
  Respuesta al usuario
```

---

Ver `plan/IMPLEMENTACION_REACT_AGENT.md` para historial de migración.
