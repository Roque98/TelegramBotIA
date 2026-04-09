# PLAN: Estadísticas reales en el bot

> **Objetivo**: Implementar estadísticas reales de uso en lugar de datos hardcodeados
> **Rama**: `feature/cal-12-estadisticas`
> **Prioridad**: 🟡 Media
> **Progreso**: 100% (6/6) ✅

---

## Contexto

`src/bot/handlers/command_handlers.py:216` tenía un TODO sin resolver con datos en cero.
Resuelto: `/stats` ahora consulta `MemoryRepository.get_user_stats()` con datos reales de BD.

---

## Datos mostrados

- Total de consultas del usuario (histórico)
- Consultas exitosas y errores con tasa de éxito
- Tiempo promedio de respuesta
- Tiempo mínimo y máximo
- Fecha de primera y última consulta

---

## Tareas

- [x] **12.1** Revisar qué datos ya están almacenados en BD (interacciones, timestamps)
- [x] **12.2** `get_user_stats(user_id)` en `MemoryRepository` con queries de conteo
- [x] **12.3** Uptime no implementado (reemplazado por métricas de usuario más útiles)
- [x] **12.4** Comando `/stats` en `command_handlers.py` usando datos reales
- [x] **12.5** Sin restricción a admins — cada usuario ve sus propias estadísticas
- [x] **12.6** Tests con mocks en `tests/handlers/test_command_handlers.py`

---

## Criterios de aceptación

- [x] `/stats` muestra datos reales obtenidos de la BD
- [x] Los números se actualizan en cada llamada (no cacheados)
