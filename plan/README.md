# Planes del Proyecto Iris Bot

> **Proyecto**: Iris - Bot conversacional con LLM
> **Ultima actualizacion**: 2026-03-24

---

## Estructura

```
plan/
├── README.md                              # Este indice
├── BACKLOG.md                             # Lista completa de mejoras identificadas (23)
├── 01-completados/                        # Planes finalizados
│   ├── PLAN_REACT_MIGRATION.md            # Migracion a ReAct (100%)
│   ├── PLAN_REFACTOR_REPOSITORY_PATTERN.md # Refactor Repository+Service (100%)
│   ├── PLAN_ARQ_05_ASYNC_SYNC.md          # Consolidar async/sync (100%)
│   ├── PLAN_ARQ_06_CACHE_EVICCION.md      # Cache con eviccion LRU (100%)
│   └── PLAN_ARQ_07_GLOBAL_STATE.md        # Global state sincronizado (100%)
├── 02-activos/                            # Planes en progreso
│   ├── PLAN_CONSOLIDAR_LEGACY.md          # Eliminar codigo legacy (19 tareas)
│   ├── PLAN_RETRY_RESILIENCE.md           # Retry con tenacity (14 tareas)
│   ├── PLAN_SEC_01_ENCRIPTACION.md        # Encriptacion segura
│   ├── PLAN_SEC_02_RATE_LIMITING.md       # Rate limiting verificacion
│   ├── PLAN_SEC_03_SQL_VALIDATOR.md       # SQL Validator robusto
│   ├── PLAN_SEC_04_CORS.md                # CORS con restricciones
│   ├── PLAN_ARQ_08_THREAD_SAFETY.md       # ToolRegistry thread-safe
│   ├── PLAN_ARQ_09_AUTH_MIDDLEWARE.md     # Auth middleware bug fix
│   ├── PLAN_CAL_10_ERROR_HANDLING.md      # Error handling ReActAgent
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
│   ├── PLAN_ARQ_25_SRC_LAYOUT.md         # Reorganización de capas src/
│   └── PLAN_DOC_26_DOCS_UPDATE.md        # Actualización y organización de docs
└── 03-ideas/                              # Ideas y propuestas
    └── IDEAS_MEJORA_BOT.md                # Ideas de mejora priorizadas
```

---

## Resumen General

| Metrica | Valor |
|---------|-------|
| Planes completados | 5 |
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

---

## Planes Activos (02-activos/)

| Plan | Progreso | Rama | Tareas |
|------|----------|------|--------|
| [Consolidar Legacy](02-activos/PLAN_CONSOLIDAR_LEGACY.md) | 0% (0/19) | `feature/consolidar-legacy` | Eliminar ~6,000 ln legacy |
| [Retry Resilience](02-activos/PLAN_RETRY_RESILIENCE.md) | 0% (0/14) | `feature/retry-resilience` | Tenacity en LLM + BD |

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
