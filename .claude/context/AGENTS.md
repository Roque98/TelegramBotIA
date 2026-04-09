# Agentes LLM

## Arquitectura: Orchestrator N-way Dinámico (ARQ-35)

El sistema usa un `AgentOrchestrator` que carga agentes desde BD y rutea dinámicamente.

```
Query del usuario
        │
        ▼
AgentOrchestrator
  │  1. Carga agentes activos desde BD (cache LRU 5 min)
  │  2. IntentClassifier → nombre del agente
  │  3. AgentBuilder.build(definition) → ReActAgent
  │  4. agent.execute(query, context)
  │  5. response.routed_agent = definition.nombre
        │
        ├─ "datos"        → DataAgent       (database_query, calculate, datetime)
        ├─ "conocimiento" → KnowledgeAgent  (knowledge_search, calculate, datetime)
        ├─ "casual"       → CasualAgent     (save_preference, save_memory, reload_permissions)
        └─ "generalista"  → GeneralistAgent (todos los tools del usuario — fallback)
```

**Definición de agentes**: vive en `BotIAv2_AgenteDef`.  
Cambiar prompt → `UPDATE BotIAv2_AgenteDef SET systemPrompt = ...` → recarga hot con tool `reload_agent_config`.

---

## Componentes del sistema de agentes

### ReActAgent (`src/agents/react/agent.py`)

```python
class ReActAgent(BaseAgent):
    name = "react"

    def __init__(
        self,
        llm: LLMProvider,
        tool_registry: ToolRegistry,
        max_iterations: int = 10,
        temperature: float = 0.1,
        system_prompt_override: Optional[str] = None,  # ARQ-35: prompt desde BD
        tool_scope: Optional[set[str]] = None,         # ARQ-35: scope del agente especialista
    )
```

- `system_prompt_override=None` → usa `REACT_SYSTEM_PROMPT` (comportamiento original).  
- `tool_scope=None` → generalista, sin filtro de scope (solo permisos del usuario).  
- `tool_scope={'database_query', 'calculate'}` → especialista, solo esas tools visibles.

### AgentBuilder (`src/agents/factory/agent_builder.py`)

```python
class AgentBuilder:
    def __init__(self, tool_registry: ToolRegistry, openai_api_key: str)

    def build(self, definition: AgentDefinition) -> ReActAgent:
        """Cache por (idAgente, version). Trigger de BD incrementa version → cache invalida."""

    def clear_instance_cache(self) -> None:
        """Llamado por AgentConfigService.invalidate_cache()."""
```

### AgentOrchestrator (`src/agents/orchestrator/orchestrator.py`)

```python
class AgentOrchestrator:
    def __init__(
        self,
        agent_config_service: AgentConfigService,
        agent_builder: AgentBuilder,
        intent_classifier: IntentClassifier,
    )

    async def execute(query, context, event_callback=None, **kwargs) -> AgentResponse:
        # Misma interfaz que ReActAgent — MainHandler no cambia

    def _resolve(agent_name, definitions) -> AgentDefinition:
        # Fallback a generalista si el nombre no coincide o el classifier falla
```

### IntentClassifier (`src/agents/orchestrator/intent_classifier.py`)

```python
class IntentClassifier:
    async def classify(self, query: str, agents: list[AgentDefinition]) -> str:
        """Retorna el nombre del agente. Fallback = 'generalista'."""
```

El prompt del classifier se construye dinámicamente con las descripciones de los agentes en BD.  
Agregar un agente nuevo actualiza el routing automáticamente sin tocar código.

### AgentConfigService (`src/domain/agent_config/agent_config_service.py`)

```python
class AgentConfigService:
    def get_active_agents(self) -> list[AgentDefinition]:
        """Cache LRU TTL 5 min. Valida placeholders {tools_description} y {usage_hints}."""

    def invalidate_cache(self) -> None:
        """Invalida cache del service + cache de instancias del builder."""

    def set_builder(self, builder: AgentBuilder) -> None:
        """Inyección tardía para evitar dependencia circular en factory.py."""
```

---

## AgentResponse

```python
class AgentResponse(BaseModel):
    success: bool
    message: Optional[str]
    data: Optional[dict]
    error: Optional[str]
    agent_name: str
    execution_time_ms: float
    steps_taken: int = 1
    metadata: dict
    timestamp: datetime
    routed_agent: Optional[str] = None  # ARQ-35: nombre del agente que respondió
```

`routed_agent` es seteado por el orchestrator y persiste en `BotIAv2_InteractionLogs.agenteNombre`.

---

## Flujo de construcción (factory.py)

```python
# 1. Crear ToolRegistry con todas las tools
tool_registry = create_tool_registry(...)

# 2. Crear AgentConfigService + AgentBuilder (inyección tardía)
agent_config_repo = AgentConfigRepository(db)
agent_config_service = AgentConfigService(repository=agent_config_repo)
agent_builder = AgentBuilder(tool_registry=tool_registry, openai_api_key=...)
agent_config_service.set_builder(agent_builder)  # evita dependencia circular

# 3. Crear IntentClassifier
intent_classifier = IntentClassifier(llm=nano_llm)

# 4. Crear Orchestrator
orchestrator = AgentOrchestrator(agent_config_service, agent_builder, intent_classifier)

# 5. Validación de startup
# Falla con RuntimeError si no hay agentes activos o falta el generalista
```

---

## Contratos Base (`src/agents/base/`)

```python
class BaseAgent(ABC):
    name: str
    async def execute(self, query: str, context: UserContext, **kwargs) -> AgentResponse: ...
    async def health_check(self) -> bool: ...
```

---

## Proveedor LLM: OpenAIProvider

**Archivo**: `src/agents/providers/openai_provider.py`

```python
class OpenAIProvider:
    def __init__(self, api_key: str, model: str)
    async def generate_messages(self, messages: list[dict], **kwargs) -> str
```

**Configuración** (`src/config/settings.py`):
```python
openai_api_key: str
openai_loop_model: str = "gpt-5.4-mini"   # ReAct loop + classifier
openai_data_model: str = "gpt-5.4"        # DatabaseTool SQL generation
```

---

## Observabilidad

```python
from src.infra.observability import get_tracer, get_metrics

tracer = get_tracer()
tracer.start_trace(user_id="123", channel="telegram")
result = tracer.end_trace()

metrics = get_metrics()
metrics.record_request(channel="telegram", duration_ms=150.0, steps=2, success=True)
metrics.record_tool_usage("database_query")
```
