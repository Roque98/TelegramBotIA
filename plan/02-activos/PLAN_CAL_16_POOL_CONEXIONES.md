# PLAN: Optimizar pool de conexiones a base de datos

> **Objetivo**: Configurar el pool de conexiones de SQL Server para soportar carga multi-usuario real
> **Rama**: `feature/cal-16-pool-conexiones`
> **Prioridad**: 🟡 Media
> **Progreso**: 0% (0/5)

---

## Contexto

`src/database/connection.py:24-36` tiene el pool configurado con valores muy conservadores:

```python
pool_size=5, max_overflow=10, pool_timeout=20,
pool_recycle=3600, pool_pre_ping=True
```

Con `pool_size=5`, si hay 6 usuarios haciendo consultas simultáneamente, el 6to usuario espera hasta que uno de los 5 slots se libere. Con `pool_timeout=20`, si espera más de 20 segundos, recibe un error.

Para un bot de empresa con decenas de usuarios concurrentes, esto es insuficiente.

---

## Valores recomendados

| Parámetro | Actual | Recomendado | Razón |
|-----------|--------|-------------|-------|
| `pool_size` | 5 | 20 | Conexiones permanentes base |
| `max_overflow` | 10 | 20 | Conexiones extra en picos |
| `pool_timeout` | 20 | 30 | Más tiempo de espera antes de error |
| `pool_recycle` | 3600 | 1800 | Reciclar más frecuente para evitar conexiones muertas |

---

## Archivos involucrados

- `src/database/connection.py`
- `src/config/settings.py` — hacer el pool configurable desde `.env`
- `.env.example` — documentar variables del pool

---

## Tareas

- [ ] **16.1** Agregar variables de configuración en `settings.py`:
  - `DB_POOL_SIZE` (default: 20)
  - `DB_MAX_OVERFLOW` (default: 20)
  - `DB_POOL_TIMEOUT` (default: 30)
  - `DB_POOL_RECYCLE` (default: 1800)
- [ ] **16.2** Actualizar `connection.py` para leer los valores desde `settings`
- [ ] **16.3** Agregar logging del estado del pool al arrancar: tamaño, overflow configurado
- [ ] **16.4** Agregar método `get_pool_status()` en `DatabaseManager` que retorne conexiones activas/disponibles
- [ ] **16.5** Documentar en `.env.example` cómo ajustar el pool según el número de usuarios esperados

---

## Criterios de aceptación

- El pool es configurable desde `.env` sin tocar código
- Los parámetros por defecto soportan al menos 20 usuarios concurrentes
- El estado del pool queda registrado en los logs al iniciar el bot
