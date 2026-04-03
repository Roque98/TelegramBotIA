# PLAN: Retry con Tenacity en LLM y BD

> **Objetivo**: Implementar reintentos automáticos con backoff exponencial en todas las operaciones críticas
> **Rama**: `feature/fun-21-retry`
> **Prioridad**: 🟢 Funcional
> **Progreso**: 0% (0/6)

---

## Contexto

`tenacity` ya está instalado en el proyecto (`requirements.txt`) pero se usa de forma inconsistente o parcial. Las llamadas a OpenAI y SQL Server pueden fallar transitoriamente:

- **OpenAI**: Rate limit (429), timeout de red, servidor caído temporalmente
- **SQL Server**: Timeout de conexión, servidor ocupado, red inestable

Sin reintentos, un fallo transitorio de 500ms resulta en un error visible al usuario. Con reintentos + backoff, el bot se recupera automáticamente.

---

## Operaciones que necesitan retry

| Operación | Archivo | Errores esperados |
|-----------|---------|------------------|
| `openai_provider.chat_completion()` | `agents/providers/openai_provider.py` | RateLimitError, APITimeoutError, APIConnectionError |
| `openai_provider.get_embedding()` | `agents/providers/openai_provider.py` | Igual |
| `database/connection.execute_query()` | `database/connection.py` | OperationalError, TimeoutError |
| `knowledge_repository.get_all_entries()` | `knowledge/knowledge_repository.py` | OperationalError |

---

## Configuración de retry propuesta

```python
@retry(
    wait=wait_exponential(multiplier=1, min=1, max=30),
    stop=stop_after_attempt(3),
    retry=retry_if_exception_type((RateLimitError, APITimeoutError)),
    before_sleep=before_sleep_log(logger, logging.WARNING),
)
```

---

## Archivos involucrados

- `src/agents/providers/openai_provider.py`
- `src/database/connection.py`
- `src/knowledge/knowledge_repository.py`
- `src/config/settings.py` — `RETRY_MAX_ATTEMPTS`, `RETRY_MAX_WAIT_SECONDS`

---

## Tareas

- [ ] **21.1** Crear `src/utils/retry_config.py` con decoradores de retry reutilizables:
  - `@retry_llm` — para llamadas a OpenAI
  - `@retry_db` — para llamadas a SQL Server
- [ ] **21.2** Aplicar `@retry_llm` en `openai_provider.py` a `chat_completion()` y `get_embedding()`
- [ ] **21.3** Aplicar `@retry_db` en `database/connection.py` a `execute_query()`
- [ ] **21.4** Agregar `RETRY_MAX_ATTEMPTS` y `RETRY_MAX_WAIT_SECONDS` en `settings.py`
- [ ] **21.5** Loguear cada reintento con nivel WARNING indicando: intento #N, error, tiempo de espera
- [ ] **21.6** Agregar tests que simulen fallos transitorios y verifiquen que el retry ocurre

---

## Criterios de aceptación

- Un error transitorio de red no genera error visible al usuario
- Después de 3 intentos fallidos, el error se propaga con contexto completo
- Cada reintento queda registrado en los logs
- Los parámetros de retry son configurables desde `.env`
