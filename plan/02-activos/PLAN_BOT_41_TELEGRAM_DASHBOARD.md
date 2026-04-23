# Plan: BOT-41 Dashboard Inline Keyboard para Telegram

> **Estado**: ⚪ No iniciado
> **Última actualización**: 2026-04-22
> **Rama Git**: `feature/bot-41-telegram-dashboard`

## Resumen de Progreso

| Fase | Progreso | Estado |
|------|----------|--------|
| Fase 1: Infraestructura base | ░░░░░░░░░░ 0% | ⏳ Pendiente |
| Fase 2: Menú principal + Overview | ░░░░░░░░░░ 0% | ⏳ Pendiente |
| Fase 3: Alertas + Logs | ░░░░░░░░░░ 0% | ⏳ Pendiente |
| Fase 4: Agentes + Usuarios + Knowledge | ░░░░░░░░░░ 0% | ⏳ Pendiente |
| Fase 5: Navegación + UX polish | ░░░░░░░░░░ 0% | ⏳ Pendiente |

**Progreso Total**: ░░░░░░░░░░ 0% (0/30 tareas)

---

## Descripción

Implementar un dashboard interactivo en Telegram usando InlineKeyboardMarkup
que permita a los administradores consultar las mismas métricas del dashboard
web sin salir del bot. Navega entre secciones con botones, refresca datos
y pagina listas directamente desde el chat.

**Secciones a cubrir:**
- Resumen general (Overview) con filtros de período
- Alertas activas (críticas y warnings)
- Logs de interacciones recientes (paginado)
- Agentes activos con detalle básico
- Usuarios registrados
- Base de conocimiento (categorías y conteos)

**Principios de diseño:**
- Solo admins tienen acceso (`get_admin_chat_ids`)
- Reutilizar la lógica de queries de `dashboard_api.py` directamente (no HTTP)
- Editar el mensaje en lugar de enviar uno nuevo (`edit_message_text`)
- Callbacks con prefijo `dash:` para namespace limpio
- Timeout graceful: si el callback es muy viejo, notificar con `answer_callback_query`

---

## Fase 1: Infraestructura base

**Objetivo**: Esqueleto del sistema — comando, service, handler de callbacks y registro
**Dependencias**: Ninguna

### Tareas

- [ ] **Inyectar `db_registry` en `bot_data`** — requerido para la vista de alertas
  - Archivo: `src/bot/telegram_bot.py` línea ~56
  - Agregar: `self.application.bot_data['db_registry'] = self.db_registry`
  - Sin esto, `DashboardService.get_alerts()` no puede conectarse a la BD de monitoreo

- [ ] **Crear `DashboardService`** — wrapper async sobre las queries de `dashboard_api.py`
  - Archivo: `src/bot/dashboard/dashboard_service.py`
  - Métodos: `get_overview(periodo)`, `get_alerts()`, `get_logs(page)`, `get_agents()`, `get_users()`, `get_knowledge()`
  - Usar `db_manager.execute_query_async()` (ya existe, usa `asyncio.to_thread` internamente)
  - Para alertas: `await repo.get_active_events_all()` directamente — NO copiar el `asyncio.run()` de `dashboard_api.py` (es un workaround de Flask síncrono, aquí ya somos async)
  - No duplicar SQL: extraer las queries de `dashboard_api.py` a este service

- [ ] **Crear `DashboardHandler`** — recibe callbacks `dash:*` y despacha a la vista correcta
  - Archivo: `src/bot/dashboard/dashboard_handler.py`
  - Registrar como `CallbackQueryHandler(pattern=r"^dash:")`
  - Dispatch por token: `dash:menu`, `dash:overview:hoy`, `dash:alerts`, `dash:logs:1`, etc.
  - Auth guard: verificar que `effective_user.id` está en `get_admin_chat_ids`
  - **Regla de oro**: llamar `await query.answer()` SIEMPRE como primera línea del handler, incluso antes del auth check. Si el callback no responde, Telegram muestra spinner infinito.
  - **No usar `require_auth`**: el decorador usa `update.message` que es `None` en callbacks. El guard propio es la única barrera.
  - Cache del admin check: guardar resultado en `context.user_data["is_admin"]` la primera vez para no hacer una query a BD en cada pulsación de botón.

- [ ] **Crear comando `/dashboard`** — punto de entrada, solo admins
  - Archivo: agregar en `src/bot/handlers/command_handlers.py`
  - Enviar mensaje con el menú principal inline
  - Si no es admin: responder con `⛔ Solo administradores`

