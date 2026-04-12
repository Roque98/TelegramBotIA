[Docs](../index.md) › [Código](README.md) › Sistema de tools

# Sistema de tools

Las tools son las capacidades accionables del agente. Cada tool encapsula una operación
específica y expone una interfaz uniforme para que el `ToolRegistry` las gestione.

---

## Estructura de archivos

```
src/agents/tools/
├── base.py                     ← BaseTool, ToolDefinition, ToolResult, ToolCategory
├── registry.py                 ← ToolRegistry (singleton, thread-safe)
├── database_tool.py            ← DatabaseTool (database_query)
├── knowledge_tool.py           ← KnowledgeTool (knowledge_search)
├── calculate_tool.py           ← CalculateTool (calculate)
├── datetime_tool.py            ← DateTimeTool (datetime)
├── preference_tool.py          ← SavePreferenceTool (save_preference)
├── save_memory_tool.py         ← SaveMemoryTool (save_memory)
├── reload_permissions_tool.py  ← ReloadPermissionsTool (reload_permissions)
├── read_attachment_tool.py     ← ReadAttachmentTool (read_attachment)
├── alert_analysis_tool.py      ← AlertAnalysisTool (alert_analysis)
└── reload_agent_config_tool.py ← ReloadAgentConfigTool (reload_agent_config)
```

---

## El contrato: BaseTool

```python
# src/agents/tools/base.py
class BaseTool(ABC):

    @property
    @abstractmethod
    def definition(self) -> ToolDefinition:
        """Metadata: nombre, descripción, parámetros, usage_hint."""

    @abstractmethod
    async def execute(self, **kwargs: Any) -> ToolResult:
        """Ejecuta la operación. Siempre recibe user_id y context como kwargs."""
```

### ToolDefinition

```python
class ToolDefinition(BaseModel):
    name: str
    description: str                          # Descripción para el LLM
    category: ToolCategory
    parameters: list[ToolParameter] = []
    examples: list[dict] = []
    returns: str = "Resultado de la operación"
    usage_hint: Optional[str] = None          # Instrucción de cuándo usar esta tool
```

### ToolResult

```python
class ToolResult(BaseModel):
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    execution_time_ms: float = 0.0

    def to_observation(self) -> str:
        """Texto formateado que el agente incluye en el scratchpad."""
```

### ToolCategory

```python
class ToolCategory(str, Enum):
    DATABASE    = "database"
    KNOWLEDGE   = "knowledge"
    CALCULATION = "calculation"
    DATETIME    = "datetime"
    UTILITY     = "utility"
    MONITORING  = "monitoring"
```

---

## Las 10 tools

### 1. database_query

**Clase**: `DatabaseTool` | **Archivo**: `database_tool.py`

Consulta la base de datos SQL Server a partir de una descripción en lenguaje natural.
Internamente usa el `openai_data_model` (GPT-5.4) para generar el SQL.

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `query` | string | Consulta en lenguaje natural |

**Flujo interno**:
1. LLM genera SQL (`SELECT`/`WITH`/`EXEC`) a partir de la descripción
2. `SQLValidator` valida que solo sea lectura
3. `DatabaseManager.execute_query(sql)` ejecuta y devuelve filas
4. LLM formatea los resultados como texto natural

**usage_hint**: `Para datos de negocio (ventas, reportes, usuarios, productos, stock, facturación): usa database_query. Obligatorio antes de responder con cualquier cifra.`

---

### 2. knowledge_search

**Clase**: `KnowledgeTool` | **Archivo**: `knowledge_tool.py`

Busca en la base de conocimiento empresarial.

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `query` | string | Término o pregunta a buscar |

**Flujo interno**:
1. `KnowledgeService.search(query)` → `list[KnowledgeEntry]`
2. Filtra por `active=1` y categorías permitidas para el rol del usuario
3. Retorna las entradas más relevantes ordenadas por prioridad

**usage_hint**: `Para políticas, procedimientos o preguntas sobre la empresa: usa knowledge_search.`

---

### 3. calculate

**Clase**: `CalculateTool` | **Archivo**: `calculate_tool.py`

