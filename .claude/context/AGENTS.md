# Agentes LLM

## Agente Principal: ReActAgent

**Archivo**: `src/agents/react/agent.py`
**Estado**: ACTIVO — arquitectura principal del sistema

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

### Flujo de `execute()`

```
1. Iniciar trace (infra/observability)
2. Construir system_prompt con lista de tools disponibles
3. Loop ReAct (máx. max_iterations):
   │
   ├─ THOUGHT: LLM genera ReActResponse (JSON estructurado)
   │   └── ReActResponse {thought, action, action_input, final_answer}
   │
   ├─ Si action == "finish":
   │   └── return AgentResponse.success(final_answer)
   │
   ├─ ACTION: tool_registry.get(action).execute(**action_input)
   │   └── observation = ToolResult
   │
   └─ OBSERVE: scratchpad.add_step(thought, action, observation)
      └── El scratchpad se incluye en el siguiente prompt
   │
4. Si se agota max_iterations → synthesize_partial()
5. Registrar métricas
6. return AgentResponse
```

### Componentes Internos

| Componente | Archivo | Responsabilidad |
|------------|---------|-----------------|
| `ReActAgent` | `react/agent.py` | Orquesta el loop ReAct |
| `Scratchpad` | `react/scratchpad.py` | Historial de pasos del loop |
| `ReActResponse` | `react/schemas.py` | Schema Pydantic de respuesta del LLM |
| `ReActStep` | `react/schemas.py` | Paso individual (thought/action/observation) |
| `REACT_SYSTEM_PROMPT` | `react/prompts.py` | Prompt del sistema (Amber) |

---

## Contratos Base (`src/agents/base/`)

```python
# agent.py
class AgentType(str, Enum):
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

    @classmethod
    def success_response(cls, agent_name, message, execution_time_ms, metadata=None) -> "AgentResponse": ...

    @classmethod
    def error_response(cls, agent_name, error, execution_time_ms) -> "AgentResponse": ...

class BaseAgent(ABC):
    name: str
    agent_type: AgentType

    @abstractmethod
    async def execute(self, query: str, context: UserContext) -> AgentResponse: ...

    async def health_check(self) -> bool: ...
```

```python
# events.py
class ConversationEvent(BaseModel):
    user_id: str
    channel: str           # "telegram" | "api" | "websocket"
    text: str
    correlation_id: str
    timestamp: datetime
    metadata: dict

    @classmethod
    def from_telegram(cls, user_id, text, chat_id, username, first_name) -> "ConversationEvent": ...

    @classmethod
    def from_api(cls, user_id, text, session_id, metadata) -> "ConversationEvent": ...

class UserContext(BaseModel):
    user_id: str
    display_name: str
    roles: list[str]
    preferences: dict
    working_memory: list[MemoryEntry]
    long_term_summary: Optional[str]

class MemoryEntry(BaseModel):
    query: str
    response: str
    timestamp: datetime
    metadata: dict
```

```python
# exceptions.py
class AgentException(Exception): ...
class LLMException(AgentException): ...
class ToolException(AgentException): ...
class MaxIterationsException(AgentException): ...
class AgentTimeoutException(AgentException): ...
```

---

## Proveedor LLM: OpenAIProvider

**Archivo**: `src/agents/providers/openai_provider.py`

```python
class OpenAIProvider(LLMProvider):
    def __init__(self, api_key: str, model: str = "gpt-4o")

    async def generate(
        self,
        messages: list[dict],
        temperature: float = 0.7,
        max_tokens: int = 2000,
        response_format: Optional[dict] = None,
    ) -> str

    async def generate_structured(
        self,
        messages: list[dict],
        schema: Type[T],
        temperature: float = 0.1,
    ) -> T
```

**Configuración** (`src/config/settings.py`):
```python
openai_api_key: str
openai_model: str = "gpt-4o"
```

---

## Integración: MainHandler + ReActAgent

**Archivo**: `src/pipeline/handler.py`

```python
class MainHandler:
    def __init__(
        self,
        react_agent: ReActAgent,
        memory_service: MemoryService,
        fallback_agent: Optional[FallbackAgent] = None,
        use_fallback_on_error: bool = True,
    )

    async def handle_telegram(self, update: Update, context) -> str
    async def handle_api(self, user_id, text, session_id, metadata) -> AgentResponse
    async def health_check(self) -> dict
```

**Flujo interno de `_process_event(event)`**:
```
1. MemoryService.get_context(event.user_id) → UserContext
2. ReActAgent.execute(query=event.text, context=user_context)
3. Si error y fallback_agent → fallback_agent.process_query(query)
4. MemoryService.record_interaction() [async, no bloqueante]
5. return AgentResponse
```

**Construcción** (`src/pipeline/factory.py`):
```python
def create_main_handler(db_manager=None) -> MainHandler:
    """Construye MainHandler con todas las dependencias inyectadas."""
    # OpenAIProvider → ReActAgent (con ToolRegistry completo)
    # MemoryService (con MemoryRepository)
    # KnowledgeService (cargada desde BD)

class HandlerManager:
    """Singleton que mantiene el MainHandler inicializado."""
    def initialize(self, db_manager=None) -> MainHandler: ...

    @property
    def handler(self) -> Optional[MainHandler]: ...

def get_handler_manager() -> HandlerManager: ...
```

---

## Observabilidad

**Archivos**: `src/infra/observability/tracing.py` y `metrics.py`

```python
from src.infra.observability import get_tracer, get_metrics

tracer = get_tracer()
tracer.start_trace(user_id="123", channel="telegram")
with tracer.span("database_query", {"table": "ventas"}):
    pass
result = tracer.end_trace()   # {trace_id, spans, duration_ms}

metrics = get_metrics()
metrics.record_request(channel="telegram", duration_ms=150.0, steps=2, success=True)
metrics.record_tool_usage("database_query")
stats = metrics.get_stats()   # counters + latencias
```