- [ ] **Registrar handlers** en `src/bot/telegram_bot.py`
  - Importar y registrar `DashboardHandler` como `CallbackQueryHandler`
  - Agregar `CommandHandler("dashboard", dashboard_command)`

- [ ] **Crear `__init__.py`** del módulo dashboard
  - Archivo: `src/bot/dashboard/__init__.py`

### Entregables
- [ ] Módulo `src/bot/dashboard/` creado y registrado
- [ ] `/dashboard` responde a admins, rechaza a no-admins

---

## Fase 2: Menú principal + Overview

**Objetivo**: Menú navegable y sección de resumen con filtros de período
**Dependencias**: Fase 1

### Tareas

- [ ] **Implementar vista del menú principal**
  - Archivo: `src/bot/dashboard/views.py`
  - Texto: nombre del bot, fecha/hora actual, versión
  - Keyboard: `[📊 Overview] [🚨 Alertas]` / `[📋 Logs] [🤖 Agentes]` / `[👥 Usuarios] [📚 Knowledge]` / `[🔄 Refrescar]`
  - Callbacks: `dash:menu` (self), `dash:overview:hoy`, `dash:alerts`, `dash:logs:1`, `dash:agents`, `dash:users`, `dash:knowledge`

- [ ] **Implementar vista Overview**
  - Archivo: `src/bot/dashboard/views.py`
  - Datos de `DashboardService.get_overview(periodo)`:
    mensajes + % cambio, usuarios activos, errores, costo USD, p50/p90
  - Top 3 agentes por requests (nombre + requests + % éxito)
  - Keyboard de filtros: `[Hoy ✓] [Ayer] [7d] [30d]` + `[🔙 Menú]`
  - Callbacks: `dash:overview:hoy`, `dash:overview:ayer`, `dash:overview:7d`, `dash:overview:30d`
  - Marcar visualmente el período activo con ✓

- [ ] **Implementar handler dispatch para overview**
  - En `DashboardHandler`: detectar `dash:overview:{periodo}` y renderizar vista
  - Editar el mensaje con `query.edit_message_text()`

### Entregables
- [ ] `/dashboard` muestra menú navegable
- [ ] Overview cambia datos al presionar filtros de período

---

## Fase 3: Alertas + Logs

**Objetivo**: Sección de alertas en tiempo real y log de interacciones paginado
**Dependencias**: Fase 1

### Tareas

- [ ] **Implementar vista de Alertas**
  - Archivo: `src/bot/dashboard/views.py`
  - Datos de `DashboardService.get_alerts()`:
    total críticos, total warnings, lista de alertas (máx 10 en mensaje)
  - Formato por alerta: equipo, IP, sensor, status, prioridad
  - Keyboard: `[🔄 Refrescar] [🔙 Menú]`
  - Si no hay alertas: mensaje `✅ Sin alertas activas`

- [ ] **Implementar vista de Logs (lista paginada)**
  - Archivo: `src/bot/dashboard/views.py`
  - `DashboardService.get_logs(page, page_size=8)`: top 50 logs, paginar localmente
  - Por log: username, query truncada (40 chars), agente, duración, estado ✅/❌
  - Keyboard: paginación `[◀] [Página N/M] [▶]` + `[🔙 Menú]`
  - Callbacks: `dash:logs:{page}`

- [ ] **Implementar handler dispatch para alertas y logs**
  - Detectar `dash:alerts` y `dash:logs:{page}`
  - Llamar al service y renderizar la vista correspondiente

### Entregables
- [ ] Alertas muestran estado actual del monitoreo
- [ ] Logs navegables con paginación funcional

---

## Fase 4: Agentes + Usuarios + Knowledge

**Objetivo**: Completar las secciones restantes del dashboard
**Dependencias**: Fase 1

### Tareas

- [ ] **Implementar vista de Agentes**
  - Archivo: `src/bot/dashboard/views.py`
  - `DashboardService.get_agents()`: lista de agentes activos
  - Por agente: nombre, descripción, modelo, temperatura, requests hoy, % éxito, tools (count)
  - Keyboard: `[🔄 Refrescar] [🔙 Menú]`

- [ ] **Implementar vista de Usuarios**
  - Datos de `DashboardService.get_users()`
  - Por usuario: nombre, rol, estado, última actividad
  - Máx 15 usuarios por mensaje — decisión deliberada: el SP puede retornar mucha gente,
    se mostrará solo los últimos 15 activos; paginación queda como mejora futura
  - Keyboard: `[🔄 Refrescar] [🔙 Menú]`

