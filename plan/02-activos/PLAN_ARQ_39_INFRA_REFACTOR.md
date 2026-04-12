# Plan: ARQ-39 — Refactorización de la capa de infraestructura (SRP)

> **Estado**: 🟡 En progreso
> **Última actualización**: 2026-04-11
> **Rama Git**: develop

## Resumen de Progreso

| Fase | Progreso | Estado |
|------|----------|--------|
| Fase 1: Mover todas las consultas a BD a domain | ██████████ 100% | ✅ Completada |
| Fase 2: Integrar sql_validator en connection | ░░░░░░░░░░ 0% | ⏳ Pendiente |
| Fase 3: Extraer SchemaIntrospector de connection | ░░░░░░░░░░ 0% | ⏳ Pendiente |
| Fase 4: Deduplicar database_url en settings | ░░░░░░░░░░ 0% | ⏳ Pendiente |
| Fase 5: Dividir MetricsCollector en clases focalizadas | ░░░░░░░░░░ 0% | ⏳ Pendiente |
| Fase 6: Eliminar código muerto (EventBus) | ░░░░░░░░░░ 0% | ⏳ Pendiente |

**Progreso Total**: █░░░░░░░░░ 17% (7/28 tareas)

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

## Fase 2: Integrar sql_validator en connection

**Objetivo**: `sql_validator.py` (151 líneas) nunca se usa — `connection.py` valida
SQL manualmente con código duplicado en dos lugares. Integrar el validador existente
y eliminar el código inline duplicado.
**Dependencias**: Ninguna (independiente de Fase 1)

### Problema actual

- `connection.py` líneas ~172-175: validación SQL inline para `execute_query`
- `connection.py` líneas ~226-229: validación SQL inline para `execute_non_query`
- `sql_validator.py` contiene `SqlValidator` completo pero nadie lo importa

### Tareas

- [ ] **Leer `src/infra/database/sql_validator.py`** para entender la API disponible
  - Identificar método/función de validación pública a usar

- [ ] **Leer `src/infra/database/connection.py`** para localizar exactamente
  las dos secciones de validación inline duplicadas

- [ ] **Actualizar `src/infra/database/connection.py`**
  - Agregar import: `from src.infra.database.sql_validator import SqlValidator`
  - Instanciar `SqlValidator` en `__init__` de `DatabaseManager`
  - Reemplazar ambos bloques de validación inline por llamada al validador
  - El comportamiento externo debe ser idéntico (mismas excepciones, mismos mensajes)

- [ ] **Verificar que `sql_validator.py` sigue existiendo** (no eliminarlo — ahora sí se usa)

- [ ] **Verificar**: `python -m pytest tests/ -x -q`

### Entregables
- [ ] `connection.py` importa y usa `SqlValidator`
- [ ] No hay lógica de validación SQL duplicada inline en `connection.py`
- [ ] `grep -r "sql_validator" src/` → al menos 1 resultado (la importación en connection)

---

## Fase 3: Extraer SchemaIntrospector de connection

**Objetivo**: `connection.py` (284 líneas) concentra 7 responsabilidades. La más
separable sin riesgo es `get_schema()` — introspección del esquema de BD.
Extraerla a su propia clase.
**Dependencias**: Fase 2 (connection.py debe estar limpio primero)

### Problema actual

`DatabaseManager` en `connection.py` mezcla:
1. Creación de engine/pool
2. Gestión de sesiones
3. `execute_query()` — ejecución de SELECTs
4. `execute_non_query()` — ejecución de INSERT/UPDATE/DELETE
5. `get_schema()` — introspección de tablas/columnas (diferente responsabilidad)
6. Validación SQL (ya migrada a Fase 2)
7. Async wrappers

### Tareas

- [ ] **Leer `src/infra/database/connection.py`** para entender la implementación
  de `get_schema()` y sus dependencias internas

- [ ] **Crear `src/infra/database/schema_introspector.py`**
  - Clase `SchemaIntrospector`
  - Constructor recibe `DatabaseManager` (o el engine directamente)
  - Método `get_schema()` con la misma firma que el actual

- [ ] **Actualizar `src/infra/database/connection.py`**
  - `get_schema()` en `DatabaseManager` delega a `SchemaIntrospector`
  - O simplemente mantener el método como wrapper para no romper callers

- [ ] **Actualizar `src/infra/database/__init__.py`** para exportar `SchemaIntrospector`

- [ ] **Buscar callers de `get_schema`**
  - `grep -r "get_schema\|\.schema" src/ --include="*.py"`
  - Evaluar si conviene migrar callers a `SchemaIntrospector` directamente

- [ ] **Verificar**: `python -m pytest tests/ -x -q`

### Entregables
- [ ] `src/infra/database/schema_introspector.py` existe con clase `SchemaIntrospector`
- [ ] `DatabaseManager` delega `get_schema()` o los callers usan `SchemaIntrospector`

---

## Fase 4: Deduplicar database_url en settings

