# Plan: ARQ-29 — Mejoras de Arquitectura inspiradas en Claude Code

> **Estado**: 🟡 En progreso
> **Última actualización**: 2026-04-01
> **Rama Git**: `develop`

## Resumen de Progreso

| Fase | Progreso | Estado |
|------|----------|--------|
| Fase 1: Tool Layer | ██████████ 100% | ✅ Completada |
| Fase 2: Agent Events | ██████████ 100% | ✅ Completada |
| Fase 3: Cost Tracking | ██████████ 100% | ✅ Completada |
| Fase 4: Memory Scopes | ██████████ 100% | ✅ Completada |
| Fase 5: Agent Archetypes | ██████████ 100% | ✅ Completada |
| Fase 6: Hooks y Permisos | ░░░░░░░░░░ 0% | ⏳ Pendiente |
| Fase 7: UX Avanzado | ░░░░░░░░░░ 0% | ⏳ Pendiente |

**Progreso Total**: ███████░░░ 73% (22/30 tareas)

---

## Descripción

Mejoras de arquitectura derivadas del análisis del código fuente de Claude Code v2.1.88.
Organizadas de mayor a menor impacto, priorizando cambios que mejoren calidad, reducción
de costos y experiencia de usuario a corto plazo.

---

## Fase 1: Tool Layer Estandarizado

**Objetivo**: Que todas las tools tengan la misma interfaz con campos estándar
**Dependencias**: Ninguna
**Impacto**: Código más mantenible, permisos por rol, mejor system prompt

### Tareas

- [x] **Definir `BaseTool` con campos estándar**
  - Archivo: `src/agents/tools/base.py`
  - Campos agregados: `is_read_only`, `is_destructive`, `is_concurrency_safe`
  - Método: `check_permissions(user_role)`
  - Commit: `feature/arq-29-tool-layer`

- [x] **Migrar todas las tools existentes a `BaseTool`**
  - Todas las tools en `src/agents/tools/` ya heredan de `BaseTool`
  - `is_read_only` y `is_destructive` definidos en cada una

- [x] **Implementar `get_tools_prompt()`**
  - Cada tool se auto-documenta via `ToolDefinition`
  - El registry agrega las descripciones dinámicamente al system prompt

- [x] **Budget-aware tool prompt**
  - `>= 95%`: solo nombres; `>= 90%`: truncar a 250 chars; default: completo
  - Archivo: `src/agents/tools/registry.py`

- [x] **"BLOCKING REQUIREMENT" en system prompt**
  - Para `database_query`: instrucción explícita en `REACT_SYSTEM_PROMPT`
  - Archivo: `src/agents/react/prompts.py`

### Entregables
- [x] `BaseTool` con campos estándar
- [x] Todas las tools migradas
- [x] System prompt actualizado

---

## Fase 2: Typed Events desde el Agente

**Objetivo**: El generador ReAct emite eventos tipados en lugar de texto crudo
**Dependencias**: Ninguna
**Impacto**: Habilita StatusMessage conectado a fases reales, mejor logging

### Tareas

- [x] **Definir modelos de eventos**
  - Archivo: `src/agents/base/agent_events.py`
  - Eventos: `AgentEventType` enum con 6 tipos, `AgentEvent(BaseModel)`
  - Labels por tool en español con emoji

- [x] **Conectar `ReActAgent` a `event_callback`**
  - Parámetro `event_callback` en `execute()`
  - Emite eventos en: session start, thought, tool call, observation, final answer
  - Archivo: `src/agents/react/agent.py`

- [x] **Conectar `StatusMessage` a eventos reales**
  - `on_agent_event` callback → `status.set_phase(event.status_text)`
  - Muestra fase real del agente en Telegram
  - Archivo: `src/bot/handlers/tools_handlers.py`

- [x] **`set_phase()` en StatusMessage**
  - Cancela el loop de rotación automática y muestra texto real del agente
  - Archivo: `src/utils/status_message.py`

### Entregables
- [x] Modelos de eventos implementados
- [x] `ReActAgent` emitiendo eventos
- [x] `StatusMessage` con fases reales

---

## Fase 3: Cost Tracking por Sesión

**Objetivo**: Registrar tokens y costo USD por conversación y por usuario
**Dependencias**: Fase 1 (BaseTool)
**Impacto**: Control de costos, visibilidad de uso

### Tareas

- [x] **Implementar `CostTracker`**
  - Archivo: `src/domain/cost/cost_tracker.py`
  - Métodos: `add_turn(model, usage)`, `get_summary()`, `primary_model`
  - Precios por modelo: `_MODEL_PRICING` dict

- [x] **`contextvars` para tracking async-safe**
  - `get_current_tracker()`, `set_current_tracker()`, `reset_current_tracker()`
  - Evita contaminación entre requests concurrentes

