# Instrucciones para Claude Code

## Proyecto
**Nombre**: Iris Bot
**Tipo**: Bot conversacional con LLM para Telegram
**Rama principal**: develop (GitFlow)

## Actualización de Contexto

### Cuándo actualizar `.claude/context/`
- Cuando se creen nuevos módulos o carpetas importantes
- Cuando cambie la arquitectura del proyecto
- Cuando se agreguen nuevos handlers, tools o agentes
- Cuando se modifique la estructura de base de datos

### Archivos a mantener actualizados
- `ARCHITECTURE.md` - Estructura de capas
- `HANDLERS.md` - Comandos del bot
- `TOOLS.md` - Sistema de herramientas
- `AGENTS.md` - Agentes LLM
- `DATABASE.md` - Esquema de BD

---

## Comportamiento de Git

### Commits Automáticos
- **Hacer commit automáticamente** cuando se completen cambios significativos:
  - Creación o modificación de archivos de código
  - Actualización de documentación o planes
  - Consolidación o refactorización de archivos
  - Finalización de una tarea del plan

### Archivos Sin Trackear
- **Revisar y agregar** archivos untracked que no estén en `.gitignore`
- No dejar archivos legítimos sin subir al repositorio
- Si hay archivos que no deberían subirse, agregarlos a `.gitignore`

### Convención de Commits
Usar formato: `tipo(scope): descripción`

Tipos:
- `feat`: Nueva funcionalidad
- `fix`: Corrección de bug
- `refactor`: Refactorización sin cambio de funcionalidad
- `docs`: Documentación
- `test`: Tests
- `chore`: Tareas de mantenimiento

Scopes del proyecto:
- `agent`: LLMAgent y agentes
- `bot`: Handlers de Telegram
- `tools`: Sistema de herramientas
- `db`: Base de datos
- `auth`: Autenticación
- `plan`: Planes de proyecto
- `skill`: Skills de Claude

### Push Automático
- Hacer push automáticamente después de cada commit
- Rama actual: seguir GitFlow (feature/*, develop, etc.)

## Documentación

La documentación del proyecto está en `docs/` con dos enfoques:
- `docs/uso/` — Para usuarios, admins e integradores
- `docs/codigo/` — Para desarrolladores
- `docs/dev/` — Para configurar el entorno

Al agregar nuevas features significativas, actualizar el archivo relevante de `docs/codigo/`
o `docs/uso/` según corresponda.

---

## Plan Activo

Planes completados recientes:
- `plan/01-completados/PLAN_REACT_MIGRATION.md` — Migración a ReAct
- `plan/01-completados/PLAN_ARQ_25_SRC_LAYOUT.md` — Reorganización de capas src/

Ideas y planes activos:
- `plan/03-ideas/IDEAS_MEJORA_BOT.md`
- `plan/02-activos/` — ver `plan/README.md` para el índice completo

## Archivos de Contexto

- `.claude/context/` - Documentación del estado actual del proyecto
- `.claude/skills/` - Skills disponibles para desarrollo
- `plan/` - Planes de proyecto con TODOs

## Skills de Referencia

Consultar estas skills para convenciones y patrones:
- `.claude/skills/gitflow-workflow/SKILL.md` - Convenciones de Git y GitHub
- `.claude/skills/project-planner/SKILL.md` - Formato de planes con TODOs
- `.claude/skills/python-bot-context-manager/SKILL.md` - Patrones de desarrollo del bot
- `.claude/skills/onenote-documentation/SKILL.md` - Documentación de proyectos para OneNote

---

## Notas Importantes

- Usar Pydantic v2 para modelos
- El proyecto usa async/await
- Base de datos: SQL Server
- LLM Provider: OpenAI (configurable)
