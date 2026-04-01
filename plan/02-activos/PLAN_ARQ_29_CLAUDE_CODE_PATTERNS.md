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
| Fase 4: Memory Scopes | ░░░░░░░░░░ 0% | ⏳ Pendiente |
| Fase 5: Agent Archetypes | ░░░░░░░░░░ 0% | ⏳ Pendiente |
| Fase 6: Hooks y Permisos | ░░░░░░░░░░ 0% | ⏳ Pendiente |
| Fase 7: UX Avanzado | ░░░░░░░░░░ 0% | ⏳ Pendiente |

**Progreso Total**: █████░░░░░ 42% (14/33 tareas)

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

- [ ] **Definir `BaseTool` con campos estándar**
  - Archivo: `src/agents/tools/base_tool.py`
  - Campos: `name`, `description`, `is_read_only`, `is_destructive`, `is_concurrency_safe`
  - Métodos: `call()`, `check_permissions(user_role)`, `get_prompt_fragment()`

- [ ] **Migrar todas las tools existentes a `BaseTool`**
  - Auditar tools en `src/agents/tools/`
  - Agregar `is_read_only` y `is_destructive` a cada una

- [ ] **Implementar `get_prompt_fragment()`**
  - Cada tool auto-documenta su uso en un string corto
  - El system prompt los agrega dinámicamente en lugar de texto hardcodeado

- [ ] **Budget-aware tool prompt**
  - Si el contexto supera el 90% de capacidad, truncar descripciones a 250 chars
  - Fallback a solo nombres si supera el 95%
  - Archivo: `src/agents/tools/tool_registry.py`

- [ ] **"BLOCKING REQUIREMENT" en system prompt**
  - Para tools críticas (consultas de datos), agregar la frase exacta al system prompt
  - Archivo: `src/agents/react/prompts.py`

### Entregables
- [ ] `BaseTool` con tests unitarios
- [ ] Todas las tools migradas
- [ ] System prompt actualizado

---

## Fase 2: Typed Events desde el Agente

**Objetivo**: El generador ReAct emite eventos tipados en lugar de texto crudo
**Dependencias**: Ninguna
**Impacto**: Habilita StatusMessage conectado a fases reales, mejor logging

### Tareas

- [ ] **Definir modelos de eventos**
  - Archivo: `src/agents/base/agent_events.py`
  - Eventos: `SessionStarted`, `ThoughtGenerated`, `ToolCalled`, `ObservationReceived`, `FinalAnswer`, `AgentError`
  - Cada evento con `session_id`, `timestamp`, `metadata`

- [ ] **Convertir `ReActAgent.run()` a generador async**
  - Que yielde eventos tipados en cada paso del loop
  - El pipeline consume el generador y reacciona a cada evento

- [ ] **Conectar `StatusMessage` a eventos reales**
  - Al recibir `ToolCalled`: mostrar "Consultando: `<nombre>`"
  - Al recibir `ThoughtGenerated`: mostrar "Razonando..."
  - Al recibir `FinalAnswer`: llamar `complete()`
  - Archivo: `src/utils/status_message.py`

- [ ] **Logging estructurado por evento**
  - Cada evento tipado se loguea con su metadata
  - Reemplaza logs de texto libre en el agente

### Entregables
- [ ] Modelos de eventos con tests
- [ ] `ReActAgent` como generador async
- [ ] `StatusMessage` con fases reales

---

## Fase 3: Cost Tracking por Sesión

**Objetivo**: Registrar tokens y costo USD por conversación y por usuario
**Dependencias**: Fase 1 (BaseTool)
**Impacto**: Control de costos, límites por usuario, visibilidad de uso

### Tareas

- [ ] **Definir modelo `SessionCost`**
  - Archivo: `src/domain/cost/cost_entity.py`
  - Campos: `session_id`, `user_id`, `model`, `input_tokens`, `output_tokens`, `cache_read_tokens`, `cache_write_tokens`, `cost_usd`, `duration_ms`

- [ ] **Implementar `CostTracker`**
  - Archivo: `src/domain/cost/cost_tracker.py`
  - Método `add_turn(response_usage)` llamado después de cada API call
  - Método `get_total()` devuelve costo acumulado del run

- [ ] **Persistir en SQL Server**
  - Tabla `CostSesiones` o columna en `LogOperaciones`
  - Agregar tokens y costo a cada registro existente

- [ ] **Límite de presupuesto por usuario**
  - Antes de cada iteración del loop ReAct, verificar `total_cost < user_limit`
  - Si se supera: terminar con mensaje informativo al usuario

- [ ] **Comando `/costo` para admins**
  - Mostrar gasto total del día/mes por usuario
  - Archivo: `src/bot/handlers/command_handlers.py`

### Entregables
- [ ] `CostTracker` con tests
- [ ] Persistencia en DB
- [ ] Límites por usuario funcionales

