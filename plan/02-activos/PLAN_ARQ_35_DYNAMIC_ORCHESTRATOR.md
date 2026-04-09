# Plan: ARQ-35 Orchestrator con Agentes Dinámicos

> **Estado**: 🟡 En progreso
> **Última actualización**: 2026-04-09 (revisión 4 — final)
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

**Progreso Total**: ░░░░░░░░░░ 0% (0/36 tareas)

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
| `ReActAgent` | Cambio menor | Agregar `system_prompt_override: Optional[str] = None` en `__init__` |
| `ToolRegistry` | Sin cambios | Sigue siendo el registro global |
| `SEC-01 PermissionService` | Sin cambios | Sigue filtrando por usuario |
| `pipeline/factory.py` | Cambio menor | Construir orchestrator + validación de startup |
| `src/agents/base/agent.py` | Cambio menor | Agregar `routed_agent: Optional[str] = None` a `AgentResponse` |
| `pipeline/handler.py` | Cambio menor | Leer `response.routed_agent` y pasarlo a observabilidad |

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

- [ ] Crear trigger `TR_AgenteDef_VersionHistorial` en `BotIAv2_AgenteDef` que se dispara
  en cada `UPDATE` de `systemPrompt`:
  - Incrementa `version = version + 1` en la fila actualizada
  - Inserta la versión anterior en `BotIAv2_AgentePromptHistorial`

  Esto garantiza el historial incluso para ediciones directas por SQL, sin depender
  de que el código de aplicación lo recuerde. El `AgentBuilder` usa `version` como
  clave de cache — sin este trigger, el cache nunca invalidaría al cambiar un prompt.

- [ ] Insertar datos iniciales: 4 agentes (datos, conocimiento, casual, generalista)
  con prompts adaptados de `REACT_SYSTEM_PROMPT` actual y sus tools correspondientes.
  Los prompts deben incluir los placeholders `{tools_description}` y `{usage_hints}`
  (ver contrato en Fase 2).

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
  - `invalidate_cache()` — invalida tanto el cache del service como el cache de instancias
    del `AgentBuilder` (se le pasa una referencia al builder en el constructor)

- [ ] Validar contrato de placeholders al cargar desde BD: si un `systemPrompt`
  no contiene `{tools_description}` o `{usage_hints}`, loguear `WARNING` y rechazar
  el agente (excluirlo de la lista activa con log explicativo). Esto evita un `KeyError`
  silencioso en runtime cuando `build_system_prompt()` intente formatear el template.

  **Contrato documentado**: todo prompt almacenado en `BotIAv2_AgenteDef.systemPrompt`
  debe contener exactamente estos dos placeholders:
  - `{tools_description}` — donde se inyecta la lista de tools visible para el usuario
  - `{usage_hints}` — donde se inyectan las instrucciones de uso filtradas por permisos

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

- [ ] Agregar `system_prompt_override: Optional[str] = None` a `ReActAgent.__init__`.
  Cuando no es `None`, se usa en lugar de `REACT_SYSTEM_PROMPT` al llamar
  `build_system_prompt()` dentro de `execute()`. Valor por defecto `None` preserva
  el comportamiento actual — no hay cambio de interfaz para quien ya usa `ReActAgent`.

- [ ] Agregar `tool_scope: Optional[set[str]] = None` a `ReActAgent.__init__` y almacenarlo
  como `self.tool_scope`. Dentro de `execute()`, pasarlo a `registry.get_tools_prompt()`
  y `registry.get_usage_hints()`:

  ```python
  system_prompt = build_system_prompt(
      tools_description=self.tools.get_tools_prompt(
          user_context=context, tool_scope=self.tool_scope
      ),
      usage_hints=self.tools.get_usage_hints(
          user_context=context, tool_scope=self.tool_scope
      ),
  )
  ```

  `tool_scope=None` mantiene el comportamiento actual (sin filtro de scope, solo permisos
  del usuario). El agente generalista siempre recibe `tool_scope=None`.
  Sin este parámetro, la especialización por agente no funciona — todos los agentes
  verían las mismas tools independientemente de su scope en BD.

- [ ] Crear `src/domain/agent_config/__init__.py` y `src/agents/factory/__init__.py`
  — paquetes Python nuevos sin estos archivos fallan en runtime al importar.

