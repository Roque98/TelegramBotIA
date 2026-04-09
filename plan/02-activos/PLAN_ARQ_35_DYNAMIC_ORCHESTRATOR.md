# Plan: ARQ-35 Orchestrator con Agentes Dinámicos

> **Estado**: 🟡 En progreso
> **Última actualización**: 2026-04-08
> **Rama Git**: `feature/arq-35-dynamic-orchestrator`

## Resumen de Progreso

| Fase | Progreso | Estado |
|------|----------|--------|
| Fase 1: Schema de BD | ░░░░░░░░░░ 0% | ⏳ Pendiente |
| Fase 2: Dominio (entity + repo + service) | ░░░░░░░░░░ 0% | ⏳ Pendiente |
| Fase 3: Agent builder dinámico | ░░░░░░░░░░ 0% | ⏳ Pendiente |
| Fase 4: Orchestrator N-way | ░░░░░░░░░░ 0% | ⏳ Pendiente |
| Fase 5: Admin tooling y recarga | ░░░░░░░░░░ 0% | ⏳ Pendiente |
| Fase 6: Tests y migración | ░░░░░░░░░░ 0% | ⏳ Pendiente |

**Progreso Total**: ░░░░░░░░░░ 0% (0/22 tareas)

---

## Descripción

Evolucionar el `AgentOrchestrator` existente (ARQ-30, actualmente binario casual/data)
a un sistema de N agentes especializados cuyos prompts, herramientas y estado activo
se gestionan enteramente desde la base de datos.

### Motivación

Con 8 tools actuales el sistema funciona bien con un agente único. Al agregar más tools
(proyección: 15-25), el LLM empieza a confundirse en la selección. Agentes especializados
mantienen cada prompt corto y cada conjunto de tools coherente, manteniendo alta precisión
sin sacrificar flexibilidad.

### Diseño central

```
Query del usuario
        │
        ▼
IntentClassifier (nano LLM)
  ← descriptions de agentes leídas desde BD →
        │
        ├─ "datos"        → DataAgent       (database_query, calculate, datetime)
        ├─ "conocimiento" → KnowledgeAgent  (knowledge_search, calculate, datetime)
        ├─ "casual"       → CasualAgent     (save_preference, save_memory)
        └─ "generalista"  → GeneralistAgent (todos los tools permitidos al usuario)
                                             ↑ fallback para queries cross-dominio
```

**Composición de tools visible por usuario:**

```
tools_visibles = scope_del_agente ∩ permisos_del_usuario
```

El agente generalista ignora el scope y usa directamente los permisos del usuario
(comportamiento idéntico al ReActAgent actual).

**Prompts desde BD:** El `systemPrompt` de cada agente vive en `BotIAv2_AgenteDef`.
Cada edición genera un registro en `BotIAv2_AgentePromptHistorial` para auditoría y rollback.

---

## Qué existe y se reutiliza

| Componente | Estado | Cambio requerido |
|------------|--------|-----------------|
| `src/agents/orchestrator/orchestrator.py` | Funcional (binario) | Refactor a N-way |
| `src/agents/orchestrator/intent_classifier.py` | Funcional (binario) | Prompt dinámico desde BD |
| `ReActAgent` | Sin cambios | Recibe prompt y tool-scope como parámetros |
| `ToolRegistry` | Sin cambios | Sigue siendo el registro global |
| `SEC-01 PermissionService` | Sin cambios | Sigue filtrando por usuario |
| `pipeline/factory.py` | Cambio menor | Construir orchestrator en lugar de react_agent directo |

---

## Fases

### Fase 1: Schema de base de datos

**Objetivo**: Tres tablas nuevas que sostienen toda la configuración de agentes.
**Dependencias**: Ninguna

- [ ] Crear `BotIAv2_AgenteDef` — definición de cada agente

  ```sql
  CREATE TABLE abcmasplus..BotIAv2_AgenteDef (
      idAgente          INT PRIMARY KEY IDENTITY,
      nombre            VARCHAR(100) UNIQUE NOT NULL,  -- 'datos', 'conocimiento', 'casual', 'generalista'
      descripcion       VARCHAR(500) NOT NULL,          -- usada por el classifier para rutear
      systemPrompt      NVARCHAR(MAX) NOT NULL,
      temperatura       DECIMAL(3,2) DEFAULT 0.1,
      maxIteraciones    INT DEFAULT 10,
      modeloOverride    VARCHAR(100) NULL,              -- NULL = usa openai_loop_model del sistema
      esGeneralista     BIT DEFAULT 0,                  -- 1 = ignora scope, usa permisos directos
      activo            BIT DEFAULT 1,
      version           INT DEFAULT 1,
      fechaActualizacion DATETIME2 DEFAULT GETDATE()
  );
  ```

