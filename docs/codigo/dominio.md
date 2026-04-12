[Docs](../index.md) › [Código](README.md) › Dominio

# Dominio

El dominio contiene la lógica de negocio y **toda la persistencia SQL**. Está organizado en 8 subdominios bajo `src/domain/`.
Cada subdominio sigue el patrón Repository + Service.

---

## Auth — `src/domain/auth/`

Gestiona usuarios, autenticación con Telegram y el sistema de permisos.

### Entidades

```python
# user_entity.py
class TelegramUser:
    user_id: int              # idUsuario en BD
    telegram_chat_id: int
    telegram_username: str
    nombre: str
    apellido: str
    rol: int
    activo: bool
```

### Repositorios

| Clase | Archivo | Responsabilidad |
|-------|---------|-----------------|
| `UserRepository` | `user_repository.py` | CRUD de usuarios en `Usuarios` |
| `TelegramAccountRepository` | `telegram_account_repository.py` | Tabla `BotIAv2_UsuariosTelegram` |
| `UserQueryRepository` | `user_query_repository.py` | Queries de búsqueda y verificación |
| `PermissionRepository` | `permission_repository.py` | Consulta `BotIAv2_Permisos` con resolución de jerarquía |

### Servicios

**`UserService`** — operaciones sobre usuarios:

```python
class UserService:
    async def get_user_by_chat_id(chat_id: int) -> Optional[TelegramUser]
    async def validate_employee(employee_id: int) -> bool
    async def register_user(chat_id, employee_id) -> str    # retorna código verificación
    async def verify_code(chat_id, code) -> bool
    async def is_registered(chat_id) -> bool
```

**`PermissionService`** — sistema de permisos SEC-01:

```python
class PermissionService:
    async def get_all_for_user(user_id, role_id, gerencia_ids, direccion_ids) -> dict[str, bool]
    # → {"tool:database_query": True, "cmd:/ia": True, ...}

    async def can(user_id, recurso: str) -> bool

    def invalidate(user_id: str)
    # Invalida el cache LRU para forzar recarga en la próxima consulta
```

El cache LRU tiene TTL de 60 segundos. Máximo 1000 entradas.

---

## Memory — `src/domain/memory/`

Gestiona el contexto conversacional del usuario entre sesiones.

### Entidades

```python
# memory_entity.py
class MemoryEntry:
    query: str
    response: str
    timestamp: datetime
    metadata: dict

class UserProfile:
    user_id: str
    resumen_contexto_laboral: Optional[str]    # "Usuario del área de ventas..."
    resumen_temas_recientes: Optional[str]     # "Últimamente pregunta sobre stock..."
    resumen_historial_breve: Optional[str]     # "Ha realizado 45 consultas..."
    num_interacciones: int
    ultima_actualizacion: datetime
```

### Repositorio

```python
class MemoryRepository:
    async def get_user_memory_profile(user_id: str) -> Optional[UserProfile]
    async def save_memory_profile(user_id: str, profile: UserProfile)
    async def get_recent_interactions(user_id: str, limit: int) -> list[MemoryEntry]
    async def save_interaction(user_id: str, entry: MemoryEntry)
```

### Servicio

```python
class MemoryService:
    def __init__(
        self,
        repository: MemoryRepository,
        permission_service: PermissionService,
        cache_ttl_seconds: int = 300,     # 5 minutos
        max_cache_size: int = 1000,
        max_working_memory: int = 10,     # últimas N interacciones
    )

    async def get_context(user_id: str) -> UserContext
    # Combina: UserProfile + últimas N interacciones + permisos cargados

    async def record_interaction(user_id: str, query: str, response: str, metadata: dict)
    # Guarda la interacción y actualiza el perfil si es necesario

    def _invalidate_user_cache(user_id: str)
    # Invalida el cache LRU del UserContext para ese usuario
```