- [x] **Capturar usage desde OpenAI**
  - `response.usage` capturado en `openai_provider.py` post-llamada
  - Archivo: `src/agents/providers/openai_provider.py`

- [x] **Persistir en tabla `CostSesiones`**
  - `_record_cost()` en pipeline al finalizar cada request
  - Archivo: `src/pipeline/handler.py`

- [x] **Comando `/costo` para admins**
  - Gasto del día por usuario, restringido a `admin_chat_ids`
  - Archivo: `src/bot/handlers/command_handlers.py`

### Entregables
- [x] `CostTracker` implementado
- [x] Persistencia en DB (`CostSesiones`)
- [x] Comando `/costo` operativo

---

## Fase 4: Memory en 3 Scopes

**Objetivo**: Separar claramente los 3 niveles de memoria del agente
**Dependencias**: Ninguna
**Impacto**: Contexto más relevante, preferencias del usuario respetadas

### Tareas

- [x] **Definir los 3 scopes en `UserContext`**
  - `user`: hechos persistentes (nombre, preferencias, historial) — cargado desde DB
  - `conversation`: mensajes recientes del thread actual — `working_memory`
  - `session`: notas temporales del run — `session_notes: list[str]`
  - Archivo: `src/agents/base/events.py`

- [x] **Inyectar memoria como bloques `<memory>` en el prompt**
  - `to_prompt_context()` genera `<memory type="user/conversation/session">`
  - Preferencias del usuario incluidas en bloque `user`
  - Archivo: `src/agents/base/events.py`

- [x] **Tool `save_memory(scope, fact)`**
  - `scope=session`: agrega a `user_context.session_notes`
  - `scope=user`: persiste via `MemoryService.update_summary()`
  - Archivo: `src/agents/tools/save_memory_tool.py`

- [x] **Fix: preferencias guardadas pero no aplicadas**
  - `SavePreferenceTool` actualiza `user_context.preferences` en el request actual
  - Invalida cache de `MemoryService` para el próximo request
  - System prompt actualizado: preferencias tienen prioridad sobre idioma por defecto
  - Commits: `3eff0aa`, `49f111f`

### Entregables
- [x] 3 scopes implementados
- [x] Bloques `<memory>` en system prompt
- [x] Tool `save_memory` registrada y operativa
- [x] Preferencias aplicadas consistentemente

#### Notas de Fase
> Bugfix post-deploy: `to_prompt_context()` omitía el dict `preferences` del prompt, y `SavePreferenceTool` no invalidaba el cache de `MemoryService`. Ambos corregidos en commits `3eff0aa` y `49f111f`.

---

## Fase 5: Agentes Especializados por Rol

**Objetivo**: Usar el modelo más barato posible según la tarea
**Dependencias**: Fase 2 (Typed Events)
**Impacto**: Reducción significativa de costos (estimado 40-60%)

### Modelos (familia gpt-5.4)

| Modelo | Caso de uso | Criterio de selección |
|--------|-------------|----------------------|
| `gpt-5.4-nano` | Clasificación de intent | Siempre — primera llamada barata |
| `gpt-5.4-mini` | Conversación casual, formateo, preferencias | Intent = casual/simple |
| `gpt-5.4` | Queries SQL complejas, síntesis multi-tool | Intent = business_data |

**Lógica de selección:** si el intent classifier detecta que la consulta involucra datos de negocio (ventas, usuarios, reportes), se usa `gpt-5.4`. Para todo lo demás, `gpt-5.4-mini`. El modelo caro solo se activa cuando realmente importa la calidad del SQL generado.

### Tareas

- [x] **Definir arquetipos de agente**
  - `CasualAgent`: conversación y preferencias, usa `gpt-5.4-mini`
  - `DataAgent`: queries SQL + síntesis de datos de negocio, usa `gpt-5.4`
  - Archivo: `src/agents/orchestrator/orchestrator.py`

- [x] **Orquestador con clasificación de intent**
  - `IntentClassifier` (nano): clasifica en `casual` o `business_data`
  - `AgentOrchestrator`: rutea al agente correcto, misma interfaz que `ReActAgent`
  - Archivo: `src/agents/orchestrator/`

- [x] **Configuración de modelos**
  - `openai_intent_model`, `openai_casual_model`, `openai_data_model` en settings
  - `create_orchestrator()` en factory reemplaza `create_react_agent()` en el pipeline

- [x] **Tests del orquestador**
  - 10 tests: IntentClassifier (5) + AgentOrchestrator (5) — todos pasando
  - Archivo: `tests/agents/test_orchestrator.py`

### Entregables
- [x] 2 arquetipos implementados (casual + data)
- [x] Orquestador con tests
- [x] Config de modelos en settings

---

## Fase 6: Hooks de Validación e Integración

**Objetivo**: Callbacks pre/post tool para validaciones de negocio y notificaciones a sistemas externos
**Dependencias**: Fase 1 (BaseTool)
**Impacto**: Validaciones de negocio reutilizables, integración con CRM/ERP

