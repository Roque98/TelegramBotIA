# PLAN: Actualización de documentación

> **Objetivo**: Mantener `.claude/context/` y `docs/estructura.md` sincronizados con el estado real del proyecto tras las migraciones recientes
> **Rama**: `feature/doc-26-docs-update`
> **Prioridad**: 🟠 Alta
> **Estado**: Pendiente

---

## Contexto

Tras completar la reorganización de capas `src/` (Plan 25) y la migración ReAct, varios archivos de contexto y documentación quedaron desactualizados o incompletos.

---

## Archivos a actualizar

### `.claude/context/`

| Archivo | Qué actualizar |
|---------|----------------|
| `ARCHITECTURE.md` | Nueva estructura `src/` con capas gateway/pipeline/domain/infra |
| `HANDLERS.md` | Comandos actuales del bot |
| `TOOLS.md` | Tools disponibles en el ReActAgent |
| `AGENTS.md` | Arquitectura multi-agent actual |
| `DATABASE.md` | Esquema de tablas actualizado |

### `docs/`

| Archivo | Qué actualizar |
|---------|----------------|
| `docs/estructura.md` | Árbol de carpetas real del proyecto |

---

## TODOs

- [ ] Revisar y actualizar `ARCHITECTURE.md` con estructura `src/` actual
- [ ] Actualizar `HANDLERS.md` con todos los handlers registrados
- [ ] Actualizar `TOOLS.md` con tools del ReActAgent
- [ ] Actualizar `AGENTS.md` con arquitectura actual
- [ ] Actualizar `DATABASE.md` con esquema real de SQL Server
- [ ] Actualizar o crear `docs/estructura.md` con árbol de carpetas

---

## Criterios de Aceptación

- Todos los archivos de `.claude/context/` reflejan el estado actual del código
- `docs/estructura.md` tiene el árbol de carpetas correcto
- No hay referencias a módulos o rutas que ya no existen