**Objetivo**: `settings.py` tiene lógica de construcción de `database_url` duplicada
en dos lugares. Una sola fuente de verdad.
**Dependencias**: Ninguna (independiente de todas las fases)

### Problema actual

`src/config/settings.py`:
- `DbConnectionConfig.database_url` (líneas ~32-60): construye URL con lógica propia
- `Settings.database_url` (líneas ~113-146): repite la misma lógica de construcción

### Tareas

- [ ] **Leer `src/config/settings.py`** para entender ambas implementaciones
  y determinar cuál es la "fuente de verdad"

- [ ] **Refactorizar `src/config/settings.py`**
  - Estrategia A: `Settings.database_url` delega a `DbConnectionConfig.database_url`
  - Estrategia B: extraer función privada `_build_database_url(...)` usada por ambas
  - Elegir la estrategia menos invasiva según la implementación real

- [ ] **Buscar callers de ambas propiedades**
  - `grep -r "database_url\|DbConnectionConfig" src/ --include="*.py"`
  - Verificar que el comportamiento es idéntico para todos los callers

- [ ] **Verificar**: `python -m pytest tests/ -x -q`

### Entregables
- [ ] Lógica de construcción de `database_url` existe solo en un lugar
- [ ] `grep -r "database_url" src/config/settings.py` → una sola implementación

---

## Fase 5: Dividir MetricsCollector en clases focalizadas

**Objetivo**: `metrics.py` (388 líneas) tiene `MetricsCollector` con 7 responsabilidades
mezcladas. Dividir en 3 clases con responsabilidad única.
**Dependencias**: Ninguna

### Problema actual

`MetricsCollector` en `src/infra/observability/metrics.py` mezcla:
1. Latencia de requests
2. Distribución de pasos ReAct
3. Contadores de requests
4. Tracking de errores
5. Uso de tools
6. Estadísticas de caché
7. Cómputo de estadísticas agregadas

### Tareas

- [ ] **Leer `src/infra/observability/metrics.py`** para mapear exactamente
  qué métodos pertenecen a cada responsabilidad

- [ ] **Diseñar la división en 3 clases:**
  - `RequestMetrics`: latencia, contadores, errores de requests
  - `AgentMetrics`: pasos ReAct, tool usage, estadísticas de agente
  - `CacheMetrics`: estadísticas de caché (hits, misses, evictions)

- [ ] **Crear las 3 nuevas clases** dentro de `metrics.py` (mismo archivo,
  no crear archivos nuevos para no romper imports)

- [ ] **Mantener `MetricsCollector` como facade** que compone las 3 clases
  para no romper callers existentes:
  ```python
  class MetricsCollector:
      def __init__(self):
          self.requests = RequestMetrics()
          self.agent = AgentMetrics()
          self.cache = CacheMetrics()
      # Métodos públicos delegan a sub-colectores
  ```

- [ ] **Buscar callers de `MetricsCollector`**
  - `grep -r "MetricsCollector\|metrics_collector" src/ --include="*.py"`
  - Verificar que el facade no rompe ningún caller

- [ ] **Verificar**: `python -m pytest tests/ -x -q`

### Entregables
- [ ] `metrics.py` tiene 3 clases especializadas + 1 facade `MetricsCollector`
- [ ] Todos los callers existentes siguen funcionando sin cambios

---

## Fase 6: Eliminar código muerto (EventBus)

**Objetivo**: `events/bus.py` (169 líneas) es código muerto — `EventBus` nunca
se usa en ningún handler, agente ni pipeline. Eliminarlo para reducir mantenimiento.
**Dependencias**: Ninguna

### Verificación previa (OBLIGATORIA)

Antes de eliminar, confirmar que realmente no se usa:

- [ ] **Ejecutar**: `grep -r "EventBus\|events.bus\|from src.infra.events" src/ tests/ --include="*.py"`
  - Si hay resultados → NO eliminar, investigar primero
  - Si no hay resultados → proceder con eliminación

### Tareas (solo si verificación confirma código muerto)

- [ ] **Eliminar `src/infra/events/bus.py`**

- [ ] **Evaluar `src/infra/events/__init__.py`**
  - Si está vacío o solo re-exporta `EventBus` → eliminar también
  - Si tiene otros contenidos → conservar

- [ ] **Evaluar `src/infra/events/`**
  - Si la carpeta queda vacía → eliminar carpeta completa

- [ ] **Verificar**: `python -m pytest tests/ -x -q`

### Entregables
- [ ] `src/infra/events/bus.py` no existe
- [ ] `grep -r "EventBus" src/ tests/` → 0 resultados

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
- [ ] `python -m pytest tests/ -x -q` pasa tras cada fase
- [ ] `connection.py` usa `SqlValidator` en lugar de validación inline duplicada
- [ ] `settings.py` tiene una sola implementación de `database_url`
- [ ] `grep -r "EventBus" src/ tests/` → 0 resultados
- [ ] `src/infra/` no tiene archivos con más de 3 responsabilidades

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
