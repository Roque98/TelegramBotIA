[Docs](../index.md) › [Código](README.md) › Infraestructura

# Infraestructura

Contiene todo lo que no es lógica de negocio: acceso a datos, observabilidad y utilidades.

---

## DatabaseManager — `src/infra/database/connection.py`

Gestiona el pool de conexiones a SQL Server usando SQLAlchemy 2.0.

```python
class DatabaseManager:
    # Pool: 5 conexiones base + 10 overflow, timeout 20s

    def execute_query(sql: str, params: dict = None) -> list[dict]
    # Ejecuta SELECT o EXEC y retorna lista de dicts

    def execute_non_query(sql: str, params: dict = None) -> int
    # Ejecuta INSERT/UPDATE/DELETE/MERGE/EXEC y retorna filas afectadas

    async def execute_query_async(sql: str, params=None) -> list[dict]
    async def execute_non_query_async(sql: str, params=None) -> int
    # Versiones async (delegan a asyncio.to_thread)

    def get_schema() -> str
    # Delega a SchemaIntrospector — retorna tablas y columnas en formato texto

    def close() -> None
```

Usa queries parametrizadas siempre (`params` como dict). La concatenación directa de
strings está prohibida para evitar SQL injection.

---

## SchemaIntrospector — `src/infra/database/schema_introspector.py`

Introspección del esquema de la BD (tablas y columnas). Extraído de `DatabaseManager`
para respetar el principio de responsabilidad única.

```python
class SchemaIntrospector:
    def __init__(self, engine) -> None: ...

    def get_schema() -> str
    # Retorna descripción de todas las tablas y sus columnas.
    # Incluye @db_retry automático.
```

`DatabaseManager.get_schema()` es un wrapper que instancia `SchemaIntrospector(self.engine)`
y delega.

---

## DatabaseRegistry — `src/infra/database/registry.py`

Gestiona múltiples conexiones a SQL Server de forma lazy y thread-safe.
Cada alias se conecta solo cuando se solicita por primera vez.

```python
class DatabaseRegistry:
    @classmethod
    def from_settings(cls) -> "DatabaseRegistry"
    # Crea el registry con las conexiones definidas en .env.
    # Siempre incluye "core" (DB_HOST/NAME/...). Aliases adicionales desde DB_CONNECTIONS.

    def get(self, alias: str = "core") -> DatabaseManager
    # Retorna el DatabaseManager para el alias. Crea la instancia lazy en el primer llamado.
    # Lanza KeyError si el alias no está configurado.

    def get_aliases(self) -> list[str]
    # Lista de alias configurados (conectados o no).

    def get_active_aliases(self) -> list[str]
    # Lista de alias con conexión activa (ya inicializados).

    def is_configured(self, alias: str) -> bool
    # True si el alias está en la configuración.

    def close_all(self) -> None
    # Cierra todas las conexiones activas. Llamar en shutdown del bot.
```

Ejemplo de uso:

```python
registry = DatabaseRegistry.from_settings()
db = registry.get("ventas")          # lazy — crea la conexión al primer uso
db_core = registry.get()             # "core" es el default
rows = db_core.execute_query("SELECT TOP 5 * FROM Clientes")
registry.close_all()                 # shutdown
```

---

## SQLValidator — `src/infra/database/sql_validator.py`

Valida que el SQL generado por el LLM sea seguro antes de ejecutarlo.
Es usado internamente por `DatabaseTool`.

**Permitido**: solo `SELECT`

**Rechazado**:
- `INSERT`, `UPDATE`, `DELETE`, `DROP`, `TRUNCATE`, `ALTER`, `CREATE`, `EXEC`
- Comandos de sistema: `xp_cmdshell`, `sp_executesql`, `openrowset`
- Múltiples statements: `;` dentro del SQL
- Comentarios sospechosos: `/* ... */` con keywords prohibidos

```python
# Usado en src/agents/tools/database_tool.py
validator = SQLValidator()
is_valid, reason = validator.validate(sql)
if not is_valid:
    return ToolResult(success=False, error=f"SQL rechazado: {reason}")
```

---

## Observabilidad — `src/infra/observability/`

Sistema de trazabilidad y métricas en memoria + persistencia en BD.

### Tracer — `tracing.py`

```python
tracer = get_tracer()

tracer.start_trace(user_id="123", channel="telegram", correlation_id="uuid")
with tracer.span("database_query", {"table": "ventas", "rows": 45}):
    # operación instrumentada
    pass
result = tracer.end_trace()
# → {trace_id, correlation_id, spans: [...], total_duration_ms: 1250}
```

### Metrics — `metrics.py`

Organizado con patrón facade: `MetricsCollector` compone tres clases internas
(`_RequestMetrics`, `_ToolMetrics`, `_CacheMetrics`). La API pública no cambia.

