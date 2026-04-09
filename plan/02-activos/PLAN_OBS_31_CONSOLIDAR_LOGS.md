# Plan: OBS-31 — Consolidar tablas de log y guardar respuesta del agente

> **Estado**: 🔵 Pendiente
> **Última actualización**: 2026-04-08
> **Rama Git**: `feature/obs-31-consolidar-logs`

## Resumen de Progreso

| Fase | Progreso | Estado |
|------|----------|--------|
| Fase 1: Nueva tabla unificada en BD | ░░░░░░░░░░ 0% | ⏳ Pendiente |
| Fase 2: Actualizar ObservabilityRepository | ░░░░░░░░░░ 0% | ⏳ Pendiente |
| Fase 3: Actualizar MemoryRepository | ░░░░░░░░░░ 0% | ⏳ Pendiente |
| Fase 4: Guardar respuesta del agente | ░░░░░░░░░░ 0% | ⏳ Pendiente |
| Fase 5: Actualizar /stats y limpiar código | ░░░░░░░░░░ 0% | ⏳ Pendiente |

**Progreso Total**: ░░░░░░░░░░ 0% (0/20 tareas)

---

## Descripción

Actualmente hay dos tablas que registran el mismo evento (un request del usuario):

- **`BotIAv2_LogOperaciones`** — escrita por `MemoryRepository.save_interaction()`: guarda query, respuesta, error, duración
- **`BotIAv2_TransactionLogs`** — escrita por `ObservabilityRepository.save_transaction()`: guarda tiempos desglosados (memory_ms, react_ms, save_ms), tools usadas, steps

Son dos filas por request con datos solapados. El objetivo es unificarlas en una sola tabla `BotIAv2_InteractionLogs` que contenga todo, y además guardar la **respuesta final del ReAct agent** (actualmente no se persiste).

`BotIAv2_ApplicationLogs` **no se toca** — tiene sentido separada porque captura logs del sistema (WARNING/ERROR de cualquier módulo).

---

## Diseño de la tabla unificada

```sql
BotIAv2_InteractionLogs
├── idLog             bigint IDENTITY PK
├── correlationId     nvarchar(50)       -- trazabilidad entre tablas
├── idUsuario         int FK → Usuarios
├── telegramChatId    bigint
├── telegramUsername  nvarchar(100)
├── comando           nvarchar(100)      -- /ia, /start, etc.
├── query             nvarchar(500)      -- pregunta del usuario
├── respuesta         nvarchar(MAX)      -- respuesta final del agente  ← NUEVO
├── mensajeError      nvarchar(MAX)
├── toolsUsadas       nvarchar(MAX)      -- JSON: ["calculate","datetime"]
├── stepsTomados      int
├── memoryMs          int
├── reactMs           int
├── saveMs            int
├── duracionMs        int                -- total
├── channel           nvarchar(50)       -- telegram, api, etc.
└── fechaEjecucion    datetime DEFAULT GETDATE()
```

---

## Fase 1: Nueva tabla en BD

- [ ] Agregar `BotIAv2_InteractionLogs` al `database/database.sql` con el DDL completo
- [ ] Agregar índices: `correlationId`, `telegramChatId`, `fechaEjecucion`, `idUsuario`
- [ ] Escribir script de migración para mover datos históricos de `LogOperaciones` + `TransactionLogs` a la nueva tabla (best-effort, los campos que coincidan)
- [ ] Marcar `BotIAv2_LogOperaciones` y `BotIAv2_TransactionLogs` como deprecated en el DDL (comentario)

## Fase 2: Actualizar ObservabilityRepository

- [ ] Reemplazar `save_transaction()` para escribir en `BotIAv2_InteractionLogs`
- [ ] Eliminar el INSERT a `BotIAv2_TransactionLogs`
- [ ] Agregar campo `respuesta` al método (recibe la respuesta final del agente)
- [ ] Mantener compatibilidad de firma para no romper el handler

## Fase 3: Actualizar MemoryRepository

- [ ] Eliminar `save_interaction()` (reemplazada por el nuevo método de ObservabilityRepository)
- [ ] Actualizar `get_recent_messages()` para leer de `BotIAv2_InteractionLogs` (campos `query` y `respuesta`)
- [ ] Actualizar `get_user_stats()` para leer de `BotIAv2_InteractionLogs`
- [ ] Actualizar `get_interaction_count()` e `increment_interaction_count()`

## Fase 4: Guardar respuesta del agente

- [ ] Identificar dónde `MainHandler` tiene la respuesta final del agente antes de enviarla a Telegram
- [ ] Pasar esa respuesta al llamado de `save_transaction()` / `ObservabilityRepository`
- [ ] Verificar en BD que `respuesta` se persiste correctamente con texto completo (nvarchar MAX)
- [ ] Validar que no se duplica la escritura (actualmente `save_interaction` + `save_transaction` escriben en paralelo)

## Fase 5: Actualizar /stats y limpiar

- [ ] Actualizar query de `get_user_stats()` apuntando a `BotIAv2_InteractionLogs`
- [ ] Dropear `BotIAv2_LogOperaciones` y `BotIAv2_TransactionLogs` del `database.sql` (o moverlas a sección legacy)
- [ ] Eliminar referencias muertas en `memory_repository.py` y `sql_repository.py`
- [ ] Verificar que `/stats` sigue funcionando correctamente

---

## Archivos afectados

| Archivo | Cambio |
|---------|--------|
| `database/database.sql` | Nueva tabla, script migración, eliminar tablas viejas |
| `src/infra/observability/sql_repository.py` | `save_transaction()` apunta a nueva tabla, recibe `respuesta` |
| `src/domain/memory/memory_repository.py` | Eliminar `save_interaction()`, actualizar queries |
| `src/pipeline/handler.py` | Pasar respuesta final al método de observabilidad |

---

## Notas

- `BotIAv2_ApplicationLogs` no se modifica — captura logs del sistema, no del usuario
- La migración de datos históricos es best-effort: `LogOperaciones` tiene `resultado` (respuesta) y `duracionMs`; `TransactionLogs` tiene los tiempos desglosados. Se pueden unir por `telegramChatId` + `fechaEjecucion` aproximada
- El campo `respuesta` en `InteractionLogs` resuelve el problema de no tener persistida la respuesta del agente para análisis y auditoría