Evalúa expresiones matemáticas de forma segura (sin `eval` directo).

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `expression` | string | Expresión matemática (ej: `"8450 * 0.15"`) |

**Operaciones soportadas**: suma, resta, multiplicación, división, potencia, raíz cuadrada,
módulo, paréntesis. No ejecuta funciones arbitrarias.

**usage_hint**: `Para cálculos matemáticos (porcentajes, sumas, raíces, etc.): usa calculate.`

---

### 4. datetime

**Clase**: `DateTimeTool` | **Archivo**: `datetime_tool.py`

Obtiene la fecha y hora actual del sistema.

Sin parámetros requeridos. Retorna fecha, hora, día de la semana y zona horaria.

**usage_hint**: `Para fechas, horas, diferencias de tiempo o cuando necesités la fecha actual para una consulta: usa datetime.`

---

### 5. save_preference

**Clase**: `SavePreferenceTool` | **Archivo**: `preference_tool.py`

Guarda preferencias del usuario en la base de datos (`BotIAv2_UserMemoryProfiles.preferencias`).

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `key` | string | Nombre de la preferencia: `alias`, `idioma`, `formato` |
| `value` | string | Valor a guardar |

Las preferencias se cargan en el `UserContext` en cada sesión y el LLM las respeta.
Invalida el cache de `MemoryService` para que la próxima sesión cargue el valor nuevo.

**usage_hint**: `Para guardar preferencias del usuario (alias, idioma, formato de respuesta): usa save_preference.`

---

### 6. save_memory

**Clase**: `SaveMemoryTool` | **Archivo**: `save_memory_tool.py`

Guarda un hecho relevante del usuario para recordarlo entre sesiones.

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `fact` | string | Hecho a recordar (ej: "trabaja en ventas sur") |

Se persiste en el `long_term_summary` del perfil de memoria.

**usage_hint**: `Para recordar datos del usuario entre sesiones (hechos persistentes): usa save_memory.`

---

### 7. reload_permissions

**Clase**: `ReloadPermissionsTool` | **Archivo**: `reload_permissions_tool.py`

Fuerza la recarga de los permisos del usuario desde la BD, invalidando el cache.
Útil cuando el admin cambió permisos y el usuario quiere que surtan efecto inmediatamente.

Sin parámetros. Esta tool es siempre visible (esPublico=1) y no requiere permisos especiales.

---

### 8. read_attachment

**Clase**: `ReadAttachmentTool` | **Archivo**: `read_attachment_tool.py`

Lee el contenido de un archivo adjunto que el usuario envió en Telegram.

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `file_id` | string | ID del archivo en Telegram |

Descarga el archivo vía Bot API y retorna su contenido como texto.

**usage_hint**: `Para leer o analizar archivos adjuntos que el usuario envió en el chat: usa read_attachment.`

---

### 9. alert_analysis

**Clase**: `AlertAnalysisTool` | **Archivo**: `alert_analysis_tool.py` | **Categoría**: `MONITORING`

Analiza alertas activas de monitoreo PRTG. Consulta eventos activos, tickets históricos,
template de escalamiento y contactos de área para generar un diagnóstico estructurado
con acciones recomendadas. Usa un LLM secundario (`data_llm`) para construir el análisis.

Requiere que la conexión `monitoreo` esté configurada en `DB_CONNECTIONS`.

| Parámetro | Tipo | Requerido | Descripción |
|-----------|------|-----------|-------------|
| `query` | string | Sí | Consulta del operador sobre las alertas |
| `ip` | string | No | Filtrar por IP exacta del equipo |
| `equipo` | string | No | Filtrar por nombre parcial del equipo |
| `solo_down` | boolean | No | Si `true`, solo incluye equipos con status `down` (default `false`) |

**Flujo interno**:
1. `AlertRepository.get_active_events()` — obtiene eventos activos con fallback BAZ_CDMX → EKT
2. Selecciona el evento más crítico (posición 0 de la lista)
3. En paralelo: tickets históricos + template ID
4. Si hay template: carga `template_info` y `escalation_matrix` en paralelo
5. Carga contactos de gerencia (área atendedora y administradora)
6. `AlertPromptBuilder.build(context)` — construye system prompt + user prompt enriquecido
7. Llama al `data_llm` con los mensajes construidos
8. Retorna análisis Markdown con `DISCLAIMER` adjunto

