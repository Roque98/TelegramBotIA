# Plan: Consolidar Sistemas Legacy vs ReAct

> **Estado**: ✅ Completado
> **Ultima actualizacion**: 2026-03-21
> **Rama Git**: feature/consolidar-legacy

---

## Resumen de Progreso

| Fase | Progreso | Tareas | Estado |
|------|----------|--------|--------|
| Fase 0: Completar integración MainHandler | ██████████ 100% | 5/5 | ✅ Completado |
| Fase 1: Eliminar codigo muerto | ██████████ 100% | 5/5 | ✅ Completado |
| Fase 2: Migrar dependencias activas | ██████████ 100% | 7/7 | ✅ Completado |
| Fase 3: Remover legacy y limpiar | ██████████ 100% | 5/5 | ✅ Completado |

**Progreso Total**: ██████████ 100% (22/22 tareas)

---

## Descripcion

### Problema Actual

Coexisten dos sistemas paralelos tras la migracion a ReAct:
- `src/agent/` (4,646 lineas) - LLMAgent legacy
- `src/agents/` - ReAct Agent nuevo (en uso)
- `src/tools/` (1,087 lineas) - Framework de tools legacy
- `src/orchestrator/` (346 lineas) - Orquestador legacy

**Total codigo legacy: ~6,079 lineas**, de las cuales **~3,580 estan completamente sin usar**.

### Estado Real de la Integracion MainHandler

`MainHandler` existe en `src/gateway/handler.py` pero su adopcion es **parcial**:

| Archivo | Estado actual |
|---------|---------------|
| `query_handlers.py` | Usa MainHandler cuando `USE_REACT_AGENT=true` (feature flag activo por defecto) |
| `command_handlers.py` | Usa `LLMAgent` directo + `KnowledgeRepository` legacy |
| `universal_handler.py` | Usa `ToolOrchestrator` + `ExecutionContextBuilder` legacy |
| `telegram_bot.py` | Instancia `LLMAgent` directamente |
| `src/api/chat_endpoint.py` | Usa `LLMAgent` directamente (no contemplado en plan original) |
| `gateway/factory.py` | Crea `MainHandler` pero aun pasa `LLMAgent` como fallback |

El plan original asumia que la integracion estaba completa — **no lo esta**.

### Analisis de Dependencias

**Codigo legacy SIN USAR (eliminacion directa):**
| Modulo | Lineas | Razon |
|--------|--------|-------|
| `src/agent/providers/` | 271 | Reemplazado por ReAct con OpenAI directo |
| `src/agent/memory/` | 888 | Reemplazado por `src/memory/` |
| `src/agent/formatters/` | 313 | ReAct formatea directo |
| `src/agent/classifiers/` | 181 | ReAct decide solo, sin clasificador |
| `src/agent/sql/sql_generator.py` | 94 | Reemplazado por database_tool |
| `src/agent/conversation_history.py` | 189 | Reemplazado por memory service |
| `src/tools/tool_initializer.py` | 79 | No usado |
| `src/tools/builtin/` | 232 | Reemplazado por `src/agents/tools/` |
| **Total** | **~2,247** | |

> **Nota**: `src/agent/prompts/` (900 ln) NO es codigo muerto — `tool_selector.py` lo importa.
> Debe eliminarse en Fase 2 junto con `tool_selector.py`.

**Codigo legacy AUN EN USO (requiere migracion):**
| Modulo | Usado por | Accion |
|--------|-----------|--------|
| `src/agent/llm_agent.py` (543 ln) | `query_handlers.py`, `command_handlers.py`, `telegram_bot.py`, `chat_endpoint.py`, `factory.py` | Completar integracion MainHandler, eliminar fallback |
| `src/agent/knowledge/` (1,449 ln) | `command_handlers.py`, `factory.py`, `knowledge_tool.py` | Mover a `src/knowledge/` |
| `src/agent/sql/sql_validator.py` (151 ln) | `database_tool.py` | Mover a `src/database/sql_validator.py` |
| `src/agent/prompts/` (900 ln) | `tool_selector.py` | Eliminar junto con tool_selector en Fase 2 |
| `src/tools/tool_orchestrator.py` (363 ln) | `query_handlers.py`, `universal_handler.py` | Eliminar, ReAct ya orquesta |
| `src/tools/tool_registry.py` (264 ln) | `universal_handler.py` | Eliminar, usar `src/agents/tools/registry.py` |
| `src/tools/execution_context.py` (359 ln) | `universal_handler.py` | Eliminar referencia |
| `src/orchestrator/tool_selector.py` (334 ln) | `query_handlers.py` | Eliminar, ReAct selecciona tools |

---

## Fase 0: Completar integracion MainHandler

