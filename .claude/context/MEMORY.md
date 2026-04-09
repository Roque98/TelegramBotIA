# Sistema de Memoria

## Arquitectura

```
┌──────────────────────────────────────────────────┐
│               WORKING MEMORY (RAM)               │
│                                                  │
│  UserContext.working_memory                      │
│  - Últimas N interacciones (max_working_memory)  │
│  - Se construye desde BD en cada sesión          │
│  - Se pierde al terminar la sesión               │
└──────────────────────────────────────────────────┘
                        │
                        ▼
┌──────────────────────────────────────────────────┐
│            LONG-TERM MEMORY (Base de datos)      │
│                                                  │
│  UserProfile (tabla UserMemoryProfiles)          │
│  - Resumen de contexto laboral                   │
│  - Temas recientes                               │
│  - Historial breve                               │
│  - Preferencias del usuario                      │
│  - Persiste entre sesiones                       │
└──────────────────────────────────────────────────┘
```

---

## Componentes

### MemoryService (Orquestador)

**Archivo**: `src/domain/memory/memory_service.py`

```python
class MemoryService:
    def __init__(
        self,
        repository: Optional[MemoryRepository] = None,
        cache_ttl_seconds: int = 300,
        max_cache_size: int = 1000,
        max_working_memory: int = 10,
    )

    # Construye UserContext completo (working + long-term)
    async def build_context(
        self,
        user_id: str,
        include_working_memory: bool = True,
        include_long_term: bool = True,
    ) -> UserContext

    # Alias para MainHandler
    async def get_context(self, user_id: str) -> UserContext

    # Registra una interacción (query + response)
    async def record_interaction(
        self,
        user_id: str,
        query: str,
        response: str,
        metadata: dict = {},
    ) -> None

    # Health check
    async def health_check(self) -> bool
```

**Cache interno** (LRU con TTL):
- Implementado con `OrderedDict` + asyncio.Lock (thread-safe)
- TTL por defecto: 300s
- Tamaño máximo: 1000 entradas
- Se invalida al registrar nueva interacción
- `_cache_hits` y `_cache_misses` disponibles para métricas

---

### MemoryRepository (Persistencia)

**Archivo**: `src/domain/memory/memory_repository.py`

```python
class MemoryRepository:
    def __init__(self, db_manager=None)

    async def get_profile(self, user_id: str) -> Optional[UserProfile]
    async def save_profile(self, profile: UserProfile) -> None
    async def get_interactions(self, user_id: str, limit: int = 10) -> list[Interaction]
    async def save_interaction(self, user_id: str, query: str, response: str, metadata: dict) -> None
    async def health_check(self) -> bool
```

---

### Entidades (`src/domain/memory/memory_entity.py`)

```python
class UserProfile(BaseModel):
    user_id: str
    display_name: str = ""
    roles: list[str] = []
    preferences: dict = {}
    long_term_summary: Optional[str] = None
    interaction_count: int = 0
    last_updated: Optional[datetime] = None

class Interaction(BaseModel):
    user_id: str
    query: str
    response: str
    timestamp: datetime
    metadata: dict = {}

class CacheEntry(BaseModel):
    data: Any
    created_at: datetime
    ttl_seconds: int

    def is_expired(self) -> bool: ...
```

---

## Tabla de Base de Datos

```sql
-- Perfiles de memoria de usuarios
CREATE TABLE UserMemoryProfiles (
    idMemoryProfile     INT PRIMARY KEY IDENTITY,
    idUsuario           INT FK UNIQUE NOT NULL,
    displayName         NVARCHAR(255),
    roles               NVARCHAR(MAX),           -- JSON array
    preferences         NVARCHAR(MAX),           -- JSON dict
    longTermSummary     NVARCHAR(MAX),
    interactionCount    INT DEFAULT 0,
    lastUpdated         DATETIME2 DEFAULT GETDATE(),
    fechaCreacion       DATETIME2 DEFAULT GETDATE()
);
```

---

## Flujo Completo

```
Usuario envía: "¿Cuántas ventas hubo ayer?"
        │
        ▼
MainHandler._process_event(event)
        │
        ├── MemoryService.get_context(user_id)
        │       │
        │       ├── Cache hit? → Retornar UserContext cacheado
        │       │
        │       └── Cache miss?
        │            ├── MemoryRepository.get_profile(user_id)
        │            ├── MemoryRepository.get_interactions(user_id, limit=10)
        │            ├── build UserContext(profile + interactions)
        │            └── Cachear (TTL=300s)
        │
        ▼ UserContext
ReActAgent.execute(query, context)
        │
        ▼ AgentResponse
        │
        └── MemoryService.record_interaction() [asyncio.create_task — no bloqueante]
                 ├── MemoryRepository.save_interaction()
                 └── Invalidar cache del usuario
```

---

## Configuración

```python
# src/config/settings.py
memory_cache_ttl: int = 300        # TTL del cache en segundos
memory_max_cache_size: int = 1000  # Máximo de entradas en cache
memory_max_working: int = 10       # Interacciones en working memory
```

## Construcción (pipeline/factory.py)

```python
def create_memory_service(db_manager=None) -> MemoryService:
    repository = MemoryRepository(db_manager=db_manager)
    return MemoryService(
        repository=repository,
        cache_ttl_seconds=300,
        max_cache_size=1000,
        max_working_memory=10,
    )
```
