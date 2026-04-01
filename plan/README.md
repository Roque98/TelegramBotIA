# Planes del Proyecto Iris Bot

> **Proyecto**: Iris - Bot conversacional con LLM
> **Ultima actualizacion**: 2026-03-28

---

## Estructura

```
plan/
├── README.md                              # Este indice
├── BACKLOG.md                             # Lista completa de mejoras identificadas (23)
├── 01-completados/                        # Planes finalizados (13)
├── 02-activos/                            # Planes en progreso
│   ├── PLAN_RETRY_RESILIENCE.md           # Retry con tenacity
│   ├── PLAN_SEC_01_ENCRIPTACION.md        # Encriptacion segura
│   ├── PLAN_SEC_02_RATE_LIMITING.md       # Rate limiting
│   ├── PLAN_SEC_03_SQL_VALIDATOR.md       # SQL Validator robusto
│   ├── PLAN_SEC_04_CORS.md                # CORS con restricciones
│   ├── PLAN_CAL_11_TESTS.md               # Cobertura tests al 80%
│   ├── PLAN_CAL_12_ESTADISTICAS.md        # Estadisticas reales
│   ├── PLAN_CAL_13_NOTIFICACIONES.md      # Notificaciones al admin
│   ├── PLAN_CAL_14_STEMMER.md             # Stemmer NLP real
│   ├── PLAN_CAL_15_FALLBACKS.md           # Fallbacks informativos
│   ├── PLAN_CAL_16_POOL_CONEXIONES.md     # Pool de conexiones
│   ├── PLAN_FUN_17_CACHE_LLM.md           # Cache para LLM
│   ├── PLAN_FUN_18_STREAMING.md           # Streaming de respuestas
│   ├── PLAN_FUN_19_RAG.md                 # RAG con vectores
│   ├── PLAN_FUN_20_MULTI_AGENTE.md        # Multi-agente especialistas
│   ├── PLAN_FUN_21_RETRY.md               # Retry con Tenacity
│   ├── PLAN_FUN_22_DASHBOARD.md           # Dashboard de monitoreo
│   ├── PLAN_FUN_23_MULTIMEDIA.md          # Soporte multimedia
│   ├── PLAN_OBS_27_OBSERVABILIDAD.md      # Observabilidad (82%)
│   └── PLAN_MIGRACION_TABLAS_IABOT.md     # Migración tablas
└── 03-ideas/                              # Ideas y propuestas
    └── IDEAS_MEJORA_BOT.md                # Ideas de mejora priorizadas
```

---

## Resumen General

| Metrica | Valor |
|---------|-------|
| Planes completados | 13 |
| Planes activos | 20 |
| Ideas documentadas | 10 |
| Backlog total | 26 mejoras |

---

## Planes Completados (01-completados/)

| Plan | Progreso | Rama | Fecha |
|------|----------|------|-------|
| [Migracion ReAct](01-completados/PLAN_REACT_MIGRATION.md) | 100% (47/47) | `feature/react-agent-migration` | 2024-02-13 |
| [Refactor Repository Pattern](01-completados/PLAN_REFACTOR_REPOSITORY_PATTERN.md) | 100% (26/26) | `feature/refactor-repository-pattern` | 2026-03-24 |
| [Consolidar async/sync](01-completados/PLAN_ARQ_05_ASYNC_SYNC.md) | 100% (8/8) | `feature/arq-05-async-sync` | 2026-03-24 |
| [Cache con evicción LRU](01-completados/PLAN_ARQ_06_CACHE_EVICCION.md) | 100% (5/5) | `feature/arq-06-cache-eviccion` | 2026-03-24 |
| [Global state sincronizado](01-completados/PLAN_ARQ_07_GLOBAL_STATE.md) | 100% (4/4) | `feature/arq-07-global-state` | 2026-03-24 |
| [Reorganización capas src/](01-completados/PLAN_ARQ_25_SRC_LAYOUT.md) | 100% (20/20) | `feature/arq-25-src-layout` | 2026-03-28 |
| [Consolidar Legacy](01-completados/PLAN_CONSOLIDAR_LEGACY.md) | 100% | `feature/consolidar-legacy` | 2026-03-21 |
| [Error Handling ReActAgent](01-completados/PLAN_CAL_10_ERROR_HANDLING.md) | 100% (5/5) | `feature/cal-10-error-handling` | 2026-03-25 |
| [Thread Safety ToolRegistry](01-completados/PLAN_ARQ_08_THREAD_SAFETY.md) | 100% | `feature/arq-08-thread-safety` | — |
| [Auth Middleware bug fix](01-completados/PLAN_ARQ_09_AUTH_MIDDLEWARE.md) | 100% | `feature/arq-09-auth-middleware` | — |
| [Struct Cleanup](01-completados/PLAN_ARQ_24_STRUCT_CLEANUP.md) | 100% | `feature/arq-24-struct-cleanup` | — |
| [Docs Update](01-completados/PLAN_DOC_26_DOCS_UPDATE.md) | 100% | `develop` | — |
| [Hot Reload dev](01-completados/PLAN_DEV_28_HOTRELOAD.md) | 100% (9/9) | `develop` | 2026-03-31 |

