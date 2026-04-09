# Plan: ARQ-35 Orchestrator con Agentes Dinámicos

> **Estado**: ✅ Completado
> **Última actualización**: 2026-04-09 (implementación completa)
> **Rama Git**: `feature/arq-35-dynamic-orchestrator`

## Resumen de Progreso

| Fase | Progreso | Estado |
|------|----------|--------|
| Fase 1: Schema de BD | ██████████ 100% | ✅ Completado |
| Fase 2: Dominio (entity + repo + service) | ██████████ 100% | ✅ Completado |
| Fase 3: Agent builder dinámico | ██████████ 100% | ✅ Completado |
| Fase 4: Orchestrator N-way | ██████████ 100% | ✅ Completado |
| Fase 5: Admin tooling y recarga | ██████████ 100% | ✅ Completado |
| Fase 6: Tests y migración | ██████████ 100% | ✅ Completado |

**Progreso Total**: ██████████ 100% (36/36 tareas)

---

## Descripción

Evolucionar el `AgentOrchestrator` existente (ARQ-30, binario casual/data)
a un sistema de N agentes especializados cuyos prompts, herramientas y estado activo
se gestionan enteramente desde la base de datos.

### Motivación

Con 8 tools actuales el sistema funciona bien con un agente único. Al agregar más tools
(proyección: 15-25), el LLM empieza a confundirse en la selección. Agentes especializados
mantienen cada prompt corto y cada conjunto de tools coherente, manteniendo alta precisión
sin sacrificar flexibilidad.

### Diseño central

```
Query del usuario
        │
        ▼
IntentClassifier (nano LLM)
  ← descriptions de agentes leídas desde BD →
        │
        ├─ "datos"        → DataAgent       (database_query, calculate, datetime)
        ├─ "conocimiento" → KnowledgeAgent  (knowledge_search, calculate, datetime)
        ├─ "casual"       → CasualAgent     (save_preference, save_memory, reload_permissions)
        └─ "generalista"  → GeneralistAgent (todos los tools permitidos al usuario)
                                             ↑ fallback para queries cross-dominio
```

---

## Fases Completadas

### Fase 1: Schema de base de datos ✅

- [x] Creada `BotIAv2_AgenteDef` — definición de cada agente
- [x] Creada `BotIAv2_AgenteTools` — tools en el scope de cada agente
- [x] Creada `BotIAv2_AgentePromptHistorial` — auditoría de cambios de prompt
- [x] Trigger `TR_AgenteDef_VersionHistorial` — auto-incrementa version, guarda historial
- [x] Datos iniciales: 4 agentes (datos, conocimiento, casual, generalista)
- [x] Columna `agenteNombre` agregada a `BotIAv2_InteractionLogs`
- [x] Recurso y permiso para `reload_agent_config` (solo Admin)

**Archivos**: `database/migrations/arq35_dynamic_orchestrator.sql`, `database/migrations/arq35_trigger_fix.sql`

**Nota**: El trigger de SQL Server requiere ejecutarse sin prefijo de BD (`arq35_trigger_fix.sql`).

---

### Fase 2: Dominio — entity, repository, service ✅

- [x] `src/domain/agent_config/agent_config_entity.py` — `AgentDefinition` (Pydantic v2)
- [x] `src/domain/agent_config/agent_config_repository.py` — `get_all_active()`, `get_by_nombre()`, `get_generalista()`
- [x] `src/domain/agent_config/agent_config_service.py` — cache LRU TTL 5 min, `invalidate_cache()`, `set_builder()`
- [x] Validación de placeholders `{tools_description}` y `{usage_hints}` al cargar desde BD

---

### Fase 3: Agent builder dinámico ✅

- [x] `src/agents/factory/__init__.py` y `src/agents/factory/agent_builder.py` — `AgentBuilder`
- [x] Cache de instancias por `(idAgente, version)` con `threading.Lock`
- [x] `AgentBuilder.clear_instance_cache()` — limpia cache de instancias
- [x] `ReActAgent` actualizado: parámetros `system_prompt_override` y `tool_scope`
- [x] `ToolRegistry.get_tools_prompt()` y `get_usage_hints()`: parámetro `tool_scope` para intersección
- [x] Inyección tardía: `agent_config_service.set_builder(agent_builder)` en factory

---

### Fase 4: Orchestrator N-way ✅