**Retorna**: Análisis estructurado en Markdown con equipo afectado, área responsable,
matriz de escalamiento, acciones recomendadas y posible causa raíz.

**Cuándo usarla**: Cuando el usuario pregunta por alertas activas, equipos caídos
o problemas de red/infraestructura en PRTG.

---

### 10. reload_agent_config

**Clase**: `ReloadAgentConfigTool` | **Archivo**: `reload_agent_config_tool.py` | **Categoría**: `UTILITY`

Recarga la configuración de agentes LLM desde la base de datos invalidando el cache.
Invalida el cache de `AgentConfigService` y el cache de instancias de `AgentBuilder`,
forzando que la próxima consulta use los prompts y configuraciones actualizados.

Sin parámetros. **Solo disponible para administradores** (`esPublico=0` en `BotIAv2_Recurso`).

**Retorna**: Confirmación de recarga con lista de agentes activos cargados desde BD
(nombre, tools, `es_generalista`, `version`).

**Cuándo usarla**: Después de modificar `systemPrompt` en `BotIAv2_AgenteDef`,
agregar/desactivar agentes o cambiar el scope de tools de un agente. Permite aplicar
cambios sin reiniciar el bot (el trigger de BD incrementa la versión automáticamente).

**Uso típico**:
1. Admin edita `systemPrompt` en `BotIAv2_AgenteDef` (trigger incrementa `version`)
2. Admin invoca `reload_agent_config` vía el bot
3. La próxima consulta de cualquier usuario usa el prompt actualizado

---

## ToolRegistry

**Archivo**: `src/agents/tools/registry.py`
**Patrón**: Singleton con double-checked locking (thread-safe)

```python
registry = ToolRegistry()

# Registrar
registry.register(DatabaseTool(db_manager=db))

# Obtener
tool = registry.get("database_query")       # Optional[BaseTool]

# Lista filtrada por permisos
tools = registry.get_tools_for_user(context)  # list[BaseTool]

# Prompt de descripción (filtrado por permisos)
prompt = registry.get_tools_prompt(user_context=context)

# Hints de uso (filtrado por permisos)
hints = registry.get_usage_hints(user_context=context)

# Reset para tests
ToolRegistry.reset()
```

Las tools se registran en `pipeline/factory.py → create_tool_registry()`.
Las 10 tools disponibles cubren las categorías: `database`, `knowledge`, `calculation`,
`datetime`, `utility` y `monitoring`.

---

## Crear una nueva tool

```python
# src/agents/tools/mi_tool.py
from src.agents.tools.base import BaseTool, ToolDefinition, ToolCategory, ToolParameter, ToolResult

class MiTool(BaseTool):

    @property
    def definition(self) -> ToolDefinition:
        return ToolDefinition(
            name="mi_tool",
            description="Descripción que verá el LLM en el prompt",
            category=ToolCategory.UTILITY,
            parameters=[
                ToolParameter(
                    name="param1",
                    type="string",
                    description="Qué es este parámetro",
                    required=True,
                )
            ],
            usage_hint="Para [caso de uso]: usa `mi_tool`",
        )

    async def execute(self, param1: str, user_id: str = None, **kwargs) -> ToolResult:
        try:
            resultado = await self._hacer_algo(param1)
            return ToolResult(success=True, data={"resultado": resultado})
        except Exception as e:
            return ToolResult(success=False, error=str(e))
```

Luego registrarla en `pipeline/factory.py → create_tool_registry()`:

```python
registry.register(MiTool())
```

Y agregar el recurso en la BD para que el sistema de permisos la controle
(ver [guia-administrador.md](../uso/guia-administrador.md) — sección Permisos).

---

**← Anterior** [Agente ReAct](agente-react.md) · [Índice](README.md) · **Siguiente →** [Pipeline y factory](pipeline.md)
