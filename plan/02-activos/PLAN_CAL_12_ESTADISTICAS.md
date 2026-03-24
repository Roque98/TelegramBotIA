# PLAN: Estadísticas reales en el bot

> **Objetivo**: Implementar estadísticas reales de uso en lugar de datos hardcodeados
> **Rama**: `feature/cal-12-estadisticas`
> **Prioridad**: 🟡 Media
> **Progreso**: 0% (0/6)

---

## Contexto

`src/bot/handlers/command_handlers.py:216` tiene un TODO sin resolver:

```python
# TODO: Implementar estadísticas reales
stats = {
    "total_messages": 0,
    "total_users": 0,
    "uptime": "N/A"
}
```

Actualmente el comando `/stats` (o equivalente) muestra datos en cero, lo cual es inútil para monitorear el bot.

---

## Datos a mostrar

- Total de mensajes procesados (histórico y últimas 24h)
- Total de usuarios activos (últimas 24h, 7 días, 30 días)
- Total de consultas a la knowledge base
- Tiempo promedio de respuesta del LLM
- Uptime del bot desde el último reinicio
- Errores en las últimas 24h

---

## Archivos involucrados

- `src/bot/handlers/command_handlers.py` — implementar comando `/stats`
- `src/memory/memory_repository.py` — queries de conteo
- `src/observability/` — leer métricas existentes
- BD: tabla de logs de interacciones (ya existe en `memory_repository.py`)

---

## Tareas

- [ ] **12.1** Revisar qué datos ya están almacenados en BD (interacciones, timestamps)
- [ ] **12.2** Crear método `get_usage_stats(days=1)` en `memory_repository.py` con queries de conteo
- [ ] **12.3** Crear método `get_uptime()` en un módulo de estado del bot (o `observability/`)
- [ ] **12.4** Implementar el comando `/stats` en `command_handlers.py` usando datos reales
- [ ] **12.5** Restringir `/stats` solo a usuarios administradores (verificar con `user_service.py`)
- [ ] **12.6** Agregar tests con mocks de BD para las queries de estadísticas

---

## Criterios de aceptación

- `/stats` muestra datos reales obtenidos de la BD
- Solo admins pueden ver las estadísticas
- Los números se actualizan en cada llamada (no cacheados de forma permanente)
