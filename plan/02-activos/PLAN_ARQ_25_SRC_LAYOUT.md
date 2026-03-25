# PLAN: Reorganización de capas en `src/`

> **Objetivo**: Dar coherencia a la estructura de `src/` separando canales de entrada, lógica de orquestación, dominios de negocio e infraestructura en carpetas con responsabilidad única y nombres inequívocos
> **Rama**: `feature/arq-25-src-layout`
> **Prioridad**: 🟠 Alta
> **Progreso**: ░░░░░░░░░░ 0% (0/20 tareas)

---

## Contexto

La estructura actual de `src/` mezcla cuatro categorías conceptuales distintas en el mismo nivel, lo que dificulta entender qué hace cada módulo a primera vista:

| Categoría | Módulos actuales | Problema |
|-----------|-----------------|----------|
| Canales de entrada | `bot/`, `chat_endpoint.py` (suelto) | `chat_endpoint.py` no tiene carpeta propia |
| Normalización | `gateway/` | `gateway/` también tiene orquestación y DI |
| Orquestación / DI | `gateway/handler.py`, `gateway/factory.py` | Mezclado con normalización de mensajes |
| Dominios de negocio | `auth/`, `memory/`, `knowledge/` | Al mismo nivel que infraestructura |
| Infraestructura | `database/`, `events/`, `observability/` | Al mismo nivel que dominios |

### Estructura objetivo

```
src/
├── api/            ← Entrypoint REST (Flask): chat_endpoint.py + futuras rutas
├── bot/            ← Entrypoint Telegram (sin cambios)
├── gateway/        ← Solo normalización multi-canal: MessageGateway
├── pipeline/       ← Orquestación del flujo + factory de dependencias
├── agents/         ← Motor LLM (sin cambios)
├── domain/         ← Lógica de negocio pura
│   ├── auth/
│   ├── memory/
│   └── knowledge/
├── infra/          ← Servicios de soporte técnico
│   ├── database/
│   ├── events/
│   └── observability/
├── config/         ← Sin cambios
└── utils/          ← Sin cambios
```

### Por qué este orden de fases

Las fases están ordenadas de menor a mayor impacto en imports:
- **Fase 1** mueve un solo archivo, casi sin dependencias externas.
- **Fase 2** separa `gateway/` en dos carpetas, afecta ~3-5 archivos.
- **Fases 3 y 4** son las más invasivas (tocan imports en toda la app), por eso van al final cuando el resto ya está estable.

---

## Resumen de Progreso

| Fase | Tareas | Progreso | Estado |
|------|--------|----------|--------|
| Fase 1: Crear `api/` | 4 | ░░░░░░░░░░ 0% | ⏳ Pendiente |
| Fase 2: Separar `gateway/` → `pipeline/` | 5 | ░░░░░░░░░░ 0% | ⏳ Pendiente |
| Fase 3: Agrupar dominios en `domain/` | 6 | ░░░░░░░░░░ 0% | ⏳ Pendiente |
| Fase 4: Agrupar infraestructura en `infra/` | 5 | ░░░░░░░░░░ 0% | ⏳ Pendiente |

---

## Fase 1 — Crear `src/api/`

**Objetivo**: Darle a `chat_endpoint.py` una carpeta propia de la que puedan colgar futuras rutas REST, en lugar de vivir suelto en la raíz de `src/`.

> **Nota de contexto**: ARQ-24 movió `chat_endpoint.py` *fuera* de `api/` porque en ese momento era carpeta de un solo archivo sin perspectiva de crecer. Ahora que el API REST es una ruta confirmada del proyecto, la carpeta tiene justificación clara.

**Dependencias**: Ninguna

### Tareas

- [ ] **25.1** Crear `src/api/__init__.py` vacío
- [ ] **25.2** Mover `src/chat_endpoint.py` → `src/api/chat_endpoint.py`
- [ ] **25.3** Actualizar referencias al módulo en scripts de arranque y en `BACKLOG.md` (que ya usa la ruta `api/chat_endpoint.py` como referencia)
- [ ] **25.4** Verificar que `pytest tests/` sigue sin errores de import

### Entregables
- [ ] `src/api/chat_endpoint.py` existente
- [ ] No queda `src/chat_endpoint.py` en la raíz

---

## Fase 2 — Separar `gateway/` en `gateway/` + `pipeline/`

**Objetivo**: Que `gateway/` sea solo el traductor de mensajes multi-canal (MessageGateway) y que la orquestación del flujo principal (MainHandler) y la construcción de dependencias (factory) tengan su carpeta propia.

**Motivación**: El nombre "gateway" hace pensar en *traducción de protocolo*, no en *coordinación de servicios*. Quien busque dónde se orquesta la respuesta del bot no mirará en `gateway/`.

