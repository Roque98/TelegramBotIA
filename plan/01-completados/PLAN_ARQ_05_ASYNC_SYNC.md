# PLAN: Consolidar mezcla async/sync

> **Objetivo**: Eliminar la mezcla de código async/sync que bloquea el event loop de Telegram
> **Rama**: `feature/arq-05-async-sync`
> **Prioridad**: 🟠 Alta
> **Progreso**: 100% (8/8)

---

## Contexto

El bot usa `python-telegram-bot` con `asyncio`. Sin embargo, varios módulos llaman a `execute_query()` (síncrono) desde dentro de métodos `async def`, lo cual **bloquea el event loop** mientras espera respuesta de la BD.

Esto significa que si la BD tarda 500ms en responder, **ningún otro usuario puede ser atendido** durante ese tiempo.

### Archivos afectados

| Archivo | Problema |
|---------|---------|
| `memory/memory_repository.py` | `async def` que llama `execute_query()` sync |
| `knowledge/knowledge_repository.py` | Igual |
| `agents/tools/database_tool.py` | Usa `run_in_executor()` — riesgo de deadlock |
| `database/connection.py` | `execute_query()` es síncrono |

---

## Estrategia

Dos opciones:
1. **Hacer `execute_query()` async** usando `aioodbc` o `aiopymssql` (cambio profundo)
2. **Wrappear `execute_query()` con `asyncio.to_thread()`** en los repositorios (cambio superficial, seguro)

**Elegimos opción 2** para minimizar riesgo. `asyncio.to_thread()` (Python 3.9+) es la forma correcta y segura de correr sync en background thread.

---

## Archivos involucrados

- `src/database/connection.py`
- `src/memory/memory_repository.py`
- `src/knowledge/knowledge_repository.py`
- `src/agents/tools/database_tool.py`

---

## Tareas

- [x] **5.1** Agregar `execute_query_async` y `execute_non_query_async` en `database/connection.py` usando `asyncio.to_thread()`
- [x] **5.2** Refactorizar `memory_repository.py`: reemplazar llamadas sync por `execute_query_async` / `execute_non_query_async`
- [x] **5.3** `knowledge_repository.py` es todo sync llamado desde contexto sync — no requiere cambio
- [x] **5.4** Refactorizar `database_tool.py`: eliminar `run_in_executor()`, usar `execute_query_async` directamente
- [x] **5.5** Verificar que `KnowledgeService.__init__()` no bloquea (es llamado en startup sync — OK)
- [x] **5.6** Agregar `pytest-asyncio` en `requirements.txt` y `pytest.ini`; corregir tests en `test_memory.py`
- [x] **5.7** Agregar log de timing en `memory_repository.get_profile()`
- [x] **5.8** Actualizar `requirements.txt` con `pytest` y `pytest-asyncio`

---

## Criterios de aceptación

- Ningún método `async def` llama directamente a `execute_query()` sin `await`
- El event loop no se bloquea durante queries a BD
- Tests async pasan al 100%
- No se usa `asyncio.get_event_loop().run_in_executor()` en código nuevo