- [ ] Crear `BotIAv2_AgenteTools` — tools en el scope de cada agente

  ```sql
  CREATE TABLE abcmasplus..BotIAv2_AgenteTools (
      idAgenteTools  INT PRIMARY KEY IDENTITY,
      idAgente       INT NOT NULL REFERENCES BotIAv2_AgenteDef(idAgente),
      nombreTool     VARCHAR(100) NOT NULL,  -- 'database_query', 'knowledge_search', etc.
      activo         BIT DEFAULT 1,
      UNIQUE (idAgente, nombreTool)
  );
  ```

- [ ] Crear `BotIAv2_AgentePromptHistorial` — auditoría de cambios de prompt

  ```sql
  CREATE TABLE abcmasplus..BotIAv2_AgentePromptHistorial (
      idHistorial   INT PRIMARY KEY IDENTITY,
      idAgente      INT NOT NULL REFERENCES BotIAv2_AgenteDef(idAgente),
      systemPrompt  NVARCHAR(MAX) NOT NULL,
      version       INT NOT NULL,
      razonCambio   VARCHAR(500),
      modificadoPor VARCHAR(100),
      fechaCreacion DATETIME2 DEFAULT GETDATE()
  );
  ```

- [ ] Insertar datos iniciales: 4 agentes (datos, conocimiento, casual, generalista)
  con prompts adaptados de `REACT_SYSTEM_PROMPT` actual y sus tools correspondientes.

---

### Fase 2: Dominio — entity, repository, service

**Objetivo**: Capa de acceso a la configuración de agentes con cache LRU.
**Dependencias**: Fase 1

- [ ] `src/domain/agent_config/agent_config_entity.py`

  ```python
  class AgentDefinition(BaseModel):
      id: int
      nombre: str
      descripcion: str
      system_prompt: str
      temperatura: float
      max_iteraciones: int
      modelo_override: Optional[str]
      es_generalista: bool
      tools: list[str]               # ['database_query', 'calculate', ...]
      activo: bool
      version: int
  ```

- [ ] `src/domain/agent_config/agent_config_repository.py`
  - `get_all_active() → list[AgentDefinition]`
  - `get_by_nombre(nombre) → Optional[AgentDefinition]`
  - `get_generalista() → Optional[AgentDefinition]`
  — JOINs `BotIAv2_AgenteDef` con `BotIAv2_AgenteTools`

- [ ] `src/domain/agent_config/agent_config_service.py`
  - Cache LRU TTL 5 min (mismo patrón que `PermissionService`)
  - `get_active_agents() → list[AgentDefinition]`
  - `invalidate_cache()` — llamado por el tool de recarga

---

### Fase 3: Agent builder dinámico

**Objetivo**: Construir una instancia de `ReActAgent` a partir de un `AgentDefinition`.
**Dependencias**: Fase 2

- [ ] `src/agents/factory/agent_builder.py` — `AgentBuilder`

  ```python
  class AgentBuilder:
      def __init__(self, tool_registry: ToolRegistry, llm_providers: dict[str, LLMProvider])

      def build(self, definition: AgentDefinition) -> ReActAgent:
          """
          Construye un ReActAgent con:
          - system_prompt = definition.system_prompt
          - tool_scope = definition.tools (filtrado luego por permisos del usuario en el prompt)
          - modelo = definition.modelo_override or default loop model
          - temperatura, max_iteraciones según definition
          """
  ```

  El filtrado final de tools visibles ocurre en `ToolRegistry.get_tools_prompt()` y
  `get_usage_hints()` — se agrega un parámetro `tool_scope: Optional[set[str]] = None`
  que intersecta con los permisos del usuario:

  ```python
  # Si el agente es generalista: tool_scope=None → usa solo permisos del usuario
  # Si el agente es especialista: tool_scope={'database_query', 'calculate'} → intersecta
  visible = [t for t in permitted_tools if tool_scope is None or t.name in tool_scope]
  ```

- [ ] Agregar parámetro `tool_scope` a `ToolRegistry.get_tools_prompt()` y `get_usage_hints()`

- [ ] Agregar cache de instancias de agente keyed por `(idAgente, version)` — evita
  reconstruir en cada request cuando la definición no cambió.

---

### Fase 4: Orchestrator N-way

**Objetivo**: Refactorizar `AgentOrchestrator` e `IntentClassifier` para N agentes
cargados dinámicamente desde BD.
**Dependencias**: Fases 2 y 3

- [ ] Actualizar `IntentClassifier` — prompt construido con las descripciones de agentes
  leídas desde `AgentConfigService`:

  ```python
  async def classify(self, query: str, agents: list[AgentDefinition]) -> str:
      """Retorna el nombre del agente seleccionado."""
      especialistas = [a for a in agents if not a.es_generalista]
      opciones = "\n".join(f"- {a.nombre}: {a.descripcion}" for a in especialistas)
      prompt = f"""Clasificá la consulta en UNA de estas categorías:
  {opciones}
  - generalista: si no encaja claramente en ninguna de las anteriores

  Respondé ÚNICAMENTE con el nombre de la categoría."""
  ```

  Si la respuesta del LLM no coincide con ningún nombre conocido → fallback a `generalista`.

