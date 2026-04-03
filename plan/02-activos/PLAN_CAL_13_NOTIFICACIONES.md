# PLAN: Notificaciones al administrador

> **Objetivo**: Notificar al admin por Telegram cuando ocurren errores críticos en el bot
> **Rama**: `feature/cal-13-notificaciones`
> **Prioridad**: 🟡 Media
> **Progreso**: 0% (0/6)

---

## Contexto

`src/bot/middleware/logging_middleware.py:99` tiene un TODO sin implementar:

```python
# TODO: Aquí se podría enviar una notificación al admin o registrar en BD
```

Actualmente, errores críticos del bot solo quedan en logs. Si el bot falla a las 3am, nadie se entera.

---

## Decisión de diseño: sin `admin_chat_ids` hardcodeados

En lugar de mantener una lista de IDs en `.env`, los destinatarios se resuelven
dinámicamente desde la BD: usuarios con rol `Administrador` (idRol = 1) que tengan
cuenta de Telegram verificada y activa.

Ventaja: cuando cambia el equipo de admins en el sistema, las notificaciones se
actualizan solas sin tocar configuración.

**Impacto colateral**: `/costo` actualmente usa `admin_chat_ids` para restringir acceso
(`command_handlers.py:290`). Debe migrarse a SEC-01 (BotPermisos) como cualquier otro
comando, y `admin_chat_ids` puede eliminarse de `settings.py`.

---

## Archivos involucrados

- `src/domain/auth/user_query_repository.py` — nuevo método `get_admin_chat_ids()`
- `src/bot/notifications/admin_notifier.py` — nuevo módulo
- `src/bot/middleware/logging_middleware.py` — implementar TODO en `log_error`
- `src/bot/handlers/command_handlers.py` — migrar `/costo` de `admin_chat_ids` a SEC-01
- `src/config/settings.py` — eliminar `admin_chat_ids`

---

## Tareas

- [ ] **13.1** Agregar `get_admin_chat_ids()` en `UserQueryRepository`
  - Query: `UsuariosTelegram JOIN Usuarios WHERE idRol = 1 AND verificado = 1 AND activo = 1`
  - Retorna `list[int]` de `telegramChatId`

- [ ] **13.2** Crear `src/bot/notifications/admin_notifier.py`
  - `async def notify_admin(bot, message, level, db_manager)`
  - Obtiene los chat IDs vía `get_admin_chat_ids()`
  - Rate limiting: máx 1 notificación por tipo de error cada 5 minutos

- [ ] **13.3** Implementar el TODO en `log_error` de `logging_middleware.py`
  - Formato del mensaje: timestamp, tipo de error, usuario afectado, traceback resumido

- [ ] **13.4** Migrar `/costo` de `admin_chat_ids` → SEC-01
  - Registrar `cmd:/costo` en BotPermisos para rol Administrador
  - Eliminar el check de `admin_chat_ids` en `command_handlers.py:290`
  - Eliminar `admin_chat_ids` de `settings.py`

- [ ] **13.5** Script SQL para registrar `cmd:/costo` en BotRecurso/BotPermisos
  - Similar a los scripts existentes en `scripts/sql/`

- [ ] **13.6** Tests con mock del bot y mock de `get_admin_chat_ids()`

---

## Criterios de aceptación

- Errores en `log_error` generan un mensaje de Telegram a todos los admins activos
- Si no hay admins con Telegram verificado, se loggea un warning y no falla
- No se spamea con el mismo error repetido (rate limiting por tipo)
- El mensaje incluye info accionable: timestamp, error, usuario, traceback resumido
- `/costo` restringido vía SEC-01, sin `admin_chat_ids` en settings
