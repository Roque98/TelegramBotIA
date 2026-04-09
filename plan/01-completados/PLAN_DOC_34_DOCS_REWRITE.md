# Plan: DOC-34 Reescritura Completa de Documentación

> **Estado**: 🟢 Completado
> **Última actualización**: 2026-04-08
> **Rama Git**: `develop`

## Resumen de Progreso

| Fase | Progreso | Estado |
|------|----------|--------|
| Fase 1: Estructura base | ██████████ 100% | ✅ Completada |
| Fase 2: Enfoque Uso | ██████████ 100% | ✅ Completada |
| Fase 3: Enfoque Código | ██████████ 100% | ✅ Completada |
| Fase 4: Enfoque Dev | ██████████ 100% | ✅ Completada |
| Fase 5: Limpieza y cierre | ██████████ 100% | ✅ Completada |

**Progreso Total**: ██████████ 100% (26/26 tareas)

---

## Descripción

La documentación actual está dispersa entre carpetas inconsistentes (`docs/archivo/`,
`docs/guia del desarrollador/`, `docs/desarrollador/`, `docs/modulos/`, `docs/api/`,
`docs/onenote/`), mezcla HTML con Markdown, y una gran parte es obsoleta o no refleja
la arquitectura actual (5 capas, ReActAgent, ARQ-33, OBS-31, etc.).

Este plan rehace toda la documentación desde cero con dos grandes enfoques:
- **Uso**: para quienes operan, configuran o usan el sistema
- **Código**: para quienes entienden, mantienen o extienden el código

---

## Nueva Estructura de `docs/`

```
docs/
├── index.md                         ← Entrada única al proyecto
│
├── uso/                             ← Para usuarios, admins, integradores
│   ├── README.md
│   ├── que-puede-hacer.md
│   ├── guia-usuario-telegram.md
│   ├── guia-administrador.md
│   ├── guia-api.md
│   └── configuracion.md
│
├── codigo/                          ← Para desarrolladores
│   ├── README.md
│   ├── arquitectura.md
│   ├── flujos.md
│   ├── agente-react.md
│   ├── tools.md
│   ├── pipeline.md
│   ├── dominio.md
│   ├── infraestructura.md
│   ├── base-de-datos.md
│   └── como-extender.md
│
└── dev/                             ← Para configurar entorno de desarrollo
    ├── setup.md
    ├── gitflow.md
    └── testing.md
```

---

## Fases

### Fase 1: Estructura Base

**Objetivo**: Crear el andamiaje vacío y el índice principal antes de escribir contenido.
**Dependencias**: Ninguna

- [ ] Crear `docs/index.md` — entrada única con descripción del proyecto, stack tecnológico y navegación a los dos enfoques
- [ ] Crear `docs/uso/README.md` — índice del enfoque uso con descripción de cada archivo
- [ ] Crear `docs/codigo/README.md` — índice del enfoque código con descripción de cada archivo
- [ ] Crear `docs/dev/README.md` — índice del enfoque dev

---

### Fase 2: Enfoque Uso

**Objetivo**: Documentación completa para usuarios finales, admins y consumidores del API.
**Dependencias**: Fase 1

- [ ] `docs/uso/que-puede-hacer.md` — Qué es Amber, qué puede responder, ejemplos de consultas, limitaciones
- [ ] `docs/uso/guia-usuario-telegram.md` — Registro (`/register`, `/verify`), comandos (`/start`, `/help`, `/ia`), cómo hacer consultas, tips para mejores resultados
- [ ] `docs/uso/guia-administrador.md` — Gestión de usuarios (activar/desactivar), permisos por recurso (`BotIAv2_Recurso`), base de conocimiento (agregar/editar artículos), monitoreo básico
- [ ] `docs/uso/guia-api.md` — Endpoint `POST /api/chat`, generación de tokens AES, ejemplos cURL y Python, códigos de error
- [ ] `docs/uso/configuracion.md` — Variables de entorno requeridas, `settings.py` explicado, configuración de BD, configuración del LLM

---

### Fase 3: Enfoque Código

**Objetivo**: Documentación completa para entender la arquitectura y el código fuente.
**Dependencias**: Fase 1

