# Planes del Proyecto Iris Bot

> **Proyecto**: Iris - Bot conversacional con LLM
> **Ultima actualizacion**: 2026-04-09

---

## Estructura

```
plan/
├── README.md                              # Este indice
├── 01-completados/                        # Planes finalizados (18)
├── 02-activos/                            # Planes en progreso (2)
│   ├── PLAN_OBS_32_LOG_IMPROVEMENTS.md   # Mejoras al sistema de logs
│   └── PLAN_ARQ_35_DYNAMIC_ORCHESTRATOR.md # Orchestrator con agentes dinámicos
└── 03-ideas/                              # Ideas y propuestas
    └── IDEAS_MEJORA_BOT.md                # Ideas de mejora priorizadas
```

---

## Resumen General

| Metrica | Valor |
|---------|-------|
| Planes completados | 18 |
| Planes activos | 4 |
| Ideas documentadas | 10 |

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
| [Consolidar logs + InteractionSteps](01-completados/PLAN_OBS_31_CONSOLIDAR_LOGS.md) | 100% (27/27) | `develop` | 2026-04-08 |
| [Observabilidad](01-completados/PLAN_OBS_27_OBSERVABILIDAD.md) | 100% (23/23) | `feature/obs-27-observabilidad` | 2026-04-08 |
| [AgentOrchestrator](01-completados/PLAN_ARQ_30_ORCHESTRATOR.md) | Descartado | — | 2026-04-08 |
| [ARQ-33 Dynamic Tool Hints](01-completados/PLAN_ARQ_33_DYNAMIC_HINTS.md) | 100% (13/13) | `develop` | 2026-04-08 |
| [DOC-34 Reescritura de documentación](01-completados/PLAN_DOC_34_DOCS_REWRITE.md) | 100% (26/26) | `develop` | 2026-04-08 |

---

## Planes Activos (02-activos/)

| Plan | Progreso | Rama | Pendiente |
|------|----------|------|-----------|
| [OBS-32 Mejoras al sistema de logs](02-activos/PLAN_OBS_32_LOG_IMPROVEMENTS.md) | 80% | `develop` | Usuario ejecuta 2 ALTER TABLE en BD |
| [ARQ-35 Orchestrator con Agentes Dinámicos](02-activos/PLAN_ARQ_35_DYNAMIC_ORCHESTRATOR.md) | 0% | `feature/arq-35-dynamic-orchestrator` | Pendiente iniciar |
| [AUTH-SP Migración Auth a Stored Procedures](02-activos/PLAN_AUTH_SP_MIGRATION.md) | 0% | `master` | Pendiente iniciar |
| [FEAT-36 Workflow de Análisis de Alertas](02-activos/PLAN_FEAT_36_ALERT_WORKFLOW.md) | 0% | `feature/feat-36-alert-workflow` | Pendiente iniciar |

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
