# Pipeline y factory

El pipeline conecta los entrypoints (Telegram/API) con el agente LLM.
Tiene tres responsabilidades: normalizar la entrada, orquestar el procesamiento,
y construir todas las dependencias al arrancar.

---

## MessageGateway

**Archivo**: `src/gateway/message_gateway.py`

Normaliza entradas de múltiples canales a un único objeto `ConversationEvent`:

```python
# Desde Telegram
event = MessageGateway.from_telegram(
    user_id=str(chat_id),
    text=message_text,
    chat_id=chat_id,
    username=username,
    first_name=first_name,
)

# Desde API REST
event = MessageGateway.from_api(
    user_id=user_id,
    text=text,
    session_id=session_id,
    metadata=metadata,
)
```

Ambos métodos devuelven un `ConversationEvent` con `correlation_id` generado (UUID).
El resto del sistema no distingue entre canales — opera sobre `ConversationEvent`.

---

## MainHandler

**Archivo**: `src/pipeline/handler.py`

Orquesta el flujo completo de procesamiento de una consulta.

```python
class MainHandler:
    def __init__(
        self,
        react_agent: ReActAgent,
        memory_service: MemoryService,
        observability_repo: ObservabilityRepository,
        cost_repository: CostRepository,
    )

    async def handle_telegram(self, update: Update, context) -> str
    async def handle_api(self, user_id, text, session_id, metadata) -> AgentResponse
    async def health_check(self) -> dict
```

### Flujo de `_process_event(event)`

```python
async def _process_event(event: ConversationEvent) -> AgentResponse:
    # 1. Cargar contexto del usuario (memoria + permisos)
    user_context = await memory_service.get_context(event.user_id)

    # 2. Ejecutar el agente
    response = await react_agent.execute(
        query=event.text,
        context=user_context,
        correlation_id=event.correlation_id,
    )

    # 3. Registrar observabilidad (fire and forget)
    asyncio.create_task(observability_repo.save_interaction_log(...))
    asyncio.create_task(observability_repo.save_interaction_steps(...))
    asyncio.create_task(cost_repository.save_cost_session(...))

    # 4. Actualizar memoria (fire and forget)
    asyncio.create_task(memory_service.record_interaction(...))

    return response
```

Los pasos 3 y 4 son `asyncio.create_task()` — no bloquean la respuesta al usuario.

---

## factory.py — Composición de dependencias

**Archivo**: `src/pipeline/factory.py`

Este archivo es el único lugar donde se construyen e inyectan todas las dependencias.
Es la "composición root" del sistema.

### Jerarquía de construcción

```
create_main_handler(db_manager)
│
├── DatabaseManager (si no se recibe uno)
│
├── KnowledgeService(db_manager)
│   └── Carga todos los artículos en memoria al arrancar
│
├── create_permission_service(db_manager)
│   └── PermissionRepository(db_manager)
│
├── create_memory_service(db_manager, permission_service)
│   └── MemoryRepository(db_manager)
│
├── create_react_agent(db_manager, knowledge_manager, memory_service, permission_service)
│   ├── OpenAIProvider(model=loop_model)   ← loop LLM
│   ├── OpenAIProvider(model=data_model)   ← data LLM
│   └── create_tool_registry(...)
│       ├── DatabaseTool(db_manager, data_llm)
│       ├── KnowledgeTool(knowledge_manager)
│       ├── CalculateTool()
│       ├── DateTimeTool()
│       ├── SavePreferenceTool(db_manager, memory_service)
│       ├── SaveMemoryTool(memory_service)
│       ├── ReloadPermissionsTool(permission_service)
│       └── ReadAttachmentTool(bot_token)
│
├── ObservabilityRepository(db_manager)
├── CostRepository(db_manager)
│
└── MainHandler(agent, memory_service, obs_repo, cost_repo)
```

### HandlerManager (singleton)

```python
class HandlerManager:
    """Mantiene el MainHandler inicializado entre requests."""

    def initialize(self, db_manager=None) -> MainHandler:
        if self._handler is None:
            self._handler = create_main_handler(db_manager)
        return self._handler

    @property
    def handler(self) -> Optional[MainHandler]: ...

def get_handler_manager() -> HandlerManager:
    """Punto de acceso global."""
```

`HandlerManager` garantiza que `create_main_handler` se ejecuta una sola vez al arrancar
(durante `TelegramBot.__init__()` o en el primer request del API), y reutiliza el mismo
`MainHandler` para todas las consultas siguientes.

---

## Arranque del sistema

```python
# main.py / telegram_bot.py
bot = TelegramBot()
# TelegramBot.__init__ llama create_main_handler(db_manager)
# → construye todo el grafo de dependencias
# → KnowledgeService carga artículos de BD
# → ReActAgent queda listo para recibir queries
bot.run()  # polling activo
```

```python
# api/chat_endpoint.py
# El handler se inicializa en el primer request o en startup
handler = get_handler_manager().handler
```
