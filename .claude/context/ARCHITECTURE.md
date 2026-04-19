# Arquitectura del Sistema

## Estructura de Capas

```
┌─────────────────────────────────────────────────────────────────┐
│                    CAPA 1: ENTRYPOINTS                          │
│                                                                 │
│  src/api/                                                       │
│  └── chat_endpoint.py     → Flask REST API (token auth)        │
│                                                                 │
│  src/bot/                                                       │
│  ├── handlers/            → CommandHandlers, QueryHandler, etc.│
│  ├── keyboards/           → Teclados inline y de respuesta     │
│  ├── middleware/          → auth, logging, token               │
│  └── telegram_bot.py      → TelegramBot (setup + arranque)     │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│               CAPA 2: BOOTSTRAP / GATEWAY / PIPELINE            │
│                                                                 │
│  src/bootstrap/                                                 │
│  ├── factory.py           → Ensamblador principal (create_main_ │
│  │                          handler — Composition Root)         │
│  ├── tool_factory.py      → Catálogo y registro de tools       │
│  ├── service_factory.py   → PermissionService, MemoryService   │
│  └── orchestrator_factory.py → AgentOrchestrator               │
│                                                                 │
│  src/gateway/                                                   │
│  └── message_gateway.py   → Normaliza Telegram/API/WS          │
│                              → ConversationEvent               │
│                                                                 │
│  src/pipeline/                                                  │
│  ├── handler.py           → MainHandler (orquesta el flujo)    │
│  └── handler_manager.py   → Singleton del MainHandler          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    CAPA 3: AGENTES LLM                          │
│                                                                 │
│  src/agents/                                                    │
│  ├── base/                → BaseAgent, AgentResponse,          │
│  │                          ConversationEvent, UserContext      │
│  ├── react/               → ReActAgent, Scratchpad, schemas    │
│  ├── factory/             → AgentBuilder (cache por versión)   │
│  ├── orchestrator/        → AgentOrchestrator, IntentClassifier│
│  ├── providers/           → OpenAIProvider (LLMProvider)       │
│  └── tools/               → BaseTool, ToolRegistry + tools     │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    CAPA 4: DOMINIO                              │
│                                                                 │
│  src/domain/                                                    │
│  ├── auth/                → TelegramUser, UserRepository,      │
│  │                          UserService                        │
│  ├── memory/              → UserProfile, MemoryRepository,     │
│  │                          MemoryService                      │
│  ├── knowledge/           → KnowledgeEntry, KnowledgeRepository│
│  │                          KnowledgeService                   │
│  ├── alerts/              → AlertEntity, AlertRepository,      │
│  │                          AlertPromptBuilder (FEAT-36/37)    │
│  ├── cost/                → CostSession, CostRepository        │
│  ├── interaction/         → InteractionRepository (todo el SQL │
│  │                          de BotIAv2_Interaction/Steps/Logs) │
│  └── notifications/       → AdminNotifier (notify_admin)       │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                  CAPA 5: INFRAESTRUCTURA                        │
│                                                                 │
│  src/infra/                                                     │
│  ├── database/            → DatabaseManager, SQLValidator,      │
│  │                          SchemaIntrospector, DatabaseRegistry│
│  └── observability/       → Tracer, MetricsCollector,          │
│                              SqlLogHandler, logging_config      │
│                                                                 │
│  src/config/              → Settings (Pydantic)                │
│  src/utils/               → encryption, rate_limiter, retry,   │
│                             input_validator, status_message     │
└─────────────────────────────────────────────────────────────────┘
```

---

## Patrones de Diseño

| Patrón | Ubicación | Propósito |
|--------|-----------|-----------|
| **Singleton** | `ToolRegistry` | Una instancia global del registro de herramientas |
| **Composition Root** | `bootstrap/` | Único lugar donde se ensamblan todas las dependencias |
| **Strategy** | `agents/providers/` | Intercambio de proveedor LLM |
| **Template Method** | `agents/tools/base.py` → `BaseTool` | Estructura común para todas las tools |
| **Gateway** | `gateway/message_gateway.py` | Normaliza entrada de múltiples canales |
| **Repository** | `domain/*/repository.py` | Acceso a datos desacoplado del dominio |
| **Service** | `domain/*/service.py` | Lógica de negocio orquestada |

---

## Flujo de una Consulta Telegram

```
1. TelegramBot recibe Update
        │
        ▼
2. bot/middleware/auth_middleware.py
   └── UserService.is_registered() → ¿puede continuar?
        │
        ▼
3. bot/handlers/query_handlers.py (texto libre)
   o   bot/handlers/tools_handlers.py (/ia, /query)
        │
        ▼
4. pipeline/handler.py → MainHandler.handle_telegram(update)
        │
        ├── gateway/message_gateway.py
        │   └── MessageGateway.from_telegram() → ConversationEvent
        │
        ├── domain/memory/memory_service.py
        │   └── MemoryService.get_context(user_id) → UserContext
        │
        ▼
5. agents/react/agent.py → ReActAgent.execute(query, context)
        │
        ├── Loop ReAct (max 10 iter.):
        │   ├── LLM genera ReActResponse (JSON)
        │   ├── Si action == "finish" → retornar respuesta
        │   └── Si action == tool_name → tool.execute(**params)
        │
        ▼ AgentResponse
        │
        └── MemoryService.record_interaction() [async, no bloqueante]
        │
        ▼
6. Respuesta enviada al usuario por Telegram
```

## Flujo de una Request REST

```
POST /api/chat
        │
        ▼
src/api/chat_endpoint.py
        │
        ├── TokenMiddleware.validar_token(token)  ← token encriptado en AES
        │
        ├── pipeline/factory.py → get_handler_manager().handler
        │
        ▼
MainHandler.handle_api(user_id, text, metadata)
        │  (mismo flujo interno que Telegram desde paso 4)
        ▼
{"success": true, "response": "...", "numero_empleado": 12345}
```

---

## Contratos Clave (`src/agents/base/`)

```python
class AgentResponse(BaseModel):
    success: bool
    message: Optional[str]
    error: Optional[str]
    agent_name: str
    agent_type: AgentType          # "react"
    execution_time_ms: float
    steps_taken: int

class UserContext(BaseModel):
    user_id: str
    display_name: str
    roles: list[str]
    preferences: dict
    working_memory: list[MemoryEntry]
    long_term_summary: Optional[str]

class ConversationEvent(BaseModel):
    user_id: str
    channel: str                   # "telegram" | "api" | "websocket"
    text: str
    correlation_id: str
    timestamp: datetime
    metadata: dict
```

---

## Dependencias Entre Módulos

```
bot/handlers → pipeline/handler → gateway/message_gateway
                               → domain/memory/memory_service
                               → agents/react/agent
                                       └── agents/tools/registry
                                               └── infra/database
                                               └── domain/knowledge
                                               └── (calculate, datetime)

bootstrap/factory → pipeline/handler (MainHandler)
                 → bootstrap/tool_factory → agents/tools/*
                 → bootstrap/service_factory → domain/auth, domain/memory
                 → bootstrap/orchestrator_factory → agents/orchestrator
                                                  → agents/factory/AgentBuilder
                 → domain/knowledge/knowledge_service
                 → infra/database/registry
```
