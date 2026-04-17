# PLAN_BOT_40_NETWORK_RESILIENCE — Resiliencia ante NetworkError de Telegram

**Rama**: `develop`
**Prioridad**: Baja
**Estado**: Completado — 2026-04-17
**Motivación**: El error `NetworkError: httpx.ReadError` aparece de forma intermitente durante el polling de Telegram. Es un error transitorio de red que se recupera automáticamente, pero actualmente se loguea como ERROR y se persiste en la BD, generando ruido en logs y alertas innecesarias.

---

## Diagnóstico

| Aspecto | Estado anterior | Estado final |
|---------|----------------|--------------|
| Nivel de log | `ERROR` | `WARNING` (es transitorio) |
| Persiste en BD (`ApplicationLogs`) | Sí | No (filtrado por TelegramNetworkFilter) |
| Notifica al admin | Sí (vía SqlLogHandler) | No |
| El bot se recupera solo | Sí | Mantener ✓ |

**Causa raíz**: No existía un error handler registrado en la `Application` de Telegram. Cuando ocurría un `NetworkError`, python-telegram-bot lo emitía como excepción no capturada, que subía al logger raíz como ERROR.

---

## Solución Implementada

### T1 — Error handler en TelegramBot
**Archivo**: `src/bot/telegram_bot.py`

Agregado método `_setup_error_handler()` que registra un handler en la `Application`:
- Captura `telegram.error.NetworkError` y lo loguea como `WARNING`
- Otros errores se logean como `ERROR` con `exc_info`
- Llamado desde `__init__` después de `_setup_handlers()`

### T2 — TelegramNetworkFilter en logging_config.py
**Archivo**: `src/infra/observability/logging_config.py`

Agregada clase `TelegramNetworkFilter` que filtra mensajes con patrones:
`httpx.ReadError`, `httpx.ConnectError`, `NetworkError`, `Conflict`

Aplicada al `SqlLogHandler` para que estos errores no se persistan en `ApplicationLogs`.

---

## TODOs

- [x] **T1** — Agregar `_setup_error_handler()` en `TelegramBot` con handler para `NetworkError`
- [x] **T2** — Crear `TelegramNetworkFilter` en `logging_config.py` y aplicarlo al `SqlLogHandler`
- [x] **T3** — Plan movido a completados
- [x] **T4** — Commit: `fix(bot): degradar NetworkError transitorio de ERROR a WARNING`

---

## Criterios de Éxito

- [x] Los `NetworkError` de polling ya no aparecen como ERROR en los logs
- [x] No se generan entradas en `ApplicationLogs` por estos errores
- [x] El bot sigue reconectándose automáticamente sin intervención
- [x] Los errores reales (no NetworkError) siguen siendo capturados correctamente
