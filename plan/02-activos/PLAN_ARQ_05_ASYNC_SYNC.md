# PLAN: Consolidar mezcla async/sync

> **Objetivo**: Eliminar la mezcla de código async/sync que bloquea el event loop de Telegram
> **Rama**: `feature/arq-05-async-sync`
> **Prioridad**: 🟠 Alta
> **Progreso**: 0% (0/8)

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

- [ ] **5.1** Agregar helper `async def run_in_thread(func, *args)` en `database/connection.py` usando `asyncio.to_thread()`
- [ ] **5.2** Refactorizar `memory_repository.py`: reemplazar `execute_query()` directo por `await run_in_thread(self.db_manager.execute_query, query, params)`
- [ ] **5.3** Refactorizar `knowledge_repository.py` con el mismo patrón
- [ ] **5.4** Refactorizar `database_tool.py`: reemplazar `run_in_executor()` por `asyncio.to_thread()`
- [ ] **5.5** Verificar que `KnowledgeService.__init__()` no bloquea (es llamado en startup, está bien sync)
- [ ] **5.6** Agregar tests async con `pytest-asyncio` para repositorios
- [ ] **5.7** Medir latencia antes y después del cambio con logs de timing
- [ ] **5.8** Actualizar `requirements.txt` si se agregan dependencias

---

## Criterios de aceptación

- Ningún método `async def` llama directamente a `execute_query()` sin `await`
- El event loop no se bloquea durante queries a BD
- Tests async pasan al 100%
- No se usa `asyncio.get_event_loop().run_in_executor()` en código nuevo
