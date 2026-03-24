# PLAN: Cache con evicción automática en MemoryService

> **Objetivo**: Prevenir el memory leak del cache de MemoryService implementando evicción LRU
> **Rama**: `feature/arq-06-cache-eviccion`
> **Prioridad**: 🟠 Alta
> **Progreso**: 100% (5/5)

---

## Contexto

`src/memory/memory_service.py` tiene un cache en memoria:

```python
self._cache: dict[str, CacheEntry] = {}
self.max_cache_size = max_cache_size  # 1000
```

El problema: **`max_cache_size` nunca se revisa**. El cache crece indefinidamente sin importar cuántos usuarios haya. En producción con 10,000 usuarios activos, el cache podría consumir varios GB de RAM.

---

## Solución propuesta

Usar `functools.lru_cache` o implementar un diccionario LRU ordenado con `collections.OrderedDict`. Python 3.8+ incluye `functools.lru_cache` pero no maneja TTL (tiempo de vida). La solución correcta es un LRU con TTL.

La clase `CacheEntry` en `memory_entity.py` ya tiene `is_expired()` y `time_remaining()`, lo que facilita la implementación.

---

## Archivos involucrados

- `src/memory/memory_service.py` — implementar evicción
- `src/memory/memory_entity.py` — `CacheEntry` (ya tiene TTL)
- `tests/test_memory_service.py` — tests de evicción

---

## Tareas

- [x] **6.1** Reemplazar `dict` por `collections.OrderedDict` en `MemoryService.__init__()`
- [x] **6.2** Implementar `_evict_if_needed()`: primero expiradas, luego LRU con `popitem(last=False)`
- [x] **6.3** `_add_to_cache()` llama `_evict_if_needed()` + `move_to_end()` en cada set
- [x] **6.4** `_get_from_cache()` llama `move_to_end()` en hits; `get_cache_stats()` incluye hit_rate, cache_hits, cache_misses
- [x] **6.5** 6 tests en `TestMemoryServiceCacheEviction`: max_size, expiradas primero, LRU, hit rate, clear reset, evict manual

---

## Criterios de aceptación

- El cache nunca supera `max_cache_size` entradas
- Las entradas expiradas son las primeras en ser eliminadas
- En producción con cualquier número de usuarios, uso de RAM es estable
- `get_cache_stats()` muestra métricas útiles