El `UserContext` se cachea en memoria (LRU) por `cache_ttl_seconds`. Cuando `SavePreferenceTool`
guarda una preferencia, llama a `_invalidate_user_cache()` para que el próximo request
cargue el contexto fresco desde BD.

---

## Knowledge — `src/domain/knowledge/`

Gestiona la base de conocimiento empresarial.

### Entidades

```python
# knowledge_entity.py
class KnowledgeEntry:
    id: int
    category_id: int
    category_name: str
    question: str
    answer: str
    keywords: list[str]
    priority: int         # 1=normal, 2=alta, 3=crítica
    active: bool
```

### Repositorio

```python
class KnowledgeRepository:
    async def get_all_active() -> list[KnowledgeEntry]
    async def search(query: str, category: Optional[str] = None) -> list[KnowledgeEntry]
    async def get_by_category(category: str) -> list[KnowledgeEntry]
```

### Servicio

```python
class KnowledgeService:
    def __init__(self, db_manager)
    # Al inicializar, carga TODOS los artículos activos en memoria (knowledge_base)

    def search(query: str, top_k: int = 5) -> list[KnowledgeEntry]
    # Búsqueda en memoria (sin acceso a BD en tiempo real)
    # Matching por keywords + question + answer

    @property
    def knowledge_base(self) -> list[KnowledgeEntry]
```

`KnowledgeService` carga todos los artículos al arrancar y los mantiene en memoria.
Si se modifican artículos en BD, es necesario reiniciar el bot para que los cargue.

---

## Cost — `src/domain/cost/`

Registra el costo de las llamadas al LLM para monitoreo y auditoría.

### Entidades

```python
# cost_entity.py
class CostSession:
    correlation_id: str
    user_id: str
    llamadas_llm: int
    tokens_prompt: int
    tokens_completion: int
    costo_usd: float
    modelo: str
    fecha_creacion: datetime
```

### Repositorio

```python
class CostRepository:
    async def save_cost_session(session: CostSession)
    async def get_total_cost_by_user(user_id: str, since: datetime) -> float
    async def get_daily_summary() -> list[dict]
```

### CostTracker

```python
class CostTracker:
    def record_llm_call(model: str, prompt_tokens: int, completion_tokens: int)
    def get_session_cost() -> CostSession
    # Calcula costo en USD según precios por modelo
```

El `MainHandler` crea un `CostTracker` por request y lo persiste al finalizar.

---

## Alerts — `src/domain/alerts/`

Gestiona el acceso a datos de alertas PRTG con fallback automático entre instancias BAZ_CDMX y EKT.

### Entidades

```python
# alert_entity.py

class AlertEvent(BaseModel):
    """Evento activo de monitoreo PRTG."""
    equipo: str          # alias: "Equipo"
    ip: str              # alias: "IP"
    sensor: str          # alias: "Sensor"
    status: str          # alias: "Status"
    mensaje: str         # alias: "Mensaje"
    prioridad: int       # alias: "Prioridad"
    id_area_atendedora: Optional[int]
    id_area_administradora: Optional[int]
    area_atendedora: str
    responsable_atendedor: str
    area_administradora: str
    responsable_administrador: str
    origen: str          # alias: "_origen" — "BAZ_CDMX" | "EKT"

    @property
    def es_ekt(self) -> bool: ...
    @property
    def es_url_sensor(self) -> bool: ...

class HistoricalTicket(BaseModel):
    """Ticket histórico de un evento similar al activo."""
    ticket: Optional[str]
    alerta: str
    detalle: str
    accion_correctiva: str

    @property
    def accion_formateada(self) -> str: ...   # Reemplaza [Salto] por \n

class Template(BaseModel):
    """Template de la aplicación asociada al evento."""
    id_template: Optional[int]
    aplicacion: str
    gerencia_desarrollo: str
    instancia: str   # "BAZ", "COMERCIO" o vacío

    @property
    def etiqueta(self) -> str: ...   # "ABCEKT" | "ABCMASplus"
    @property
    def es_ekt(self) -> bool: ...

class EscalationLevel(BaseModel):
    """Un nivel de la matriz de escalamiento del template."""
    nivel: int
    nombre: str
    puesto: str
    extension: str
    celular: str
    correo: str
    tiempo_escalacion: str

class AreaContacto(BaseModel):
    """Datos de contacto de una gerencia."""
    gerencia: str
    correos: str        # alias: "direccion_correo"
    extensiones: str

class AlertContext(BaseModel):
    """Agregado completo de un evento enriquecido — se pasa al PromptBuilder."""
    evento: AlertEvent
    tickets: list[HistoricalTicket]
    template: Optional[Template]
    matriz: list[EscalationLevel]
    contacto_atendedora: Optional[AreaContacto]
    contacto_administradora: Optional[AreaContacto]
    query_usuario: str
```

