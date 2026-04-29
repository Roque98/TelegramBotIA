# Plan: BOT-41 Dashboard Inline Keyboard para Telegram

> **Estado**: âª No iniciado
> **Ãltima actualizaciÃ³n**: 2026-04-22
> **Rama Git**: `feature/bot-41-telegram-dashboard`

## Resumen de Progreso

| Fase | Progreso | Estado |
|------|----------|--------|
| Fase 1: Infraestructura base | ââââââââââ 0% | â³ Pendiente |
| Fase 2: MenÃº principal + Overview | ââââââââââ 0% | â³ Pendiente |
| Fase 3: Alertas + Logs | ââââââââââ 0% | â³ Pendiente |
| Fase 4: Agentes + Usuarios + Knowledge | ââââââââââ 0% | â³ Pendiente |
| Fase 5: NavegaciÃ³n + UX polish | ââââââââââ 0% | â³ Pendiente |

**Progreso Total**: ââââââââââ 0% (0/30 tareas)

---

## DescripciÃ³n

Implementar un dashboard interactivo en Telegram usando InlineKeyboardMarkup
que permita a los administradores consultar las mismas mÃ©tricas del dashboard
web sin salir del bot. Navega entre secciones con botones, refresca datos
y pagina listas directamente desde el chat.

**Secciones a cubrir:**
- Resumen general (Overview) con filtros de perÃ­odo
- Alertas activas (crÃ­ticas y warnings)
- Logs de interacciones recientes (paginado)
- Agentes activos con detalle bÃ¡sico
- Usuarios registrados
- Base de conocimiento (categorÃ­as y conteos)

**Principios de diseÃ±o:**
- Solo admins tienen acceso (`get_admin_chat_ids`)
- Reutilizar la lÃ³gica de queries de `dashboard_api.py` directamente (no HTTP)
- Editar el mensaje en lugar de enviar uno nuevo (`edit_message_text`)
- Callbacks con prefijo `dash:` para namespace limpio
- Timeout graceful: si el callback es muy viejo, notificar con `answer_callback_query`

---

## Fase 1: Infraestructura base

**Objetivo**: Esqueleto del sistema â comando, service, handler de callbacks y registro
**Dependencias**: Ninguna

### Tareas

- [ ] **Inyectar `db_registry` en `bot_data`** â requerido para la vista de alertas
  - Archivo: `src/bot/telegram_bot.py` lÃ­nea ~56
  - Agregar: `self.application.bot_data['db_registry'] = self.db_registry`
  - Sin esto, `DashboardService.get_alerts()` no puede conectarse a la BD de monitoreo

- [ ] **Crear `DashboardService`** â wrapper async sobre las queries de `dashboard_api.py`
  - Archivo: `src/bot/dashboard/dashboard_service.py`
  - MÃ©todos: `get_overview(periodo)`, `get_alerts()`, `get_logs(page)`, `get_agents()`, `get_users()`, `get_knowledge()`
  - Usar `db_manager.execute_query_async()` (ya existe, usa `asyncio.to_thread` internamente)
  - Para alertas: `await repo.get_active_events_all()` directamente â NO copiar el `asyncio.run()` de `dashboard_api.py` (es un workaround de Flask sÃ­ncrono, aquÃ­ ya somos async)
  - No duplicar SQL: extraer las queries de `dashboard_api.py` a este service

- [ ] **Crear `DashboardHandler`** â recibe callbacks `dash:*` y despacha a la vista correcta
  - Archivo: `src/bot/dashboard/dashboard_handler.py`
  - Registrar como `CallbackQueryHandler(pattern=r"^dash:")`
  - Dispatch por token: `dash:menu`, `dash:overview:hoy`, `dash:alerts`, `dash:logs:1`, etc.
  - Auth guard: verificar que `effective_user.id` estÃ¡ en `get_admin_chat_ids`
  - **Regla de oro**: llamar `await query.answer()` SIEMPRE como primera lÃ­nea del handler, incluso antes del auth check. Si el callback no responde, Telegram muestra spinner infinito.
  - **No usar `require_auth`**: el decorador usa `update.message` que es `None` en callbacks. El guard propio es la Ãºnica barrera.
  - Cache del admin check: guardar resultado en `context.user_data["is_admin"]` la primera vez para no hacer una query a BD en cada pulsaciÃ³n de botÃ³n.

- [ ] **Crear comando `/dashboard`** â punto de entrada, solo admins
  - Archivo: agregar en `src/bot/handlers/command_handlers.py`
  - Enviar mensaje con el menÃº principal inline
  - Si no es admin: responder con `â Solo administradores`

- [ ] **Registrar handlers** en `src/bot/telegram_bot.py`
  - Importar y registrar `DashboardHandler` como `CallbackQueryHandler`
  - Agregar `CommandHandler("dashboard", dashboard_command)`

