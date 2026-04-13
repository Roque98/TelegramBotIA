[Docs](../index.md) › [Código](README.md) › Arquitectura

# Arquitectura

El sistema está organizado en 5 capas con dependencias unidireccionales (capas superiores
dependen de inferiores, nunca al revés).

---

## Las 5 capas

```
┌─────────────────────────────────────────────────────────────────┐
│                    CAPA 1: ENTRYPOINTS                          │
│                                                                 │
│  src/api/chat_endpoint.py     → Flask REST API (token AES)     │
│  src/bot/telegram_bot.py      → TelegramBot (arranque)         │
│  src/bot/handlers/            → Handlers de comandos y texto   │
│  src/bot/keyboards/           → Teclados inline y de respuesta │
│  src/bot/middleware/          → auth, logging, token           │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                 CAPA 2: GATEWAY / PIPELINE                      │
│                                                                 │
│  src/gateway/message_gateway.py  → Normaliza Telegram/API/WS   │
│                                     a ConversationEvent        │
│  src/pipeline/handler.py          → MainHandler (orquesta)     │
│  src/pipeline/factory.py          → Composición de dependencias│
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    CAPA 3: AGENTES LLM                          │
│                                                                 │
│  src/agents/orchestrator/      → AgentOrchestrator (ruteo N-   │
│                                  way por intent), Intentclassi-│
│                                  fier (nano LLM → agent name)  │
│  src/agents/factory/           → AgentBuilder (construye y     │
│                                  cachea instancias ReActAgent   │
│                                  desde AgentDefinition en BD)  │
│  src/agents/react/agent.py     → ReActAgent (loop principal)   │
│  src/agents/react/prompts.py   → System/user/continue prompts  │
│  src/agents/react/scratchpad.py→ Historial de pasos del loop   │
│  src/agents/react/schemas.py   → ReActResponse (Pydantic)      │
│  src/agents/providers/         → OpenAIProvider (LLMProvider)  │
│  src/agents/tools/             → ToolRegistry + 10 tools       │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    CAPA 4: DOMINIO                              │
│                                                                 │
│  src/domain/auth/              → UserEntity, UserService,      │
│                                  PermissionService (SEC-01)    │
│  src/domain/memory/            → UserContext, MemoryService    │
│  src/domain/knowledge/         → KnowledgeEntry, KnowledgeSvc  │
│  src/domain/cost/              → CostTracker, CostRepository   │
│  src/domain/alerts/            → AlertEvent, AlertRepository,  │
│                                  AlertPromptBuilder (PRTG)     │
│  src/domain/agent_config/      → AgentDefinition,              │
│                                  AgentConfigRepository,        │
│                                  AgentConfigService            │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                  CAPA 5: INFRAESTRUCTURA                        │
│                                                                 │
│  src/infra/database/           → DatabaseManager, SQLValidator, │
│                                  DatabaseRegistry (multi-conn  │
│                                  lazy por alias desde .env)    │
│  src/infra/observability/      → Tracer, MetricsCollector,      │
│                                  SqlLogHandler                  │
│  src/infra/notifications/      → AdminNotifier (notify_admin   │
│                                  con rate-limiting, admins     │
│                                  desde BD)                     │
│  src/config/                   → Settings (Pydantic), logging  │
│  src/utils/                    → encryption, rate_limiter,     │
│                                  retry, input_validator        │
└─────────────────────────────────────────────────────────────────┘
```

---

## Patrones de diseño

| Patrón | Dónde | Por qué |
|--------|-------|---------|
| **Singleton** | `ToolRegistry`, `HandlerManager` | Una instancia global durante toda la vida del proceso |
| **Factory** | `pipeline/factory.py` | Composición de todas las dependencias en un solo lugar |
| **Strategy** | `agents/providers/` | Permite intercambiar el proveedor LLM sin tocar el agente |
| **Template Method** | `agents/tools/base.py → BaseTool` | Estructura común para todas las tools |
| **Gateway** | `gateway/message_gateway.py` | Normaliza múltiples canales de entrada a un objeto uniforme |
| **Repository** | `domain/*/repository.py` | Acceso a datos desacoplado de la lógica de negocio |
| **Service** | `domain/*/service.py` | Lógica de negocio orquestada sobre repositorios |

---

## Contratos clave

Estos son los tipos que cruzan capas y que todo desarrollador debe conocer.

### `ConversationEvent` — entrada normalizada