> **Nota**: El control de acceso por rol (deny/allow por rol, bloqueo de tools por permisos) está **delegado a [SEC-01](PLAN_SEC_01_PERMISOS_MIGRATION.md)**. Esta fase cubre hooks para casos que van más allá de permisos: validaciones de negocio y notificaciones a sistemas externos.

### Tareas

- [ ] **`FunctionHook`: callbacks pre-ejecución de tool**
  - Hook puede retornar `False` para bloquear la tool call con un mensaje descriptivo
  - Casos de uso (no cubiertos por SEC-01): validar que el usuario no acceda a registros de otro usuario, checks de integridad de datos antes de escribir
  - Archivo: `src/agents/hooks/function_hook.py`

- [ ] **`HttpHook`: POST a webhook después de una tool**
  - Notificar sistemas externos (CRM, ERP) cuando el agente modifica datos
  - Configurable por nombre de tool
  - Archivo: `src/agents/hooks/http_hook.py`

- [ ] **Integrar hooks con `ToolRegistry.execute()`**
  - Antes de ejecutar: correr pre-hooks registrados para esa tool
  - Después de ejecutar: correr post-hooks
  - Si pre-hook retorna `False`: retornar `ToolResult.error_result` con el mensaje del hook
  - Archivo: `src/agents/tools/registry.py`

### Entregables
- [ ] `FunctionHook` y `HttpHook` con tests
- [ ] Integración en `ToolRegistry` con tests

---

## Fase 7: UX Avanzado

**Objetivo**: Mejorar experiencia del usuario en casos de uso específicos
**Dependencias**: Fase 2 (Typed Events)
**Impacto**: Menor frustración del usuario, soporte para archivos

### Tareas

- [ ] **Auto-backgrounding**
  - Si el agente supera 15s, enviar "Sigo trabajando, esto toma más de lo esperado..."
  - Continuar async y enviar resultado cuando termine
  - Archivo: `src/pipeline/handler.py`

- [ ] **`verificationNudgeNeeded`**
  - Si el agente completa 3+ tool calls sin ninguna verificación, agregar reminder
  - "¿Verificaste el resultado?" en el siguiente mensaje del sistema

- [ ] **Soporte para archivos adjuntos de Telegram**
  - Guardar documento externamente, inyectar `[Archivo: nombre.pdf, 42KB]` en contexto
  - Tool `read_attachment(id)` para que el agente pida el contenido
  - Archivo: `src/bot/handlers/message_handlers.py`

- [ ] **`activeForm` en StatusMessage**
  - Cada tool tiene su propio mensaje de progreso (ej. "Consultando base de datos...")
  - `StatusMessage.set_tool_active(tool_name)` muestra el mensaje del tool activo

### Entregables
- [ ] Auto-backgrounding con tests
- [ ] Soporte básico para archivos
- [ ] StatusMessage con mensajes de tool

---

## Riesgos y Mitigaciones

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|--------------|---------|------------|
| Migración de tools rompe compatibilidad | Media | Alto | Migrar una tool a la vez con tests antes/después |
| Generador async cambia interfaz del pipeline | Alta | Alto | Adapter pattern para mantener interfaz actual mientras se migra |
| Cost tracking agrega latencia | Baja | Medio | Guardar en DB de forma async (fire-and-forget) |
| Arquetipos de agente complican debugging | Media | Medio | Logging exhaustivo del arquetipo usado por request |

---

## Criterios de Éxito

- [x] Todas las tools usan `BaseTool` con campos estándar
- [x] El costo por conversación se registra en DB
- [x] El StatusMessage muestra la fase real del agente
- [x] Preferencias del usuario se aplican consistentemente entre sesiones
- [x] Al menos 2 arquetipos de agente operativos (casual + data con 3 modelos)
- [ ] Los hooks pre/post permiten bloquear tool calls por validaciones de negocio (SEC-01 cubre el bloqueo por rol/permisos)

---

## Historial de Cambios

| Fecha | Cambio | Autor |
|-------|--------|-------|
| 2026-04-01 | Creación del plan | Roque98 |
| 2026-04-01 | Fases 1-3 completadas | Roque98 |
| 2026-04-01 | Fase 4 completada — memory scopes + save_memory tool | Roque98 |
| 2026-04-01 | Fix: preferencias no se aplicaban (cache + prompt) | Roque98 |
| 2026-04-01 | Fase 5: modelos actualizados a familia gpt-5.4 | Roque98 |
| 2026-04-01 | Fase 5 completada — IntentClassifier + AgentOrchestrator | Roque98 |
| 2026-04-02 | Fase 6 actualizada — permisos por rol delegados a SEC-01, hooks acotados a validaciones de negocio e integraciones externas | Roque98 |
