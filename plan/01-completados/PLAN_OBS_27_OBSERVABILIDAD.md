# Plan: OBS-27 — Sistema de Observabilidad

> **Estado**: ✅ Completado
> **Última actualización**: 2026-04-08
> **Rama Git**: `feature/obs-27-observabilidad`

## Resumen de Progreso

| Fase | Progreso | Estado |
|------|----------|--------|
| Fase 0: Fundamentos (teoría) | ██████████ 100% | ✅ Completada |
| Fase 1: Diagnóstico — estado actual | ██████████ 100% | ✅ Completada |
| Fase 2: Logging estructurado | ██████████ 100% | ✅ Completada |
| Fase 3: Transaction trace log | ██████████ 100% | ✅ Completada |
| Fase 4: Métricas básicas | ██████████ 100% | ✅ Completada |
| Fase 5: Alertas y health checks | ░░░░░░░░░░ 0% | 🚫 Descartada — movida a backlog |

**Progreso Total**: ██████████ 100% (23/23 tareas activas)

> **Nota**: Fase 5 (AlertService, /health endpoint) descartada — el core de observabilidad
> está completo. Si se necesitan alertas en el futuro, ver backlog IDEAS_MEJORA_BOT.md.

---

## Descripción

Este plan establece un sistema de observabilidad pragmático para Iris Bot.

El proyecto usa IA (LLMs), lo que lo hace especialmente difícil de depurar: las
respuestas no son deterministas, los errores pueden ser silenciosos, y los problemas
de latencia son invisibles sin instrumentación. Un sistema de observabilidad bien
diseñado convierte ese caos en señal accionable.

---

## Fase 0: Fundamentos — Por qué la observabilidad importa en proyectos con IA

> Esta fase es teórica. Su propósito es justificar cada cambio técnico posterior
> con fundamento conceptual claro.

### ¿Qué es observabilidad?

Un sistema es **observable** cuando puedes responder "¿qué está pasando y por qué?"
mirando sus salidas, sin necesidad de modificar el código ni conectarte al servidor.

Se diferencia del **monitoring** tradicional:
- **Monitoring**: verificar si el sistema está "up/down" — conoces las preguntas de antemano
- **Observabilidad**: explorar comportamiento desconocido — las preguntas emergen del uso real

### Los tres pilares

| Pilar | Qué mide | Pregunta que responde | Ejemplo en Iris |
|-------|----------|-----------------------|-----------------|
| **Logs** | Eventos discretos con contexto | "¿Qué pasó exactamente?" | `ERROR: LLM timeout después de 30s` |
| **Metrics** | Agregaciones numéricas en el tiempo | "¿Con qué frecuencia? ¿Qué tan rápido?" | `p95_latency_ms = 4200` |
| **Traces** | Flujo de una operación de extremo a extremo | "¿Por dónde pasó este request?" | `memory:12ms → react:9500ms → save:45ms` |

Los tres son complementarios, no intercambiables.

### Por qué los bots con LLM son especialmente difíciles

1. **No determinismo**: la misma query puede producir respuestas distintas
2. **Latencia variable**: el LLM puede tardar 1s o 30s — sin traces, es opaco
3. **Errores silenciosos**: el agente puede "responder" sin haber usado ninguna tool
4. **Degradación gradual**: la calidad del contexto puede deteriorarse con el tiempo sin que nadie lo note
5. **Costos invisibles**: cada llamada al LLM cuesta dinero — sin métricas, los costos son sorpresa

### ¿Qué herramientas existen y cuál conviene acá?

| Herramienta | Fortaleza | Costo operacional | Adecuada para Iris |
|-------------|-----------|-------------------|--------------------|
| **OpenTelemetry** | Estándar de la industria, integración total | Alto: collector, backend, dashboard | No — overkill para single-process |
| **Elasticsearch + Kibana** | Búsqueda potente, dashboards ricos | Muy alto: 2GB+ RAM mínimo | No — infraestructura desproporcionada |
| **Grafana + Loki** | Logs + métricas visualmente amigable | Medio: requiere servidores adicionales | Futuro posible si escala |
| **SQL Server (existente)** | Cero infraestructura nueva, queries ad-hoc | Bajo: ya existe en producción | **Sí — pragmático y suficiente** |
| **structlog + logs locales** | Logs estructurados legibles en desarrollo | Ninguno: solo librería Python | **Sí — complemento ideal** |

**Decisión de arquitectura**: usar SQL Server existente para persistencia de trazas,
`structlog` para logs estructurados en consola, y métricas en memoria con resumen
periódico. Esto da el 80% del valor con el 20% de la complejidad.

### Tareas