```python
# src/agents/base/events.py
class ConversationEvent(BaseModel):
    user_id: str          # Telegram chat_id o numero_empleado como string
    channel: str          # "telegram" | "api" | "websocket"
    text: str             # Consulta del usuario
    correlation_id: str   # UUID único de la interacción
    timestamp: datetime
    metadata: dict        # Datos extra según canal (chat_id, username, etc.)
```

### `UserContext` — contexto del usuario para el agente

```python
# src/agents/base/events.py
class UserContext(BaseModel):
    user_id: str
    display_name: str              # "Ángel" o alias configurado
    roles: list[str]               # Roles del usuario en el sistema
    preferences: dict              # {"alias": "Ángel", "idioma": "español"}
    working_memory: list[MemoryEntry]   # Últimas N interacciones
    long_term_summary: Optional[str]    # Resumen generado por LLM
    permisos: dict[str, bool]      # {"tool:database_query": True, ...}
    permisos_loaded: bool          # False hasta que PermissionService carga
```

### `AgentResponse` — salida del agente

```python
# src/agents/base/agent.py
class AgentResponse(BaseModel):
    success: bool
    message: Optional[str]         # Respuesta para mostrar al usuario
    error: Optional[str]           # Descripción del error si success=False
    agent_name: str                # "ReActAgent"
    agent_type: AgentType          # AgentType.REACT
    execution_time_ms: float
    steps_taken: int               # Pasos del loop ReAct ejecutados
```

### `ToolResult` — salida de una tool

```python
# src/agents/tools/base.py
class ToolResult(BaseModel):
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    execution_time_ms: float = 0.0

    def to_observation(self) -> str:
        """Texto que el agente incluye en el scratchpad."""
```

### `AgentDefinition` — configuración de un agente desde BD

```python
# src/domain/agent_config/agent_config_entity.py
class AgentDefinition(BaseModel):
    id: int
    nombre: str                       # Clave de ruteo del orchestrator
    descripcion: str                  # Descripción para el IntentClassifier
    system_prompt: str                # Prompt inyectado al construir el agente
    modelo_override: Optional[str]    # Modelo específico o None para usar el default
    max_iteraciones: int
    temperatura: float
    es_generalista: bool              # True → agente de fallback, ve todas las tools permitidas
    tools: list[str]                  # Nombres de tools en scope (especialistas)
    version: int                      # Incrementado por trigger al editar el prompt
```

### `AgentOrchestrator` — punto de entrada al sistema de agentes

```python
# src/agents/orchestrator/orchestrator.py
class AgentOrchestrator:
    """
    Expone la misma interfaz que ReActAgent (.execute()) pero rutea
    la consulta al agente especializado correcto usando IntentClassifier.
    MainHandler no sabe cuántos agentes existen.
    """
    async def execute(
        self,
        query: str,
        context: UserContext,
        event_callback: Optional[Callable] = None,
        **kwargs,
    ) -> AgentResponse:
        ...
```

---

## Dependencias entre módulos

```
bot/handlers ──────────────────────────────────────────────► pipeline/handler
                                                                    │
                                                          ┌─────────┴──────────┐
                                                          │                    │
                                                   gateway/               domain/memory/
                                                 message_gateway          memory_service
                                                          │
                                                 agents/orchestrator
                                                  AgentOrchestrator
                                                          │
                                          ┌───────────────┴───────────────┐
                                   IntentClassifier               agents/factory/
                                   (nano LLM)                     AgentBuilder
                                                                          │
                                                                   agents/react/
                                                                      agent
                                                                          │
                                                          ┌───────────────┴───────────┐
                                                   agents/tools/              agents/providers/
                                                    registry                  openai_provider
                                                          │
                                          ┌───────────────┼───────────────┐
                                     infra/database   domain/knowledge   (calculate, datetime)

pipeline/factory ──► agents/orchestrator/AgentOrchestrator
                 ──► agents/factory/AgentBuilder
                 ──► agents/react/agent (construido por AgentBuilder)
                 ──► agents/providers/openai_provider
                 ──► agents/tools/* (registra 10 tools)
                 ──► domain/agent_config/agent_config_service
                 ──► domain/memory/memory_service
                 ──► domain/knowledge/knowledge_service
                 ──► domain/auth/permission_service
                 ──► domain/interaction/interaction_repository
                 ──► infra/notifications/admin_notifier (inyectado como Protocol)
```

---

[Índice](README.md) · **Siguiente →** [Flujos del sistema](flujos.md)