- [x] `IntentClassifier` refactorizado — prompt dinámico desde descripciones de agentes en BD
- [x] `AgentOrchestrator` refactorizado — N agentes desde BD, construcción lazy, fallback a generalista
- [x] Comportamiento cuando no hay generalista → `AgentConfigException` → error gracioso al usuario
- [x] `routed_agent: Optional[str] = None` agregado a `AgentResponse`
- [x] `agenteNombre` registrado en `ObservabilityRepository.save_interaction()`
- [x] `MainHandler._save_interaction()` pasa `agente_nombre=response.routed_agent`
- [x] `pipeline/factory.py` actualizado: `create_agent_orchestrator()`, wiring completo
- [x] Validación de startup en `create_agent_orchestrator()`: falla si no hay agentes o generalista

---

### Fase 5: Admin tooling y recarga ✅

- [x] `src/agents/tools/reload_agent_config_tool.py` — `ReloadAgentConfigTool`
- [x] Registrada en `create_tool_registry()` en `factory.py`
- [x] Inyección tardía del service tras construcción del orchestrator
- [x] Documentación en `docs/uso/guia-administrador.md` sección "Gestión de agentes"

---

### Fase 6: Tests y migración ✅

- [x] Tests unitarios `tests/agents/test_orchestrator.py` (20 tests, todos pasan)
  - `TestIntentClassifier`: 7 tests — clasificación, fallbacks, match parcial
  - `TestAgentOrchestrator`: 9 tests — routing, fallbacks, event_callback, health_check
  - `TestAgentBuilder`: 4 tests — scope, cache, clear_instance_cache
- [x] Test de integración `scripts/test_orchestrator.py` (todos pasan con LLM real)
  - Carga desde BD, validación de placeholders, construcción de agentes
  - Cache LRU, invalidación, clasificación LLM 4/4
- [x] `scripts/run_migration.py` — runner de migraciones SQL con soporte GO
- [x] Documentación actualizada: `.claude/context/AGENTS.md`, `.claude/context/DATABASE.md`

---

## Criterios de éxito — todos cumplidos ✅

- ✅ Agregar un nuevo agente requiere solo un `INSERT` en BD + recarga (sin deploy)
- ✅ Cambiar el prompt de un agente requiere solo un `UPDATE` en BD + recarga
- ✅ El `MainHandler` no tiene conocimiento de cuántos agentes existen
- ✅ El `ReActAgent` no cambió su interfaz pública (parámetros nuevos son opcionales)
- ✅ Consultas cross-dominio llegan al generalista, no fallan silenciosamente
- ✅ Cada interacción registra en `BotIAv2_InteractionLogs` el `nombre` del agente que respondió

---

## Archivos creados/modificados

### Nuevos
- `database/migrations/arq35_dynamic_orchestrator.sql`
- `database/migrations/arq35_trigger_fix.sql`
- `scripts/run_migration.py`
- `scripts/test_orchestrator.py`
- `src/agents/factory/__init__.py`
- `src/agents/factory/agent_builder.py`
- `src/agents/tools/reload_agent_config_tool.py`
- `src/domain/agent_config/__init__.py`
- `src/domain/agent_config/agent_config_entity.py`
- `src/domain/agent_config/agent_config_repository.py`
- `src/domain/agent_config/agent_config_service.py`

### Modificados
- `src/agents/base/agent.py` — `routed_agent` en `AgentResponse`
- `src/agents/orchestrator/__init__.py` — actualizar exports
- `src/agents/orchestrator/intent_classifier.py` — N-way dinámico
- `src/agents/orchestrator/orchestrator.py` — N-way dinámico desde BD
- `src/agents/react/agent.py` — `system_prompt_override`, `tool_scope`
- `src/agents/tools/registry.py` — parámetro `tool_scope`
- `src/infra/observability/sql_repository.py` — `agente_nombre`
- `src/pipeline/factory.py` — wiring completo ARQ-35
- `src/pipeline/handler.py` — pasa `agente_nombre`
- `database/database.sql` — columna `agenteNombre`, referencia ARQ-35
- `tests/agents/test_orchestrator.py` — reescrito para N-way
- `docs/uso/guia-administrador.md` — sección gestión de agentes
- `.claude/context/AGENTS.md` — documentación actualizada
- `.claude/context/DATABASE.md` — tablas ARQ-35