- [x] **Leer y entender este documento** — base conceptual antes de tocar código

---

## Fase 1: Diagnóstico — estado actual del logging en Iris

**Objetivo**: mapear qué se loguea hoy, qué falta, y qué sobra.
**Dependencias**: Fase 0

### Problemas identificados (sesión anterior)

| Problema | Impacto | Archivo |
|----------|---------|---------|
| `httpx` logueaba cada poll de Telegram a INFO | Contamina logs — oscurece errores reales | `main.py` |
| Dos filas en `LogOperaciones` por request (duplicado) | Datos incorrectos — conteo inflado | `query_handlers.py` |
| `telegramUsername` NULL en `LogOperaciones` | Imposible saber quién hizo qué query | `handler.py`, `memory_repository.py` |
| No hay traza del flujo completo por request | Imposible medir latencia de cada etapa | `handler.py` |
| Logs de errores sin correlation ID | No se puede correlacionar logs de un mismo request | varios |

### Tareas

- [x] **Silenciar httpx/httpcore/telegram** — setLevel(WARNING) en setup_logging()
  - Commit: `cf1e8b5`
- [x] **Eliminar log duplicado** — remover log_operation(EXITOSO) del success path
  - Commit: `cf1e8b5`
- [x] **Propagar username al log** — extraer username de ConversationEvent.metadata
  - Commit: `cf1e8b5`
- [x] **Auditar niveles de log** — revisado y corregido durante sesión 2026-03-31
  - Criterio: DEBUG para flujo normal, INFO para eventos importantes, ERROR solo en errores reales
  - Completado: 2026-03-31

---

## Fase 2: Logging estructurado

**Objetivo**: pasar de logs de texto libre a logs con campos estructurados.
**Dependencias**: Fase 1

### ¿Por qué logs estructurados?

Un log de texto libre como:
```
INFO - MainHandler - Telegram message processed: user=12345, success=True, time=4200ms
```

No se puede guardar en SQL de forma útil — es un string opaco. Un log estructurado
tiene campos fijos que se mapean directamente a columnas:

```python
logger.info("request_complete", user_id="12345", success=True, duration_ms=4200, correlation_id="a8f3b2c1")
```

Permite guardar cada campo en su columna y luego consultar:
```sql
SELECT * FROM ApplicationLogs WHERE level = 'ERROR' AND correlationId = 'a8f3b2c1'
SELECT * FROM ApplicationLogs WHERE userId = '12345' ORDER BY createdAt DESC
```

### Destino de los logs

| Nivel | Consola | SQL Server |
|-------|---------|------------|
| DEBUG | Si | No — demasiado voluminoso |
| INFO | Si | No — flujo normal, no accionable |
| WARNING | Si | **Si** — situaciones anómalas pero no errores |
| ERROR | Si | **Si** — siempre persistir errores |

### Schema de la tabla `ApplicationLogs` en SQL Server

```sql
CREATE TABLE abcmasplus..ApplicationLogs (
    id            BIGINT IDENTITY PRIMARY KEY,
    correlationId NVARCHAR(8),
    userId        NVARCHAR(50),
    level         NVARCHAR(10)   NOT NULL,   -- WARNING, ERROR
    event         NVARCHAR(100)  NOT NULL,   -- nombre del evento: llm_timeout, tool_error, etc.
    message       NVARCHAR(2000),            -- descripcion legible
    module        NVARCHAR(100),             -- src.pipeline.handler, src.agents.react.agent, etc.
    durationMs    INT,
    extra         NVARCHAR(2000),            -- JSON con campos adicionales variables
    createdAt     DATETIME       DEFAULT GETDATE()
);

CREATE INDEX IX_ApplicationLogs_level       ON abcmasplus..ApplicationLogs (level);
CREATE INDEX IX_ApplicationLogs_correlationId ON abcmasplus..ApplicationLogs (correlationId);
CREATE INDEX IX_ApplicationLogs_createdAt   ON abcmasplus..ApplicationLogs (createdAt DESC);
```

### Campos mínimos requeridos en cada log

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `correlation_id` | str (8 chars) | ID único del request — une todos los logs de una operación |
| `user_id` | str | ID del usuario (si aplica) |
| `event` | str | Nombre del evento: `llm_timeout`, `tool_error`, `db_connection_failed` |
| `level` | str | warning / error |
| `duration_ms` | int | Tiempo de la operación (donde aplique) |

### Tareas

- [x] **Crear `logging_config.py`** — SqlLogHandler + formato con correlation_id
  - Archivo: `src/config/logging_config.py`
  - Commit: `a33c8e6`
