# PLAN: Cache de respuestas del LLM

> **Objetivo**: Reducir costos de API y latencia cacheando respuestas del LLM para preguntas repetidas
> **Rama**: `feature/fun-17-cache-llm`
> **Prioridad**: 🟢 Funcional
> **Progreso**: 0% (0/7)

---

## Contexto

Actualmente cada mensaje del usuario genera una llamada nueva a la API de OpenAI, aunque sea una pregunta idéntica a una respondida hace 5 minutos. En un bot empresarial, muchas preguntas son recurrentes:

- "¿Cuál es el horario de trabajo?"
- "¿Cómo solicito vacaciones?"
- "¿Cuál es el teléfono de IT?"

Cachear estas respuestas puede reducir costos de API en un 30-50% y la latencia de respuesta de ~2s a ~50ms.

---

## Estrategia de cache

- **Clave de cache**: Hash del prompt completo (query normalizada + contexto de knowledge base)
- **TTL**: Configurable, default 1 hora (las políticas de empresa no cambian frecuentemente)
- **Invalidación manual**: Comando `/clear_cache` para admins
- **No cachear**: Preguntas con datos personales del usuario (ej. "¿cuántos días de vacaciones me quedan a mí?")

---

## Archivos involucrados

- `src/agents/providers/openai_provider.py` — interceptar llamadas al LLM
- `src/agents/react/agent.py` — lógica de decisión de qué cachear
- `src/config/settings.py` — `LLM_CACHE_ENABLED`, `LLM_CACHE_TTL_SECONDS`
- `src/bot/handlers/command_handlers.py` — comando `/clear_cache` para admins

---

## Tareas

- [ ] **17.1** Crear `src/agents/cache/llm_cache.py` con clase `LLMCache`:
  - `get(prompt_hash)` → respuesta o None
  - `set(prompt_hash, response, ttl)`
  - `invalidate_all()`
  - `get_stats()` → hit rate, total entries
- [ ] **17.2** Implementar detección de queries "personalizadas" que no deben cachearse (contienen pronombres personales: "yo", "mi", "mis", "me")
- [ ] **17.3** Integrar `LLMCache` en `openai_provider.py` como wrapper transparente
- [ ] **17.4** Agregar `LLM_CACHE_ENABLED` y `LLM_CACHE_TTL_SECONDS` en `settings.py`
- [ ] **17.5** Implementar comando `/cache_stats` para admins (hit rate, ahorros estimados)
- [ ] **17.6** Implementar comando `/clear_cache` para admins
- [ ] **17.7** Agregar tests con mocks del provider para verificar hits y misses

---

## Criterios de aceptación

- Preguntas idénticas dentro del TTL no generan llamada al LLM
- Preguntas personalizadas (con "mi", "yo") nunca se cachean
- El hit rate es visible para admins
- El cache es desactivable con `LLM_CACHE_ENABLED=false`
