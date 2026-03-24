# PLAN: Dashboard web de monitoreo

> **Objetivo**: Crear un dashboard web simple para visualizar métricas y estado del bot en tiempo real
> **Rama**: `feature/fun-22-dashboard`
> **Prioridad**: 🟢 Funcional
> **Progreso**: 0% (0/8)

---

## Contexto

El proyecto ya tiene un módulo `src/observability/` con código de métricas, pero no hay forma de visualizarlas. Actualmente hay que revisar logs manualmente para saber si el bot funciona bien.

Un dashboard web simple permitiría ver en tiempo real:
- Si el bot está activo
- Cuántas respuestas se han dado hoy
- Tiempo promedio de respuesta
- Errores recientes
- Estado de la conexión a BD

---

## Stack tecnológico propuesto

- **Backend**: Flask (ya instalado) + endpoint `/metrics`
- **Frontend**: HTML simple con Chart.js (sin framework frontend, sin build step)
- **Datos**: Leer de `observability/` + BD
- **Autenticación**: Token simple en header (mismo token del endpoint de chat)

---

## Pantallas del dashboard

1. **Resumen general**: uptime, mensajes hoy, usuarios activos, errores hoy
2. **Gráfica de actividad**: mensajes por hora (últimas 24h)
3. **Tiempo de respuesta**: percentil 50/90/99 del día
4. **Errores recientes**: últimos 10 errores con timestamp y tipo
5. **Estado de servicios**: BD, LLM API, bot Telegram (verde/rojo)

---

## Archivos involucrados

- `src/api/` — nuevos endpoints `/metrics` y `/dashboard`
- `src/observability/` — fuente de datos
- `src/templates/dashboard.html` — frontend (nuevo)
- `src/config/settings.py` — `DASHBOARD_ENABLED`, `DASHBOARD_TOKEN`

---

## Tareas

- [ ] **22.1** Crear endpoint `GET /metrics` que retorne JSON con todas las métricas actuales
- [ ] **22.2** Crear endpoint `GET /dashboard` que sirva el HTML del dashboard
- [ ] **22.3** Crear `src/templates/dashboard.html` con:
  - Cards de resumen (uptime, mensajes, errores)
  - Gráfica de actividad por hora con Chart.js (CDN)
  - Tabla de errores recientes
  - Indicadores de estado de servicios (verde/rojo)
- [ ] **22.4** Implementar auto-refresh del dashboard cada 30 segundos (JavaScript simple)
- [ ] **22.5** Agregar autenticación básica al dashboard (token en query string o header)
- [ ] **22.6** Agregar `DASHBOARD_ENABLED` y `DASHBOARD_TOKEN` en `settings.py`
- [ ] **22.7** Crear endpoint `GET /health` simple (sin auth) que retorne `{"status": "ok"}` para monitoreo externo
- [ ] **22.8** Documentar URL del dashboard en README

---

## Criterios de aceptación

- Dashboard accesible en `http://host:port/dashboard` con token correcto
- Los datos se actualizan automáticamente cada 30 segundos
- El endpoint `/health` responde sin autenticación (para load balancers)
- Si `DASHBOARD_ENABLED=false`, los endpoints retornan 404
