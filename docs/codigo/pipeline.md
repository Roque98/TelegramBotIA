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
        react_agent: Any,  # AgentOrchestrator (o ReActAgent) — ambos exponen .execute()
        memory_service: MemoryService,
        observability_repo: InteractionRepository,  # src/domain/interaction/
        cost_repository: CostRepository,
    )

    async def handle_telegram(self, update: Update, context) -> str
    async def handle_api(self, user_id, text, session_id, metadata) -> AgentResponse
    async def health_check(self) -> dict
```

`MainHandler` recibe el `AgentOrchestrator` como `react_agent`. Ambos exponen la misma interfaz `.execute(query, context, event_callback)`, por lo que el handler no necesita conocer cuántos agentes existen ni cuál fue seleccionado. El campo `response.routed_agent` refleja el nombre del agente que respondió efectivamente.

### Flujo de `_process_event(event)`

```python
async def _process_event(event: ConversationEvent) -> AgentResponse:
    # 1. Cargar contexto del usuario (memoria + permisos)
    user_context = await memory_service.get_context(event.user_id)

    # 2. Delegar al AgentOrchestrator (clasifica intent → selecciona agente → ejecuta)
    response = await react_agent.execute(
        query=event.text,
        context=user_context,
        event_callback=event_callback,
    )

    # 3. Registrar observabilidad (fire and forget)
    asyncio.create_task(_save_interaction(event, response, ...))
    #   → save_interaction, save_steps, save_agent_routing, increment_interaction_count

    # 4. Persistir costo si está disponible (fire and forget)
    asyncio.create_task(_record_cost(event.user_id, cost, ...))

    return response
```

Los pasos 3 y 4 son `asyncio.create_task()` — no bloquean la respuesta al usuario.

---

## factory.py — Composición de dependencias

**Archivo**: `src/pipeline/factory.py`

Este archivo es el único lugar donde se construyen e inyectan todas las dependencias.
Es la "composición root" del sistema.

### `_build_tool_catalog()`

Construye el catálogo completo de tools disponibles como un `dict[str, Callable]`. Cada entrada es una **lambda** que instancia la tool solo cuando es necesario. La clave coincide con el sufijo del campo `recurso` en `BotIAv2_Recurso` (formato `tool:<clave>`).

```python
def _build_tool_catalog(
    db_manager, knowledge_manager, memory_service,
    permission_service, agent_config_service, data_llm,
    db_registry, bot_token,
) -> dict[str, Any]:
    return {
        "database_query":      lambda: DatabaseTool(db_manager=db_source, llm_provider=data_llm),
        "knowledge_search":    lambda: KnowledgeTool(knowledge_manager=knowledge_manager),
        "calculate":           lambda: CalculateTool(),
        "datetime":            lambda: DateTimeTool(),
        "save_preference":     lambda: SavePreferenceTool(db_manager, memory_service),
        "save_memory":         lambda: SaveMemoryTool(memory_service),
        "reload_permissions":  lambda: ReloadPermissionsTool(permission_service),
        "reload_agent_config": lambda: ReloadAgentConfigTool(agent_config_service),
        "read_attachment":     lambda: ReadAttachmentTool(bot_token),
        "alert_analysis":      lambda: AlertAnalysisTool(
                                   repo=AlertRepository(db_registry.get("monitoreo")),
                                   llm=data_llm,
                               ),
    }
```

`create_tool_registry()` consulta `BotIAv2_Recurso` para obtener las tools activas en el proyecto y solo instancia las que corresponden. Si la BD no está disponible en el arranque, registra el catálogo completo como fallback.

### `create_agent_orchestrator()`

Crea el orquestador dinámico N-way (ARQ-35). Maneja la inyección tardía de `AgentBuilder` en `AgentConfigService` para evitar dependencia circular:

```python
def create_agent_orchestrator(
    db_manager: Any,
    tool_registry: ToolRegistry,
    data_llm: Any,
) -> tuple[AgentOrchestrator, AgentConfigService]:

    # 1. Capa de dominio
    agent_config_repo    = AgentConfigRepository(db_manager=db_manager)
    agent_config_service = AgentConfigService(repository=agent_config_repo)

    # 2. Builder (sin service aún — evita dependencia circular)
    agent_builder = AgentBuilder(tool_registry=tool_registry, openai_api_key=...)

    # 3. Inyección tardía: service puede limpiar cache del builder al invalidar
    agent_config_service.set_builder(agent_builder)

    # 4. Classifier usa el modelo más barato (loop_model)
    nano_llm = OpenAIProvider(model=settings.openai_loop_model)
    intent_classifier = IntentClassifier(llm=nano_llm)

    # 5. Orquestrador
    orchestrator = AgentOrchestrator(agent_config_service, agent_builder, intent_classifier)

    # 6. Validación de startup — falla rápido si no hay agentes o falta el generalista
    agents = agent_config_service.get_active_agents()
    # raises RuntimeError si agents está vacío o no hay esGeneralista=1

    return orchestrator, agent_config_service
```

### Jerarquía de construcción

```
create_main_handler(db_manager)
│
├── DatabaseManager (si no se recibe uno)
├── DatabaseRegistry.from_settings()          ← multi-BD (DB-37)
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
├── OpenAIProvider(model=data_model)           ← data LLM compartido
│
├── create_tool_registry(db_manager, ..., db_registry=db_registry)
│   ├── _build_tool_catalog(...)               ← lambdas de todas las tools
│   ├── consulta BotIAv2_Recurso → active_tool_names
│   ├── DatabaseTool(db_registry, data_llm)
│   ├── KnowledgeTool(knowledge_manager)
│   ├── CalculateTool(), DateTimeTool()
│   ├── SavePreferenceTool, SaveMemoryTool
│   ├── ReloadPermissionsTool(permission_service)
│   ├── ReloadAgentConfigTool(agent_config_service)  ← inyectado después
│   ├── ReadAttachmentTool(bot_token)
│   └── AlertAnalysisTool(AlertRepository, data_llm)
│
├── create_agent_orchestrator(db_manager, tool_registry, data_llm)
│   ├── AgentConfigRepository(db_manager)
│   ├── AgentConfigService(repo, ttl=300)      ← cache LRU 5 min
│   ├── AgentBuilder(tool_registry, api_key)   ← cache por (id, version)
│   ├── agent_config_service.set_builder(...)  ← inyección tardía
│   ├── IntentClassifier(nano_llm)
│   └── AgentOrchestrator(service, builder, classifier)
│
├── ObservabilityRepository(db_manager)
├── CostRepository(db_manager)
│
└── MainHandler(react_agent=orchestrator, memory_service, obs_repo, cost_repo)
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

---

**← Anterior** [Sistema de tools](tools.md) · [Índice](README.md) · **Siguiente →** [Dominio](dominio.md)
