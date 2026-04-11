# Plan: ARQ-38 — Reorganización de archivos mal ubicados

> **Estado**: 🟢 Completado
> **Última actualización**: 2026-04-11
> **Commit**: `d56357c`

## Resumen de Progreso

| Fase | Progreso | Estado |
|------|----------|--------|
| Fase 1: Mover admin_notifier a dominio | ██████████ 100% | ✅ Completada |
| Fase 2: Mover orchestrator y factory a pipeline | ██████████ 100% | ✅ Completada |
| Fase 3: Mover personality y logging_config | ██████████ 100% | ✅ Completada |
| Fase 4: Limpiar scripts y raíz | ██████████ 100% | ✅ Completada |

**Progreso Total**: ██████████ 100% (24/24 tareas)

---

## Descripción

El proyecto tiene varios archivos ubicados en la capa equivocada de la arquitectura.
El problema más severo es una violación de dependencias: `src/pipeline/handler.py`
(Capa 2) importa desde `src/bot/notifications/` (Capa 1). Las otras issues son
de clasificación conceptual incorrecta pero no generan dependencias inversas.

**Arquitectura objetivo (5 capas, dependencias solo hacia abajo):**
```
Capa 1: src/bot/, src/api/
Capa 2: src/gateway/, src/pipeline/
Capa 3: src/agents/react/, src/agents/tools/, src/agents/providers/
Capa 4: src/domain/
Capa 5: src/infra/, src/config/, src/utils/
```

---

## Fase 1: Mover admin_notifier a dominio

**Objetivo**: Eliminar la violación de capas — pipeline no debe importar de bot.
**Dependencias**: Ninguna

### Problema actual
`src/pipeline/handler.py` (Capa 2) y `src/bot/middleware/logging_middleware.py` (Capa 1)
importan desde `src/bot/notifications/admin_notifier.py` (Capa 1).
La solución es mover `admin_notifier` a `src/domain/notifications/` (Capa 4),
desde donde ambas capas superiores pueden importarlo correctamente.

### Tareas

- [ ] **Crear `src/domain/notifications/__init__.py`**
  - Contenido: `from .admin_notifier import notify_admin, reset_rate_cache`

- [ ] **Mover `admin_notifier.py`** de `src/bot/notifications/` a `src/domain/notifications/`
  - Archivo origen: `src/bot/notifications/admin_notifier.py`
  - Archivo destino: `src/domain/notifications/admin_notifier.py`
  - Sin cambios en el contenido del archivo

- [ ] **Actualizar import en `src/pipeline/handler.py`**
  - Línea 158: `from src.bot.notifications.admin_notifier import notify_admin`
  - → `from src.domain.notifications.admin_notifier import notify_admin`

- [ ] **Actualizar import en `src/bot/middleware/logging_middleware.py`**
  - Línea 102: `from src.bot.notifications.admin_notifier import notify_admin`
  - → `from src.domain.notifications.admin_notifier import notify_admin`

- [ ] **Actualizar `src/bot/notifications/__init__.py`**
  - Quitar el re-export de admin_notifier (o eliminar el archivo si queda vacío)

- [ ] **Actualizar import en `tests/domain/test_admin_notifier.py`**
  - Línea 13: `from src.bot.notifications.admin_notifier import ...`
  - → `from src.domain.notifications.admin_notifier import ...`

- [ ] **Eliminar `src/bot/notifications/`** si queda vacío (o dejar `__init__.py` vacío)

- [ ] **Verificar**: `python -c "from src.domain.notifications import notify_admin; print('OK')"`

### Entregables
- [ ] `src/domain/notifications/admin_notifier.py` existe
- [ ] `grep -r "bot.notifications" src/ tests/` → sin resultados

---

## Fase 2: Mover orchestrator y factory a pipeline

**Objetivo**: `orchestrator` y `factory` son coordinadores de ciclo de vida de agentes,
no implementaciones de agentes. Pertenecen a la Capa 2 (pipeline).
**Dependencias**: Ninguna (independiente de Fase 1)

### Problema actual
`src/agents/orchestrator/` y `src/agents/factory/` viven en Capa 3 (agents)
pero coordinan agentes desde afuera — son responsabilidad de pipeline.
`src/agents/orchestrator/` ya importa de `src/domain/agent_config/` (Capa 4),
lo cual viola la idea de que Capa 3 solo depende de Capa 4/5 para datos puros.

### Tareas

- [ ] **Mover `src/agents/orchestrator/` → `src/pipeline/orchestrator/`**
  - Archivos: `orchestrator.py`, `intent_classifier.py`, `__init__.py`

- [ ] **Mover `src/agents/factory/` → `src/pipeline/agent_factory/`**
  - Archivos: `agent_builder.py`, `__init__.py`
  - Nota: se renombra la carpeta a `agent_factory/` para no confundirse con `pipeline/factory.py`

- [ ] **Actualizar imports en `src/pipeline/factory.py`**
  - `from src.agents.factory.agent_builder import AgentBuilder`
    → `from src.pipeline.agent_factory.agent_builder import AgentBuilder`
  - `from src.agents.orchestrator.orchestrator import AgentOrchestrator`
    → `from src.pipeline.orchestrator.orchestrator import AgentOrchestrator`
  - `from src.agents.orchestrator.intent_classifier import IntentClassifier`
    → `from src.pipeline.orchestrator.intent_classifier import IntentClassifier`

