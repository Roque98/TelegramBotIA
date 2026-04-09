# Dominio

El dominio contiene la lógica de negocio. Está organizado en 4 subdominios bajo `src/domain/`.
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
