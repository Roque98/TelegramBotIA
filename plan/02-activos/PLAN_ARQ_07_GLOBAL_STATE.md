# PLAN: Eliminar global state mutable en chat_endpoint

> **Objetivo**: Reemplazar el global state sin sincronización en el endpoint REST por un patrón seguro
> **Rama**: `feature/arq-07-global-state`
> **Prioridad**: 🟠 Alta
> **Progreso**: 100% (4/4)

---

## Contexto

`src/api/chat_endpoint.py` usaba una variable global mutable sin locks:

```python
_main_handler = None

def get_main_handler():
    global _main_handler
    if _main_handler is None:
        _main_handler = create_main_handler(DatabaseManager())
    return _main_handler
```

Si dos requests HTTP llegaban simultáneamente (antes de que `_main_handler` se inicializara), se creaban **dos instancias** de `MainHandler`, cada una con su propia conexión a BD y estado separado.

---

## Solución implementada

Se reemplazó la función lazy `get_main_handler()` con el `HandlerManager` singleton de `src/gateway/factory.py`. La inicialización ahora ocurre una sola vez en el bloque `if __name__ == "__main__"` antes de `app.run()`.

---

## Archivos involucrados

- `src/api/chat_endpoint.py` — refactorizado
- `src/gateway/factory.py` — `HandlerManager` (ya existía)

---

## Tareas

- [x] **7.1** Reemplazar la función `get_main_handler()` con una llamada al `HandlerManager` de `gateway/factory.py`
- [x] **7.2** Inicializar `HandlerManager` antes de `app.run()` en lugar de lazy
- [x] **7.3** Eliminar la variable global `_main_handler` y función `get_main_handler()`
- [x] **7.4** Verificar que Flask en modo multi-thread funciona correctamente con el singleton

---

## Criterios de aceptación

- [x] No existe ninguna variable global mutable sin sincronización en `chat_endpoint.py`
- [x] Múltiples requests simultáneas comparten la misma instancia de `MainHandler`
- [x] La inicialización ocurre una sola vez al arrancar la app
