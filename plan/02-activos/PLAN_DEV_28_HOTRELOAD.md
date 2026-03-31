# Plan: DEV-28 — Hot Reload (Auto-restart en cambios de código)

> **Estado**: ⚪ No iniciado
> **Última actualización**: 2026-03-31
> **Rama Git**: feature/dev-28-hotreload

## Resumen de Progreso

| Fase | Progreso | Estado |
|------|----------|--------|
| Fase 1: Script de desarrollo | ░░░░░░░░░░ 0% | ⏳ Pendiente |
| Fase 2: Configuración de watcher | ░░░░░░░░░░ 0% | ⏳ Pendiente |
| Fase 3: Integración y documentación | ░░░░░░░░░░ 0% | ⏳ Pendiente |

**Progreso Total**: ░░░░░░░░░░ 0% (0/9 tareas)

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

- [ ] **Agregar `watchfiles` a Pipfile** como dev dependency
  - Archivo: `Pipfile`
  - Comando: `pipenv install watchfiles --dev`

- [ ] **Crear `run_dev.py`** en la raíz del proyecto
  - Archivo: `run_dev.py`
  - Responsabilidad: lanzar `main.py` como subproceso y relanzarlo cuando watchfiles detecte cambios en `src/`

- [ ] **Manejar señales de cierre** (Ctrl+C) correctamente
  - Terminar el subproceso del bot antes de salir
  - Evitar procesos zombie o puertos ocupados

### Entregables
- [ ] `run_dev.py` funcional que reinicia el bot al guardar cualquier `.py` en `src/`

---

## Fase 2: Configuración de watcher

**Objetivo**: Ajustar qué archivos disparan el reinicio y cuáles se ignoran
**Dependencias**: Fase 1

### Tareas

- [ ] **Definir patrones a observar**: solo `src/**/*.py` y `main.py`
  - Ignorar: `__pycache__/`, `*.pyc`, `.env`, `tests/`, `plan/`, `docs/`

- [ ] **Agregar debounce / cooldown** para evitar reinicios múltiples
  al guardar varios archivos rápido (ej. refactor con IDE)
  - `watchfiles` tiene debounce nativo configurable

- [ ] **Log claro del reinicio**: mostrar qué archivo cambió y timestamp
  - Ej: `[hot-reload] src/agents/react/agent.py modificado — reiniciando...`

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
