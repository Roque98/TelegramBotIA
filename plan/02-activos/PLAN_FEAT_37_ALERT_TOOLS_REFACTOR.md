# Plan: FEAT-37 — Refactor Alert Tools (4 tools estructuradas)

> **Estado**: ⚪ No iniciado
> **Última actualización**: 2026-04-09
> **Rama Git**: `feature/feat-37-alert-tools-refactor`

## Resumen de Progreso

| Fase | Progreso | Estado |
|------|----------|--------|
| Fase 1: Preparación | ░░░░░░░░░░ 0% | ⏳ Pendiente |
| Fase 2: Implementar 4 tools | ░░░░░░░░░░ 0% | ⏳ Pendiente |
| Fase 3: BD — registrar tools y actualizar agente | ░░░░░░░░░░ 0% | ⏳ Pendiente |
| Fase 4: Deprecar alert_analysis_tool | ░░░░░░░░░░ 0% | ⏳ Pendiente |
| Fase 5: Testing y documentación | ░░░░░░░░░░ 0% | ⏳ Pendiente |

**Progreso Total**: ░░░░░░░░░░ 0% (0/22 tareas)

---

## Descripción

Refactorizar la tool monolítica `alert_analysis_tool` en 4 tools especializadas
que retornan **datos estructurados** (JSON/dict) en lugar de Markdown generado
por un LLM interno. El agente ReAct recibe los datos y genera la respuesta
directamente, eliminando el doble-LLM y reduciendo costo y latencia.

### Motivación

| Problema actual | Solución |
|-----------------|----------|
| 2 LLMs en cascada (outer + inner) | 1 solo LLM (outer ReAct agent) |
| ~$0.015 por consulta | ~$0.006 por consulta |
| ~50s latencia | ~15s latencia |
| Respuesta siempre muestra 1 alerta | Agent decide qué mostrar |
| Tool decide formato | Agent controla presentación |

### Tools resultantes

| Tool | Descripción |
|------|-------------|
| `get_active_alerts` | Lista alertas activas con filtros opcionales |
| `get_historical_tickets` | Tickets históricos de un nodo/IP |
| `get_escalation_matrix` | Matriz de escalamiento por IP o template |
| `get_alert_detail` | Contexto completo de una alerta (tickets + escalamiento + contactos) |

---

## Fase 1: Preparación

**Objetivo**: Crear rama, revisar entidades y repositorio existentes
**Dependencias**: Ninguna

### Tareas

- [ ] **Crear feature branch** — `feature/feat-37-alert-tools-refactor` desde `develop`
- [ ] **Revisar `alert_entity.py`** — validar que `AlertEvent` y `AlertContext` tienen
  los campos necesarios para retorno estructurado (sin cambios si ya están bien)
- [ ] **Revisar `alert_repository.py`** — verificar que `get_historical_tickets`,
  `get_template_info`, `get_escalation_matrix` y `get_contacto_gerencia` retornan
  datos usables como dict/list directamente

### Entregables
- [ ] Rama creada y pusheada
- [ ] Lista de ajustes necesarios en repositorio/entidades (puede ser vacía)

---

## Fase 2: Implementar las 4 tools

**Objetivo**: 4 tools nuevas que retornan datos estructurados, sin LLM interno
**Dependencias**: Fase 1

### Tareas

- [ ] **`get_active_alerts_tool.py`**
  - Archivo: `src/agents/tools/get_active_alerts_tool.py`
  - Wrappea `AlertRepository.get_active_events()`
  - Parámetros: `ip?`, `equipo?`, `solo_down?`
  - Retorna: `{"total": N, "alertas": [{"equipo", "ip", "sensor", "status", "prioridad", "detalle", "area_atendedora", "responsable_atendedor"}]}`

- [ ] **`get_historical_tickets_tool.py`**
  - Archivo: `src/agents/tools/get_historical_tickets_tool.py`
  - Wrappea `AlertRepository.get_historical_tickets(ip, sensor?)`
  - Parámetros: `ip` (requerido), `sensor?`
  - Retorna: `{"ip": "...", "total_tickets": N, "tickets": [{"fecha", "descripcion", "estado", "resolucion"}]}`

- [ ] **`get_escalation_matrix_tool.py`**
  - Archivo: `src/agents/tools/get_escalation_matrix_tool.py`
  - Obtiene template_id por IP, luego matriz de escalamiento
  - Parámetros: `ip` (requerido)
  - Retorna: `{"ip": "...", "template": "...", "niveles": [{"nivel", "nombre", "puesto", "contacto", "tiempo_respuesta"}]}`