---

## Fase 4: Memory en 3 Scopes

**Objetivo**: Separar claramente los 3 niveles de memoria del agente
**Dependencias**: Ninguna (mejora del sistema actual)
**Impacto**: Contexto más relevante, menos tokens gastados en memoria irrelevante

### Tareas

- [ ] **Definir los 3 scopes**
  - `UserMemory`: hechos del usuario, persistente entre conversaciones (ya existe en DB)
  - `ConversationMemory`: hechos del thread actual, persiste mientras la conversación está activa
  - `SessionMemory`: notas temporales del run actual, se borran al terminar el run
  - Archivo: `src/domain/memory/memory_scopes.py`

- [ ] **Actualizar `MemoryService` para manejar scopes**
  - `get_context()` carga los 3 scopes y los mergea
  - Cada scope tiene TTL independiente
  - Archivo: `src/domain/memory/memory_service.py`

- [ ] **Inyectar memoria como bloque `<memory>` en system prompt**
  - Separar claramente qué viene de cada scope
  - Formato: `<memory type="user">...</memory>` etc.
  - Archivo: `src/agents/react/prompts.py`

- [ ] **Tool `save_memory(scope, fact)`**
  - Permite al agente guardar hechos importantes en el scope correcto
  - Solo `user` y `conversation` son persistentes

### Entregables
- [ ] 3 scopes implementados con tests
- [ ] System prompt con bloques `<memory>`
- [ ] Tool de escritura de memoria

---

## Fase 5: Agentes Especializados por Rol

**Objetivo**: Usar el modelo más barato posible según la tarea
**Dependencias**: Fase 2 (Typed Events)
**Impacto**: Reducción significativa de costos (estimado 40-60%)

### Tareas

- [ ] **Definir arquetipos de agente**
  - `ExploreAgent`: solo tools de lectura, usa modelo barato (gpt-4o-mini)
  - `DataAgent`: solo queries SQL, usa modelo barato
  - `SynthesisAgent`: respuesta final al usuario, usa modelo capaz (gpt-4o)
  - Archivo: `src/agents/archetypes/`

- [ ] **Orquestador que asigna arquetipos por tarea**
  - Detectar si la consulta requiere solo lectura o escritura
  - Asignar arquetipo apropiado
  - Archivo: `src/agents/orchestrator.py`

- [ ] **Configuración de modelo por arquetipo**
  - `EXPLORE_MODEL`, `DATA_MODEL`, `SYNTHESIS_MODEL` en config
  - Permite cambiar modelos sin tocar código

- [ ] **Tests de integración por arquetipo**
  - Verificar que cada arquetipo use el modelo correcto
  - Verificar que las tools restringidas no estén disponibles

### Entregables
- [ ] 3 arquetipos implementados
- [ ] Orquestador con tests
- [ ] Config de modelos documentada

---

## Fase 6: Hooks y Permisos por Rol

**Objetivo**: Sistema de hooks pre/post tool y permisos basados en rol de usuario
**Dependencias**: Fase 1 (BaseTool)
**Impacto**: Seguridad mejorada, integraciones con sistemas externos

### Tareas

- [ ] **`FunctionHook`: callbacks pre-ejecución de tool**
  - Hook puede retornar `False` para bloquear la tool call
  - Caso de uso: bloquear escritura a registros de otro usuario
  - Archivo: `src/agents/hooks/function_hook.py`

- [ ] **`HttpHook`: POST a webhook después de una tool**
  - Notificar sistemas externos (CRM, ERP) cuando el agente modifica datos
  - Configurable por tipo de tool y rol de usuario
  - Archivo: `src/agents/hooks/http_hook.py`

- [ ] **Deny/allow rules con prefix matching**
  - `allow: ["get_*", "list_*"]` + `deny: ["delete_*"]` por rol
  - Parsear desde config o DB
  - Archivo: `src/agents/permissions/permission_rules.py`

- [ ] **Integrar hooks con `BaseTool.call()`**
  - Antes de ejecutar: correr pre-hooks
  - Después de ejecutar: correr post-hooks
  - Si pre-hook bloquea: retornar error descriptivo al agente

### Entregables
- [ ] `FunctionHook` y `HttpHook` con tests
- [ ] Permission rules con tests
- [ ] Integración en BaseTool

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

- [ ] Todas las tools usan `BaseTool` con campos estándar
- [ ] El costo por conversación se registra en DB
- [ ] El StatusMessage muestra la fase real del agente
- [ ] Al menos 2 arquetipos de agente operativos (Explore + Synthesis)
- [ ] Los hooks pre/post permiten bloquear tool calls por rol

---

## Historial de Cambios

| Fecha | Cambio | Autor |
|-------|--------|-------|
| 2026-04-01 | Creación del plan | Roque98 |
