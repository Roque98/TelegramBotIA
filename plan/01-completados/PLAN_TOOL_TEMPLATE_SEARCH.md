# Plan: Tool — template_search_by_name

> **Estado**: 🟢 Completado
> **Última actualización**: 2026-04-22
> **Rama Git**: develop

## Resumen de Progreso

| Fase | Progreso | Estado |
|------|----------|--------|
| Fase 1: Repositorio | ██████████ 100% | ✅ Completada |
| Fase 2: Tool Python | ██████████ 100% | ✅ Completada |
| Fase 3: Registro en factory | ██████████ 100% | ✅ Completada |
| Fase 4: Migración SQL | ██████████ 100% | ✅ Completada |
| Fase 5: Prompt del agente | ██████████ 100% | ✅ Completada |

**Progreso Total**: ██████████ 100% (13/13 tareas)

---

## Descripción

Agregar la tool `template_search_by_name` que permite al agente encontrar templates
buscando por nombre parcial de aplicación. Consulta en paralelo banco (`Template_GetByNombre`)
y EKT (`Template_GetByNombre_ekt`), etiquetando cada resultado con su origen (`instancia`).

Esto habilita flujos como:
> *"¿Cuál es la matriz de escalamiento de ppServicios?"*
1. Agente llama `template_search_by_name(nombre="ppServicios")` → recibe `id=15037, instancia="BAZ"`
2. Agente llama `get_escalation_matrix(template_id=15037, usar_ekt=False)`

---

## Fase 1: Repositorio

**Objetivo**: Agregar `get_templates_by_nombre()` al `AlertRepository`.
**Archivo**: `src/domain/alerts/alert_repository.py`
**Dependencias**: Ninguna

### Tareas

- [x] **Agregar `get_templates_by_nombre(nombre: str) -> list[Template]`** en `AlertRepository`
  - Consulta BAZ y EKT en paralelo con `asyncio.gather`
  - Filas con error se ignoran con warning

### Entregables
- [x] Método implementado y correctamente tipado

---

## Fase 2: Tool Python

**Objetivo**: Crear `TemplateSearchByNameTool`.
**Archivo**: `src/agents/tools/template_search_by_name_tool.py`

### Tareas

- [x] **Crear `TemplateSearchByNameTool`**
  - `is_read_only=True`, validación mínimo 2 chars, campo `truncado`

### Entregables
- [x] Archivo creado

---

## Fase 3: Registro en factory

**Objetivo**: Registrar la tool en `tool_factory.py`.

### Tareas

- [x] **Agregar al catálogo en `_build_tool_catalog()`**
  - Import y lambda junto a `get_template_by_id`

### Entregables
- [x] Tool instanciable desde el factory

---

## Fase 4: Migración SQL

**Objetivo**: Script `018_template_search_by_name_tool.sql`.

### Tareas

- [x] **Crear script idempotente** con registro en Recurso, copia de permisos y alta en AgenteTools

### Entregables
- [x] Script SQL creado (`scripts/migrations/018_template_search_by_name_tool.sql`)

---

## Fase 5: Prompt del agente

**Objetivo**: Prompt del agente `alertas` actualizado.

### Tareas

- [x] **Agregar flujo nombre→id en prompt** (migraciones 019–023)
- [x] **Prohibir acción inventada "present_templates"** (migración 023)
- [x] **Snapshots** guardados en historial antes de cada actualización

### Entregables
- [x] Prompt actualizado con instrucciones detalladas para `template_search_by_name`
- [x] Snapshots guardados

---

## Criterios de Éxito

- [x] *"Dame la matriz de escalamiento de ppServicios"* → el agente llama `template_search_by_name` + `get_escalation_matrix`
- [x] Si el template existe en EKT → `usar_ekt=true` se pasa correctamente
- [x] Si hay múltiples coincidencias → el agente presenta la lista al usuario con `finish`
- [x] Si no hay resultados → mensaje claro al usuario
- [x] Script SQL es idempotente

---

## Historial de Cambios

| Fecha | Cambio | Autor |
|-------|--------|-------|
| 2026-04-21 | Creación del plan | Claude |
| 2026-04-21 | Agregar fases 4-5 | Claude |
| 2026-04-22 | Marcado como completado (todo implementado) | Claude |