- [ ] **`get_alert_detail_tool.py`**
  - Archivo: `src/agents/tools/get_alert_detail_tool.py`
  - Combina en paralelo: tickets + template + escalamiento + contactos
  - Parámetros: `ip` (requerido)
  - Retorna: objeto completo con todas las secciones enriquecidas

- [ ] **Actualizar `src/agents/tools/__init__.py`** — exportar las 4 tools nuevas
- [ ] **Actualizar `src/pipeline/factory.py`** — instanciar y registrar las 4 tools

### Entregables
- [ ] 4 archivos de tools implementados
- [ ] Tools registradas en el pipeline

---

## Fase 3: BD — registrar tools y actualizar agente

**Objetivo**: Registrar las 4 tools en BD y actualizar el system prompt del agente alertas
**Dependencias**: Fase 2

### Tareas

- [ ] **Migración `010_feat37_alert_tools_refactor.sql`**
  - Archivo: `scripts/migrations/010_feat37_alert_tools_refactor.sql`
  - Registrar las 4 tools en `BotIAv2_Recurso`
  - Asignar permisos por rol (roles 1,2,3,4,7,8) en `BotIAv2_Permisos`
  - Agregar las 4 tools al scope del agente alertas en `BotIAv2_AgenteTools`
  - Eliminar `alert_analysis` del scope del agente alertas

- [ ] **Migración `010`**: actualizar system prompt del agente alertas
  - Nuevo prompt: instruye al agent a usar datos JSON estructurados
  - Define cómo presentar la lista de alertas, detalle, tickets, escalamiento
  - Incrementar `version` en `BotIAv2_AgenteDef`

- [ ] **Ejecutar migración 010 en BD**

### Entregables
- [ ] Script SQL idempotente creado y ejecutado
- [ ] System prompt del agente alertas actualizado en BD

---

## Fase 4: Deprecar alert_analysis_tool

**Objetivo**: Eliminar la tool monolítica y el LLM interno
**Dependencias**: Fase 3 (BD actualizada antes de eliminar la tool)

### Tareas

- [ ] **Eliminar `alert_analysis_tool.py`**
  - Archivo: `src/agents/tools/alert_analysis_tool.py`

- [ ] **Eliminar `alert_prompt_builder.py`**
  - Archivo: `src/domain/alerts/alert_prompt_builder.py`
  - Ya no existe LLM interno — el builder no tiene uso

- [ ] **Limpiar `src/agents/tools/__init__.py`** — remover export de `alert_analysis`
- [ ] **Limpiar `src/pipeline/factory.py`** — remover instanciación de `alert_analysis`

### Entregables
- [ ] `alert_analysis_tool.py` eliminado
- [ ] `alert_prompt_builder.py` eliminado
- [ ] Sin referencias huérfanas en el codebase

---

## Fase 5: Testing y documentación

**Objetivo**: Validar el flujo completo y actualizar documentación
**Dependencias**: Fase 4

### Tareas

- [ ] **Reiniciar bot** y probar cada tool en Telegram:
  - "¿hay alertas activas?" → `get_active_alerts`
  - "¿qué tickets ha tenido 10.118.57.142?" → `get_historical_tickets`
  - "¿cuál es la matriz de escalamiento de X?" → `get_escalation_matrix`
  - "dame el detalle completo de la alerta más crítica" → `get_active_alerts` + `get_alert_detail`

- [ ] **Actualizar `.claude/context/TOOLS.md`** — documentar las 4 tools nuevas
- [ ] **Merge a `develop`** con `--no-ff`

### Entregables
- [ ] Flujo validado en Telegram
- [ ] Documentación actualizada
- [ ] Merge a develop completado

---

## Riesgos y Mitigaciones

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|--------------|---------|------------|
| `get_historical_tickets` retorna objetos no serializables | Media | Medio | Serializar a dict en la tool antes de retornar |
| El agente no sabe cómo formatear los datos JSON | Media | Alto | System prompt con ejemplos explícitos de entrada/salida |
| Migración 010 no desactiva bien `alert_analysis` del scope | Baja | Medio | Verificar con SELECT antes y después de ejecutar |

---

## Criterios de Éxito

- [ ] "¿hay alertas activas?" responde en < 15s con lista correcta
- [ ] "dame el detalle de X" llama máximo 2 tools (get_active_alerts + get_alert_detail)
- [ ] Sin LLM interno — 0 llamadas a `gpt-5.4` durante el flujo
- [ ] Costo por consulta < $0.008
- [ ] `alert_analysis_tool.py` y `alert_prompt_builder.py` eliminados

---

## Historial de Cambios

| Fecha | Cambio | Autor |
|-------|--------|-------|
| 2026-04-09 | Creación del plan | Angel David / Claude |