- [ ] **Actualizar import interno en `src/pipeline/orchestrator/orchestrator.py`**
  - `from src.agents.factory.agent_builder import AgentBuilder`
    → `from src.pipeline.agent_factory.agent_builder import AgentBuilder`

- [ ] **Actualizar import en `src/domain/agent_config/agent_config_service.py`**
  - `from src.agents.factory.agent_builder import AgentBuilder`
    → `from src.pipeline.agent_factory.agent_builder import AgentBuilder`

- [ ] **Actualizar imports en `tests/agents/test_orchestrator.py`**
  - `from src.agents.orchestrator import AgentOrchestrator, IntentClassifier`
    → `from src.pipeline.orchestrator import AgentOrchestrator, IntentClassifier`
  - `from src.agents.orchestrator.orchestrator import AgentConfigException`
    → `from src.pipeline.orchestrator.orchestrator import AgentConfigException`
  - Las 4 referencias a `src.agents.factory.agent_builder`
    → `src.pipeline.agent_factory.agent_builder`

- [ ] **Mover `tests/agents/test_orchestrator.py` → `tests/pipeline/test_orchestrator.py`**
  - El test refleja pipeline, no agents directos

- [ ] **Eliminar `src/agents/orchestrator/` y `src/agents/factory/`** (carpetas vacías)

- [ ] **Verificar**: `python -c "from src.pipeline.orchestrator import AgentOrchestrator; print('OK')"`

### Entregables
- [ ] `src/pipeline/orchestrator/` y `src/pipeline/agent_factory/` existen
- [ ] `grep -r "agents.orchestrator\|agents.factory" src/ tests/` → sin resultados

---

## Fase 3: Mover personality.py y logging_config.py

**Objetivo**: `src/config/` debe contener solo settings y configuración pura.
**Dependencias**: Ninguna

### Tareas — personality.py

- [ ] **Mover `src/config/personality.py` → `src/agents/personality.py`**
  - Es lógica del agente (tono, nombre, instrucciones), no configuración de infraestructura

- [ ] **Actualizar imports** — buscar con:
  `grep -r "config.personality" src/ --include="*.py"`
  y actualizar cada uno a `src.agents.personality`

### Tareas — logging_config.py

- [ ] **Mover `src/config/logging_config.py` → `src/infra/observability/logging_config.py`**
  - Contiene `SqlLogHandler` que persiste logs en BD — es infraestructura, no config

- [ ] **Actualizar imports** — buscar con:
  `grep -r "config.logging_config" src/ --include="*.py"`
  y actualizar cada uno a `src.infra.observability.logging_config`

- [ ] **Verificar**: `python -c "from src.agents.personality import *; from src.infra.observability.logging_config import *; print('OK')"`

### Entregables
- [ ] `src/agents/personality.py` existe
- [ ] `src/infra/observability/logging_config.py` existe
- [ ] `grep -r "config.personality\|config.logging_config" src/` → sin resultados

---

## Fase 4: Limpiar scripts y raíz

**Objetivo**: Separar scripts de utilidad de tests manuales. Limpiar raíz.
**Dependencias**: Ninguna

### Tareas — mover tests manuales de scripts/

- [ ] **Mover `scripts/test_orchestrator.py` → `tests/integration/test_orchestrator_manual.py`**
- [ ] **Mover `scripts/test_message.py` → `tests/integration/test_message_manual.py`**
- [ ] **Mover `scripts/test_memory_flow.py` → `tests/integration/test_memory_flow.py`**
- [ ] **Mover `scripts/test_increment.py` → `tests/integration/test_increment.py`**
- [ ] **Mover `scripts/test_conversation_history.py` → `tests/integration/test_conversation_history.py`**
- [ ] **Mover `scripts/test_encoding_variations.py` → `tests/integration/test_encoding_variations.py`**
- [ ] **Mover `scripts/test_key_derivation.py` → `tests/integration/test_key_derivation.py`**

### Tareas — limpiar raíz

- [ ] **Mover `check_config.py` → `scripts/check_config.py`**

### Tareas — eliminar ejemplos legacy

- [ ] **Eliminar `examples/EjemploSimple_legacy.py`**
- [ ] **Eliminar `examples/SalidaEstructurada_legacy.py`**

### Entregables
- [ ] `scripts/test_*.py` → sin archivos
- [ ] `check_config.py` no existe en raíz
- [ ] `examples/` solo contiene los 2 ejemplos no-legacy

---

## Riesgos y Mitigaciones

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|--------------|---------|------------|
| Import olvidado que rompe runtime | Media | Alto | Grep exhaustivo antes y después de cada fase |
| `agent_config_service.py` (dominio) importa de pipeline tras Fase 2 | Alta | Medio | Usar import diferido (TYPE_CHECKING) si es solo para type hints |
| Tests que usan paths directos | Baja | Bajo | Revisar `tests/` con grep tras cada fase |

---

## Criterios de Éxito

- [ ] `python -m pytest tests/ -x` pasa sin errores tras cada fase
- [ ] `grep -r "bot.notifications.admin_notifier" src/` → 0 resultados
- [ ] `grep -r "agents.orchestrator\|agents.factory" src/ tests/` → 0 resultados
- [ ] `grep -r "config.personality\|config.logging_config" src/` → 0 resultados
- [ ] `src/config/` contiene solo `settings.py` y `__init__.py`

---

## Historial de Cambios

| Fecha | Cambio | Autor |
|-------|--------|-------|
| 2026-04-11 | Creación del plan | Angel David |