```python
metrics = get_metrics()

metrics.record_request(channel="telegram", duration_ms=1250, steps=3, success=True)
metrics.record_tool_usage("database_query")
metrics.record_cache_hit()

stats = metrics.get_stats()
# → {requests, latency, steps, errors_by_type, tools_usage, cache}
```

### SqlLogHandler — `src/infra/observability/logging_config.py`

Handler de logging Python estándar que escribe a `BotIAv2_ApplicationLogs`.
Se inyecta en el logger raíz al arrancar, por lo que todos los `logger.error()`
del sistema quedan persistidos automáticamente.

```python
sql_handler = get_sql_handler()
sql_handler.set_repository(interaction_repo)  # InteractionRepository
# A partir de aquí, logger.error("msg") → BotIAv2_ApplicationLogs
```

> La persistencia SQL está en `src/domain/interaction/InteractionRepository.save_log_sync()`.
> `sql_repository.py` es solo un re-export stub por compatibilidad.

---

## Utilidades — `src/utils/`

### encryption_util.py

Encriptación AES compatible con el sistema C# legacy.

```python
from src.utils.encryption_util import EncryptionUtil

enc = EncryptionUtil(key="clave_de_32_caracteres_exactamente")
token = enc.encrypt("12345:1712500000")     # → string base64
plain = enc.decrypt(token)                  # → "12345:1712500000"
```

### rate_limiter.py

Límite de requests por usuario usando ventana deslizante.

```python
limiter = RateLimiter(max_requests=10, window_seconds=60)
allowed = limiter.check(user_id="123")   # True/False
```

### retry.py

Decorador de retry con backoff exponencial para LLM y BD.

```python
@retry(
    max_attempts=settings.retry_llm_max_attempts,
    min_wait=settings.retry_llm_min_wait,
    max_wait=settings.retry_llm_max_wait,
    exceptions=(LLMException, ConnectionError),
)
async def call_llm(...):
    ...
```

### input_validator.py

Validación de input del usuario antes de pasarlo al agente.

```python
is_valid, reason = InputValidator.validate(text)
# Rechaza: texto > 2000 chars, patrones de inyección de prompt, contenido vacío
```

### status_message.py

Mensajes de estado progresivo que Telegram muestra mientras el agente procesa.

```python
status = StatusMessage(context, chat_id)
await status.show("Consultando la base de datos...")
# El mensaje se edita in-place cuando llega la respuesta real
```

---

## AdminNotifier — `src/infra/notifications/admin_notifier.py`

Envía notificaciones de errores críticos al administrador vía Telegram.

Vive en `src/infra/` porque es infraestructura de notificación (Capa 5).
Recibe `bot: Any` como parámetro — no importa nada de `telegram` directamente,
por lo que no pertenece a `src/bot/` (Capa 1).
El pipeline (`MainHandler`) lo recibe como un **Protocol** inyectado desde `factory.py`.

**Cómo funciona**:

- Resuelve los destinatarios dinámicamente consultando en BD los usuarios con rol Administrador que tengan Telegram verificado y activo.
- Aplica **rate limiting**: máximo 1 notificación por tipo de error cada 5 minutos (clave `NIVEL:TipoExcepcion`) para evitar spam.
- Si no hay admins con Telegram verificado, loggea un warning y retorna sin fallar.

```python
# src/infra/notifications/admin_notifier.py
async def notify_admin(
    bot: Any,
    db_manager: Any = None,
    level: str = "ERROR",           # "ERROR", "CRITICAL", "WARNING"
    error: Optional[BaseException] = None,
    message: str = "",
    user_info: str = "desconocido",
) -> None
# Envía el mensaje a todos los admins Telegram activos.
```

**Patrón de inyección** (en `pipeline/factory.py`):

```python
from src.bot.notifications.admin_notifier import notify_admin
import functools

# db_manager pre-llenado — MainHandler solo ve la firma del Protocol
admin_notify = functools.partial(notify_admin, db_manager=db)
handler = MainHandler(..., admin_notifier=admin_notify)
```

El `AdminNotifier` Protocol en `pipeline/handler.py` define la firma que espera el handler:

```python
class AdminNotifier(Protocol):
    async def __call__(
        self, bot, level="ERROR", error=None, message="", user_info="desconocido"
    ) -> None: ...
```

Uso directo desde `logging_middleware.py` (Capa 1 → Capa 5, dependencia válida):

```python
from src.bot.notifications.admin_notifier import notify_admin

await notify_admin(
    bot=context.bot,
    db_manager=context.bot_data.get("db_manager"),
    level="ERROR",
    error=context.error,
    user_info="12345 (@juan)",
)
```

El mensaje incluye nivel, timestamp, usuario afectado, tipo de excepción y el último frame del traceback. Usa Markdown de Telegram.

Función auxiliar para tests:

```python
reset_rate_cache()   # Limpia el cache de rate limiting
```

---

**← Anterior** [Dominio](dominio.md) · [Índice](README.md) · **Siguiente →** [Base de datos](base-de-datos.md)