---

## Planes Activos (02-activos/)

| Plan | Progreso | Rama | Tareas |
|------|----------|------|--------|
| [Observabilidad](02-activos/PLAN_OBS_27_OBSERVABILIDAD.md) | 11% (3/28) | `feature/obs-27-observabilidad` | Logs, traces y métricas |
| [Retry Resilience](02-activos/PLAN_RETRY_RESILIENCE.md) | 0% (0/14) | `feature/retry-resilience` | Tenacity en LLM + BD |
| [Claude Code Patterns](02-activos/PLAN_ARQ_29_CLAUDE_CODE_PATTERNS.md) | 0% (0/33) | `feature/arq-29-claude-code-patterns` | Tool layer, events, cost, memory, archetypes |

---

## Ideas de Mejora (03-ideas/)

| # | Idea | Impacto | Esfuerzo |
|---|------|---------|----------|
| 1 | Consolidar sistemas legacy vs ReAct | Alto | Medio |
| 2 | Cache para LLM | Alto | Medio |
| 3 | Multi-agente con especialistas | Alto | Alto |
| 4 | RAG con base de conocimiento vectorial | Alto | Alto |
| 5 | Streaming de respuestas | Medio | Bajo |
| 6 | Retry con backoff exponencial | Medio | Bajo |
| 7 | Dashboard web de monitoreo | Medio | Alto |
| 8 | Feedback del usuario | Medio | Medio |
| 9 | Soporte multimedia | Medio | Alto |
| 10 | Scheduled tasks / recordatorios | Bajo | Medio |

Ver detalle completo en [IDEAS_MEJORA_BOT.md](03-ideas/IDEAS_MEJORA_BOT.md)

---

## Como Usar

### Crear Nuevo Plan
1. Usar plantilla de `.claude/skills/project-planner/SKILL.md`
2. Crear archivo `plan/02-activos/PLAN_<NOMBRE>.md`
3. Agregar entrada a este README
4. Commit: `docs(plan): crear plan <nombre>`

### Completar un Plan
1. Verificar que todas las tareas esten marcadas `[x]`
2. Mover de `02-activos/` a `01-completados/`
3. Actualizar este README
4. Commit: `docs(plan): completar plan <nombre>`

### Promover una Idea a Plan
1. Elegir idea de `03-ideas/`
2. Crear plan formal en `02-activos/PLAN_<NOMBRE>.md`
3. Actualizar ambos README
4. Commit: `docs(plan): promover idea <nombre> a plan activo`

---

## Estados

| Estado | Carpeta | Descripcion |
|--------|---------|-------------|
| Idea | `03-ideas/` | Propuesta sin plan formal |
| Activo | `02-activos/` | Plan con tareas en progreso |
| Completado | `01-completados/` | Todas las fases terminadas |
