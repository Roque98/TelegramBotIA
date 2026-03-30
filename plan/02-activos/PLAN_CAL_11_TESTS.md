# PLAN: Aumentar cobertura de tests al 80%

> **Objetivo**: Llevar la cobertura de tests a un mínimo del 80%
> **Rama**: `feature/cal-11-tests`
> **Prioridad**: 🟡 Media
> **Progreso**: 45% (5/11) — rutas actualizadas post migración ARQ-25

---

## Contexto

Tras la migración ARQ-25, la estructura `src/` cambió a capas:
`gateway/` · `pipeline/` · `domain/` · `infra/` · `api/` · `bot/` · `agents/` · `utils/`

Varios tests ya existen. Las tareas pendientes cubren los módulos sin tests o con cobertura baja.

---

## Estado actual de cobertura por módulo

| Módulo (ruta actual) | Tests existentes | Estado |
|----------------------|-----------------|--------|
| `src/agents/base/` | `tests/agents/test_base.py` | ✅ Cubierto |
| `src/agents/react/` | `tests/agents/test_react_agent.py` | ✅ Cubierto |
| `src/agents/tools/` | `tests/agents/test_tools.py` | ✅ Cubierto |
| `src/gateway/` | `tests/gateway/test_gateway.py` | ✅ Cubierto |
| `src/pipeline/` | `tests/gateway/test_gateway.py` (parcial) | ⚠️ Parcial |
| `src/domain/memory/` | `tests/memory/test_memory.py` | ✅ Cubierto |
| `src/domain/knowledge/` | — | ❌ Sin tests |
| `src/domain/auth/` | `tests/auth/test_auth_middleware.py` (parcial) | ⚠️ Parcial |
| `src/infra/observability/` | `tests/observability/test_observability.py` | ✅ Cubierto |
| `src/infra/database/` | — | ❌ Sin tests |
| `src/infra/events/` | — | ❌ Sin tests |
| `src/api/` | — | ❌ Sin tests |
| `src/bot/handlers/` | `tests/handlers/test_tools_handlers.py` (parcial) | ⚠️ Parcial |
| `src/utils/` | `tests/utils/test_retry.py` (parcial) | ⚠️ Parcial |

---

## Tareas

### ✅ Completadas
- [x] **11.1** Tests para `src/agents/base/` (AgentResponse, BaseAgent, events, exceptions)
- [x] **11.2** Tests para `src/agents/react/` (schemas, scratchpad, ReActAgent loop)
- [x] **11.3** Tests para `src/agents/tools/` (registry, tools individuales)
- [x] **11.4** Tests para `src/domain/memory/` (MemoryRepository, MemoryService, cache TTL)
- [x] **11.5** Tests para `src/infra/observability/` (Tracer, MetricsCollector)

### 🔲 Pendientes
- [ ] **11.6** Escribir tests para `src/api/chat_endpoint.py` (con Flask/httpx test client)
- [ ] **11.7** Completar tests para `src/pipeline/` — `factory.py` y `handler.py` (MainHandler paths: error, timeout)
- [ ] **11.8** Escribir tests para `src/domain/knowledge/` (KnowledgeService, KnowledgeRepository con BD mock)
- [ ] **11.9** Completar tests para `src/domain/auth/` (UserService, UserRepository, UserEntity)
- [ ] **11.10** Escribir tests para `src/infra/database/` (connection pool, sql_validator) y `src/infra/events/bus.py`
- [ ] **11.11** Completar tests para `src/utils/` — `input_validator.py`, `rate_limiter.py`, `encryption_util.py`
- [ ] **11.12** Completar tests para `src/bot/handlers/` — `command_handlers.py`, `query_handlers.py`, `registration_handlers.py`
- [ ] **11.13** Agregar tests de concurrencia para `ToolRegistry` y `MemoryService`
- [ ] **11.14** Configurar `pytest-cov` y CI (GitHub Actions) para reportar cobertura en cada PR

---

## Criterios de aceptación

- `pytest --cov=src --cov-report=html` reporta ≥80% de cobertura global
- Todos los módulos principales tienen al menos 70% de cobertura
- CI falla si la cobertura baja del 80%