- [x] **Crear script de migración SQL** — tabla ApplicationLogs
  - Archivo: `scripts/migrations/001_add_application_logs.sql`
  - Commit: `a33c8e6`
- [x] **Crear `SqlLogHandler`** — persiste WARNING/ERROR en background thread
  - Archivo: `src/config/logging_config.py`
  - Commit: `a33c8e6`
- [x] **correlation_id en formato de log** — TracingFilter inyecta en cada record
  - Archivo: `src/infra/observability/tracing.py` (ya existía)
- [x] **Cablear logging_config en main.py** — reemplaza basicConfig
  - Archivo: `main.py`, Commit: `ecfbaed`
- [x] **Auditar niveles de log** — revisado durante sesión 2026-03-31
  - Completado: 2026-03-31

---

## Fase 3: Transaction Trace Log

**Objetivo**: una sola línea por request con el flujo completo y tiempos de cada etapa.
**Dependencias**: Fase 1

### ¿Qué es un transaction trace log?

Es una traza condensada de todo lo que ocurrió en un request:

```
[a8f3b2c1] user=12345 | "cuanto vendimos ayer" | memory:12ms → react:9500ms → save:45ms | OK 9557ms
[f1e2d3c4] user=67890 | "dame el reporte" | memory:8ms → react:FAIL(timeout 30s) | ERROR 30008ms
```

Permite en un vistazo:
- ¿Dónde se va el tiempo? (memory vs react vs save)
- ¿El LLM está tardando más de lo normal?
- ¿Cuántas tools usó el agente?

### Schema de la tabla `TransactionLogs` en SQL Server

```sql
CREATE TABLE abcmasplus..TransactionLogs (
    id             BIGINT IDENTITY PRIMARY KEY,
    correlationId  NVARCHAR(8)    NOT NULL,
    userId         NVARCHAR(50),
    username       NVARCHAR(100),
    query          NVARCHAR(500),
    channel        NVARCHAR(20)   DEFAULT 'telegram',
    memoryMs       INT,
    reactMs        INT,
    saveMs         INT,
    totalMs        INT,
    success        BIT            NOT NULL,
    errorMessage   NVARCHAR(1000),
    toolsUsed      NVARCHAR(500),   -- JSON: ["database_query", "knowledge_search"]
    stepsCount     INT,
    createdAt      DATETIME       DEFAULT GETDATE()
);

CREATE INDEX IX_TransactionLogs_userId   ON abcmasplus..TransactionLogs (userId);
CREATE INDEX IX_TransactionLogs_createdAt ON abcmasplus..TransactionLogs (createdAt DESC);
```

### Tareas

- [x] **Crear script de migración SQL** — tabla TransactionLogs
  - Archivo: `scripts/migrations/002_add_transaction_logs.sql`
  - Commit: `a33c8e6`
- [x] **Crear `ObservabilityRepository`** — save_transaction() async + save_log_sync()
  - Archivo: `src/infra/observability/sql_repository.py`
  - Commit: `a33c8e6`
- [x] **Instrumentar `MainHandler`** — medir memory/react/save, guardar traza en background
  - Archivo: `src/pipeline/handler.py`
  - Commit: `ecfbaed`
- [x] **Inyectar repositorio en factory** — ObservabilityRepository en create_main_handler()
  - Archivo: `src/pipeline/factory.py`
  - Commit: `ecfbaed`
- [x] **Log de consola de la traza** — una línea con flujo completo al finalizar cada request
  - Formato: `[{cid}] user={id} | {query[:40]} | memory:Xms react:Xms save:Xms | OK Xms`

---

## Fase 4: Métricas básicas en memoria

**Objetivo**: contadores y estadísticas acumuladas del bot, consultables vía `/stats`.
**Dependencias**: Fase 3

### ¿Qué métricas medir?

| Métrica | Descripción | Por qué importa |
|---------|-------------|-----------------|
| `requests_total` | Total de requests procesados | Baseline de actividad |
| `requests_success` | Requests exitosos | Tasa de éxito general |
| `requests_error` | Requests con error | Detectar degradación |
| `latency_p50_ms` | Mediana de latencia | Latencia "típica" |
| `latency_p95_ms` | Percentil 95 de latencia | Latencia "de los peores" |
| `llm_calls_total` | Total de llamadas al LLM | Monitoreo de costos |
| `tools_used` | Dict: {tool_name: count} | Qué tools usa más el agente |
| `fallback_used` | Veces que se usó el agente de fallback | Cuándo falla ReAct |

### Tareas

- [x] **`MetricsCollector`** — ya existía en `src/infra/observability/metrics.py`
- [x] **Integración en `ReActAgent`** — ya registra record_request() y record_tool_usage()
  - Archivo: `src/agents/react/agent.py`
