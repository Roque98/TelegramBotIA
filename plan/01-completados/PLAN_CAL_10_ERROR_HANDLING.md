# PLAN: Refactorizar error handling en ReActAgent

> **Objetivo**: Eliminar código duplicado en el manejo de errores del agente ReAct
> **Rama**: `feature/cal-10-error-handling`
> **Prioridad**: 🟡 Media
> **Progreso**: 100% (5/5) ✅ COMPLETADO 2026-03-25

---

## Contexto

`src/agents/react/agent.py` tenía tres bloques `except` casi idénticos que
duplicaban: cálculo de `elapsed_ms`, logging, `_record_error_metrics()` y
construcción de `AgentResponse.error_response()`.

---

## Archivos involucrados

- `src/agents/react/agent.py`
- `tests/agents/test_react_agent.py`

---

## Tareas

- [x] **10.1** Crear `_handle_agent_error(error, start_time, scratchpad, kwargs, tracer) -> AgentResponse`
- [x] **10.2** Reemplazar los tres bloques `except` por una sola llamada a `_handle_agent_error()`
- [x] **10.3** Agregar manejo específico para `ToolException` (nombre del tool en el mensaje)
- [x] **10.4** Agregar `asyncio.CancelledError`: limpia métricas y re-lanza para propagación correcta
- [x] **10.5** Agregar tests: `LLMException`, `MaxIterationsException`, `ToolException`, `Exception` genérica, `steps_taken`, `CancelledError` propagación e integración

---

## Criterios de aceptación

- [x] El manejo de errores está en un solo lugar (`_handle_agent_error`)
- [x] Agregar un nuevo tipo de excepción requiere cambiar solo `_handle_agent_error()`
- [x] Tests cubren `MaxIterationsException`, `LLMException`, `ToolException` y `Exception` genérica

---

## Commits

- `ab86e09` refactor(agent): centralizar error handling en ReActAgent — CAL-10
