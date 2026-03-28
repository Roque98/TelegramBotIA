# Estructura del Proyecto

> **Última actualización:** 2026-03-28
> **Estado:** Arquitectura ReAct activa — 9 módulos en `src/`

---

## Árbol de Directorios

```
TelegramBotIA/
│
├── src/                          # Código fuente principal
│   ├── api/                      # Entrypoints REST
│   │   └── chat_endpoint.py      # Flask API con autenticación por token
│   │
│   ├── bot/                      # Entrypoints Telegram
│   │   ├── telegram_bot.py       # TelegramBot (orquestador)
│   │   ├── handlers/
│   │   │   ├── command_handlers.py    # /start, /help, /stats, /cancel
│   │   │   ├── query_handlers.py      # Mensajes de texto → MainHandler
│   │   │   ├── registration_handlers.py # /register, /verify, /resend
│   │   │   └── tools_handlers.py      # /ia, /query → MainHandler
│   │   ├── keyboards/
│   │   │   ├── inline_keyboards.py
│   │   │   └── main_keyboard.py
│   │   └── middleware/
│   │       ├── auth_middleware.py     # Valida usuario por chat_id
│   │       ├── logging_middleware.py  # Registra interacciones
│   │       └── token_middleware.py    # Valida tokens AES (para API REST)
│   │
│   ├── gateway/                  # Normalización multi-canal
│   │   └── message_gateway.py    # MessageGateway: Telegram/API/WS → ConversationEvent
│   │
│   ├── pipeline/                 # Orquestación del flujo principal
│   │   ├── handler.py            # MainHandler: coordina Gateway+Memory+ReAct
│   │   └── factory.py            # HandlerManager + factory functions (DI)
│   │
│   ├── agents/                   # Motor LLM (ReAct)
│   │   ├── base/
│   │   │   ├── agent.py          # BaseAgent, AgentResponse
│   │   │   ├── events.py         # ConversationEvent, UserContext, MemoryEntry
│   │   │   └── exceptions.py     # LLMException, ToolException, etc.
│   │   ├── react/
│   │   │   ├── agent.py          # ReActAgent (loop principal)
│   │   │   ├── prompts.py        # REACT_SYSTEM_PROMPT, REACT_USER_PROMPT
│   │   │   ├── schemas.py        # ReActResponse, ReActStep, ActionType
│   │   │   └── scratchpad.py     # Historial de pasos del loop
│   │   ├── providers/
│   │   │   └── openai_provider.py  # OpenAIProvider (LLMProvider)
│   │   └── tools/
│   │       ├── base.py           # BaseTool, ToolResult, ToolDefinition, ToolCategory
│   │       ├── registry.py       # ToolRegistry (singleton, thread-safe)
│   │       ├── database_tool.py  # database_query — consultas SQL
│   │       ├── knowledge_tool.py # knowledge_search — base de conocimiento
│   │       ├── calculate_tool.py # calculate — expresiones matemáticas
│   │       ├── datetime_tool.py  # get_datetime — fecha/hora actual
│   │       └── preference_tool.py # save_preference — preferencias de usuario
│   │
│   ├── domain/                   # Lógica de negocio pura
│   │   ├── auth/
│   │   │   ├── user_entity.py    # TelegramUser, PermissionResult, Operation
│   │   │   ├── user_repository.py
│   │   │   └── user_service.py   # UserService (registro, verificación, permisos)
│   │   ├── memory/
│   │   │   ├── memory_entity.py  # UserProfile, Interaction, CacheEntry
│   │   │   ├── memory_repository.py
│   │   │   └── memory_service.py # MemoryService (cache LRU + persistencia)
│   │   └── knowledge/
│   │       ├── knowledge_entity.py    # KnowledgeEntry, KnowledgeCategory
│   │       ├── knowledge_repository.py
│   │       └── knowledge_service.py   # KnowledgeService (búsqueda + scoring)
│   │
│   ├── infra/                    # Servicios técnicos de soporte
│   │   ├── database/
│   │   │   ├── connection.py     # DatabaseManager (pool SQL Server)
│   │   │   └── sql_validator.py  # SQLValidator (solo SELECT, anti-injection)
│   │   ├── events/
│   │   │   └── bus.py            # EventBus (comunicación entre componentes)
│   │   └── observability/
│   │       ├── metrics.py        # MetricsCollector (contadores + latencias)
│   │       └── tracing.py        # Tracer, TraceSpan (distributed tracing)
│   │
│   ├── config/
│   │   ├── settings.py           # Settings (Pydantic BaseSettings, desde .env)
│   │   └── personality.py        # BOT_PERSONALITY (nombre, tono, empresa)
│   │
│   └── utils/
│       ├── encryption_util.py    # AES encryption (tokens del API REST)
│       ├── input_validator.py    # Validación de inputs de usuario
│       ├── rate_limiter.py       # Rate limiting por usuario
│       ├── retry.py              # Decorador retry con backoff
│       └── status_message.py     # Mensajes de estado progresivo en Telegram
│
├── tests/
│   ├── agents/         # Tests de ReActAgent, BaseAgent, tools
│   ├── auth/           # Tests de TokenMiddleware, encryption
│   ├── gateway/        # Tests de MessageGateway, MainHandler, factory
│   ├── handlers/       # Tests de tools_handlers
│   ├── memory/         # Tests de MemoryService, MemoryRepository
│   ├── observability/  # Tests de Tracer, MetricsCollector
│   └── utils/          # Tests de retry
│
├── scripts/
│   ├── generar_token.py          # Generar token de prueba para API REST
│   ├── diagnostics/              # Scripts de diagnóstico de BD y configuración
│   └── ...
│
├── examples/
│   ├── ejemplo_chat_api.py       # Ejemplos de uso del API REST
│   └── ejemplo_encryption.py     # Ejemplos de encriptación
│
├── docs/
│   ├── desarrollador/            # Guías para contribuidores
│   ├── futuros-features/         # Roadmap e ideas (pre-sistema plan/)
│   ├── onenote/                  # Snapshots de progreso
│   └── ...                       # Docs de módulos específicos
│
├── plan/                         # Sistema de planificación activo
│   ├── BACKLOG.md                # Lista completa de mejoras
│   ├── 01-completados/           # Planes finalizados
│   ├── 02-activos/               # Planes en progreso
│   └── 03-ideas/                 # Ideas sin plan formal
│
├── database/
│   └── migrations/               # Scripts SQL de estructura
│
├── main.py                       # Punto de entrada (arranca TelegramBot)
├── Pipfile / requirements.txt    # Dependencias
├── .env.example                  # Variables de entorno requeridas
└── CLAUDE.md                     # Instrucciones para Claude Code
```

