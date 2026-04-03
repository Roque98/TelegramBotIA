# Plan: ARQ-30 — Consolidar AgentOrchestrator

> **Estado**: ⚪ No iniciado
> **Última actualización**: 2026-04-03
> **Rama Git**: `feature/arq-30-orchestrator`

## Resumen de Progreso

| Fase | Progreso | Estado |
|------|----------|--------|
| Fase 1: Tests y validación de integración | ░░░░░░░░░░ 0% | ⏳ Pendiente |
| Fase 2: Especialización de tools por agente | ░░░░░░░░░░ 0% | ⏳ Pendiente |
| Fase 3: Observabilidad del orquestador | ░░░░░░░░░░ 0% | ⏳ Pendiente |
| Fase 4: Limpieza y documentación | ░░░░░░░░░░ 0% | ⏳ Pendiente |

**Progreso Total**: ░░░░░░░░░░ 0% (0/18 tareas)

---

## Descripción

El `AgentOrchestrator` existe y está integrado en el pipeline, pero está sin consolidar:
no tiene tests, no emite métricas propias, y ambos agentes (casual y data) comparten
exactamente el mismo conjunto de 8 tools — cuando deberían estar especializados.

Este plan convierte el orchestrator de "código que funciona" a "componente production-ready"
que puede usarse como base en proyectos derivados.

### Estado actual (2026-04-03)

**Lo que existe y funciona:**
- `src/agents/orchestrator/orchestrator.py` — routing casual vs business_data ✅
- `src/agents/orchestrator/intent_classifier.py` — clasifica con nano LLM, fallback a BUSINESS_DATA ✅
- `src/pipeline/factory.py:create_orchestrator()` — crea ambos agentes con 3 modelos LLM ✅
- Integrado en `MainHandler` vía `react_agent=orchestrator` ✅

**Lo que falta:**
- Cero tests para `orchestrator.py` ni `intent_classifier.py`
- `casual_agent` y `data_agent` reciben las 8 tools idénticas — sin diferenciación
- El orchestrator no loguea ni mide el costo de clasificar intent
- `create_llm_provider()` en factory está marcado como legacy pero no eliminado
- No hay forma de desactivar el routing y usar un agente único (útil en debugging)

---

## Fase 1: Tests y validación de integración

**Objetivo**: verificar que el orchestrator funciona correctamente end-to-end con tests.
**Dependencias**: Ninguna
**Duración estimada**: 1 día

### Tareas

- [ ] **Tests para `IntentClassifier`** — verificar clasificación y fallback
  - Archivo: `tests/agents/orchestrator/test_intent_classifier.py`
  - Casos: query de negocio → BUSINESS_DATA, saludo → CASUAL, error del LLM → BUSINESS_DATA
  - Usar mock del LLM provider

- [ ] **Tests para `AgentOrchestrator`** — verificar routing al agente correcto
  - Archivo: `tests/agents/orchestrator/test_orchestrator.py`
  - Casos: intent CASUAL → casual_agent.execute(), intent BUSINESS_DATA → data_agent.execute()
  - Verificar que el response del agente seleccionado se retorna sin modificar

- [ ] **Test de integración con factory** — verificar que `create_orchestrator()` instancia correctamente
  - Archivo: `tests/pipeline/test_factory.py` (agregar casos)
  - Verificar que los 3 modelos LLM se configuran con settings correctos

- [ ] **Crear `tests/agents/orchestrator/__init__.py`**
  - Archivo: `tests/agents/orchestrator/__init__.py`

### Entregables
- [ ] `tests/agents/orchestrator/` con tests pasando
- [ ] Cobertura de los caminos críticos: routing, fallback, error del classifier

---

## Fase 2: Especialización de tools por agente

**Objetivo**: que cada agente tenga solo las tools que necesita, reduciendo tokens y mejorando precisión.
**Dependencias**: Fase 1
**Duración estimada**: 1 día

### Contexto: por qué especializar

Actualmente `create_orchestrator()` crea ambos agentes con las mismas 8 tools:
```python
casual_agent = create_react_agent(casual_llm, db_manager, knowledge_manager, ...)
data_agent   = create_react_agent(data_llm,   db_manager, knowledge_manager, ...)
```

El problema: el `casual_agent` con `gpt-mini` recibe el schema de `database_query` en cada prompt,
aunque nunca lo va a usar para "hola, ¿cómo estás?". Esto:
1. Consume tokens innecesarios en cada request casual
2. Puede confundir al modelo y hacerlo intentar tools que no debería

### Especialización propuesta

| Tool | CasualAgent | DataAgent | Razón |
|------|-------------|-----------|-------|
| `database_query` | ❌ No | ✅ Sí | Solo data_agent hace SQL |
| `knowledge_search` | ✅ Sí | ✅ Sí | Ambos pueden buscar conocimiento |
| `calculate` | ❌ No | ✅ Sí | Cálculos son dominio de datos |
| `get_datetime` | ✅ Sí | ✅ Sí | Ambos pueden necesitar fecha |
| `save_preference` | ✅ Sí | ❌ No | Preferencias son contexto casual |
| `save_memory` | ✅ Sí | ❌ No | Memoria es contexto casual |
| `reload_permissions` | ❌ No | ✅ Sí (admin) | Solo agente con permisos admin |
| `read_attachment` | ❌ No | ✅ Sí | Archivos son dominio de datos |

### Tareas

- [ ] **Crear `create_casual_tool_registry()`** en factory
  - Archivo: `src/pipeline/factory.py`
  - Tools: knowledge_search, get_datetime, save_preference, save_memory
  - Registrar con el `ToolRegistry` respectivo

