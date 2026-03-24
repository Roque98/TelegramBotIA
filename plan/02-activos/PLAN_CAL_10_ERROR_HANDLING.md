# PLAN: Refactorizar error handling en ReActAgent

> **Objetivo**: Eliminar código duplicado en el manejo de errores del agente ReAct
> **Rama**: `feature/cal-10-error-handling`
> **Prioridad**: 🟡 Media
> **Progreso**: 0% (0/5)

---

## Contexto

`src/agents/react/agent.py` tiene tres bloques `except` casi idénticos:

```python
except MaxIterationsException as e:
    elapsed_ms = (time.perf_counter() - start_time) * 1000
    logger.error(f"Max iterations: {e}")
    self._record_error_metrics(...)
    return AgentResponse.error_response(...)

except LLMException as e:
    elapsed_ms = (time.perf_counter() - start_time) * 1000  # duplicado
    logger.error(f"LLM error: {e}")                          # duplicado
    self._record_error_metrics(...)                           # duplicado
    return AgentResponse.error_response(...)                  # duplicado

except Exception as e:
    elapsed_ms = (time.perf_counter() - start_time) * 1000  # duplicado
    logger.exception(f"Unexpected error: {e}")
    self._record_error_metrics(...)                           # duplicado
    return AgentResponse.error_response(...)                  # duplicado
```

Esto viola DRY y hace que cualquier cambio en el manejo de errores requiera modificar 3 lugares.

---

## Archivos involucrados

- `src/agents/react/agent.py`
- `tests/test_react_agent.py`

---

## Tareas

- [ ] **10.1** Crear método privado `_handle_agent_error(error: Exception, start_time: float) -> AgentResponse` que centralice:
  - Cálculo de `elapsed_ms`
  - Logging apropiado según tipo de excepción
  - Llamada a `_record_error_metrics()`
  - Construcción de `AgentResponse.error_response()`
- [ ] **10.2** Reemplazar los tres bloques `except` por llamadas a `_handle_agent_error()`
- [ ] **10.3** Agregar manejo específico para `ToolException` si no existe
- [ ] **10.4** Agregar mecanismo para interrumpir el loop mid-execution (ej. `asyncio.CancelledError`)
- [ ] **10.5** Agregar tests para cada tipo de excepción

---

## Criterios de aceptación

- El manejo de errores está en un solo lugar
- Agregar un nuevo tipo de excepción requiere cambiar solo `_handle_agent_error()`
- Tests cubren `MaxIterationsException`, `LLMException`, y `Exception` genérica
