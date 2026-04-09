# Plan: OBS-31 — Consolidar logs + trazabilidad de pasos del agente

> **Estado**: 🟡 En progreso
> **Última actualización**: 2026-04-08
> **Rama Git**: `feature/obs-31-consolidar-logs`

## Resumen de Progreso

| Fase | Progreso | Estado |
|------|----------|--------|
| Fase 1: InteractionLogs (tabla unificada) | ██████████ 100% | ✅ Completada |
| Fase 2: ObservabilityRepository | ██████████ 100% | ✅ Completada |
| Fase 3: MemoryRepository | ██████████ 100% | ✅ Completada |
| Fase 4: Guardar respuesta del agente | ██████████ 100% | ✅ Completada |
| Fase 5: Limpiar código legacy | ██████████ 100% | ✅ Completada |
| Fase 6: InteractionSteps (trazabilidad por paso) | ░░░░░░░░░░ 0% | ⏳ Pendiente |

**Progreso Total**: ████████░░ 75% (20/27 tareas)

---

## Descripción

`BotIAv2_InteractionLogs` reemplazó a `LogOperaciones` + `TransactionLogs`:
una fila por request con query, respuesta, tiempos desglosados, tools y correlationId.

La Fase 6 agrega `BotIAv2_InteractionSteps`: una fila por **paso** del loop ReAct,
que permite reconstruir el trace completo de un request: qué prompt se envió,
qué respondió el LLM, qué tool se llamó con qué parámetros, cuánto tardó cada uno.

---

## Diseño de BotIAv2_InteractionSteps

```sql
BotIAv2_InteractionSteps
├── idStep        bigint IDENTITY PK
├── correlationId nvarchar(50)   -- FK a InteractionLogs
├── stepNum       int            -- orden: 1, 2, 3...
├── tipo          nvarchar(20)   -- 'llm_call' | 'tool_call'
├── nombre        nvarchar(100)  -- modelo (gpt-5-mini) o tool (calculate)
├── entrada       nvarchar(MAX)  -- prompt enviado al LLM / params de la tool (JSON)
├── salida        nvarchar(MAX)  -- respuesta raw del LLM / resultado de la tool
├── tokensIn      int NULL       -- solo llm_call
├── tokensOut     int NULL       -- solo llm_call
├── duracionMs    int
└── fechaInicio   datetime DEFAULT GETDATE()
```

**Reconstrucción de un request completo:**
```sql
SELECT s.stepNum, s.tipo, s.nombre, s.entrada, s.salida,
       s.tokensIn, s.tokensOut, s.duracionMs
FROM BotIAv2_InteractionSteps s
WHERE s.correlationId = 'abc123'
ORDER BY s.stepNum
```

---

## Fase 6: InteractionSteps

### BD
- [ ] Agregar `BotIAv2_InteractionSteps` al `database/database.sql`
- [ ] Índices: `correlationId`, `fechaInicio`

### ReActAgent (`src/agents/react/agent.py`)
- [ ] En `execute()`: mantener lista `step_traces` durante el loop
- [ ] Instrumentar llamada LLM: capturar `entrada` (user_prompt), `salida` (response_text raw),
      tokens del `cost_tracker`, duración
- [ ] Instrumentar tool call: capturar `entrada` (action_input JSON), `salida` (observation),
      duración
- [ ] Incluir `step_traces` en `response.data["step_traces"]`

### ObservabilityRepository (`src/infra/observability/sql_repository.py`)
- [ ] Agregar `save_steps(correlation_id, steps)` que inserta en batch en `InteractionSteps`

### MainHandler (`src/pipeline/handler.py`)
- [ ] En `_save_interaction()`: leer `step_traces` de `response.data` y llamar `save_steps()`

---

## Archivos afectados (Fase 6)

| Archivo | Cambio |
|---------|--------|
| `database/database.sql` | Nueva tabla BotIAv2_InteractionSteps |
| `src/agents/react/agent.py` | Instrumentar loop para capturar step_traces |
| `src/infra/observability/sql_repository.py` | Agregar save_steps() |
| `src/pipeline/handler.py` | Llamar save_steps() con step_traces |

---

## Notas

- `entrada` y `salida` truncadas a 4000 chars para evitar filas gigantes
- Para llm_call: `entrada` = último user_prompt (no el system prompt — es estático)
- Los tokens se leen del `cost_tracker.turns[-1]` justo después del LLM call
- `BotIAv2_ApplicationLogs` no se modifica