- [ ] **Crear `create_data_tool_registry()`** en factory
  - Archivo: `src/pipeline/factory.py`
  - Tools: database_query, knowledge_search, calculate, get_datetime, reload_permissions, read_attachment

- [ ] **Actualizar `create_orchestrator()`** para usar registries especializados
  - Archivo: `src/pipeline/factory.py`
  - `casual_agent` recibe `casual_registry`, `data_agent` recibe `data_registry`

- [ ] **Actualizar tests** — verificar que cada agente tiene solo sus tools
  - Archivo: `tests/agents/orchestrator/test_orchestrator.py`

### Entregables
- [ ] `casual_agent` con 4 tools, `data_agent` con 6 tools
- [ ] Tests verificando especialización

---

## Fase 3: Observabilidad del orquestador

**Objetivo**: que el orchestrator emita métricas y logs propios, no solo los de los agentes hijos.
**Dependencias**: Fase 1
**Duración estimada**: 0.5 días

### Qué medir

El orchestrator actualmente loguea la clasificación de intent pero no:
- El costo (tokens) de la llamada de clasificación
- La distribución de intents (¿cuántos % son casual vs business_data?)
- La latencia de clasificación (classify_ms) en las métricas globales

### Tareas

- [ ] **Log estructurado de clasificación** — nivel INFO con intent, classify_ms, y query truncada
  - Archivo: `src/agents/orchestrator/orchestrator.py`
  - Formato: `intent_classified | query='{q[:40]}' intent=casual classify_ms=45`

- [ ] **Registrar classify_ms en MetricsCollector** — nueva métrica `intent_classify_ms`
  - Archivo: `src/agents/orchestrator/orchestrator.py`
  - Usar `get_metrics().record_intent_classification(intent, classify_ms)`
  - Extender `MetricsCollector` con método `record_intent_classification()`

- [ ] **Agregar `intentRoute` a `TransactionLogs`** — columna opcional para saber qué agente respondió
  - Archivo: `scripts/migrations/003_add_intent_route.sql`
  - Columna: `intentRoute NVARCHAR(20) NULL` — valores: 'casual', 'data', NULL (si no pasa por orchestrator)
  - Propagar desde orchestrator → MainHandler vía metadata de AgentResponse

### Entregables
- [ ] Logs de clasificación visibles en consola con format estructurado
- [ ] `MetricsCollector` con distribución de intents
- [ ] Migration SQL lista para ejecutar

---

## Fase 4: Limpieza y documentación

**Objetivo**: dejar el componente listo para ser referencia en proyectos derivados.
**Dependencias**: Fases 1-3
**Duración estimada**: 0.5 días

### Tareas

- [ ] **Eliminar `create_llm_provider()`** — función legacy en factory.py
  - Archivo: `src/pipeline/factory.py`
  - Verificar que nadie la llama (`grep -r "create_llm_provider"`)
  - Si hay referencias, migrarlas a `create_orchestrator()`

- [ ] **Agregar flag `use_orchestrator` en settings** — permite bypass para debugging
  - Archivo: `src/config/settings.py`
  - `use_orchestrator: bool = True`
  - En factory: si False, usa single ReActAgent con `openai_model`

- [ ] **Actualizar `.claude/context/AGENTS.md`** — documentar orchestrator, intent classifier, especialización
  - Archivo: `.claude/context/AGENTS.md`

### Entregables
- [ ] Factory limpio sin código legacy
- [ ] `AGENTS.md` actualizado con diagrama de routing

---

## Arquitectura del orchestrator consolidado

```
Usuario: "cuanto vendimos ayer?"
         │
         ▼
  IntentClassifier (nano — barato)
    classify_ms: ~50ms
         │
    intent=BUSINESS_DATA
         │
         ▼
  DataAgent (gpt-5.4)
  Tools: database_query, knowledge_search,
         calculate, get_datetime,
         reload_permissions, read_attachment
         │
         ▼
  AgentResponse → MainHandler


Usuario: "hola! ¿cómo estás?"
         │
         ▼
  IntentClassifier (nano — barato)
    classify_ms: ~45ms
         │
    intent=CASUAL
         │
         ▼
  CasualAgent (gpt-mini — económico)
  Tools: knowledge_search, get_datetime,
         save_preference, save_memory
         │
         ▼
  AgentResponse → MainHandler
```

---

## Criterios de Éxito

- [ ] `pytest tests/agents/orchestrator/` pasa sin errores
- [ ] `casual_agent` tiene exactamente 4 tools, `data_agent` tiene exactamente 6
- [ ] Los logs muestran `intent_classified | query=... intent=... classify_ms=...` en cada request
- [ ] `MetricsCollector.get_stats()` incluye distribución de intents
- [ ] `create_llm_provider()` eliminado del factory
- [ ] `.claude/context/AGENTS.md` actualizado

---

## Riesgos y Mitigaciones

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|--------------|---------|------------|
| Casual queries necesitan `database_query` (ej: "¿cuántos mensajes mandé?") | Media | Medio | Revisar casos borde en tests; ajustar clasificador si ocurre |
| Eliminar `create_llm_provider()` rompe código externo no rastreado | Baja | Alto | Grep exhaustivo antes de eliminar |
| `save_preference`/`save_memory` necesarias en data_agent también | Baja | Bajo | Agregar si se detecta en uso real |

---

## Historial de Cambios

| Fecha | Cambio |
|-------|--------|
| 2026-04-03 | Creación del plan — diagnóstico del estado actual |
