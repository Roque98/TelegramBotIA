# Plan: OBS-27 — Sistema de Observabilidad

> **Estado**: 🟡 En progreso
> **Última actualización**: 2026-03-31
> **Rama Git**: `feature/obs-27-observabilidad`

## Resumen de Progreso

| Fase | Progreso | Estado |
|------|----------|--------|
| Fase 0: Fundamentos (teoría) | ░░░░░░░░░░ 0% | ⏳ Pendiente |
| Fase 1: Diagnóstico — estado actual | ░░░░░░░░░░ 0% | ⏳ Pendiente |
| Fase 2: Logging estructurado | ░░░░░░░░░░ 0% | ⏳ Pendiente |
| Fase 3: Transaction trace log | ░░░░░░░░░░ 0% | ⏳ Pendiente |
| Fase 4: Métricas básicas | ░░░░░░░░░░ 0% | ⏳ Pendiente |
| Fase 5: Alertas y health checks | ░░░░░░░░░░ 0% | ⏳ Pendiente |

**Progreso Total**: ░░░░░░░░░░ 0% (0/28 tareas)

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

- [ ] **Leer y entender este documento** — base conceptual antes de tocar código

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
  - Archivo: `main.py`
  - Commit: `cf1e8b5`
- [x] **Eliminar log duplicado** — remover log_operation(EXITOSO) del success path
  - Archivo: `src/bot/handlers/query_handlers.py`
  - Commit: `cf1e8b5`
- [x] **Propagar username al log** — extraer username de ConversationEvent.metadata
  - Archivo: `src/pipeline/handler.py`, `src/domain/memory/memory_repository.py`
  - Commit: `cf1e8b5`
- [ ] **Auditar niveles de log** — revisar todos los `logger.info/debug/error` en src/
  - Criterio: DEBUG para flujo normal, INFO para eventos importantes, ERROR solo en errores reales
  - Archivos: todos los módulos en `src/`

---

## Fase 2: Logging estructurado

**Objetivo**: pasar de logs de texto libre a logs con campos estructurados.
**Dependencias**: Fase 1

### ¿Por qué logs estructurados?

Un log de texto libre como:
```
INFO - MainHandler - Telegram message processed: user=12345, success=True, time=4200ms
```

No se puede filtrar ni agregar. Un log estructurado:
```json
{"level": "info", "event": "request_complete", "user_id": "12345", "success": true, "duration_ms": 4200, "correlation_id": "a8f3b2c1"}
```

Permite consultas como: `WHERE duration_ms > 5000 AND success = false`.

### Campos mínimos requeridos en cada log

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `correlation_id` | str (8 chars) | ID único del request — une todos los logs de una operación |
| `user_id` | str | ID del usuario |
| `event` | str | Nombre del evento: `request_start`, `llm_call`, `tool_use`, `request_complete` |
| `duration_ms` | int | Tiempo de la operación (donde aplique) |
| `level` | str | debug / info / warning / error |

### Tareas

- [ ] **Agregar `structlog`** — instalar y configurar como reemplazo de logging stdlib
  - Archivo: `requirements.txt` o `Pipfile`
  - Configurar en: `src/config/logging_config.py` (nuevo)
- [ ] **Agregar correlation_id al ConversationEvent** — ya existe, verificar que se propaga
  - Archivo: `src/agents/base/events.py`
- [ ] **Crear contexto de log por request** — bind correlation_id al inicio de cada request
  - Archivo: `src/pipeline/handler.py`
- [ ] **Migrar logs críticos a structlog** — al menos handler.py, react agent, memory service
  - Archivos: `src/pipeline/handler.py`, `src/agents/react/agent.py`, `src/domain/memory/memory_service.py`

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

- [ ] **Crear script de migración SQL** — crear tabla TransactionLogs
  - Archivo: `scripts/migrations/add_transaction_logs.sql`
