# PLAN_OBS_32 — Mejoras al Sistema de Logs

**ID**: OBS-32
**Tipo**: Observabilidad / Calidad de datos
**Rama**: `develop`
**Estado**: En progreso
**Creado**: 2026-04-08

---

## Problema

Análisis de los datos reales en BD reveló 5 defectos en el sistema de logs:

1. **`CostSesiones` sin `correlationId`** — imposible JOIN exacto costo ↔ interacción
2. **`InteractionLogs` sin flag `exitoso`** — hay que inferir éxito con `mensajeError IS NULL`
3. **`InteractionSteps.fechaInicio` incorrecto** — refleja el INSERT en batch al final, no el inicio real del paso
4. **`InteractionLogs` INSERT silencioso** — si el usuario no está en `UsuariosTelegram`, la fila se pierde sin error
5. **`ApplicationLogs.extra` siempre NULL** — el campo existe pero nunca se popula; en errores no hay contexto (traceback, módulo que falló)

---

## Solución

### Fase 1 — DDL (usuario ejecuta en BD)
- `ALTER TABLE BotIAv2_CostSesiones ADD correlationId nvarchar(50) NULL`
- `ALTER TABLE BotIAv2_InteractionLogs ADD exitoso bit NOT NULL DEFAULT 1`
- `ALTER TABLE BotIAv2_InteractionLogs ALTER COLUMN idUsuario int NULL`

### Fase 2 — Python
- `cost_entity.py`: agregar campo `correlation_id: Optional[str]`
- `cost_repository.py`: incluir `correlationId` en INSERT
- `handler.py`: pasar `correlation_id` a `_record_cost()`
- `sql_repository.py`: pasar `exitoso` en `save_interaction()`; cambiar INSERT para que nunca falle silenciosamente; incluir `fechaInicio` en `save_steps()`
- `agent.py`: capturar timestamp real al inicio de cada paso y pasarlo en `step_traces`
- `logging_config.py`: popular `extra` con traceback en `SqlLogHandler.emit()`

---

## Tareas

### Fase 1 — DDL [ 0/3 ]
- [x] Escribir script DDL en `database/database.sql`
- [ ] Usuario ejecuta ALTER TABLE CostSesiones (add correlationId)
- [ ] Usuario ejecuta ALTER TABLE InteractionLogs (add exitoso, nullable idUsuario)

### Fase 2 — Python [ 6/6 ]
- [x] `cost_entity.py` — agregar `correlation_id: Optional[str] = None`
- [x] `cost_repository.py` — incluir `correlationId` en INSERT de `save_session()`
- [x] `handler.py` — pasar `correlation_id` a `_record_cost()` y a `cost_repo.save_session()`
- [x] `sql_repository.py` — fix INSERT silencioso + agregar `exitoso` + `fechaInicio` en steps
- [x] `agent.py` — capturar timestamp real por paso en `step_traces`
- [x] `logging_config.py` — popular `extra` con traceback en `SqlLogHandler`

---

## DDL a ejecutar

```sql
-- Fix 1: correlationId en CostSesiones
IF NOT EXISTS (
    SELECT 1 FROM abcmasplus.INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_NAME = 'BotIAv2_CostSesiones' AND COLUMN_NAME = 'correlationId'
)
BEGIN
    ALTER TABLE abcmasplus..BotIAv2_CostSesiones ADD correlationId nvarchar(50) NULL
    PRINT 'CostSesiones.correlationId agregado'
END

-- Fix 2: exitoso en InteractionLogs
IF NOT EXISTS (
    SELECT 1 FROM abcmasplus.INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_NAME = 'BotIAv2_InteractionLogs' AND COLUMN_NAME = 'exitoso'
)
BEGIN
    ALTER TABLE abcmasplus..BotIAv2_InteractionLogs ADD exitoso bit NOT NULL DEFAULT 1
    PRINT 'InteractionLogs.exitoso agregado'
END

-- Fix 4: idUsuario nullable (para no perder filas de usuarios no registrados)
ALTER TABLE abcmasplus..BotIAv2_InteractionLogs ALTER COLUMN idUsuario int NULL
```