- [ ] `docs/codigo/arquitectura.md` — Las 5 capas del sistema con diagrama ASCII, patrones de diseño usados (Singleton, Factory, Strategy, Repository, Gateway), contratos clave (`AgentResponse`, `UserContext`, `ConversationEvent`)
- [ ] `docs/codigo/flujos.md` — Flujo completo de un mensaje Telegram (10 pasos), flujo de una request API, flujo interno del loop ReAct con JSON de ejemplo, flujo de registro de usuario
- [ ] `docs/codigo/agente-react.md` — Cómo piensa el agente (Think-Act-Observe), system prompt y `{usage_hints}` dinámicos (ARQ-33), scratchpad, síntesis por timeout, filtrado por permisos
- [ ] `docs/codigo/tools.md` — Contrato `BaseTool`/`ToolDefinition`/`ToolResult`, las 8 tools con parámetros y ejemplos, `ToolRegistry` (singleton, filtrado por permisos), `usage_hint` por tool
- [ ] `docs/codigo/pipeline.md` — `MainHandler` y su flujo `_process_event`, `factory.py` como composición root de DI, `MessageGateway` como normalizador de canales
- [ ] `docs/codigo/dominio.md` — Dominio Auth (entidad, repositorios, servicio), Memory (perfil de usuario, working memory, cache), Knowledge (artículos, categorías, búsqueda), Cost (tracking de costos LLM)
- [ ] `docs/codigo/infraestructura.md` — `DatabaseManager` (pool, SQLValidator), sistema de observabilidad (traces + métricas + logs en BD), `EventBus`, utils (encryption, rate limiter, retry, input validator)
- [ ] `docs/codigo/base-de-datos.md` — Todas las tablas `BotIAv2_*` con columnas, tipos y propósito, diagrama de relaciones, ejemplos de queries
- [ ] `docs/codigo/como-extender.md` — Receta para nueva tool (5 pasos), receta para nuevo comando Telegram, receta para nuevo dominio, checklist de extensión

---

### Fase 4: Enfoque Dev

**Objetivo**: Documentación para configurar el entorno y trabajar en el proyecto.
**Dependencias**: Fase 1

- [ ] `docs/dev/setup.md` — Clonar, virtualenv (`GPT5-Cxk5mELR`), instalar dependencias, configurar `.env`, primera ejecución
- [ ] `docs/dev/gitflow.md` — GitFlow del proyecto: branches (`feature/*`, `develop`, `master`), convención de commits, proceso de PR, cuándo hacer push
- [ ] `docs/dev/testing.md` — Tests unitarios (`pytest`), scripts de prueba manual (`scripts/test_message.py`), cómo interpretar logs y tablas de observabilidad

---

### Fase 5: Limpieza y Cierre

**Objetivo**: Eliminar documentación obsoleta y actualizar referencias.
**Dependencias**: Fases 2, 3 y 4

- [ ] Eliminar `docs/archivo/` (contenido obsoleto pre-ReAct)
- [ ] Eliminar `docs/guia del desarrollador/` (HTML, reemplazado por `docs/codigo/`)
- [ ] Eliminar `docs/onenote/` (dumps internos que no aportan a lectores externos)
- [ ] Eliminar `docs/desarrollador/`, `docs/modulos/`, `docs/api/`, `docs/resumen.md` (reemplazados)
- [ ] Actualizar `README.md` raíz con enlace a `docs/index.md`
- [ ] Actualizar `CLAUDE.md`: quitar referencia al archivo onenote de 2024
- [ ] Commit y push del resultado completo

---

## Criterios de Éxito

- Un desarrollador nuevo puede entender la arquitectura leyendo solo `docs/codigo/`
- Un admin puede gestionar usuarios y permisos leyendo solo `docs/uso/guia-administrador.md`
- No hay archivos duplicados ni documentación desactualizada en `docs/`
- Todos los archivos son `.md` (sin HTML)
- La raíz `docs/index.md` es el único punto de entrada necesario

---

## Notas

- Fuente de verdad para código: `.claude/context/` (ARCHITECTURE.md, AGENTS.md, TOOLS.md, HANDLERS.md, DATABASE.md)
- No crear documentación de roadmap futuro ni planes — eso vive en `plan/`
- Estilo: español, sin emojis decorativos, tablas donde haya más de 3 items comparables, bloques de código para todo lo ejecutable
