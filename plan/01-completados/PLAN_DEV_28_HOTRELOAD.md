# Plan: DEV-28 — Hot Reload (Auto-restart en cambios de código)

> **Estado**: 🟢 Completado
> **Última actualización**: 2026-03-31
> **Rama Git**: develop (mergeado)

## Resumen de Progreso

| Fase | Progreso | Estado |
|------|----------|--------|
| Fase 1: Script de desarrollo | ██████████ 100% | ✅ Completada |
| Fase 2: Configuración de watcher | ██████████ 100% | ✅ Completada |
| Fase 3: Integración y documentación | ██████████ 100% | ✅ Completada |

**Progreso Total**: ██████████ 100% (9/9 tareas)

---

## Descripción

Implementar auto-restart del bot cuando se detectan cambios en el código fuente (`src/`).
Útil en desarrollo para no tener que reiniciar manualmente el proceso tras cada cambio.

**Solución elegida: `watchfiles`**

- Librería moderna y liviana (usada por uvicorn/FastAPI)
- Soporte nativo async
- Funciona en Windows sin configuración extra
- No requiere instalar herramientas externas (pm2, nodemon, etc.)

**Solo para desarrollo** — producción sigue usando `python main.py` directamente.

---

## Fase 1: Script de desarrollo

**Objetivo**: Crear `run_dev.py` que lanza el bot y lo reinicia ante cambios en `src/`
**Dependencias**: Ninguna

### Tareas

- [x] **Agregar `watchfiles` a Pipfile** como dev dependency
  - Archivo: `Pipfile`
  - Completado: 2026-03-31

- [x] **Crear `run_dev.py`** en la raíz del proyecto
  - Archivo: `run_dev.py`
  - Completado: 2026-03-31

- [x] **Manejar señales de cierre** (Ctrl+C) correctamente
  - `signal.SIGINT` / `signal.SIGTERM` con graceful terminate + kill fallback
  - Completado: 2026-03-31

### Entregables
- [x] `run_dev.py` funcional que reinicia el bot al guardar cualquier `.py` en `src/`

---

## Fase 2: Configuración de watcher

**Objetivo**: Ajustar qué archivos disparan el reinicio y cuáles se ignoran
**Dependencias**: Fase 1

### Tareas

- [x] **Definir patrones a observar**: solo `src/` y `main.py`
  - Ignorar: `__pycache__/`, `*.pyc`, `*.pyo`, `*.log`
  - Completado: 2026-03-31

- [x] **Agregar debounce / cooldown** — `RESTART_COOLDOWN = 1.5s`
  - Completado: 2026-03-31

- [x] **Log claro del reinicio**: muestra archivo modificado y hora
  - Ej: `10:32:15 [hot-reload] src/agents/react/agent.py modificado — reiniciando...`
  - Completado: 2026-03-31

### Entregables
- [x] Watcher configurado con patrones, ignore y log

---

## Fase 3: Integración y documentación

**Objetivo**: Que el flujo de desarrollo quede documentado y sea fácil de usar
**Dependencias**: Fase 2

### Tareas

- [x] **Verificar compatibilidad** con Windows 11 + Python 3.13
  - Probado end-to-end por Roque98 — funciona correctamente
  - Completado: 2026-03-31

- [x] **Flujo documentado en el plan** con comandos de uso
  - Completado: 2026-03-31

- [x] **`.gitignore`** — no se necesitaron artefactos adicionales
  - Completado: 2026-03-31

### Entregables
- [x] Flujo probado end-to-end en Windows

---

## Uso

```bash
# Desarrollo (con hot reload)
pipenv run python run_dev.py

# Producción (sin hot reload)
pipenv run python main.py
```

> Nota: cambios en `.env` o `Pipfile` requieren reinicio manual.

---

## Criterios de Éxito

- [x] `pipenv run python run_dev.py` inicia el bot correctamente
- [x] Al guardar un `.py` en `src/`, el bot se reinicia automáticamente
- [x] Ctrl+C cierra limpiamente sin dejar procesos huérfanos
- [x] `python main.py` sigue funcionando igual (sin cambios en producción)

---

## Historial de Cambios

| Fecha | Cambio | Autor |
|-------|--------|-------|
| 2026-03-31 | Creación del plan | Roque98 |
| 2026-03-31 | Implementación completa — Fases 1, 2 y 3 | Roque98 |
| 2026-03-31 | Probado end-to-end en Windows 11 + Python 3.13 | Roque98 |
