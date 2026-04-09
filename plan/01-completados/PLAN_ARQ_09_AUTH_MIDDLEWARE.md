# PLAN: Bug fix en auth middleware (verificación de comandos públicos)

> **Objetivo**: Corregir la verificación de comandos públicos que usa substring en lugar de startswith
> **Rama**: `feature/arq-09-auth-middleware`
> **Prioridad**: 🟠 Alta
> **Progreso**: 100% (3/3) ✅ COMPLETADO 2026-03-25

---

## Contexto

`src/bot/middleware/auth_middleware.py` verificaba si un mensaje contenía un comando público:

```python
# BUG: busca substring, no prefijo
if any(cmd in message_text for cmd in self.PUBLIC_COMMANDS):
    return True
```

El problema: `in` busca el string como **substring**, no como prefijo. Mensajes como
`"quiero deregister mi cuenta"` pasaban la validación porque `"/register"` está
contenido en `"deregister"`.

---

## Archivos involucrados

- `src/bot/middleware/auth_middleware.py`
- `tests/auth/test_auth_middleware.py`

---

## Tareas

- [x] **9.1** Reemplazar `any(cmd in message_text ...)` por `any(message_text.startswith(cmd) ...)`
- [x] **9.2** Verificar que también funciona para mensajes con argumentos (`/start param`) — cubierto por `startswith`
- [x] **9.3** Agregar tests:
  - `/register` → público ✅
  - `deregister` → NO público ✅
  - `/register extra_args` → público ✅
  - Texto aleatorio con substring de comando → NO público ✅

---

## Criterios de aceptación

- [x] Solo los mensajes que **comienzan** con un comando público son tratados como públicos
- [x] Textos que contienen comandos como substring son rechazados correctamente
- [x] Tests pasan al 100%

---

## Commits

- `365633f` fix(auth): corregir verificación de comandos públicos con startswith — ARQ-09
