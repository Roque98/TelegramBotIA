# Infraestructura

Contiene todo lo que no es lógica de negocio: acceso a datos, observabilidad, eventos y utilidades.

---

## DatabaseManager — `src/infra/database/connection.py`

Gestiona el pool de conexiones a SQL Server usando SQLAlchemy 2.0.

```python
class DatabaseManager:
    # Pool: 5 conexiones base + 10 overflow, timeout 20s

    def execute_query(sql: str, params: dict = None) -> list[dict]
    # Ejecuta SELECT y retorna lista de dicts

    def execute_non_query(sql: str, params: dict = None) -> int
    # Ejecuta INSERT/UPDATE/DELETE y retorna filas afectadas

    def execute_stored_procedure(proc_name: str, params: dict = None) -> list[dict]

    async def health_check() -> bool
    # Verifica que la conexión está activa
```

Usa queries parametrizadas siempre (`params` como dict). La concatenación directa de
strings está prohibida para evitar SQL injection.

---

## SQLValidator — `src/infra/database/sql_validator.py`

Valida que el SQL generado por el LLM sea seguro antes de ejecutarlo.

**Permitido**: `SELECT`, `WITH`, `EXEC`

**Rechazado**:
- `INSERT`, `UPDATE`, `DELETE`, `DROP`, `TRUNCATE`, `ALTER`, `CREATE`
- Comentarios: `--`, `/*`, `*/`
- Múltiples statements: `;` dentro del SQL
- Acceso a tablas del sistema: `sys.`, `information_schema`

```python
# src/agents/tools/database_tool.py
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

```python
metrics = get_metrics()

metrics.record_request(channel="telegram", duration_ms=1250, steps=3, success=True)
metrics.record_tool_usage("database_query")
metrics.record_llm_call(model="gpt-5.4-mini", tokens=450, duration_ms=800)

stats = metrics.get_stats()
# → {total_requests, success_rate, avg_duration_ms, tool_usage_counts, ...}
```

### ObservabilityRepository — `sql_repository.py`

Persiste los datos de observabilidad en las tablas `BotIAv2_*` de SQL Server:

```python
class ObservabilityRepository:
    async def save_interaction_log(
        correlation_id, user_id, channel, query, response,
        success, duration_ms, steps_taken, error=None
    )
    # → BotIAv2_InteractionLogs

    async def save_interaction_steps(correlation_id, steps: list[dict])
    # → BotIAv2_InteractionSteps (un registro por paso del loop ReAct)

    async def save_application_log(level, message, module, exception=None)
    # → BotIAv2_ApplicationLogs
```

### SqlLogHandler — `src/config/logging_config.py`

Handler de logging Python estándar que escribe a `BotIAv2_ApplicationLogs`.
Se inyecta en el logger raíz al arrancar, por lo que todos los `logger.error()`
del sistema quedan persistidos automáticamente.

```python
sql_handler = get_sql_handler()
sql_handler.set_repository(obs_repo)
# A partir de aquí, logger.error("msg") → BotIAv2_ApplicationLogs
```

---

## EventBus — `src/infra/events/bus.py`

Bus de eventos pub/sub en memoria para comunicación desacoplada entre componentes.

```python
bus = EventBus()

# Suscribir
bus.subscribe("user_registered", handler_func)

# Publicar
await bus.publish("user_registered", {"user_id": "123", "channel": "telegram"})
```

Actualmente usado principalmente para eventos de registro de usuario y errores críticos
que deben notificarse al admin.

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
