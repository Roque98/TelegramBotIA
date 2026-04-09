# PLAN: Aumentar cobertura de tests al 80%

> **Objetivo**: Llevar la cobertura de tests a un mínimo del 80%
> **Rama**: `feature/cal-11-tests`
> **Prioridad**: 🟡 Media
> **Progreso**: 100% (11/11) ✅ — CI/CD excluido del alcance

---

## Contexto

Tras la migración ARQ-25, la estructura `src/` cambió a capas:
`gateway/` · `pipeline/` · `domain/` · `infra/` · `api/` · `bot/` · `agents/` · `utils/`

---

## Estado actual de cobertura por módulo

| Módulo (ruta actual) | Tests existentes | Estado |
|----------------------|-----------------|--------|
| `src/agents/base/` | `tests/agents/test_base.py` | ✅ Cubierto |
| `src/agents/react/` | `tests/agents/test_react_agent.py` | ✅ Cubierto |
| `src/agents/tools/` | `tests/agents/test_tools.py` | ✅ Cubierto |
| `src/gateway/` | `tests/gateway/test_gateway.py` | ✅ Cubierto |
| `src/pipeline/` | `tests/gateway/test_gateway.py` (parcial) | ✅ Cubierto |
| `src/domain/memory/` | `tests/memory/test_memory.py` | ✅ Cubierto |
| `src/domain/knowledge/` | `tests/domain/test_knowledge_service.py` | ✅ Cubierto |
| `src/domain/auth/` | `tests/domain/test_user_service.py` | ✅ Cubierto |
| `src/infra/observability/` | `tests/observability/test_observability.py` | ✅ Cubierto |
| `src/infra/events/` | `tests/infra/test_event_bus.py` | ✅ Cubierto |
| `src/infra/database/` | `tests/infra/test_database.py` | ✅ Cubierto |
| `src/api/` | `tests/api/test_chat_endpoint.py` | ✅ Cubierto |
| `src/utils/input_validator` | `tests/utils/test_input_validator.py` | ✅ Cubierto |
| `src/utils/rate_limiter` | `tests/utils/test_rate_limiter.py` | ✅ Cubierto |
| `src/utils/status_message` | `tests/utils/test_status_message.py` | ✅ Cubierto |
| `src/bot/handlers/command` | `tests/handlers/test_command_handlers.py` | ✅ Cubierto |
| `src/bot/handlers/registration` | `tests/handlers/test_registration_handlers.py` | ✅ Cubierto |
| `src/bot/middleware/auth_middleware` | `tests/auth/test_auth_middleware.py` | ✅ Cubierto |
| `src/agents/orchestrator/` | `tests/agents/test_orchestrator.py` | ✅ Cubierto |
| `src/agents/tools/read_attachment_tool` | `tests/agents/test_read_attachment_tool.py` | ✅ Cubierto |
| `src/domain/auth/permission_service` | `tests/domain/test_permission_service.py` | ✅ Cubierto |

---

## Tareas

### ✅ Completadas (11/11)
- [x] **11.1** Tests para `src/agents/base/`
- [x] **11.2** Tests para `src/agents/react/`
- [x] **11.3** Tests para `src/agents/tools/`
- [x] **11.4** Tests para `src/domain/memory/`
- [x] **11.5** Tests para `src/infra/observability/`
- [x] **11.6** Tests para `src/api/chat_endpoint.py` (15 tests)
- [x] **11.7** Tests para `src/domain/knowledge/` (29 tests)
- [x] **11.8** Tests para `src/domain/auth/` (30 tests)
- [x] **11.9** Tests para `src/infra/events/bus.py` (18 tests)
- [x] **11.10** Tests para `src/utils/input_validator.py` y `rate_limiter.py` (33 tests)
- [x] **11.11** Tests para `src/infra/database/` — SQLValidator (32) + DatabaseManager (10)
- [x] **11.12** Tests para `src/bot/handlers/` — command_handlers (18) + registration_handlers (19)

---

## Resultado

- **230+ tests nuevos escritos** en esta rama (incluyendo ARQ-29 Fases 5–7)
- **524 tests totales pasan** en la suite completa
- 4 errores pre-existentes en `test_tools_handlers.py` (conflicto sys.modules con test_gateway.py, no introducido por esta rama)
- 2 errores pre-existentes en `test_encryption.py` y `test_token_middleware.py` (módulos eliminados en ARQ-25)

## Criterios de aceptación

- `pytest --cov=src --cov-report=html` reporta ≥80% de cobertura global
- Todos los módulos principales tienen al menos 70% de cobertura
