# PLAN: Bug fix en auth middleware (verificación de comandos públicos)

> **Objetivo**: Corregir la verificación de comandos públicos que usa substring en lugar de startswith
> **Rama**: `feature/arq-09-auth-middleware`
> **Prioridad**: 🟠 Alta
> **Progreso**: 0% (0/3)

---

## Contexto

`src/bot/middleware/auth_middleware.py` verifica si un mensaje contiene un comando público:

```python
message_text = update.message.text if update.message else ""
if any(cmd in message_text for cmd in self.PUBLIC_COMMANDS):
    return True
```

El problema: `in` busca el string como **substring**, no como prefijo. Esto significa que si `PUBLIC_COMMANDS` contiene `/register`, un mensaje que diga `"quiero deregister mi cuenta"` pasaría la validación como comando público (porque `"/register"` está contenido en `"deregister"`).

Un atacante que sepa los comandos públicos podría evadir la autenticación enviando mensajes que contengan esas palabras.

---

## Archivos involucrados

- `src/bot/middleware/auth_middleware.py`
- `tests/test_auth_middleware.py`

---

## Tareas

- [ ] **9.1** Reemplazar `any(cmd in message_text for cmd in self.PUBLIC_COMMANDS)` por `any(message_text.startswith(cmd) for cmd in self.PUBLIC_COMMANDS)`
- [ ] **9.2** Verificar que también funciona para mensajes con argumentos (ej. `/start param`)
- [ ] **9.3** Agregar tests:
  - `/register` → público ✅
  - `deregister` → NO público ✅
  - `/register extra_args` → público ✅
  - Texto aleatorio con substring de comando → NO público ✅

---

## Criterios de aceptación

- Solo los mensajes que **comienzan** con un comando público son tratados como públicos
- Textos que contienen comandos como substring son rechazados correctamente
- Tests pasan al 100%
