# PLAN: Notificaciones al administrador

> **Objetivo**: Completar los TODOs de notificaciones al admin en el logging middleware
> **Rama**: `feature/cal-13-notificaciones`
> **Prioridad**: 🟡 Media
> **Progreso**: 0% (0/6)

---

## Contexto

`src/bot/middleware/logging_middleware.py` tiene al menos dos TODOs sin implementar:

```python
# línea 99:
# TODO: enviar notificación al admin

# líneas 157-159:
# TODO: notificar error crítico al admin
```

Actualmente, errores críticos del bot solo quedan en logs. Si el bot falla a las 3am, nadie se entera hasta que alguien revisa los logs manualmente.

---

## Canales de notificación propuestos

1. **Telegram directo**: Enviar mensaje a un `ADMIN_CHAT_ID` configurado en `.env` (opción más simple, sin dependencias externas)
2. **Email**: Alternativa si el admin no usa Telegram activamente
3. **Ambos**: Configurable por severidad

Recomendación: **Telegram directo** — ya tenemos el bot, no requiere librerías adicionales.

---

## Tipos de alertas

| Evento | Severidad | Canal |
|--------|-----------|-------|
| Error no controlado | CRÍTICO | Telegram |
| Fallo de conexión a BD | CRÍTICO | Telegram |
| Usuario bloqueado por brute force | ALTA | Telegram |
| Bot reiniciado | INFO | Telegram |
| Error de LLM repetido (3+ veces) | ALTA | Telegram |

---

## Archivos involucrados

- `src/bot/middleware/logging_middleware.py` — completar TODOs
- `src/config/settings.py` — `ADMIN_CHAT_ID`, `ADMIN_NOTIFICATIONS_ENABLED`
- `.env.example` — documentar variables
- `src/bot/notifications/` — nuevo módulo para envío de notificaciones (o helper en `utils/`)

---

## Tareas

- [ ] **13.1** Agregar `ADMIN_CHAT_ID` y `ADMIN_NOTIFICATIONS_ENABLED` en `settings.py` y `.env.example`
- [ ] **13.2** Crear `src/bot/notifications/admin_notifier.py` con método `async def notify_admin(bot, message, level)`
- [ ] **13.3** Implementar los dos TODOs en `logging_middleware.py` usando `admin_notifier`
- [ ] **13.4** Agregar rate limiting a las notificaciones (máximo 1 por tipo de error cada 5 minutos, para no spam)
- [ ] **13.5** Formato de notificación legible: timestamp, tipo de error, usuario afectado, traceback resumido
- [ ] **13.6** Agregar tests con mock del bot para verificar que se envía la notificación correcta

---

## Criterios de aceptación

- Errores críticos generan un mensaje de Telegram al admin automáticamente
- Si `ADMIN_NOTIFICATIONS_ENABLED=false`, no se envía nada (útil para desarrollo)
- No se spamea al admin con el mismo error repetido
- El formato del mensaje es legible y contiene info accionable