- [ ] **Crear dataclass `TransactionTrace`** — objeto que acumula los tiempos durante un request
  - Archivo: `src/pipeline/transaction_trace.py`
- [ ] **Instrumentar `MainHandler`** — iniciar y completar la traza en cada request
  - Archivo: `src/pipeline/handler.py`
- [ ] **Guardar traza en SQL Server** — extender `MemoryRepository` con `save_transaction()`
  - Archivo: `src/domain/memory/memory_repository.py`
- [ ] **Log de consola de la traza** — imprimir la línea resumida al completar el request
  - Formato: `[{correlation_id}] user={user_id} | {query[:40]} | memory:{mem}ms → react:{react}ms | {status} {total}ms`

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

### Diferencia entre p50 y p95

- **p50 (mediana)**: la mitad de los requests terminan en este tiempo o menos.
  Si p50 = 2s, la experiencia "normal" es 2s.
- **p95**: el 95% de los requests termina en este tiempo o menos.
  Si p95 = 15s, 1 de cada 20 usuarios espera 15s — eso es un problema aunque p50 sea bueno.

Los LLMs típicamente tienen p95 muy alto (timeouts, llamadas costosas). Medirlo permite
detectar si el p95 sube con el tiempo (degradación gradual).

### Tareas

- [ ] **Crear `MetricsCollector`** — clase singleton con contadores y histograma de latencias
  - Archivo: `src/pipeline/metrics.py`
- [ ] **Integrar en `MainHandler`** — registrar cada request al completarse
  - Archivo: `src/pipeline/handler.py`
- [ ] **Exponer vía health_check** — agregar métricas al response de `health_check()`
  - Archivo: `src/pipeline/handler.py`
- [ ] **Comando `/stats` en Telegram** — mostrar métricas al admin del bot
  - Archivo: `src/bot/handlers/admin_handlers.py`
- [ ] **Reset periódico** — limpiar contadores cada 24h para métricas "del día"

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
- [ ] **Integrar con notificaciones Telegram al admin** — reusar sistema de PLAN_CAL_13
  - Depende de: `PLAN_CAL_13_NOTIFICACIONES.md`
- [ ] **Health check endpoint en API** — `/health` responde con estado completo
  - Archivo: `src/api/` (si existe)

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
MemoryService  ReActAgent ── logs estructurados por paso
   │            │             (Thought, Action, Observation)
   └───┬────────┘
       │
       ▼
  TransactionTrace completada
       │
  ┌────┴──────────────────┐
  │                       │
Log de consola      TransactionLogs (SQL Server)
(1 línea, legible)  (persistente, consultable)
                           │
                    MetricsCollector
                    (en memoria, p50/p95)
                           │
                     /stats en Telegram
```

---

## Criterios de Éxito

- [ ] Cada request genera exactamente **un log de consola** con el flujo completo
- [ ] Cada request genera exactamente **una fila** en `TransactionLogs`
- [ ] Puedo responder "¿cuánto tardó el LLM en promedio ayer?" con una query SQL
- [ ] Puedo responder "¿qué tools usa más el agente?" con una query SQL
- [ ] El bot notifica automáticamente cuando hay errores consecutivos

---

## Riesgos y Mitigaciones

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|--------------|---------|------------|
| structlog incompatible con código existente | Baja | Medio | Wrapper de compatibilidad o migrar gradualmente |
| TransactionLogs crece sin control | Media | Bajo | Retención de 90 días con DELETE periódico |
| Overhead de guardar traza impacta latencia | Baja | Bajo | Guardar en background task (asyncio.create_task) |
| Métricas en memoria se pierden al reiniciar | Alta | Bajo | Son métricas "del ciclo de vida actual" — aceptable |

---

## Historial de Cambios

| Fecha | Cambio |
|-------|--------|
| 2026-03-31 | Creación del plan |
| 2026-03-31 | Fase 1 parcialmente completada (fixes de sesión anterior) |
