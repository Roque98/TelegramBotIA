[Docs](../index.md) › [Código](README.md) › Flujos del sistema

# Flujos del sistema

---

## Flujo de un mensaje Telegram

```
1. TelegramBot recibe Update (python-telegram-bot polling)
   └── src/bot/telegram_bot.py

2. AuthMiddleware intercepta ANTES de los handlers
   └── src/bot/middleware/auth_middleware.py
   ├── UserService.get_user_by_chat_id(chat_id) → TelegramUser
   ├── Si no registrado → responde "usá /register" y CORTA
   └── Cachea telegram_user en context.user_data

3. Handler según tipo de mensaje:
   ├── Texto libre → QueryHandler (src/bot/handlers/query_handlers.py)
   └── /ia o /query → tools_handlers.py

4. QueryHandler.handle_text_message(update, context)
   ├── Verifica que usuario está activo
   ├── Verifica permiso cmd:/ia vía UserService
   └── Delega a MainHandler.handle_telegram(update, context)

5. MainHandler._process_event(event)
   └── src/pipeline/handler.py
   ├── MessageGateway.from_telegram() → ConversationEvent
   ├── MemoryService.get_context(user_id) → UserContext
   │   └── Incluye permisos cargados de PermissionService
   └── AgentOrchestrator.execute(query, user_context) → AgentResponse
       └── Expone la misma interfaz que ReActAgent (.execute())

5b. AgentOrchestrator rutea dinámicamente (ver sección siguiente)
    └── src/agents/orchestrator/orchestrator.py

6. ReActAgent seleccionado ejecuta loop ReAct (ver sección Loop ReAct)
   └── src/agents/react/agent.py

7. MainHandler registra observabilidad (no bloqueante)
   ├── ObservabilityRepository.save_interaction_log()
   ├── ObservabilityRepository.save_interaction_steps()
   └── CostRepository.save_cost_session()

8. MemoryService.record_interaction() (async, no bloqueante)
   └── Actualiza working_memory del usuario

9. Respuesta enviada al usuario vía Telegram
   └── Si > 4000 chars: se divide en múltiples mensajes
```

---

## Flujo de orquestación dinámica (ARQ-35)

Cuando `MainHandler` delega al `AgentOrchestrator`, éste selecciona el agente correcto
antes de ejecutar el loop ReAct. `MainHandler` no sabe cuántos agentes existen —
`AgentOrchestrator` expone la misma interfaz `.execute()`.

```
AgentOrchestrator.execute(query, user_context)
└── src/agents/orchestrator/orchestrator.py

1. AgentConfigService.get_active_agents()
   └── Carga definiciones desde BotIAv2_AgenteDef (cache en memoria)
       Campos relevantes: nombre, descripcion, systemPrompt, temperatura,
                          maxIteraciones, esGeneralista, tools

2. IntentClassifier.classify(query, definitions)
   └── src/agents/orchestrator/intent_classifier.py
   ├── Llama a modelo nano (gpt-5.4-mini o similar) con un prompt compacto
   │   que lista los agentes especializados y sus descripciones
   ├── Respuesta esperada: nombre de un agente o "generalista"
   └── ClassifyResult(agent_name, confidence, used_fallback)

3. AgentOrchestrator._resolve(agent_name, definitions)
   ├── Busca la AgentDefinition por nombre exacto
   └── Si no existe → fallback al agente con esGeneralista=1

4. AgentBuilder.build(definition)
   └── src/agents/factory/agent_builder.py
   ├── Cache hit (idAgente, version)? → retorna instancia existente
   └── Cache miss → construye nuevo ReActAgent:
       ├── OpenAIProvider con definition.modeloOverride o openai_loop_model
       ├── temperature = definition.temperatura
       ├── max_iterations = definition.maxIteraciones
       ├── system_prompt_override = definition.systemPrompt
       └── tool_scope = set(definition.tools) [None para generalista]

5. ReActAgent.execute(query, user_context)
   └── Loop Think-Act-Observe con la configuración del agente seleccionado
       (ver sección "El loop ReAct")

6. AgentOrchestrator enriquece AgentResponse:
   ├── response.routed_agent = definition.nombre
   ├── response.classify_ms  = duración del clasificador
   ├── response.agent_confidence = confidence del ClassifyResult
   └── Inyecta step del clasificador en response.data["step_traces"]
```

### Diagrama de componentes

```
MainHandler
    │
    └── AgentOrchestrator.execute(query, context)
            │
            ├── AgentConfigService ──→ BD: BotIAv2_AgenteDef
            │
            ├── IntentClassifier ──→ LLM nano
            │       └── ClassifyResult(agent_name="datos", confidence=0.95)
            │
            ├── _resolve() ──→ AgentDefinition("datos")
            │
            ├── AgentBuilder.build(definition)
            │       └── ReActAgent(system_prompt=..., temp=0.1, tools=["database_query",...])
            │
            └── ReActAgent.execute(query, context)
                    └── AgentResponse (routed_agent="datos")
```

