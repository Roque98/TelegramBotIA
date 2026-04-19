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
- `agent`: LLMAgent y agentes (src/agents/)
- `bootstrap`: Composition Root y factories (src/bootstrap/)
- `pipeline`: MainHandler y HandlerManager (src/pipeline/)
- `bot`: Handlers de Telegram (src/bot/)
- `tools`: Sistema de herramientas (src/agents/tools/)
- `db`: Base de datos (src/infra/database/)
- `infra`: Infraestructura transversal (src/infra/)
- `domain`: Lógica de negocio (src/domain/)
- `auth`: Autenticación (src/domain/auth/)
- `api`: Endpoint REST (src/api/)
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

## Arquitectura de Capas

El proyecto sigue una arquitectura de capas con dependencias unidireccionales.
Las capas superiores dependen de las inferiores, nunca al revés.

```
src/bootstrap/   → Composition Root: único lugar donde se ensamblan dependencias
src/pipeline/    → Flujo de conversación (MainHandler, HandlerManager)
src/agents/      → Lógica de agentes (ReAct, factory, orchestrator, tools)
src/domain/      → Lógica de negocio (auth, memory, knowledge, alerts, cost)
src/infra/       → Infraestructura (database, observability, notifications)
src/bot/         → Entrypoint Telegram (handlers, middleware, keyboards)
src/api/         → Entrypoint REST (chat_endpoint)
src/gateway/     → Normalización de canales a ConversationEvent
```

### Reglas de arquitectura
- Nuevas dependencias entre objetos solo se crean en `src/bootstrap/`
- Cada módulo tiene una sola responsabilidad (SRP)
- Nunca importar `src/bot/` o `src/api/` desde capas internas
- `src/domain/` no importa de `src/agents/` ni `src/pipeline/`

---

## Estándares de Código

### Comentarios
- Solo escribir comentarios cuando el **WHY** no es obvio: constraints ocultos, workarounds, invariantes no evidentes
- Nunca explicar QUÉ hace el código — los nombres de funciones y variables ya lo dicen
- Sin docstrings multi-párrafo — máximo una línea cuando sea necesario
- Sin comentarios de contexto de tarea ("agregado para X", "usado por Y", "fix de issue #123")

### Diseño
- No agregar manejo de errores para escenarios imposibles — confiar en las garantías del framework
- No agregar abstracciones prematuras — tres líneas similares no justifican un helper
- No diseñar para requisitos hipotéticos futuros — solo lo que la tarea requiere
- Validar solo en los bordes del sistema (input de usuario, APIs externas)

### Tipado
- Usar tipos concretos cuando se conocen — evitar `Any` salvo en firmas de factory
- `Optional[X]` solo cuando `None` es un valor válido y distinto
- Nunca usar `Optional[Any]` — es redundante

---

## Notas Importantes

- Usar Pydantic v2 para modelos
- El proyecto usa async/await
- Base de datos: SQL Server
- LLM Provider: OpenAI (configurable)
