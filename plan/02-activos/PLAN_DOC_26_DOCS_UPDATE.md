# PLAN: Actualización y organización de documentación

> **Objetivo**: Llevar toda la documentación del proyecto al estado actual del código — eliminando referencias obsoletas, reflejando la nueva estructura de `src/` (ARQ-25) y consolidando docs dispersos o redundantes
> **Rama**: `feature/doc-26-docs-update`
> **Prioridad**: 🟠 Alta
> **Progreso**: ░░░░░░░░░░ 0% (0/22 tareas)

---

## Contexto

El proyecto tiene ~57 archivos de documentación (~24,600 líneas). Tras las reorganizaciones ARQ-24 y ARQ-25, muchos documentos referencian rutas que ya no existen. Los más críticos son los archivos en `.claude/context/` porque Claude los lee en cada sesión para tomar decisiones.

### Inventario de problemas encontrados

| Grupo | Archivos | Problema principal |
|-------|----------|--------------------|
| `.claude/context/` | 5 archivos | Rutas `src/agent/` → deben ser `src/agents/`, `src/domain/`, etc. |
| `docs/estructura.md` | 1 archivo (439 ln) | Rutas antiguas de `database/`, `auth/`, etc. |
| `docs/ANALISIS_CODIGO_ARQUITECTURA.md` | 1 archivo (2,540 ln) | 50+ referencias a rutas obsoletas + arquitectura vieja |
| `docs/futuros-features/` | 6 archivos (3,907 ln) | Duplica información del sistema `plan/`, referencias rotas |
| `docs/todos/` | 2 archivos (1,213 ln) | Posiblemente obsoletos; duplican el BACKLOG |
| `resumen.md` (raíz) | 1 archivo (33 ln) | No está en `docs/`, contenido a verificar |
| `README.md` raíz | 1 archivo (131 ln) | 2 referencias a paths incorrectos |

### Tabla de rutas: Antigua → Actual

| Ruta antigua (documentada) | Ruta actual (código real) |
|---------------------------|--------------------------|
| `src/agent/` | `src/agents/` |
| `src/auth/` | `src/domain/auth/` |
| `src/memory/` | `src/domain/memory/` |
| `src/knowledge/` | `src/domain/knowledge/` |
| `src/database/` | `src/infra/database/` |
| `src/events/` | `src/infra/events/` |
| `src/observability/` | `src/infra/observability/` |
| `src/chat_endpoint.py` | `src/api/chat_endpoint.py` |
| `src/gateway/handler.py` | `src/pipeline/handler.py` |
| `src/gateway/factory.py` | `src/pipeline/factory.py` |

### Por qué este orden de fases

- **Fase 1** (`.claude/context/`) es la más urgente: son los archivos que Claude lee en cada sesión para orientarse en el proyecto.
- **Fase 2** (`docs/` técnicos) afectan a desarrolladores que consultan la estructura.
- **Fase 3** (limpieza de redundantes) reduce ruido pero no bloquea a nadie.

---

## Resumen de Progreso

| Fase | Tareas | Progreso | Estado |
|------|--------|----------|--------|
| Fase 1: Actualizar `.claude/context/` | 6 | ░░░░░░░░░░ 0% | ⏳ Pendiente |
| Fase 2: Actualizar docs técnicos clave | 7 | ░░░░░░░░░░ 0% | ⏳ Pendiente |
| Fase 3: Limpiar docs obsoletos/redundantes | 9 | ░░░░░░░░░░ 0% | ⏳ Pendiente |

---

## Fase 1 — Actualizar `.claude/context/`

**Objetivo**: Que Claude tenga un mapa preciso del código al inicio de cada sesión.

**Archivos a actualizar**:

- `.claude/context/INDEX.md` — Fecha obsoleta (2024-02-13), menciona ramas completadas
- `.claude/context/ARCHITECTURE.md` — Diagrama usa `src/agent/` en lugar de `src/agents/`, no refleja la nueva estructura de capas (`domain/`, `infra/`, `pipeline/`)
- `.claude/context/AGENTS.md` — Múltiples referencias a `src/agent/` (60, 120, 145, 163, 178, 200, 210)
- `.claude/context/MEMORY.md` — Apunta a `src/agent/memory/` (ahora `src/domain/memory/`)
- `.claude/context/PROMPTS.md` — Apunta a `src/agent/prompts/`

**Dependencias**: Ninguna

### Tareas

- [ ] **26.1** Actualizar `INDEX.md` — fecha, rama actual, estado del proyecto, lista de archivos de contexto disponibles
- [ ] **26.2** Reescribir `ARCHITECTURE.md` — reflejar la nueva estructura de 9 carpetas (`api/`, `bot/`, `gateway/`, `pipeline/`, `agents/`, `domain/`, `infra/`, `config/`, `utils/`) con descripción de responsabilidad de cada capa
- [ ] **26.3** Actualizar `AGENTS.md` — corregir todas las rutas `src/agent/` → `src/agents/`, verificar que los patrones documentados siguen vigentes
- [ ] **26.4** Actualizar `MEMORY.md` — corregir rutas `src/agent/memory/` → `src/domain/memory/`
- [ ] **26.5** Actualizar `PROMPTS.md` — corregir rutas, verificar si los templates descritos siguen existiendo
- [ ] **26.6** Verificar `HANDLERS.md`, `TOOLS.md`, `DATABASE.md` — si hay referencias obsoletas, corregirlas (probablemente menores)