---

## Variables de Entorno Requeridas

```env
# Telegram
TELEGRAM_BOT_TOKEN=...

# OpenAI
OPENAI_API_KEY=...
OPENAI_MODEL=gpt-4o

# Base de datos (SQL Server)
DB_SERVER=...
DB_DATABASE=...
DB_USERNAME=...
DB_PASSWORD=...

# Encriptación (API REST)
ENCRYPTION_KEY=...

# Opcionales
MEMORY_CACHE_TTL=300
MEMORY_MAX_WORKING=10
```

---

## Puntos de Entrada

| Entrypoint | Comando | Descripción |
|-----------|---------|-------------|
| Bot Telegram | `python main.py` | Arranca el bot en modo polling |
| API REST | `python src/api/chat_endpoint.py` | Arranca servidor Flask en puerto 5000 |

---

## Patrones Clave

| Patrón | Dónde | Para qué |
|--------|-------|----------|
| Singleton | `ToolRegistry` | Registro global de tools |
| Factory + DI | `pipeline/factory.py` | Construir el árbol de dependencias |
| Repository | `domain/*/repository.py` | Acceso a datos desacoplado |
| Strategy | `agents/providers/` | Intercambiar proveedor LLM |
| Gateway | `gateway/message_gateway.py` | Normalizar múltiples canales |
| ReAct Loop | `agents/react/agent.py` | Razonamiento + acción iterativo |