- [ ] **Implementar vista de Knowledge**
  - Datos de `DashboardService.get_knowledge()`
  - Resumen: total categorías, total entradas, búsquedas hoy
  - Lista de categorías: icono + nombre + cantidad de entradas
  - Keyboard: `[🔄 Refrescar] [🔙 Menú]`

- [ ] **Registrar dispatch para las 3 secciones**
  - Detectar `dash:agents`, `dash:users`, `dash:knowledge` en `DashboardHandler`

### Entregables
- [ ] Las 6 secciones del dashboard son accesibles desde el menú
- [ ] Todos los datos provienen de la BD sin HTTP calls

---

## Fase 5: Navegación + UX polish

**Objetivo**: Experiencia fluida, errores manejados, feedback inmediato
**Dependencias**: Fases 2, 3, 4

### Tareas

- [ ] **`dash:refresh` genérico** — refrescar la vista actual sin volver al menú
  - Guardar `context.user_data["dash_current_view"]` con la última vista
  - `dash:refresh` re-llama la misma vista con datos nuevos

- [ ] **Feedback inmediato en callbacks lentos**
  - Llamar `query.answer("Cargando...")` antes de las queries a BD
  - En error de BD: `query.answer("Error al cargar datos", show_alert=True)` + log

- [ ] **Timeout graceful**
  - Si `edit_message_text` falla con `MessageNotModified`: ignorar silenciosamente
  - Si el mensaje es demasiado viejo (error de Telegram): responder con nuevo mensaje

- [ ] **Límite de longitud de mensaje**
  - Si el texto supera 4096 chars: truncar lista y agregar `… y N más`
  - Aplicar en vistas de logs, alertas y agentes

- [ ] **Teclado de volver al menú** en todas las vistas
  - Helper `back_to_menu_row()` que retorna la fila con `[🔙 Menú]`
  - `[🔄 Refrescar]` en vistas que tienen datos variables (alertas, overview, logs)

- [ ] **Registro del handler en bootstrap**
  - Verificar que `DashboardHandler` está registrado antes que el `QueryHandler` genérico
  - El `CallbackQueryHandler(pattern=r"^dash:")` no debe colisionar con `page:` existente

### Entregables
- [ ] Navegación fluida entre todas las secciones
- [ ] Errores no rompen el chat, solo muestran mensaje amigable
- [ ] Todos los callbacks tienen `answer()` inmediato

---

## Estructura de archivos

```
src/bot/dashboard/
├── __init__.py
├── dashboard_handler.py   ← dispatch de callbacks dash:*
├── dashboard_service.py   ← queries a BD (async)
└── views.py               ← funciones de renderizado (texto + keyboard)
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

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|--------------|---------|------------|
| ~~Queries bloquean loop asyncio~~ | ~~Media~~ | ~~Alto~~ | Resuelto: `execute_query_async` ya usa `asyncio.to_thread` internamente |
| `asyncio.run()` copiado de Flask al service | Alta | Alto | En el service usar `await` directo, no `asyncio.run()` |
| `db_registry` no disponible para alertas | Alta | Alto | Inyectar en `bot_data` en Fase 1 (tarea explícita) |
| Spinner infinito en botón por falta de `answer()` | Alta | Medio | `query.answer()` como primera línea del handler, siempre |
| Mensaje supera 4096 chars | Alta | Medio | Truncar lista con contador "y N más" |
| Rate limiting de Telegram en `edit_message_text` | Media | Bajo | Catch de `RetryAfter` en Fase 5, reintentar después del delay |
| Colisión de CallbackQueryHandler | Baja | Medio | Registrar `dash:` handler antes del handler genérico |
| AlertRepository no disponible (BD monitoreo offline) | Media | Bajo | Try/except ya en dashboard_api, replicar patrón; mostrar "Sin datos" |

---

## Criterios de Éxito

- [ ] `/dashboard` solo funciona para admins
- [ ] Todas las 6 secciones muestran datos reales de la BD
- [ ] La navegación edita el mensaje existente (no genera spam)
- [ ] Los filtros de período en Overview cambian los datos correctamente
- [ ] Los logs se pagina correctamente (50 logs, 8 por página = 7 páginas)
- [ ] Alertas muestran estado en tiempo real con el mismo origen que el dashboard web

---

## Historial de Cambios

| Fecha | Cambio | Autor |
|-------|--------|-------|
| 2026-04-22 | Creación del plan | Angel David Roque Ayala |
| 2026-04-22 | Revisión: gaps de db_registry, answer() obligatorio, asyncio.run, cache admin | Angel David Roque Ayala |
