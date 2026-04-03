# PLAN: Notificaciones al administrador

> **Objetivo**: Notificar al admin por Telegram cuando ocurren errores críticos en el bot
> **Rama**: `feature/cal-13-notificaciones`
> **Prioridad**: 🟡 Media
> **Progreso**: 0% (0/5)

---

## Contexto

`src/bot/middleware/logging_middleware.py:99` tiene un TODO sin implementar:

```python
# TODO: Aquí se podría enviar una notificación al admin o registrar en BD
```

Actualmente, errores críticos del bot solo quedan en logs. Si el bot falla a las 3am, nadie se entera hasta que alguien revise los logs manualmente.

---

## Lo que ya existe

- `admin_chat_ids: list[int]` en `src/config/settings.py:51` — lista de IDs de Telegram con acceso admin. Ya se usa en `command_handlers.py:290` para restringir `/costo`. **No hace falta crear ADMIN_CHAT_ID** — se reutiliza esto.
- `application.add_error_handler(logging_middleware.log_error)` en `setup_logging_middleware()` — el hook ya está conectado, solo falta implementar el TODO dentro de `log_error`.

---

## Tipos de alertas

| Evento | Severidad |
|--------|-----------|
| Error no controlado (unhandled exception) | CRÍTICO |
| Fallo de conexión a BD | CRÍTICO |
| Error de LLM repetido | ALTA |

---

## Archivos involucrados

- `src/bot/middleware/logging_middleware.py` — implementar TODO en `log_error`
- `src/bot/notifications/admin_notifier.py` — nuevo módulo
- `src/config/settings.py` — agregar `admin_notifications_enabled: bool`

---

## Tareas

- [ ] **13.1** Agregar `admin_notifications_enabled: bool = True` en `settings.py`
- [ ] **13.2** Crear `src/bot/notifications/admin_notifier.py` con `async def notify_admin(bot, message, level)`
- [ ] **13.3** Implementar el TODO en `log_error` de `logging_middleware.py` usando `admin_notifier`
- [ ] **13.4** Rate limiting: máximo 1 notificación por tipo de error cada 5 minutos (evitar spam)
- [ ] **13.5** Tests con mock del bot para verificar que se envía la notificación correcta

---

## Criterios de aceptación

- Errores en `log_error` generan un mensaje de Telegram a todos los `admin_chat_ids`
- Si `admin_notifications_enabled=false` o `admin_chat_ids` está vacío, no se envía nada
- No se spamea con el mismo error repetido (rate limiting por tipo)
- El mensaje incluye: timestamp, tipo de error, usuario afectado, traceback resumido
