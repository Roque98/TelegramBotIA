# Diagrama de Flujo — Sistema Actual (ReAct)

> **Última actualización:** 2026-03-28
> **Arquitectura:** ReAct Agent (Reasoning + Acting)

---

## Flujo General — Mensaje de Telegram

```
┌─────────────────────────────────────────────────────────────────┐
│                    Usuario en Telegram                           │
│            "¿Cuántas ventas hubo ayer?"                         │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                  AuthMiddleware                                  │
│  - Verifica registro y estado activo (UserService)              │
│  - Cachea TelegramUser en context.user_data                     │
│  - Rechaza usuarios no registrados con mensaje apropiado        │
└────────────────────────────┬────────────────────────────────────┘
                             │ Usuario válido
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│              Handler (QueryHandler / tools_handlers)            │
│  - Extrae texto/comando                                         │
│  - Verifica permiso para el comando via UserService             │
│  - Llama a MainHandler.handle_telegram(update, context)         │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    MainHandler._process_event()                  │
│                                                                  │
│  1. MessageGateway.normalize() → ConversationEvent              │
│  2. MemoryService.get_context(user_id) → UserContext            │
│     ├── Cache hit (TTL=300s) → UserContext inmediato            │
│     └── Cache miss → BD (profile + últimas 10 interacciones)   │
│  3. ReActAgent.execute(query, context) → AgentResponse          │
│  4. MemoryService.record_interaction() [no-bloqueante]          │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
                  [Ver: Loop ReAct abajo]
```

---

## Loop ReAct — ReActAgent.execute()

```
ReActAgent recibe: query="¿Cuántas ventas hubo ayer?", context=UserContext
         │
         ▼
┌─────────────────────────────────────────────────────────────────┐
│  Construir system_prompt:                                       │
│  - Identidad del bot (REACT_SYSTEM_PROMPT)                      │
│  - tools_description (ToolRegistry.get_tools_prompt())          │
│  - user_context (nombre, rol, historial)                        │
└────────────────────────────┬────────────────────────────────────┘
         │
         ▼
┌───────────────────────────────────────────────────────────────────┐
│                    ITERACIÓN DEL LOOP (máx. 10)                   │
│                                                                   │
│  OpenAIProvider.generate_structured(prompt, ReActResponse)        │
│          │                                                        │
│          ▼                                                        │
│  {                                                                │
│    "thought": "Necesito consultar la base de datos",             │
│    "action": "database_query",                                    │
│    "action_input": {"query": "ventas de ayer"},                   │
│    "final_answer": null                                           │
│  }                                                                │
│          │                                                        │
│          ├─ action == "finish" ──────────────────────────────────┼──► AgentResponse
│          │                                                        │
│          └─ action == tool_name                                   │
│                    │                                              │
│                    ▼                                              │
│          ToolRegistry.get(action) → BaseTool                      │
│                    │                                              │
│                    ▼                                              │
│          tool.execute(**action_input) → ToolResult                │
│                    │                                              │
│          scratchpad.add_step(thought, action, observation)        │
│                    │                                              │
│          ──────────┘ (siguiente iteración con scratchpad)         │
└───────────────────────────────────────────────────────────────────┘
```

---

## Flujo DATABASE — Tool database_query

```
action_input: {"query": "ventas de ayer"}
         │
         ▼
DatabaseTool.execute(query="ventas de ayer")
         │
         ├── 1. LLM genera SQL desde lenguaje natural
         │         SELECT COUNT(*) FROM Ventas
         │         WHERE CAST(fecha AS DATE) = CAST(GETDATE()-1 AS DATE)
         │
         ├── 2. SQLValidator.validate(sql)
         │         ✅ Solo SELECT/WITH/EXEC permitido
         │         ❌ INSERT/UPDATE/DELETE bloqueado
         │
         ├── 3. DatabaseManager.execute_query(sql) → [{count: 45}]
         │
         └── 4. LLM formatea → "Ayer se registraron 45 ventas"
                    │
                    ▼
         ToolResult(success=True, observation="Ayer se registraron 45 ventas")
```

---

## Flujo KNOWLEDGE — Tool knowledge_search

```
action_input: {"query": "¿Cómo solicito vacaciones?"}
         │
         ▼
KnowledgeTool.execute(query="¿Cómo solicito vacaciones?")
         │
         ▼
KnowledgeService.search(query)
         │
         ├── Scoring por keywords + prioridad + similitud
         ├── Retorna top N entradas relevantes
         │
         ▼
ToolResult(
    success=True,
    observation="Para solicitar vacaciones debes..."
)
```

---

## Flujo GENERAL — Sin tools (saludos, conversación)

```
query: "Hola, ¿cómo estás?"
         │
         ▼
LLM decide:
{
    "thought": "Es un saludo, respondo directamente",
    "action": "finish",
    "action_input": {},
    "final_answer": "¡Hola! Estoy aquí para ayudarte..."
}
         │
         ▼
AgentResponse(success=True, message="¡Hola! Estoy aquí para ayudarte...")
         │
         ▼
Handler envía respuesta al usuario (split si > 4000 chars)
```

---

## Flujo REST API

```
POST /api/chat
{"token": "<AES encriptado>", "message": "¿Cuántos clientes hay?"}
         │
         ▼
TokenMiddleware
  - Desencripta token AES
  - Verifica timestamp < TTL (3 min)
  - Extrae numero_empleado
         │
         ▼
ChatEndpoint
  - Construye ConversationEvent via MessageGateway.normalize_api()
  - MainHandler._process_event(event) → AgentResponse
         │
         ▼
{"success": true, "response": "...", "numero_empleado": 12345}
```

---

## Componentes Clave

| Componente | Archivo | Responsabilidad |
|-----------|---------|-----------------|
| `TelegramBot` | `src/bot/telegram_bot.py` | Arranque y registro de handlers |
| `AuthMiddleware` | `src/bot/middleware/auth_middleware.py` | Validación de usuarios |
| `MainHandler` | `src/pipeline/handler.py` | Coordinador del flujo principal |
| `MessageGateway` | `src/gateway/message_gateway.py` | Normalización multi-canal |
| `ReActAgent` | `src/agents/react/agent.py` | Motor de razonamiento LLM |
| `ToolRegistry` | `src/agents/tools/registry.py` | Registro de tools disponibles |
| `MemoryService` | `src/domain/memory/memory_service.py` | Contexto y persistencia |
| `UserService` | `src/domain/auth/user_service.py` | Autenticación y permisos |