- [ ] **Crear `__init__.py`** del mÃ³dulo dashboard
  - Archivo: `src/bot/dashboard/__init__.py`

### Entregables
- [ ] MÃ³dulo `src/bot/dashboard/` creado y registrado
- [ ] `/dashboard` responde a admins, rechaza a no-admins

---

## Fase 2: MenÃº principal + Overview

**Objetivo**: MenÃº navegable y secciÃ³n de resumen con filtros de perÃ­odo
**Dependencias**: Fase 1

### Tareas

- [ ] **Implementar vista del menÃº principal**
  - Archivo: `src/bot/dashboard/views.py`
  - Texto: nombre del bot, fecha/hora actual, versiÃ³n
  - Keyboard: `[ð Overview] [ð¨ Alertas]` / `[ð Logs] [ð¤ Agentes]` / `[ð¥ Usuarios] [ð Knowledge]` / `[ð Refrescar]`
  - Callbacks: `dash:menu` (self), `dash:overview:hoy`, `dash:alerts`, `dash:logs:1`, `dash:agents`, `dash:users`, `dash:knowledge`

- [ ] **Implementar vista Overview**
  - Archivo: `src/bot/dashboard/views.py`
  - Datos de `DashboardService.get_overview(periodo)`:
    mensajes + % cambio, usuarios activos, errores, costo USD, p50/p90
  - Top 3 agentes por requests (nombre + requests + % Ã©xito)
  - Keyboard de filtros: `[Hoy â] [Ayer] [7d] [30d]` + `[ð MenÃº]`
  - Callbacks: `dash:overview:hoy`, `dash:overview:ayer`, `dash:overview:7d`, `dash:overview:30d`
  - Marcar visualmente el perÃ­odo activo con â

- [ ] **Implementar handler dispatch para overview**
  - En `DashboardHandler`: detectar `dash:overview:{periodo}` y renderizar vista
  - Editar el mensaje con `query.edit_message_text()`

### Entregables
- [ ] `/dashboard` muestra menÃº navegable
- [ ] Overview cambia datos al presionar filtros de perÃ­odo

---

## Fase 3: Alertas + Logs

**Objetivo**: SecciÃ³n de alertas en tiempo real y log de interacciones paginado
**Dependencias**: Fase 1

### Tareas

- [ ] **Implementar vista de Alertas**
  - Archivo: `src/bot/dashboard/views.py`
  - Datos de `DashboardService.get_alerts()`:
    total crÃ­ticos, total warnings, lista de alertas (mÃ¡x 10 en mensaje)
  - Formato por alerta: equipo, IP, sensor, status, prioridad
  - Keyboard: `[ð Refrescar] [ð MenÃº]`
  - Si no hay alertas: mensaje `â Sin alertas activas`

- [ ] **Implementar vista de Logs (lista paginada)**
  - Archivo: `src/bot/dashboard/views.py`
  - `DashboardService.get_logs(page, page_size=8)`: top 50 logs, paginar localmente
  - Por log: username, query truncada (40 chars), agente, duraciÃ³n, estado â/â
  - Keyboard: paginaciÃ³n `[â] [PÃ¡gina N/M] [â¶]` + `[ð MenÃº]`
  - Callbacks: `dash:logs:{page}`

- [ ] **Implementar handler dispatch para alertas y logs**
  - Detectar `dash:alerts` y `dash:logs:{page}`
  - Llamar al service y renderizar la vista correspondiente

### Entregables
- [ ] Alertas muestran estado actual del monitoreo
- [ ] Logs navegables con paginaciÃ³n funcional

---

## Fase 4: Agentes + Usuarios + Knowledge

**Objetivo**: Completar las secciones restantes del dashboard
**Dependencias**: Fase 1

### Tareas

- [ ] **Implementar vista de Agentes**
  - Archivo: `src/bot/dashboard/views.py`
  - `DashboardService.get_agents()`: lista de agentes activos
  - Por agente: nombre, descripciÃ³n, modelo, temperatura, requests hoy, % Ã©xito, tools (count)
  - Keyboard: `[ð Refrescar] [ð MenÃº]`

- [ ] **Implementar vista de Usuarios**
  - Datos de `DashboardService.get_users()`
  - Por usuario: nombre, rol, estado, Ãºltima actividad
  - MÃ¡x 15 usuarios por mensaje â decisiÃ³n deliberada: el SP puede retornar mucha gente,
    se mostrarÃ¡ solo los Ãºltimos 15 activos; paginaciÃ³n queda como mejora futura
  - Keyboard: `[ð Refrescar] [ð MenÃº]`

- [ ] **Implementar vista de Knowledge**
  - Datos de `DashboardService.get_knowledge()`
  - Resumen: total categorÃ­as, total entradas, bÃºsquedas hoy
  - Lista de categorÃ­as: icono + nombre + cantidad de entradas
  - Keyboard: `[ð Refrescar] [ð MenÃº]`

