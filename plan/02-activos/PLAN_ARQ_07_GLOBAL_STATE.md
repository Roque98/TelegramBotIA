# PLAN: Eliminar global state mutable en chat_endpoint

> **Objetivo**: Reemplazar el global state sin sincronización en el endpoint REST por un patrón seguro
> **Rama**: `feature/arq-07-global-state`
> **Prioridad**: 🟠 Alta
> **Progreso**: 0% (0/4)

---

## Contexto

`src/api/chat_endpoint.py` usa una variable global mutable sin locks:

```python
_main_handler = None

def get_main_handler():
    global _main_handler
    if _main_handler is None:
        _main_handler = create_main_handler(DatabaseManager())
    return _main_handler
```

Si dos requests HTTP llegan simultáneamente (antes de que `_main_handler` se inicialice), se crean **dos instancias** de `MainHandler`, cada una con su propia conexión a BD y estado separado. Esto puede causar inconsistencias y doble consumo de recursos.

---

## Solución propuesta

Usar el `HandlerManager` singleton que ya existe en `src/gateway/factory.py` — fue diseñado exactamente para esto. Alternativamente, inicializar el handler al arrancar la app Flask (en el startup hook) en lugar de hacerlo lazy.

---

## Archivos involucrados

- `src/api/chat_endpoint.py` — refactorizar inicialización
- `src/gateway/factory.py` — `HandlerManager` (ya existe)

---

## Tareas

- [ ] **7.1** Reemplazar la función `get_main_handler()` con una llamada al `HandlerManager` de `gateway/factory.py`
- [ ] **7.2** Inicializar `HandlerManager` en el startup de Flask (`@app.before_first_request` o equivalente) en lugar de lazy
- [ ] **7.3** Eliminar la variable global `_main_handler` y función `get_main_handler()`
- [ ] **7.4** Verificar que Flask en modo multi-thread funciona correctamente con el singleton

---

## Criterios de aceptación

- No existe ninguna variable global mutable sin sincronización en `chat_endpoint.py`
- Múltiples requests simultáneas comparten la misma instancia de `MainHandler`
- La inicialización ocurre una sola vez al arrancar la app