---

## Flujo de un request REST

```
POST /api/chat
└── src/api/chat_endpoint.py

1. TokenMiddleware.validate_token(token)
   ├── Desencripta AES → "numero_empleado:timestamp"
   ├── Verifica TTL (< 3 minutos)
   └── Si inválido → 401 AUTH_FAILED

2. pipeline/factory.py → get_handler_manager().handler
   └── HandlerManager devuelve el MainHandler ya inicializado (singleton)

3. MainHandler.handle_api(user_id, text, session_id, metadata)
   └── Mismo flujo interno desde el paso 5 de Telegram hacia adelante

4. Retorna JSON:
   {"success": true, "response": "...", "numero_empleado": 12345}
```

---

## El loop ReAct

El loop es el corazón del sistema. Implementa el patrón Think-Act-Observe:

```
ReActAgent.execute(query="¿Cuántas ventas hubo ayer?", context=user_context)
│
├─ Construir system_prompt
│   ├── tools_description: lista de tools visibles según permisos del usuario
│   └── usage_hints: instrucciones específicas por tool, también filtradas por permisos
│
├─ Construir user_prompt
│   ├── user_context: preferencias, working_memory, long_term_summary
│   ├── scratchpad: "" (vacío en primer paso)
│   └── query: "¿Cuántas ventas hubo ayer?"
│
├─ ITERACIÓN 1:
│   ├─ LLM genera ReActResponse (JSON):
│   │   {
│   │     "thought": "Necesito consultar la BD para obtener las ventas de ayer",
│   │     "action": "database_query",
│   │     "action_input": {"query": "ventas de ayer"},
│   │     "final_answer": null
│   │   }
│   │
│   ├─ action != "finish" → ejecutar tool
│   ├─ registry.get("database_query").execute(query="ventas de ayer")
│   │   └── ToolResult(success=True, data=[{"count": 45, "total": 127500}])
│   │
│   ├─ scratchpad.add_step(thought, "database_query", observation)
│   └─ build_continue_prompt(observation) → LLM recibe la observación
│
├─ ITERACIÓN 2:
│   ├─ LLM genera:
│   │   {
│   │     "thought": "Ya tengo los datos. Puedo responder.",
│   │     "action": "finish",
│   │     "action_input": {},
│   │     "final_answer": "Ayer se registraron *45 ventas* por $127.500"
│   │   }
│   │
│   └─ action == "finish" → return AgentResponse.success(final_answer)
│
└─ Si se alcanza max_iterations (10):
    └─ synthesize_partial() → LLM genera respuesta parcial con lo acumulado
```

### Flujo de nudge (anti-loop)

A partir del paso 3, si el agente no ha llegado a "finish", se agrega un recordatorio:

```
> Has completado varios pasos. Si ya tenés suficiente información para responder, usá 'finish'.
```

Esto evita que el LLM entre en loops innecesarios.

---

## Flujo de registro de usuario

```
Usuario envía /register
        │
        ▼
RegistrationHandlers.cmd_register()
├── "Por favor ingresá tu número de legajo:"
└── Estado: WAITING_FOR_EMPLOYEE_ID

Usuario envía: "4521"
        │
        ▼
RegistrationHandlers.handle_employee_id()
├── UserService.validate_employee(4521)
│   ├── ❌ No existe → "Número no encontrado. Intentá de nuevo."
│   └── ✅ Existe → crear registro + enviar código de 6 dígitos
└── Estado: END (espera /verify)

Usuario envía /verify 482951
        │
        ▼
RegistrationHandlers.cmd_verify()
├── UserService.verify_code(chat_id, "482951")
│   ├── ❌ Incorrecto o expirado → "Código inválido"
│   └── ✅ Correcto → marcar verificado=1, activar cuenta
└── "¡Bienvenido! Ya podés hacer consultas."
```

---

## Flujo de carga de permisos

Los permisos no se cargan en el momento de auth, sino lazy al construir el `UserContext`:

```
MemoryService.get_context(user_id)
│
├── MemoryRepository.get_profile(user_id) → UserProfile
├── PermissionService.get_all_for_user(user_id)
│   ├── Cache LRU hit? → devuelve inmediatamente
│   └── Cache miss → PermissionRepository.query_permissions()
│       └── JOIN entre BotPermisos, BotRecurso, BotTipoEntidad
│           con resolución de jerarquía (definitivo > permisivo)
│
└── UserContext(
        ...,
        permisos={"tool:database_query": True, "tool:calculate": True, ...},
        permisos_loaded=True
    )
```

El `ToolRegistry` usa `permisos_loaded` para filtrar:
- Si `permisos_loaded=True`: muestra solo tools con `permisos["tool:nombre"] == True`
- Si `permisos_loaded=False`: muestra solo tools marcadas como siempre visibles
  (`reload_permissions`, `finish`)

---

**← Anterior** [Arquitectura](arquitectura.md) · [Índice](README.md) · **Siguiente →** [Agente ReAct](agente-react.md)
