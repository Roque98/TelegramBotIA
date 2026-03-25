# PLAN: ToolRegistry thread-safe

> **Objetivo**: Proteger el singleton ToolRegistry contra race conditions en entornos multi-thread
> **Rama**: `feature/arq-08-thread-safety`
> **Prioridad**: 🟠 Alta
> **Progreso**: 100% (4/4) ✅ COMPLETADO 2026-03-25

---

## Contexto

`src/agents/tools/registry.py` implementa un singleton sin locks:

```python
class ToolRegistry:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
```

Si dos threads verifican `_instance is None` simultáneamente, ambos crean una instancia nueva. Resultado: dos registros con tools diferentes, comportamiento inconsistente del agente.

Adicionalmente, `clear()` y `reset()` son métodos públicos que en producción podrían ser llamados accidentalmente.

---

## Archivos involucrados

- `src/agents/tools/registry.py`
- `tests/agents/test_tools.py`

---

## Tareas

- [x] **8.1** Agregar `threading.Lock` como atributo de clase en `ToolRegistry`
- [x] **8.2** Proteger `__new__` con double-checked locking:
  ```python
  _lock = threading.Lock()
  def __new__(cls):
      if cls._instance is None:
          with cls._lock:
              if cls._instance is None:
                  cls._instance = super().__new__(cls)
      return cls._instance
  ```
- [x] **8.3** Agregar `.. warning::` docstring a `clear()` y `reset()` indicando que son solo para tests
- [x] **8.4** Agregar test de concurrencia: crear 10 threads que instancien `ToolRegistry` simultáneamente y verificar que solo hay una instancia

---

## Criterios de aceptación

- [x] 10 threads creando `ToolRegistry()` simultáneamente siempre producen la misma instancia
- [x] El test de concurrencia pasa de forma consistente
- [x] `clear()` y `reset()` documentados como solo para uso en tests

---

## Commits

- `ef3a08c` feat(tools): thread-safe singleton en ToolRegistry — ARQ-08