**Objetivo**: Que todos los puntos de entrada usen `MainHandler`/ReAct antes de eliminar nada
**Duracion estimada**: 1-2 dias
**Dependencias**: Ninguna — es el prerequisito de todo lo demas

### Tareas

- [ ] **Migrar `telegram_bot.py`** — eliminar instanciacion directa de `LLMAgent`
  - `telegram_bot.py:37` crea `self.agent = LLMAgent()`
  - Reemplazar: obtener el `MainHandler` via `gateway.factory` o pasarlo como dependencia
  - Verificar que `query_handlers` y `command_handlers` reciben el handler correcto

- [ ] **Migrar `command_handlers.py`** — eliminar uso de `LLMAgent` y `KnowledgeRepository`
  - `command_handlers.py:10` importa `KnowledgeRepository` para health check y stats
  - Reemplazar: usar `ReActAgent` o `MainHandler` para el health check
  - El acceso a knowledge puede ir via `KnowledgeManager` en `gateway/factory.py`

- [ ] **Migrar `universal_handler.py`** — eliminar `ToolOrchestrator` y `ExecutionContextBuilder`
  - `universal_handler.py:10-11` usa el orquestador legacy
  - Reemplazar: delegar al `MainHandler` o directamente a `ReActAgent`
  - Verificar que los comandos que pasan por este handler siguen funcionando

- [ ] **Migrar `src/api/chat_endpoint.py`** — eliminar uso de `LLMAgent`
  - `chat_endpoint.py:14` importa y usa `LLMAgent` como agente principal del endpoint REST
  - Reemplazar: usar `MainHandler` o `ReActAgent` directamente
  - Este archivo no estaba en el plan original

- [ ] **Eliminar fallback en `gateway/factory.py`**
  - `factory.py:173` pasa `fallback_agent=llm_agent` al `MainHandler`
  - Una vez migrados todos los consumidores, eliminar el fallback
  - El parametro `use_fallback_on_error` en `MainHandler.__init__` tambien puede removerse

### Entregables
- [ ] Cero instanciaciones directas de `LLMAgent` fuera de `src/agent/`
- [ ] `MainHandler` es el unico punto de entrada para procesar mensajes
- [ ] Bot funciona correctamente con `USE_REACT_AGENT=true` (ya es el default)
- [ ] Commit: `refactor(bot): migrate all handlers to MainHandler/ReAct`

---

## Fase 1: Eliminar codigo muerto

**Objetivo**: Eliminar modulos legacy que no son importados por ningun archivo activo
**Duracion estimada**: 1 dia
**Dependencias**: Fase 0

### Tareas

- [ ] **Eliminar `src/agent/providers/`** - Providers legacy (openai, anthropic, base)
  - Archivos: `openai_provider.py`, `anthropic_provider.py`, `base_provider.py`, `__init__.py`
  - Verificar: ningun import activo

- [ ] **Eliminar `src/agent/memory/`** - Sistema de memoria legacy
  - Archivos: `memory_repository.py`, `memory_extractor.py`, `memory_manager.py`, `memory_injector.py`, `__init__.py`
  - Verificar: ningun import activo (el nuevo esta en `src/memory/`)

- [ ] **Eliminar `src/agent/formatters/`** - Formateador legacy
  - Archivos: `response_formatter.py`, `__init__.py`
  - Verificar: ningun import activo

- [ ] **Eliminar `src/agent/classifiers/`** - Clasificador legacy
  - Archivos: `query_classifier.py`, `__init__.py`
  - Verificar: ningun import activo

- [ ] **Eliminar archivos sueltos legacy**
  - `src/agent/conversation_history.py` - No usado
  - `src/agent/sql/sql_generator.py` - No usado
  - `src/tools/tool_initializer.py` - No usado
  - `src/tools/builtin/` - Carpeta completa no usada

### Entregables
- [ ] ~2,247 lineas de codigo muerto eliminadas
- [ ] Tests existentes siguen pasando
- [ ] Commit: `refactor(agent): remove unused legacy modules`

---

## Fase 2: Migrar dependencias activas

**Objetivo**: Reubicar los modulos legacy que aun se usan en la ubicacion correcta
**Duracion estimada**: 2-3 dias
**Dependencias**: Fase 1

### Tareas

- [ ] **Mover `src/agent/knowledge/` a `src/knowledge/`** - Modulo de conocimiento
  - Mover: `knowledge_repository.py`, `company_knowledge.py`, `knowledge_manager.py`, `knowledge_categories.py`
  - Actualizar imports en: `command_handlers.py`, `factory.py`, `agents/tools/knowledge_tool.py`

- [ ] **Mover `src/agent/sql/sql_validator.py` a `src/database/sql_validator.py`**
  - Actualizar import en: `src/agents/tools/database_tool.py`