### Repositorio

```python
class AlertRepository:
    def __init__(self, db_manager) -> None: ...
    # Recibe el DatabaseManager del alias "monitoreo" (BAZ_CDMX)

    async def get_active_events(
        ip: Optional[str] = None,
        equipo: Optional[str] = None,
        solo_down: bool = False,
    ) -> list[AlertEvent]
    # Combina PrtgObtenerEventosEnriquecidos + ...Performance
    # Fallback automático a versiones _EKT si BAZ retorna vacío

    async def get_historical_tickets(ip: str, sensor: str) -> list[HistoricalTicket]
    # TOP 15 tickets históricos; fallback a versión EKT

    async def get_template_id(ip: str, url: Optional[str] = None) -> Optional[dict]
    # Obtiene idTemplate e instancia para el IP o URL dado

    async def get_template_info(template_id: int, usar_ekt: bool = False) -> Optional[Template]
    # Fallback automático a versión EKT

    async def get_escalation_matrix(template_id: int, usar_ekt: bool = False) -> list[EscalationLevel]
    # Ordenada por nivel; fallback automático a versión EKT

    async def get_contacto_gerencia(id_gerencia: int, usar_ekt: bool = False) -> Optional[AreaContacto]
```

**Estrategia de fallback**: todos los métodos intentan primero los SPs de la instancia BAZ_CDMX. Si retornan vacío, reintenta con los SPs `_EKT` que usan `OPENDATASOURCE` internamente. Nunca lanza excepciones al llamador — retorna `[]` o `None` en caso de error.

### AlertPromptBuilder

`AlertPromptBuilder` construye el par `(system_prompt, user_prompt)` listo para pasar al LLM. Recibe un `AlertContext` completo y genera un prompt enriquecido con cuatro secciones:

1. **ALERTA ACTIVA** — datos del evento, IP, sensor, áreas responsables y contactos
2. **TICKETS HISTÓRICOS** — hasta 15 tickets previos con acciones correctivas (`[Salto]` → `\n`)
3. **TEMPLATE Y ESCALAMIENTO** — nombre de aplicación, gerencia de desarrollo y matriz de escalamiento por niveles
4. **INSTRUCCIÓN** — estructura Markdown exacta que debe seguir el LLM para su respuesta en Telegram

```python
class AlertPromptBuilder:
    def build(self, context: AlertContext) -> tuple[str, str]
    # Retorna (system_prompt, user_prompt)
```

---

## Interaction — `src/domain/interaction/`

Centraliza toda la persistencia SQL relacionada con interacciones del bot.
Todas las consultas a las tablas `BotIAv2_*` pasan por aquí (ARQ-39).

