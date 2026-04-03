# PLAN: Fallbacks informativos en handlers

> **Objetivo**: Informar claramente al usuario cuando se está mostrando información de respaldo (fallback)
> **Rama**: `feature/cal-15-fallbacks`
> **Prioridad**: 🟡 Media
> **Progreso**: 0% (0/5)

---

## Contexto

`src/bot/handlers/command_handlers.py:16-70` tiene dos métodos que devuelven datos hardcodeados cuando la BD falla, sin avisar al usuario:

```python
def _get_categories_from_db():
    try:
        # ... query BD
    except Exception:
        return [  # Silencioso — el usuario cree que son datos reales
            {'name': 'PROCESOS', 'display_name': 'Procesos', 'icon': '⚙️', 'entry_count': 0},
            ...
        ]
```

El usuario ve categorías con 0 entradas sin saber que la BD está caída. Además, el mismo bloque de fallback está duplicado en dos métodos distintos.

---

## Archivos involucrados

- `src/bot/handlers/command_handlers.py`

---

## Tareas

- [ ] **15.1** Extraer los datos de fallback a una constante compartida `DEFAULT_CATEGORIES` para eliminar la duplicación
- [ ] **15.2** Cuando se usa el fallback, agregar un mensaje de aviso al usuario:
  > ⚠️ _Algunos datos no están disponibles en este momento. Mostrando información limitada._
- [ ] **15.3** Loguear como `WARNING` (no solo silencioso) cuando se activa el fallback, incluyendo la excepción original
- [ ] **15.4** Implementar el mismo patrón de aviso en `_get_example_questions_from_db()`
- [ ] **15.5** Agregar tests que verifiquen que el mensaje de aviso aparece cuando se simula un fallo de BD

---

## Criterios de aceptación

- El usuario siempre sabe cuándo está viendo información de respaldo
- No hay código de fallback duplicado
- Los logs incluyen la causa del fallback