- [ ] Agregar cache de instancias de agente keyed por `(idAgente, version)` en `AgentBuilder`
  con `threading.Lock` (mismo patrón que `ToolRegistry`). El bot maneja requests
  concurrentes — sin lock, dos requests simultáneos que desencadenen una construcción
  pueden corromper el dict del cache:

  ```python
  self._cache: dict[tuple[int, int], ReActAgent] = {}
  self._lock = threading.Lock()

  def build(self, definition: AgentDefinition) -> ReActAgent:
      key = (definition.id, definition.version)
      with self._lock:
          if key not in self._cache:
              self._cache[key] = self._do_build(definition)
          return self._cache[key]
  ```

  El trigger de BD garantiza que `version` cambia al editar el prompt,
  por lo que el cache invalida correctamente sin lógica adicional.

- [ ] Definir `AgentBuilder.clear_instance_cache()` — limpia el dict de instancias cacheadas.
  Resolver la dependencia circular en `factory.py` con inyección tardía:
  service y builder se construyen por separado, luego se conectan:

  ```python
  agent_config_service = AgentConfigService(AgentConfigRepository(db))
  agent_builder = AgentBuilder(tool_registry, llm_providers)
  agent_config_service.set_builder(agent_builder)  # inyección tardía
  ```

  `set_builder()` almacena la referencia; `invalidate_cache()` llama ambos métodos.
  Esto evita pasar el builder al constructor del service (que aún no existe en ese punto).

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
          response = await agent.execute(query=query, context=context, ...)
          response.routed_agent = definition.nombre  # para observabilidad
          return response
  ```

- [ ] Definir comportamiento cuando no hay agente generalista activo en BD:
  - `_resolve()` lanza `AgentConfigException` con mensaje claro
  - `AgentOrchestrator.execute()` la captura, notifica al admin vía `admin_notifier`
    y retorna `AgentResponse.error_response("Servicio temporalmente no disponible")`
  - Nunca falla silenciosamente ni produce una excepción no manejada hacia el usuario

- [ ] Agregar `routed_agent: Optional[str] = None` a `AgentResponse` en
  `src/agents/base/agent.py`. Pydantic v2 rechaza atributos dinámicos no declarados —
  sin esta tarea, `response.routed_agent = definition.nombre` en el orchestrator
  falla silenciosamente o lanza `ValidationError`.

- [ ] Registrar `agenteNombre` en observabilidad:
  - Agregar columna `agenteNombre VARCHAR(100) NULL` a `BotIAv2_InteractionLogs` vía migration SQL
  - Actualizar `ObservabilityRepository.save_interaction_log()` para recibir y persistir el campo
  - Actualizar `MainHandler._process_event()` para leer `response.routed_agent` y
    pasarlo a `save_interaction_log()` — este es el único cambio necesario en `MainHandler`

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

  Registrar en factory y agregar recurso + permiso en BD:
  ```sql
  -- Recurso
  INSERT INTO abcmasplus..BotIAv2_Recurso (recurso, tipoRecurso, descripcion, esPublico)
  VALUES ('tool:reload_agent_config', 'tool', 'Recarga configuración de agentes desde BD', 0);

  -- Permiso para rol Admin (idRol=1) — sin esto, la tool existe pero nadie puede invocarla
  DECLARE @idRecurso INT = SCOPE_IDENTITY();
  DECLARE @idAuth INT = (SELECT idTipoEntidad FROM abcmasplus..BotIAv2_TipoEntidad WHERE nombre = 'autenticado');
  INSERT INTO abcmasplus..BotIAv2_Permisos (idTipoEntidad, idEntidad, idRecurso, idRolRequerido, permitido)
  VALUES (@idAuth, 0, @idRecurso, 1, 1);  -- idRol=1 = Admin
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

- [ ] Validación de startup en `pipeline/factory.py → create_main_handler()`:
  después de construir `AgentConfigService`, verificar que hay al menos un agente activo
  y un agente generalista. Si no, lanzar `RuntimeError` con mensaje explícito que impida
  arrancar el bot en un estado inoperante. Mejor fallar en startup que dejar el sistema
  enviando notificaciones de error al admin en cada request del día.

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