- [ ] **Registrar dispatch para las 3 secciones**
  - Detectar `dash:agents`, `dash:users`, `dash:knowledge` en `DashboardHandler`

### Entregables
- [ ] Las 6 secciones del dashboard son accesibles desde el menÃº
- [ ] Todos los datos provienen de la BD sin HTTP calls

---

## Fase 5: NavegaciÃ³n + UX polish

**Objetivo**: Experiencia fluida, errores manejados, feedback inmediato
**Dependencias**: Fases 2, 3, 4

### Tareas

- [ ] **`dash:refresh` genÃ©rico** â refrescar la vista actual sin volver al menÃº
  - Guardar `context.user_data["dash_current_view"]` con la Ãºltima vista
  - `dash:refresh` re-llama la misma vista con datos nuevos

- [ ] **Feedback inmediato en callbacks lentos**
  - Llamar `query.answer("Cargando...")` antes de las queries a BD
  - En error de BD: `query.answer("Error al cargar datos", show_alert=True)` + log

- [ ] **Timeout graceful**
  - Si `edit_message_text` falla con `MessageNotModified`: ignorar silenciosamente
  - Si el mensaje es demasiado viejo (error de Telegram): responder con nuevo mensaje

- [ ] **LÃ­mite de longitud de mensaje**
  - Si el texto supera 4096 chars: truncar lista y agregar `â¦ y N mÃ¡s`
  - Aplicar en vistas de logs, alertas y agentes

- [ ] **Teclado de volver al menÃº** en todas las vistas
  - Helper `back_to_menu_row()` que retorna la fila con `[ð MenÃº]`
  - `[ð Refrescar]` en vistas que tienen datos variables (alertas, overview, logs)

- [ ] **Registro del handler en bootstrap**
  - Verificar que `DashboardHandler` estÃ¡ registrado antes que el `QueryHandler` genÃ©rico
  - El `CallbackQueryHandler(pattern=r"^dash:")` no debe colisionar con `page:` existente

### Entregables
- [ ] NavegaciÃ³n fluida entre todas las secciones
- [ ] Errores no rompen el chat, solo muestran mensaje amigable
- [ ] Todos los callbacks tienen `answer()` inmediato

---

## Estructura de archivos

```
src/bot/dashboard/
âââ __init__.py
âââ dashboard_handler.py   â dispatch de callbacks dash:*
âââ dashboard_service.py   â queries a BD (async)
âââ views.py               â funciones de renderizado (texto + keyboard)
```

**Callbacks registrados:**
```
dash:menu
dash:overview:{hoy|ayer|7d|30d}
dash:alerts
dash:logs:{page}
dash:agents
dash:users
dash:knowledge
dash:refresh
```

---

## Riesgos y Mitigaciones

| Riesgo | Probabilidad | Impacto | MitigaciÃ³n |
|--------|--------------|---------|------------|
| ~~Queries bloquean loop asyncio~~ | ~~Media~~ | ~~Alto~~ | Resuelto: `execute_query_async` ya usa `asyncio.to_thread` internamente |
| `asyncio.run()` copiado de Flask al service | Alta | Alto | En el service usar `await` directo, no `asyncio.run()` |
| `db_registry` no disponible para alertas | Alta | Alto | Inyectar en `bot_data` en Fase 1 (tarea explÃ­cita) |
| Spinner infinito en botÃ³n por falta de `answer()` | Alta | Medio | `query.answer()` como primera lÃ­nea del handler, siempre |
| Mensaje supera 4096 chars | Alta | Medio | Truncar lista con contador "y N mÃ¡s" |
| Rate limiting de Telegram en `edit_message_text` | Media | Bajo | Catch de `RetryAfter` en Fase 5, reintentar despuÃ©s del delay |
| ColisiÃ³n de CallbackQueryHandler | Baja | Medio | Registrar `dash:` handler antes del handler genÃ©rico |
| AlertRepository no disponible (BD monitoreo offline) | Media | Bajo | Try/except ya en dashboard_api, replicar patrÃ³n; mostrar "Sin datos" |

---

## Criterios de Ãxito

- [ ] `/dashboard` solo funciona para admins
- [ ] Todas las 6 secciones muestran datos reales de la BD
- [ ] La navegaciÃ³n edita el mensaje existente (no genera spam)
- [ ] Los filtros de perÃ­odo en Overview cambian los datos correctamente
- [ ] Los logs se pagina correctamente (50 logs, 8 por pÃ¡gina = 7 pÃ¡ginas)
- [ ] Alertas muestran estado en tiempo real con el mismo origen que el dashboard web

---

## Historial de Cambios

| Fecha | Cambio | Autor |
|-------|--------|-------|
| 2026-04-22 | CreaciÃ³n del plan | Angel David Roque Ayala |
| 2026-04-22 | RevisiÃ³n: gaps de db_registry, answer() obligatorio, asyncio.run, cache admin | Angel David Roque Ayala |