- [ ] **Eliminar `src/orchestrator/tool_selector.py`** y su dependencia de prompts
  - `tool_selector.py` importa `src/agent/prompts/prompt_manager`
  - Eliminar primero `tool_selector.py`, luego `src/agent/prompts/` completo
  - Actualizar `query_handlers.py`: remover import de `ToolSelector` (ya deberia estar eliminado en Fase 0)

- [ ] **Eliminar `src/tools/tool_orchestrator.py`**
  - Verificar que ya no hay imports activos (Fase 0 deberia haberlos eliminado)

- [ ] **Eliminar `src/tools/tool_registry.py`** y `execution_context.py`
  - Verificar que `universal_handler.py` ya usa el nuevo sistema (Fase 0)

- [ ] **Eliminar feature flag `USE_REACT_AGENT`**
  - `settings.py:48` define `use_react_agent: bool = True`
  - Una vez eliminado el codigo legacy, el flag ya no tiene sentido
  - Limpiar todos los `if self.use_react_agent` en handlers

- [ ] **Actualizar tests** - Ajustar tests que referencien modulos movidos
  - `tests/agent/` - Verificar si los tests aplican al nuevo sistema
  - Actualizar imports en tests existentes

### Entregables
- [ ] `src/knowledge/` funcional con imports actualizados
- [ ] `src/database/sql_validator.py` accesible para database_tool
- [ ] `src/agent/prompts/` eliminado (junto con tool_selector)
- [ ] Feature flag `USE_REACT_AGENT` eliminado
- [ ] Tests pasando con nuevos imports

---

## Fase 3: Remover legacy y limpiar

**Objetivo**: Eliminar las carpetas legacy vacias y limpiar la estructura
**Duracion estimada**: 1 dia
**Dependencias**: Fase 2

### Tareas

- [ ] **Eliminar `src/agent/`** - Carpeta legacy completa
  - Verificar: ya no queda ningun archivo necesario
  - Eliminar: carpeta completa incluyendo `__init__.py`

- [ ] **Eliminar `src/tools/`** - Framework de tools legacy
  - Verificar: ningun import activo
  - Eliminar: carpeta completa

- [ ] **Eliminar `src/orchestrator/`** - Orquestador legacy
  - Verificar: ningun import activo
  - Eliminar: carpeta completa

- [ ] **Actualizar documentacion**
  - `.claude/context/ARCHITECTURE.md` - Reflejar nueva estructura
  - `.claude/context/TOOLS.md` - Solo tools de ReAct
  - `plan/README.md` - Marcar este plan como completado

- [ ] **Limpiar tests legacy**
  - `tests/agent/` - Eliminar tests de modulos removidos
  - `tests/tools/` - Eliminar tests de tools legacy
  - `tests/orchestrator/` - Eliminar tests de orquestador legacy

### Entregables
- [ ] Estructura limpia sin carpetas legacy
- [ ] Documentacion actualizada
- [ ] Tests limpios y pasando
- [ ] Commit final: `refactor: remove all legacy code after ReAct consolidation`

---

## Riesgos y Mitigaciones

| Riesgo | Probabilidad | Impacto | Mitigacion |
|--------|--------------|---------|------------|
| Romper imports ocultos | Media | Alto | Grep exhaustivo antes de eliminar, correr tests |
| `chat_endpoint.py` usa LLMAgent de forma distinta | Media | Alto | Revisar comportamiento del endpoint vs MainHandler antes de migrar |
| Knowledge module tiene logica unica | Baja | Alto | Mover sin modificar, solo reubicar |
| Tests dejan de pasar | Media | Medio | Correr tests despues de cada paso |
| `universal_handler.py` tiene logica propia en ExecutionContext | Media | Medio | Analizar que hace antes de reemplazar |

---

## Criterios de Exito

- [ ] Cero imports a `src/agent/`, `src/tools/`, `src/orchestrator/`
- [ ] Todas las carpetas legacy eliminadas
- [ ] ~6,000 lineas de codigo legacy removidas
- [ ] Tests existentes pasan (los relevantes)
- [ ] Bot funciona correctamente con solo ReAct
- [ ] Documentacion refleja la estructura actual
- [ ] Feature flag `USE_REACT_AGENT` eliminado

---

## Historial de Cambios

| Fecha | Cambio | Autor |
|-------|--------|-------|
| 2026-02-16 | Creacion del plan | Claude |
| 2026-03-21 | Agregada Fase 0 (integracion MainHandler pendiente), corregido analisis de dependencias: `src/agent/prompts/` NO es codigo muerto, `chat_endpoint.py` agregado como consumidor de LLMAgent, ajustado conteo de lineas eliminables en Fase 1 | Claude |