- [ ] Actualizar `AgentOrchestrator` — N agentes desde BD, construcción lazy, fallback:

  ```python
  class AgentOrchestrator:
      def __init__(
          self,
          agent_config_service: AgentConfigService,
          agent_builder: AgentBuilder,
          intent_classifier: IntentClassifier,
      )

      async def execute(self, query, context, ...):
          definitions = await self.agent_config_service.get_active_agents()
          agent_name = await self.intent_classifier.classify(query, definitions)
          definition = self._resolve(agent_name, definitions)  # fallback a generalista si no existe
          agent = self.agent_builder.build(definition)
          return await agent.execute(query=query, context=context, ...)
  ```

- [ ] Actualizar `pipeline/factory.py`:
  - Construir `AgentConfigService(AgentConfigRepository(db))`
  - Construir `AgentBuilder(tool_registry, llm_providers)`
  - Construir `AgentOrchestrator` con los tres componentes anteriores
  - `MainHandler` recibe el orchestrator en lugar del react_agent directo
    (la interfaz `.execute()` es idéntica — MainHandler no cambia)

---

### Fase 5: Admin tooling y recarga en caliente

**Objetivo**: Gestionar agentes desde BD sin reiniciar el bot.
**Dependencias**: Fase 4

- [ ] Agregar tool `reload_agent_config` — invalida el cache de `AgentConfigService`
  y el cache de instancias del `AgentBuilder`:

  ```python
  class ReloadAgentConfigTool(BaseTool):
      # Similar a ReloadPermissionsTool
      # esPublico=0, solo admins
  ```

  Registrar en factory y agregar recurso en BD:
  ```sql
  INSERT INTO BotIAv2_Recurso (recurso, tipoRecurso, esPublico)
  VALUES ('tool:reload_agent_config', 'tool', 0);
  ```

- [ ] SQL de administración — queries listos para copiar/pegar:
  - Ver agentes activos con sus tools
  - Editar `systemPrompt` (con INSERT automático a historial)
  - Activar/desactivar agente
  - Ver historial de versiones de un prompt
  - Hacer rollback a versión anterior

  Documentar en `docs/uso/guia-administrador.md` sección nueva "Gestión de agentes".

---

### Fase 6: Tests y migración

**Objetivo**: Validar el sistema completo y limpiar el código ARQ-30 descartado.
**Dependencias**: Fases 3, 4 y 5

- [ ] Tests unitarios `tests/test_agent_builder.py`:
  - Build de agente con tool_scope correcto
  - Intersección scope ∩ permisos funciona
  - Cache de instancias por (id, version)

- [ ] Tests unitarios `tests/test_orchestrator.py`:
  - Routing correcto a cada agente
  - Fallback a generalista cuando intent no coincide
  - Fallback a generalista cuando el classifier falla

- [ ] Test de integración `scripts/test_orchestrator.py`:
  - Query de datos → rutea a datos agent → usa database_query
  - Query de política → rutea a conocimiento agent → usa knowledge_search
  - Saludo → rutea a casual agent → finish directo sin tools
  - Query ambiguo → rutea a generalista → tiene todas las tools permitidas

- [ ] Limpiar archivos del ARQ-30 descartado si quedó código muerto.

---

## Criterios de éxito

- Agregar un nuevo agente requiere solo un `INSERT` en BD + recarga (sin deploy)
- Cambiar el prompt de un agente requiere solo un `UPDATE` en BD + recarga
- El `MainHandler` no tiene conocimiento de cuántos agentes existen
- El `ReActAgent` no cambió su interfaz pública
- Consultas cross-dominio llegan al generalista, no fallan silenciosamente
- Cada interacción registra en `BotIAv2_InteractionLogs` el `nombre` del agente que respondió

---

## Decisiones de diseño registradas

| Decisión | Alternativa descartada | Razón |
|----------|----------------------|-------|
| Tools genéricas compartidas (calculate, datetime, etc.) | Agentes 100% aislados | Evita duplicar config en cada agente; las tools genéricas no generan ambigüedad de routing |
| Fallback a generalista por nombre desconocido o error | Multi-agent chaining | Chaining duplica latencia y costo; el generalista absorbe el peor caso correctamente |
| Cache de instancias por (idAgente, version) | Rebuild en cada request | Rebuild es barato, pero el cache evita lecturas de BD innecesarias en alta frecuencia |
| Prompt del agente en BD con historial | Prompt en archivo .py con env override | BD es la única fuente de verdad sin deploy; historial habilita rollback |
| IntentClassifier construye su prompt desde las descripciones en BD | Prompt hardcodeado | Agregar un agente nuevo actualiza automáticamente el routing sin tocar código |

---

## Notas de seguridad

- El `systemPrompt` editado en BD pasa por `InputValidator.validate()` antes de persistir
  (longitud máxima, detección de patrones de inyección obvios)
- Los cambios de prompt requieren permiso `tool:reload_agent_config` para activarse
  (sin recarga explícita, el bot sigue usando el prompt cacheado)
- `BotIAv2_AgentePromptHistorial` es append-only — ningún proceso borra registros de historial
