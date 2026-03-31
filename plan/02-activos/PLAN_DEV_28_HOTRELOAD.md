# Plan: DEV-28 — Hot Reload (Auto-restart en cambios de código)

> **Estado**: ⚪ No iniciado
> **Última actualización**: 2026-03-31
> **Rama Git**: feature/dev-28-hotreload

## Resumen de Progreso

| Fase | Progreso | Estado |
|------|----------|--------|
| Fase 1: Script de desarrollo | ██████████ 100% | ✅ Completada |
| Fase 2: Configuración de watcher | ██████████ 100% | ✅ Completada |
| Fase 3: Integración y documentación | ░░░░░░░░░░ 0% | ⏳ Pendiente |

**Progreso Total**: ████░░░░░░ 33% (3/9 tareas)

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
- [ ] `run_dev.py` funcional que reinicia el bot al guardar cualquier `.py` en `src/`

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
- [ ] Watcher configurado con patrones, ignore y log

---

## Fase 3: Integración y documentación

**Objetivo**: Que el flujo de desarrollo quede documentado y sea fácil de usar
**Dependencias**: Fase 2

### Tareas

- [ ] **Actualizar `README.md`** con instrucciones de desarrollo
  - Sección: `## Desarrollo local`
  - Comandos: `pipenv run python run_dev.py` vs `pipenv run python main.py`

- [ ] **Agregar entrada en `.gitignore`** si hace falta para artefactos del watcher

- [ ] **Verificar compatibilidad** con Windows 11 + Python 3.13 (entorno actual)

### Entregables
- [ ] Documentación actualizada
- [ ] Flujo probado end-to-end en Windows

---

## Diseño técnico

### `run_dev.py` (esquema)

```
1. Iniciar subproceso: subprocess.Popen(["python", "main.py"])
2. Iniciar watchfiles observando src/ y main.py
3. Al detectar cambio:
   a. Log: archivo modificado
   b. Terminar subproceso actual (graceful + kill si no responde)
   c. Esperar que libere recursos (pequeño sleep)
   d. Lanzar nuevo subproceso
4. Al recibir Ctrl+C:
   a. Terminar subproceso
   b. Salir limpiamente
```

### Dependencias nuevas

| Librería | Tipo | Versión |
|----------|------|---------|
| `watchfiles` | dev | `>=0.21` |

---

## Riesgos y Mitigaciones

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|--------------|---------|------------|
| Puerto Telegram ocupado al reiniciar | Media | Alto | Usar `stop()` graceful del bot antes de matar el proceso |
| Bucle infinito de reinicios por error de sintaxis | Baja | Medio | El proceso falla rápido; el watcher espera el próximo cambio |
| No detecta cambios en `.env` | Baja | Bajo | Documentar que cambios de config requieren reinicio manual |

---

## Criterios de Éxito

- [ ] `pipenv run python run_dev.py` inicia el bot correctamente
- [ ] Al guardar un `.py` en `src/`, el bot se reinicia en menos de 3 segundos
- [ ] Ctrl+C cierra limpiamente sin dejar procesos huérfanos
- [ ] `python main.py` sigue funcionando igual (sin cambios en producción)

---

## Historial de Cambios

| Fecha | Cambio | Autor |
|-------|--------|-------|
| 2026-03-31 | Creación del plan | Roque98 |