**Dependencias**: Fase 1 completada

### Tareas

- [ ] **25.5** Crear `src/pipeline/__init__.py` vacío
- [ ] **25.6** Mover `src/gateway/handler.py` → `src/pipeline/handler.py`
- [ ] **25.7** Mover `src/gateway/factory.py` → `src/pipeline/factory.py`
- [ ] **25.8** Actualizar imports internos entre los archivos movidos (referencias cruzadas entre handler ↔ factory ↔ message_gateway)
- [ ] **25.9** Actualizar imports externos: `api/chat_endpoint.py`, `bot/telegram_bot.py`, cualquier otro que importe desde `src.gateway.handler` o `src.gateway.factory`

### Entregables
- [ ] `src/gateway/` contiene solo `message_gateway.py` + `__init__.py`
- [ ] `src/pipeline/` contiene `handler.py` + `factory.py` + `__init__.py`
- [ ] `pytest tests/` sigue sin errores

---

## Fase 3 — Agrupar dominios de negocio en `src/domain/`

**Objetivo**: Separar visualmente los módulos que contienen *lógica de negocio pura* (entidades, repositorios, servicios) de los módulos de infraestructura técnica.

**Afecta**: Todo código que importe desde `src.auth`, `src.memory` o `src.knowledge`.

**Dependencias**: Fase 2 completada

### Tareas

- [ ] **25.10** Crear `src/domain/__init__.py`, `src/domain/auth/`, `src/domain/memory/`, `src/domain/knowledge/`
- [ ] **25.11** Mover contenido de `src/auth/` → `src/domain/auth/`
- [ ] **25.12** Mover contenido de `src/memory/` → `src/domain/memory/`
- [ ] **25.13** Mover contenido de `src/knowledge/` → `src/domain/knowledge/`
- [ ] **25.14** Actualizar todos los imports del proyecto (`agents/tools/`, `pipeline/factory.py`, `pipeline/handler.py`, `bot/middleware/`, etc.)
- [ ] **25.15** Verificar tests y arranque del bot y API

### Entregables
- [ ] `src/auth/`, `src/memory/`, `src/knowledge/` eliminados de la raíz de `src/`
- [ ] `src/domain/{auth,memory,knowledge}/` con el mismo contenido
- [ ] `pytest tests/` y arranque sin errores

---

## Fase 4 — Agrupar infraestructura en `src/infra/`

**Objetivo**: Separar los servicios técnicos de soporte (base de datos, bus de eventos, trazabilidad) de la lógica de negocio.

**Afecta**: Todo código que importe desde `src.database`, `src.events` o `src.observability`.

**Dependencias**: Fase 3 completada

### Tareas

- [ ] **25.16** Crear `src/infra/__init__.py`, `src/infra/database/`, `src/infra/events/`, `src/infra/observability/`
- [ ] **25.17** Mover contenido de `src/database/` → `src/infra/database/`
- [ ] **25.18** Mover contenido de `src/events/` → `src/infra/events/`
- [ ] **25.19** Mover contenido de `src/observability/` → `src/infra/observability/`
- [ ] **25.20** Actualizar todos los imports del proyecto y verificar arranque completo (bot + API REST)

### Entregables
- [ ] `src/database/`, `src/events/`, `src/observability/` eliminados de la raíz de `src/`
- [ ] `src/infra/{database,events,observability}/` con el mismo contenido
- [ ] `pytest tests/` y arranque sin errores

---

## Criterios de Éxito

- [ ] `src/` tiene exactamente 9 carpetas de primer nivel con responsabilidad única: `api/`, `bot/`, `gateway/`, `pipeline/`, `agents/`, `domain/`, `infra/`, `config/`, `utils/`
- [ ] Ningún archivo `.py` suelto en la raíz de `src/` (solo `__init__.py`)
- [ ] `pytest tests/` pasa sin `ImportError` ni `ModuleNotFoundError`
- [ ] El bot de Telegram y el API REST arrancan correctamente
- [ ] Un desarrollador nuevo puede deducir la responsabilidad de cada carpeta solo leyendo su nombre

---

## Riesgos

| Riesgo | Probabilidad | Mitigación |
|--------|-------------|------------|
| Import circular al mover domain/infra | Media | Mover un dominio a la vez, verificar tests entre cada movimiento |
| Referencia a ruta de módulo en cadena de texto (ej. logging, strings) | Baja | Grep de `src.auth`, `src.memory`, etc. antes de mover |
| `__init__.py` con re-exports que ocultan la ruta real | Baja | Revisar `__init__.py` de cada módulo antes de mover |

---

## Historial de Cambios

| Fecha | Cambio |
|-------|--------|
| 2026-03-25 | Creación del plan |
