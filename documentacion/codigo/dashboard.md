[Docs](../index.md) › [Código](README.md) › Dashboard Telegram

# Dashboard Telegram (BOT-41)

Panel de administración inline en Telegram. Permite a los administradores consultar
métricas, alertas, logs y configuración del bot sin salir del chat, usando mensajes
editables con teclados inline.

---

## Módulo

```
src/bot/dashboard/
├── __init__.py
├── dashboard_handler.py   ← CallbackQueryHandler (despacho y auth)
├── dashboard_service.py   ← Queries async (lógica de datos)
└── views.py               ← Render de texto HTML + InlineKeyboardMarkup
```

---

## Flujo de una interacción

```
Usuario pulsa botón → callback_data "dash:section:param"
    │
    ▼
DashboardHandler.handle()
    1. query.answer()              — evita spinner infinito en el botón
    2. Auth guard (user_data cache) — verifica admin una sola vez por sesión
    3. DashboardService(db_manager, db_registry)
    4. _dispatch(section, parts, service) → (text, keyboard)
    5. query.edit_message_text(text, keyboard, parse_mode="HTML")
```

El mensaje se **edita** en lugar de enviarse como nuevo — evita spam en el chat.

---

## Esquema de callback data

```
dash:menu
dash:overview:hoy
dash:overview:ayer
dash:overview:7d
dash:overview:30d
dash:alerts
dash:logs:1
dash:logs:2
dash:agents
dash:users
dash:knowledge
dash:noop          ← botón sin acción (labels de header)
```

---

## Auth guard

El guard verifica que el `chat_id` esté en la lista de admins, cacheando el resultado
en `context.user_data["is_admin"]` para no ejecutar la query en cada pulsación:

```python
is_admin = context.user_data.get("is_admin")
if is_admin is None:
    admin_ids = await UserQueryRepository(db_manager).get_admin_chat_ids()
    is_admin = chat_id in admin_ids
    context.user_data["is_admin"] = is_admin
```

Si no es admin, edita el mensaje con un aviso y no procede al dispatch.

---

## DashboardService

Wrapper async sobre las queries SQL del dashboard. Acepta `db_manager` (BD principal)
y `db_registry` (multi-conexión, para alertas de monitoreo).

| Método | Descripción |
|--------|-------------|
| `get_overview(periodo)` | Métricas del período: mensajes, usuarios activos, errores, costo, p50/p90, top agentes. Períodos: `hoy`, `ayer`, `7d`, `30d` |
| `get_alerts()` | Alertas activas de BAZ y EKT combinadas (usa `AlertRepository.get_active_events_all()`). Requiere `db_registry` |
| `get_logs(page, page_size=8)` | Últimas 50 interacciones paginadas de 8 en 8 |
| `get_agents()` | Agentes activos con configuración y requests del día |
| `get_users()` | Hasta 15 usuarios Telegram (vía `BotIAv2_sp_GetAllUsuariosTelegram`) |
| `get_knowledge()` | Estadísticas de categorías de base de conocimiento |

Las queries paralelas dentro de cada método usan `asyncio.gather()` internamente
via el helper `_gather(*coros)`.

---

## Registro

`register_dashboard_handlers(application)` en `dashboard_handler.py` registra un
`CallbackQueryHandler` con patrón `^dash:`. Se llama desde `telegram_bot.py` al
construir la aplicación.

Las deps `db_manager` y `db_registry` se inyectan en `context.bot_data` al arrancar
el bot en `src/bootstrap/factory.py`.

---

## Vistas disponibles

| Vista | Datos mostrados |
|-------|-----------------|
| Menú principal | Botones de navegación a todas las secciones |
| Overview | Total mensajes (% vs período anterior), usuarios activos, errores, costo USD, latencia p50/p90, top agentes con tasa de éxito |
| Alertas | Conteo de críticos (prioridad ≥ 4) y warnings; tabla de hasta 20 alertas con equipo, IP, sensor, status |
| Logs | Tabla paginada de interacciones: username, query (50 chars), agente, duración, estado, costo |
| Agentes | Configuración de cada agente activo: temperatura, max iteraciones, tools, requests hoy |
| Usuarios | Hasta 15 usuarios: nombre, rol, estado, verificado, última actividad |
| Base de conocimiento | Categorías con íconos y cantidad de entradas; total y búsquedas del día |

---

## Agregar una nueva sección

1. Agregar un método en `DashboardService.get_<seccion>()` con la query correspondiente
2. Agregar una función `render_<seccion>(data) -> (str, InlineKeyboardMarkup)` en `views.py`
3. Agregar el caso `if section == "<seccion>":` en `_dispatch()` en `dashboard_handler.py`
4. Agregar el botón con `callback_data="dash:<seccion>"` en `render_menu()` en `views.py`

---

**← Anterior** [Pipeline y factory](pipeline.md) · [Índice](README.md) · **Siguiente →** [Tools](tools.md)
