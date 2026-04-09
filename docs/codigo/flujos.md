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
   └── ReActAgent.execute(query, user_context) → AgentResponse

6. ReActAgent ejecuta loop ReAct (ver sección siguiente)
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
