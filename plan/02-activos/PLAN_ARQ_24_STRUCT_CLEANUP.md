# PLAN: Limpieza estructural del proyecto

> **Objetivo**: Eliminar código muerto, archivos mal ubicados e inconsistencias de naming que generan confusión y rompen la ejecución de tests
> **Rama**: `feature/arq-24-struct-cleanup`
> **Prioridad**: 🟠 Alta
> **Progreso**: 0% (0/4)

---

## Contexto

Un análisis exhaustivo del proyecto reveló tres categorías de problemas estructurales:

1. **Tests obsoletos con imports rotos** — tres carpetas apuntan a módulos que ya no existen tras la migración a la arquitectura ReAct. Causan `ImportError` inmediato si pytest los recolecta.
2. **Archivos de diagnóstico sueltos en la raíz** — cinco `test_*.py` en la raíz son scripts de diagnóstico manual (conexión a BD, variables de entorno) que pytest ejecuta involuntariamente y fallan porque dependen de infraestructura externa.
3. **Inconsistencias de naming** — `Ejemplos/` (mayúscula, legacy) coexiste con `examples/` (minúscula, actual); `src/api/` es una carpeta con un único archivo.

---

## Archivos / carpetas involucradas

**Eliminar (tests obsoletos — arquitectura anterior):**
- `tests/agent/` — imports a `src.agent.*` (singular) que no existe; reemplazado por `tests/agents/`
- `tests/tools/` — imports a `src.tools` que no existe; reemplazado por `tests/agents/test_tools.py`
- `tests/orchestrator/` — imports a `src.orchestrator` que no existe
- `tests/test_agent.py` — importa `src.agent.llm_agent` que no existe

**Mover a `scripts/diagnostics/`:**
- `test_db_connection.py`
- `test_db_final.py`
- `test_env_loading.py`
- `test_simple_connection.py`
- `test_tools_manual.py`

**Renombrar:**
- `Ejemplos/` → `examples/legacy/`

**Consolidar:**
- `src/api/chat_endpoint.py` → `src/chat_endpoint.py` (eliminar carpeta `src/api/`)

---

## Tareas

- [ ] **24.1** Verificar que `tests/agent/`, `tests/tools/` y `tests/orchestrator/` no contienen
  tests válidos que hayan sido actualizados recientemente (revisar git log de cada archivo).
  Si alguno tiene lógica reutilizable, migrar el caso de test a la carpeta correcta antes de
  eliminar.

- [ ] **24.2** Eliminar carpetas y archivos con tests obsoletos:
  - `tests/agent/` (completo)
  - `tests/tools/` (completo)
  - `tests/orchestrator/` (completo)
  - `tests/test_agent.py`

- [ ] **24.3** Mover los 5 scripts de diagnóstico de la raíz a `scripts/diagnostics/`:
  - Crear `scripts/diagnostics/` si no existe
  - Mover `test_db_connection.py`, `test_db_final.py`, `test_env_loading.py`,
    `test_simple_connection.py`, `test_tools_manual.py`
  - Verificar que `pytest.ini` tiene `testpaths = tests` para que pytest no los recolecte

- [ ] **24.4** Limpiar inconsistencias de naming:
  - Renombrar `Ejemplos/` → `examples/legacy/` (consolidar bajo `examples/`)
  - Mover `src/api/chat_endpoint.py` a `src/chat_endpoint.py`
  - Eliminar carpeta vacía `src/api/`
  - Actualizar todos los imports de `src.api.chat_endpoint` a `src.chat_endpoint`

---

## Criterios de aceptación

- `pytest tests/` se ejecuta sin `ImportError` ni `ModuleNotFoundError`
- No hay archivos `test_*.py` en la raíz del proyecto
- Solo existe una carpeta `examples/` (minúscula)
- `src/api/` no existe; `chat_endpoint.py` vive en `src/`
- `git status` no muestra archivos legítimos sin trackear

---

## Notas

- La tarea 24.1 es la más delicada: revisar antes de borrar para no perder lógica de test válida.
- La tarea 24.4 (mover `chat_endpoint.py`) requiere buscar todos los imports en el proyecto
  y actualizarlos — usar grep antes de mover.
- El orden de ejecución es 24.1 → 24.2 → 24.3 → 24.4.
