# PLAN: Aumentar cobertura de tests al 80%

> **Objetivo**: Llevar la cobertura de tests del ~46% actual a un mínimo del 80%
> **Rama**: `feature/cal-11-tests`
> **Prioridad**: 🟡 Media
> **Progreso**: 0% (0/9)

---

## Contexto

El proyecto tiene ~2,432 líneas de tests para ~5,244 líneas de código fuente (~46% de cobertura). Los módulos sin cobertura son:

- `src/api/` — endpoint REST sin ningún test
- `src/gateway/` — factory y handler sin tests
- `src/observability/` — sin tests
- Tests existentes: no cubren concurrencia, error handling extremo, ni timeouts

---

## Módulos a cubrir

| Módulo | Cobertura actual | Meta |
|--------|-----------------|------|
| `api/` | 0% | 70% |
| `gateway/` | 0% | 70% |
| `observability/` | 0% | 60% |
| `agents/react/` | ~40% | 85% |
| `memory/` | ~50% | 80% |
| `knowledge/` | ~50% | 80% |
| `auth/` | ~60% | 85% |
| `database/` | ~40% | 75% |

---

## Tareas

- [ ] **11.1** Configurar `pytest-cov` para generar reporte HTML de cobertura
- [ ] **11.2** Escribir tests para `src/api/chat_endpoint.py` (con Flask test client)
- [ ] **11.3** Escribir tests para `src/gateway/factory.py` y `handler.py`
- [ ] **11.4** Agregar tests de concurrencia para `ToolRegistry` y `MemoryService`
- [ ] **11.5** Agregar tests de timeout para llamadas a LLM y BD (con mocks)
- [ ] **11.6** Agregar tests para `src/observability/`
- [ ] **11.7** Completar tests faltantes en `agents/react/agent.py` (error paths)
- [ ] **11.8** Agregar tests de integración para `KnowledgeService` con BD mock
- [ ] **11.9** Configurar CI (GitHub Actions) para ejecutar tests y reportar cobertura en cada PR

---

## Criterios de aceptación

- `pytest --cov=src --cov-report=html` reporta ≥80% de cobertura global
- Todos los módulos principales tienen al menos 70% de cobertura
- Tests de concurrencia incluidos
- CI falla si la cobertura baja del 80%
