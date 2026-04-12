# Plan: ARQ-39 — Refactorización de la capa de infraestructura (SRP)

> **Estado**: 🟢 Completado
> **Última actualización**: 2026-04-11
> **Rama Git**: develop

## Resumen de Progreso

| Fase | Progreso | Estado |
|------|----------|--------|
| Fase 1: Mover todas las consultas a BD a domain | ██████████ 100% | ✅ Completada |
| Fase 2: Integrar sql_validator en connection | ██████████ 100% | ✅ Ya resuelto |
| Fase 3: Extraer SchemaIntrospector de connection | ██████████ 100% | ✅ Completada |
| Fase 4: Deduplicar database_url en settings | ██████████ 100% | ✅ Completada |
| Fase 5: Dividir MetricsCollector en clases focalizadas | ██████████ 100% | ✅ Completada |
| Fase 6: Eliminar código muerto (EventBus) | ██████████ 100% | ✅ Completada |

**Progreso Total**: ██████████ 100% (28/28 tareas)

---

## Descripción

La capa de infraestructura (`src/infra/`) tiene múltiples violaciones del principio
de responsabilidad única (SRP). El problema más grave es que `sql_repository.py`
vive en `infra/observability/` pero contiene lógica de persistencia de negocio
(interacciones, routing de agentes, pasos ReAct). Además, `connection.py` concentra
7 responsabilidades y hay código muerto que nunca se usa.

**Análisis de impacto:**
- 1,448 líneas de 3,048 (47%) con problemas de SRP
- 3 archivos críticos, 2 moderados, 2 de código muerto

**Principios del plan:**
- Cada fase es independiente y no rompe el código existente
- Se dejan re-export stubs donde sea necesario para compatibilidad
- Los tests deben pasar después de cada fase
- Priorizado por impacto arquitectónico (capas primero, limpieza después)

---

## Fase 1: Mover todas las consultas a BD a domain ✅

**Objetivo**: Todas las consultas a BD deben vivir en domain, sin excepción.
`sql_repository.py` completo (los 4 métodos) se mueve a `src/domain/interaction/`.
**Dependencias**: Ninguna
**Commit**: `e549192`

### Decisión tomada

El plan original proponía dejar `save_log_sync` en observability. El criterio
adoptado fue más amplio: **todas las consultas SQL deben estar en domain**,
incluidos los logs. `infra/observability/` solo debe tener lógica de instrumentación
(tracing, métricas, handlers de logging), no SQL directo.

### Tareas

- [x] **Leer `src/infra/observability/sql_repository.py`** — 4 métodos identificados
- [x] **Crear `src/domain/interaction/__init__.py`** — exporta `InteractionRepository`
- [x] **Crear `src/domain/interaction/interaction_repository.py`**
  - Los 4 métodos: `save_interaction`, `save_agent_routing`, `save_steps`, `save_log_sync`
  - Clase `InteractionRepository` (nombre correcto para domain)
- [x] **Convertir `src/infra/observability/sql_repository.py` en stub**
  - 3 líneas: re-export `InteractionRepository as ObservabilityRepository` para compatibilidad
- [x] **Actualizar `src/pipeline/handler.py`** — import y type annotation
- [x] **Actualizar `src/pipeline/factory.py`** — import e instanciación
- [x] **Actualizar `src/infra/observability/logging_config.py`** — referencia en docstring
- [x] **Actualizar `src/infra/observability/__init__.py`** — eliminar re-export de sql_repository

### Entregables
- [x] `src/domain/interaction/interaction_repository.py` existe con los 4 métodos
- [x] `src/infra/observability/sql_repository.py` es solo un stub de 3 líneas
- [x] `grep -r "ObservabilityRepository" src/` → solo el stub (no callers activos)

---

## Fase 2: Integrar sql_validator en connection ✅

**Estado**: Ya resuelto — análisis del plan era incorrecto.

### Hallazgo

Al leer `src/agents/tools/database_tool.py` se encontró que `SQLValidator` YA está
siendo usado (líneas 68-70):
```python
from src.infra.database.sql_validator import SQLValidator
self.sql_validator = SQLValidator()
```

Las validaciones inline en `connection.py` son **guardas de tipo** (¿es SELECT? ¿es INSERT?)
y sirven un propósito diferente al `SQLValidator` (que valida seguridad de SQL generado por LLM).
No son código duplicado — son responsabilidades distintas:
- `connection.py`: verifica que el método se llame con el tipo de query correcto
- `SQLValidator` en `DatabaseTool`: valida seguridad del SQL generado por el LLM antes de ejecutarlo

No se requiere ningún cambio.

---

## Fase 3: Extraer SchemaIntrospector de connection ✅

**Objetivo**: Extraer `get_schema()` de `DatabaseManager` a su propia clase.
**Dependencias**: Ninguna
**Commit**: incluido en commit de ARQ-39

### Tareas

- [x] **Crear `src/infra/database/schema_introspector.py`** — clase `SchemaIntrospector(engine)`
  con el método `get_schema()` y su propio `@db_retry`
- [x] **Simplificar `DatabaseManager.get_schema()`** — 3 líneas que instancian y delegan a `SchemaIntrospector`
- [x] **Limpiar imports en `connection.py`** — eliminar `inspect` (ya no se usa directamente)