### Entregables
- [ ] Todos los archivos `.claude/context/` referencian rutas reales del código
- [ ] `INDEX.md` tiene fecha actual y estado correcto del proyecto

---

## Fase 2 — Actualizar docs técnicos clave

**Objetivo**: Que los documentos que un desarrollador consulta al integrarse al proyecto sean precisos.

**Dependencias**: Fase 1 completada

### Tareas

- [ ] **26.7** Actualizar `docs/estructura.md` — reescribir la sección de estructura `src/` con las nuevas carpetas, eliminar referencias a rutas antiguas (`database/`, `auth/`, etc.)
- [ ] **26.8** Actualizar `README.md` raíz — corregir 2 referencias con rutas incorrectas a `COMMIT_GUIDELINES.md` y `GITFLOW.md`
- [ ] **26.9** Revisar `docs/SISTEMA_AUTENTICACION.md` — actualizar rutas de `src/auth/` → `src/domain/auth/` en las secciones de código
- [ ] **26.10** Revisar `docs/CHAT_API_GUIDE.md` y `docs/API_ENDPOINTS.md` — verificar que las rutas de arranque (`python src/api/chat_endpoint.py`) sean correctas
- [ ] **26.11** Revisar `docs/desarrollador/GUIA_DESARROLLADOR.md` (1,896 ln) — actualizar estructura de carpetas y referencias de paths
- [ ] **26.12** Actualizar `docs/desarrollador/DIAGRAMA_FLUJO_ACTUAL.md` — reflejar el flujo real con `pipeline/`, `gateway/`, `domain/`
- [ ] **26.13** Mover `resumen.md` de la raíz → `docs/resumen.md` o incorporarlo al README

### Entregables
- [ ] `docs/estructura.md` refleja la estructura real de `src/`
- [ ] `README.md` sin referencias a rutas incorrectas
- [ ] Docs de desarrollador coherentes con el código actual

---

## Fase 3 — Limpiar docs obsoletos y redundantes

**Objetivo**: Reducir el ruido documental eliminando duplicados y archivando material obsoleto.

**Dependencias**: Fase 2 completada

### Tareas

- [ ] **26.14** Evaluar `docs/ANALISIS_CODIGO_ARQUITECTURA.md` (2,540 ln) — decidir si archivarlo en `docs/archivo/` o actualizarlo; tiene valor histórico pero 50+ rutas obsoletas lo hacen confuso como referencia activa
- [ ] **26.15** Evaluar `docs/futuros-features/` (6 archivos, 3,907 ln) — este material fue creado antes del sistema `plan/`. Decisión: ¿archivar en `docs/archivo/futuros-features/` o mantener como referencia de roadmap de alto nivel?
- [ ] **26.16** Evaluar `docs/todos/` (2 archivos, 1,213 ln) — probable duplicado del `plan/BACKLOG.md`. Decidir si archivar o eliminar
- [ ] **26.17** Limpiar `docs/todos.md` (9 ln, placeholder vacío) — eliminar o completar
- [ ] **26.18** Revisar `docs/onenote/` — verificar si los snapshots siguen siendo útiles o se pueden mover a `docs/archivo/`
- [ ] **26.19** Crear `docs/archivo/` si se decide archivar material (en lugar de eliminar — conserva historial)
- [ ] **26.20** Actualizar `docs/index.md` — reflejar la nueva organización de `docs/`
- [ ] **26.21** Actualizar `CLAUDE.md` raíz — la sección "Plan Activo" sigue apuntando al PLAN_REACT_MIGRATION completado
- [ ] **26.22** Actualizar `plan/README.md` y `plan/BACKLOG.md` — mover ARQ-25 a completados, actualizar contadores

### Entregables
- [ ] `docs/` sin archivos placeholder vacíos
- [ ] Material obsoleto en `docs/archivo/` en lugar de mezclado con docs activos
- [ ] `CLAUDE.md` apunta al plan activo correcto
- [ ] `plan/` refleja el estado real del proyecto

---

## Criterios de Éxito

- [ ] Ningún archivo en `.claude/context/` referencia una ruta de código que no existe
- [ ] `docs/estructura.md` describe la estructura `src/` actual
- [ ] `README.md` sin referencias rotas
- [ ] `docs/` está organizado de forma que un desarrollador nuevo pueda orientarse sin confusión
- [ ] `CLAUDE.md` tiene el plan activo correcto

---

## Riesgos

| Riesgo | Mitigación |
|--------|-----------|
| Archivar docs que todavía se usan como referencia | Preguntar antes de archivar `futuros-features/` y `todos/` |
| Perder información valiosa al limpiar | Usar `docs/archivo/` en lugar de eliminar directamente |
| `ANALISIS_CODIGO_ARQUITECTURA.md` es muy grande para actualizar manualmente | Decidir primero si tiene valor activo o es histórico |

---

## Historial de Cambios

| Fecha | Cambio |
|-------|--------|
| 2026-03-28 | Creación del plan |
