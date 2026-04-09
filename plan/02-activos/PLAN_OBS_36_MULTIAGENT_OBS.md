# PLAN_OBS_36 — Observabilidad para Multi-Agente

**ID**: OBS-36
**Tipo**: Observabilidad
**Rama**: `feature/obs-36-multiagent-observability`
**Estado**: En progreso
**Creado**: 2026-04-09

---

## Contexto

Con ARQ-35 implementado (orchestrator N-way con agentes dinámicos desde BD), los logs quedaron
incompletos: no se persiste la decisión de ruteo, la confianza del clasificador, tokens agregados
por request, ni si se usó fallback. Los métodos de cache metrics existen pero nunca se llaman.

---

## Fases

### Fase 1 — Extensión de tablas existentes
- [ ] Crear `database/migrations/obs36_multiagent_observability.sql`
  - ALTERs en `BotIAv2_InteractionLogs`: totalInputTokens, totalOutputTokens, llmIteraciones,
    usedFallback, classifyMs, agentConfidence, costUSD
  - Nueva tabla `BotIAv2_AgentRouting`

### Fase 2 — IntentClassifier retorna confianza
- [ ] Modificar `src/agents/orchestrator/intent_classifier.py`
  - `classify()` retorna `ClassifyResult(agent_name, confidence, alternatives)`
  - Nuevo dataclass/Pydantic model `ClassifyResult`
- [ ] Actualizar `src/agents/orchestrator/orchestrator.py`
  - Consumir `ClassifyResult` en lugar de `str`
  - Pasar confidence y alternatives al response

### Fase 3 — Persistir routing en BD
- [ ] Actualizar `src/infra/observability/sql_repository.py`
  - Nuevo método `save_agent_routing()`
  - Agregar campos nuevos a `save_interaction_log()`
- [ ] Actualizar `src/agents/orchestrator/orchestrator.py`
  - Llamar `save_agent_routing()` en cada request
- [ ] Actualizar `src/pipeline/handler.py`
  - Pasar totalInputTokens, totalOutputTokens, llmIteraciones, usedFallback, costUSD

### Fase 4 — Cache metrics
- [ ] Instrumentar `src/domain/agent_config/agent_config_service.py`
  - `record_cache_hit/miss("agent_config")` en `get_active_agents()`
- [ ] Instrumentar `src/agents/factory/agent_builder.py`
  - `record_cache_hit/miss("agent_instance")` en `get_or_build()`

### Fase 5 — Analytics SQL
- [ ] Crear `scripts/analytics_multiagent.sql`
  - Distribución de ruteo por agente
  - Latencia promedio classify + react por agente
  - Costo USD por agente (últimos 7 días)
  - Tasa de fallback por hora
  - Top errores por agente

---

## Archivos clave

| Archivo | Cambio |
|---------|--------|
| `database/migrations/obs36_multiagent_observability.sql` | Nuevo |
| `src/agents/orchestrator/intent_classifier.py` | Retornar ClassifyResult |
| `src/agents/orchestrator/orchestrator.py` | Consumir ClassifyResult, persistir routing |
| `src/infra/observability/sql_repository.py` | save_agent_routing(), campos nuevos |
| `src/pipeline/handler.py` | Pasar campos nuevos a save_interaction_log() |
| `src/domain/agent_config/agent_config_service.py` | Cache metrics |
| `src/agents/factory/agent_builder.py` | Cache metrics |
| `scripts/analytics_multiagent.sql` | Nuevo |