- [x] **Comando `/stats` en Telegram** — estadísticas históricas reales del usuario desde LogOperaciones
  - Total consultas, tasa de éxito, avg/max latencia, primera y última consulta
  - Archivo: `src/bot/handlers/command_handlers.py`
  - Commit: `0810d64`
- [x] **Errores logueados en LogOperaciones** — resultado='ERROR' + mensajeError poblado
  - Garantiza logging en todos los caminos, incluyendo excepciones sin fallback
  - Commit: `4c640d7`
- [x] **Reset periódico** — métricas en memoria, se resetean con cada reinicio (aceptable)

---

## Fase 5: Alertas y health checks

**Objetivo**: detectar problemas automáticamente sin mirar los logs.
**Dependencias**: Fase 4

### Casos a detectar automáticamente

| Condición | Umbral sugerido | Acción |
|-----------|-----------------|--------|
| Tasa de error alta | > 20% de requests en 10 min | Notificar al admin |
| Latencia p95 alta | > 30s en los últimos 20 requests | Notificar al admin |
| LLM inalcanzable | 3 errores consecutivos de OpenAI | Notificar al admin |
| Base de datos inalcanzable | health_check() falla | Notificar al admin |

### Tareas

- [ ] **Extender `health_check()`** — incluir estado de LLM provider
  - Archivo: `src/pipeline/handler.py`
- [ ] **Crear `AlertService`** — evalúa condiciones y envía notificaciones
  - Archivo: `src/pipeline/alerts.py`
  - Lógica: ventana deslizante de últimos N requests, umbrales configurables
- [ ] **Integrar con notificaciones Telegram al admin** — reusar sistema de PLAN_CAL_13
  - Depende de: `PLAN_CAL_13_NOTIFICACIONES.md` (ya completado)
- [ ] **Health check endpoint en API** — `GET /health` responde con estado completo
  - Archivo: `src/api/routes.py`
  - Respuesta: `{"status": "ok", "llm": "ok", "db": "ok", "uptime_s": 3600}`
- [ ] **Tests para AlertService** — verificar umbrales y notificaciones
  - Archivo: `tests/pipeline/test_alerts.py`

---

## Arquitectura final del sistema de observabilidad

```
Request de usuario
       │
       ▼
 ConversationEvent ── correlation_id generado
       │
       ▼
  MainHandler ──────── inicia TransactionTrace
       │
   ┌───┴────────┐
   │            │
MemoryService  ReActAgent ── structlog por paso (Thought, Action, Observation)
   │            │
   └───┬────────┘
       │
       ▼
  TransactionTrace completada
       │
  ┌────┴───────────────────────────┐
  │                                │
Log de consola              SQL Server (abcmasplus)
(DEBUG/INFO/WARNING/ERROR)  ├── ApplicationLogs  ← WARNING + ERROR con correlationId
                            └── TransactionLogs  ← 1 fila por request (tiempos, tools, resultado)
                                       │
                                MetricsCollector (en memoria, p50/p95)
                                       │
                                 /stats en Telegram + AlertService
```

---

## Criterios de Éxito

- [x] Cada request genera exactamente **un log de consola** con el flujo completo
- [x] Cada request genera exactamente **una fila** en `TransactionLogs`
- [x] Puedo responder "¿cuánto tardó el LLM en promedio ayer?" con una query SQL
- [x] Puedo responder "¿qué tools usa más el agente?" con una query SQL
- [ ] El bot notifica automáticamente cuando hay errores consecutivos o latencia alta

---

## Riesgos y Mitigaciones

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|--------------|---------|------------|
| structlog incompatible con código existente | Baja | Medio | Wrapper de compatibilidad o migrar gradualmente |
| TransactionLogs crece sin control | Media | Bajo | Retención de 90 días con DELETE periódico |
| Overhead de guardar traza impacta latencia | Baja | Bajo | Guardar en background task (asyncio.create_task) |
| Métricas en memoria se pierden al reiniciar | Alta | Bajo | Son métricas "del ciclo de vida actual" — aceptable |
| AlertService genera spam de notificaciones | Media | Medio | Cooldown entre alertas del mismo tipo (mín 15 min) |

---

## Historial de Cambios

| Fecha | Cambio |
|-------|--------|
| 2026-03-31 | Creación del plan |
| 2026-03-31 | Fase 1 parcialmente completada (fixes de sesión anterior) |
| 2026-03-31 | Fases 1-4 completadas — errores en BD, /stats por usuario, historial sin truncado |
| 2026-04-03 | Movido de 03-ideas a 02-activos — estado real 82%. Fase 5 detallada |