### Entregables
- [x] `src/infra/database/schema_introspector.py` existe con clase `SchemaIntrospector`
- [x] `DatabaseManager.get_schema()` delega completamente — sin lógica propia

---

## Fase 4: Deduplicar database_url en settings ✅

**Objetivo**: Una sola implementación de `database_url`.
**Dependencias**: Ninguna

### Tareas

- [x] **Refactorizar `Settings.database_url`** — delega a `DbConnectionConfig`:
  ```python
  return DbConnectionConfig(alias="core", host=self.db_host, ...).database_url
  ```
  La fuente de verdad es `DbConnectionConfig.database_url`. La lógica de `Settings`
  queda en 5 líneas en lugar de 35.

### Entregables
- [x] `Settings.database_url` no tiene lógica propia — construye un `DbConnectionConfig` y delega

---

## Fase 5: Dividir MetricsCollector en clases focalizadas ✅

**Objetivo**: Organizar `MetricsCollector` con el patrón facade.
**Dependencias**: Ninguna

### Tareas

- [x] **Crear `_RequestMetrics`** — latencia, contadores, pasos, errores, fallbacks
- [x] **Crear `_ToolMetrics`** — uso de tools por nombre
- [x] **Crear `_CacheMetrics`** — hits y misses de caché
- [x] **Refactorizar `MetricsCollector`** como facade:
  - `self._requests = _RequestMetrics()`
  - `self._tools = _ToolMetrics()`
  - `self._cache = _CacheMetrics()`
  - Un único `self._lock` en el facade — atomicidad garantizada
  - API pública idéntica (sin cambios para callers)

### Entregables
- [x] `metrics.py` tiene 3 clases internas + 1 facade `MetricsCollector`
- [x] API pública sin cambios — callers no necesitan modificaciones

---

## Fase 6: Eliminar código muerto (EventBus) ✅

**Objetivo**: Eliminar `EventBus` — nunca se usa en producción.
**Dependencias**: Ninguna

### Verificación

Grep confirmó que `EventBus` solo existe en sus propios archivos (`src/infra/events/`)
y en `tests/infra/test_event_bus.py`. Ningún handler, agente ni pipeline lo importa.

### Tareas

- [x] **Eliminar `src/infra/events/bus.py`**
- [x] **Eliminar `src/infra/events/__init__.py`**
- [x] **Eliminar carpeta `src/infra/events/`**
- [x] **Eliminar `tests/infra/test_event_bus.py`** (test de código eliminado)
- [x] **Actualizar `src/infra/__init__.py`** — quitar mención de events en el docstring

### Entregables
- [x] `src/infra/events/` no existe
- [x] `grep -r "EventBus" src/` → 0 resultados

---

## Riesgos y Mitigaciones

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|--------------|---------|------------|
| `save_interaction` tiene 21 parámetros — caller difícil de actualizar | Alta | Alto | Mantener misma firma exacta al mover; no refactorizar parámetros en esta fase |
| `connection.py` tiene lógica de sesión entrelazada con query execution | Media | Alto | Leer implementación completa antes de extraer; hacer cambios mínimos |
| `MetricsCollector` puede tener estado compartido entre responsabilidades | Media | Medio | Diseñar facade antes de dividir; verificar que no hay estado cruzado |
| `EventBus` puede tener callers en archivos de test o scripts | Baja | Bajo | Grep en `tests/` y `scripts/` antes de eliminar |
| `settings.py` — las dos `database_url` pueden diferir sutilmente | Media | Alto | Leer ambas implementaciones y comparar campo por campo antes de deduplicar |

---

## Criterios de Éxito

- [x] `src/domain/interaction/interaction_repository.py` existe con los 4 métodos (incluido `save_log_sync`)
- [x] `src/infra/observability/sql_repository.py` es stub — sin SQL directo
- [x] `SQLValidator` ya era usado por `DatabaseTool` — corrección de análisis incorrecto
- [x] `src/infra/database/schema_introspector.py` existe — `DatabaseManager.get_schema()` delega
- [x] `Settings.database_url` delega a `DbConnectionConfig.database_url` — una sola implementación
- [x] `metrics.py` tiene 3 clases internas + facade `MetricsCollector`
- [x] `grep -r "EventBus" src/` → 0 resultados
- [x] `src/infra/events/` eliminado

---

## Orden de Ejecución Recomendado

Las fases son independientes entre sí (excepto Fase 3 que depende de Fase 2).
Orden sugerido por impacto y riesgo:

1. **Fase 6** (más simple, solo eliminar) — calentamiento
2. **Fase 4** (cambio quirúrgico en settings) — bajo riesgo
3. **Fase 2** (integrar validador existente) — bajo riesgo
4. **Fase 3** (extraer SchemaIntrospector, depende de Fase 2)
5. **Fase 5** (dividir MetricsCollector con facade) — moderado
6. **Fase 1** (mover lógica de negocio) — mayor impacto, más callers

---

## Historial de Cambios

| Fecha | Cambio | Autor |
|-------|--------|-------|
| 2026-04-11 | Creación del plan | Angel David |
| 2026-04-11 | Fase 1 completada — todos los métodos SQL movidos a domain (incluido save_log_sync) | Angel David |
| 2026-04-11 | Fases 3-6 completadas — plan cerrado | Angel David |