```python
class InteractionRepository:
    def __init__(self, db_manager) -> None: ...

    async def save_interaction(
        correlation_id, user_id, username, query, respuesta,
        channel, memory_ms, react_ms, save_ms, total_ms,
        error_message=None, tools_used=None, steps_count=0,
        agente_nombre=None, total_input_tokens=None,
        total_output_tokens=None, llm_iteraciones=None,
        used_fallback=False, classify_ms=None,
        agent_confidence=None, cost_usd=None,
    ) -> bool
    # → BotIAv2_InteractionLogs (via SP BotIAv2_sp_GuardarInteraccion)

    async def save_agent_routing(
        correlation_id, query, agente_seleccionado, classify_ms,
        confidence=None, alternatives=None, used_fallback=False,
    ) -> bool
    # → BotIAv2_AgentRouting

    async def save_steps(correlation_id, steps: list[dict]) -> bool
    # → BotIAv2_InteractionSteps (un INSERT por cada paso del loop ReAct)

    def save_log_sync(
        level, event, message, correlation_id=None,
        user_id=None, module=None, duration_ms=None, extra=None,
    ) -> bool
    # → BotIAv2_ApplicationLogs (síncrono, llamado desde threads de logging)
```

`InteractionRepository` se instancia en `pipeline/factory.py` y se inyecta en
`MainHandler` (para los tres primeros métodos) y en `SqlLogHandler`
(para `save_log_sync`).

---

## Notifications — `src/domain/notifications/`

Envío de alertas al administrador vía Telegram.

```python
async def notify_admin(
    bot, db_manager=None,
    level="ERROR",
    error=None,
    message="",
    user_info="desconocido",
) -> None
# Resuelve admins desde BD y envía mensaje con rate limiting (1 por tipo cada 5 min)
```

---

## AgentConfig — `src/domain/agent_config/`

Gestiona la configuración dinámica de agentes LLM almacenada en BD, con cache LRU de 5 minutos.

### Entidad

```python
# agent_config_entity.py
class AgentDefinition(BaseModel):
    id: int
    nombre: str
    descripcion: str
    system_prompt: str       # Debe contener {tools_description} y {usage_hints}
    temperatura: float
    max_iteraciones: int
    modelo_override: Optional[str]   # None → usa el modelo default del sistema
    es_generalista: bool             # True → accede a todas sus tools permitidas
    tools: list[str]                 # Nombres de tools en scope (vacío para el generalista)
    activo: bool
    version: int                     # Incrementado por trigger TR_AgenteDef_VersionHistorial
```

### Repositorio

```python
# agent_config_repository.py
class AgentConfigRepository:
    def __init__(self, db_manager: Any) -> None: ...

    def get_all_active(self) -> list[AgentDefinition]
    # Consulta BotIAv2_AgenteDef JOIN BotIAv2_AgenteTools — solo activo=1

    def get_by_nombre(self, nombre: str) -> Optional[AgentDefinition]

    def get_generalista(self) -> Optional[AgentDefinition]
    # Filtra por esGeneralista=1 AND activo=1
```

Las tools de cada agente se obtienen mediante `STRING_AGG` en una subconsulta sobre `BotIAv2_AgenteTools` y se deserializan como `list[str]`.

### Servicio y cache LRU

```python
# agent_config_service.py
class AgentConfigService:
    def __init__(
        self,
        repository: AgentConfigRepository,
        cache_ttl_seconds: int = 300,   # TTL de 5 minutos
    ) -> None: ...

    def set_builder(self, builder: "AgentBuilder") -> None
    # Inyección tardía para evitar dependencia circular con AgentBuilder

    def get_active_agents(self) -> list[AgentDefinition]
    # Retorna agentes activos desde cache (LRU) o BD
    # Excluye agentes cuyo systemPrompt no contenga {tools_description} y {usage_hints}

    def invalidate_cache(self) -> None
    # Invalida el cache del service Y el cache de instancias del AgentBuilder
```

El cache es thread-safe (`threading.Lock`). Al invocar `invalidate_cache()`, también se llama a `AgentBuilder.clear_instance_cache()` para forzar la reconstrucción de todas las instancias de agentes activos. Las métricas de cache hits/misses se reportan a `get_metrics()`.

---

**← Anterior** [Pipeline y factory](pipeline.md) · [Índice](README.md) · **Siguiente →** [Infraestructura](infraestructura.md)
