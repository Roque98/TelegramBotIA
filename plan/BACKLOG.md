# BACKLOG — Iris Bot

> **Última actualización**: 2026-03-25
> **Completados**: 7 de 26
> **Total de mejoras identificadas**: 26
> **Fuente**: Análisis exhaustivo del código fuente

---

## 🔴 Críticas — Seguridad (4)

| # | Plan | Archivo clave | Estado |
|---|------|---------------|--------|
| 1 | [Encriptación segura](02-activos/PLAN_SEC_01_ENCRIPTACION.md) | `utils/encryption_util.py` | Pendiente |
| 2 | [Rate limiting verificación](02-activos/PLAN_SEC_02_RATE_LIMITING.md) | `auth/user_service.py` | Pendiente |
| 3 | [SQL Validator robusto](02-activos/PLAN_SEC_03_SQL_VALIDATOR.md) | `database/sql_validator.py` | Pendiente |
| 4 | [CORS con restricciones](02-activos/PLAN_SEC_04_CORS.md) | `api/chat_endpoint.py` | Pendiente |

---

## 🟠 Alta — Arquitectura y Estabilidad (6)

| # | Plan | Archivo clave | Estado |
|---|------|---------------|--------|
| 5 | [Consolidar async/sync](01-completados/PLAN_ARQ_05_ASYNC_SYNC.md) | `memory/`, `knowledge/`, `agents/tools/` | ✅ Completado |
| 6 | [Cache con evicción](01-completados/PLAN_ARQ_06_CACHE_EVICCION.md) | `memory/memory_service.py` | ✅ Completado |
| 7 | [Global state sincronizado](01-completados/PLAN_ARQ_07_GLOBAL_STATE.md) | `api/chat_endpoint.py` | ✅ Completado |
| 8 | [ToolRegistry thread-safe](01-completados/PLAN_ARQ_08_THREAD_SAFETY.md) | `agents/tools/registry.py` | ✅ Completado |
| 9 | [Auth middleware bug fix](01-completados/PLAN_ARQ_09_AUTH_MIDDLEWARE.md) | `bot/middleware/auth_middleware.py` | ✅ Completado |
| 24 | [Limpieza estructural](01-completados/PLAN_ARQ_24_STRUCT_CLEANUP.md) | `tests/`, `src/api/`, raíz | ✅ Completado |
| 25 | [Reorganización de capas `src/`](02-activos/PLAN_ARQ_25_SRC_LAYOUT.md) | `src/gateway/`, `src/chat_endpoint.py` | Pendiente |
| 26 | [Actualización de documentación](02-activos/PLAN_DOC_26_DOCS_UPDATE.md) | `.claude/context/`, `docs/estructura.md` | Pendiente |

---

## 🟡 Media — Calidad de Código (7)

| # | Plan | Archivo clave | Estado |
|---|------|---------------|--------|
| 10 | [Error handling ReActAgent](01-completados/PLAN_CAL_10_ERROR_HANDLING.md) | `agents/react/agent.py` | ✅ Completado |
| 11 | [Cobertura de tests al 80%](02-activos/PLAN_CAL_11_TESTS.md) | `tests/` | Pendiente |
| 12 | [Estadísticas reales](02-activos/PLAN_CAL_12_ESTADISTICAS.md) | `bot/handlers/command_handlers.py` | Pendiente |
| 13 | [Notificaciones al admin](02-activos/PLAN_CAL_13_NOTIFICACIONES.md) | `bot/middleware/logging_middleware.py` | Pendiente |
| 14 | [Stemmer NLP real](03-ideas/PLAN_CAL_14_STEMMER.md) | `knowledge/knowledge_service.py` | Backlog |
| 15 | [Fallbacks informativos](03-ideas/PLAN_CAL_15_FALLBACKS.md) | `bot/handlers/command_handlers.py` | Backlog |
| 16 | [Pool de conexiones](03-ideas/PLAN_CAL_16_POOL_CONEXIONES.md) | `infra/database/connection.py` | Backlog |

---

## 🟢 Funcionalidades Nuevas (7)

| # | Plan | Archivo clave | Estado |
|---|------|---------------|--------|
| 17 | [Cache para LLM](02-activos/PLAN_FUN_17_CACHE_LLM.md) | `agents/providers/` | Pendiente |
| 18 | [Streaming de respuestas](02-activos/PLAN_FUN_18_STREAMING.md) | `agents/react/agent.py` | Pendiente |
| 19 | [RAG con vectores](02-activos/PLAN_FUN_19_RAG.md) | `knowledge/` | Pendiente |
| 20 | [Multi-agente especialistas](02-activos/PLAN_FUN_20_MULTI_AGENTE.md) | `agents/` | Pendiente |
| 21 | [Retry con Tenacity](02-activos/PLAN_FUN_21_RETRY.md) | `agents/`, `database/` | Pendiente |
| 22 | [Dashboard de monitoreo](02-activos/PLAN_FUN_22_DASHBOARD.md) | `observability/` | Pendiente |
| 23 | [Soporte multimedia](02-activos/PLAN_FUN_23_MULTIMEDIA.md) | `bot/handlers/` | Pendiente |

---

## Leyenda de estados

| Estado | Significado |
|--------|-------------|
| Pendiente | No iniciado |
| En progreso | Tiene rama activa |
| Completado | Mergeado a develop |
| Descartado | Se decidió no implementar |
