# PLAN: Limpieza estructural del proyecto

> **Objetivo**: Eliminar código muerto, archivos mal ubicados e inconsistencias de naming que generan confusión y rompen la ejecución de tests
> **Rama**: `feature/arq-24-struct-cleanup`
> **Prioridad**: 🟠 Alta
> **Progreso**: 100% (4/4) ✅ COMPLETADO 2026-03-25

---

## Contexto

Análisis exhaustivo reveló tres categorías de problemas estructurales:
tests obsoletos con imports rotos, scripts de diagnóstico sueltos en raíz
ejecutados involuntariamente por pytest, e inconsistencias de naming.

---

## Archivos / carpetas involucradas

**Eliminados (tests obsoletos — arquitectura anterior):**
- `tests/agent/` — imports a `src.agent.*` (singular) inexistente
- `tests/tools/` — imports a `src.tools` inexistente
- `tests/orchestrator/` — imports a `src.orchestrator` inexistente
- `tests/test_agent.py` — importaba `src.agent.llm_agent` inexistente

**Movidos a `scripts/diagnostics/`:**
- `test_db_connection.py`, `test_db_final.py`, `test_env_loading.py`
- `test_simple_connection.py`, `test_tools_manual.py`

**Renombrados/consolidados:**
- `Ejemplos/EjemploSimple.py` → `examples/EjemploSimple_legacy.py`
- `Ejemplos/SalidaEstructurada.py` → `examples/SalidaEstructurada_legacy.py`
- `src/api/chat_endpoint.py` → `src/chat_endpoint.py`

---

## Tareas

- [x] **24.1** Verificar git log de tests obsoletos (todos del commit `f453740`, arquitectura vieja confirmada)
- [x] **24.2** Eliminar 14 archivos en `tests/agent/`, `tests/tools/`, `tests/orchestrator/` y `tests/test_agent.py`
- [x] **24.3** Mover 5 scripts de diagnóstico de raíz → `scripts/diagnostics/`
- [x] **24.4** Consolidar `Ejemplos/` → `examples/`, mover `src/api/chat_endpoint.py` → `src/chat_endpoint.py`, actualizar referencias

---

## Criterios de aceptación

- [x] `pytest tests/` se ejecuta sin `ImportError` ni `ModuleNotFoundError`
- [x] No hay archivos `test_*.py` en la raíz del proyecto
- [x] Solo existe una carpeta `examples/` (minúscula)
- [x] `src/api/` eliminada; `chat_endpoint.py` vive en `src/`
- [x] No quedan referencias a `src.api` ni `src/api` en el proyecto

---

## Commits

- `(pendiente)` chore(struct): limpieza estructural del proyecto — ARQ-24
