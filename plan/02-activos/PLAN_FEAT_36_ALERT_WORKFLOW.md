# Plan: FEAT-36 — Workflow de Análisis de Alertas

> **Estado**: ⚪ No iniciado
> **Última actualización**: 2026-04-10
> **Rama Git**: `feature/feat-36-alert-workflow`

## Resumen de Progreso

| Fase | Progreso | Estado |
|------|----------|--------|
| Fase 1: Infraestructura BD multi-conexión | ░░░░░░░░░░ 0% | ⏳ Pendiente |
| Fase 2: Dominio — entidades y repositorio | ░░░░░░░░░░ 0% | ⏳ Pendiente |
| Fase 3: Prompt Builder | ░░░░░░░░░░ 0% | ⏳ Pendiente |
| Fase 4: Alert Tool (orquestador interno) | ░░░░░░░░░░ 0% | ⏳ Pendiente |
| Fase 5: Agente especializado en BD | ░░░░░░░░░░ 0% | ⏳ Pendiente |
| Fase 6: Integración y validación | ░░░░░░░░░░ 0% | ⏳ Pendiente |

**Progreso Total**: ░░░░░░░░░░ 0% (0/38 tareas)

---

## Descripción

Portar e integrar el workflow de análisis de alertas de monitoreo PRTG
(del sistema GS-prod) al bot Iris, adaptado a la arquitectura ReAct.

El análisis de alertas es complejo: requiere consultar **dos instancias
de SQL Server distintas** (BAZ_CDMX y EKT), enriquecer los eventos con
tickets históricos, templates y matrices de escalamiento, y luego llamar
al LLM con un prompt especializado.

La estrategia elegida es **Tool con sub-workflow interno**: el agente
`alertas` recibe la consulta, el tool `alert_analysis` ejecuta
internamente todo el pipeline de datos + LLM, y devuelve al loop ReAct
el análisis formateado como observación final.

---

## Decisiones Arquitectónicas

### ¿Tool, Workflow separado, o ambos?

**Decisión: Tool con sub-workflow interno** (Opción híbrida)

```
Usuario
  └─→ Orchestrator (intent classifier)
        └─→ Agente "alertas" (especializado, scope reducido)
              └─→ ReAct loop
                    └─→ alert_analysis [tool]
                          ├─ fetch eventos     (BD monitoreo)
                          ├─ enrich tickets    (BD monitoreo)
                          ├─ enrich template   (BD core)
                          ├─ enrich matriz     (BD core)
                          ├─ build prompt
                          └─ LLM call (secundario)
                    └─→ finish con análisis formateado
```

**Por qué no workflow separado:** Iris ya tiene auth, observabilidad,
cost tracking y status messages todos integrados en el ReAct loop.
Un pipeline paralelo duplicaría esa infraestructura.

**Por qué no múltiples tool calls del ReAct loop:** El análisis requiere
orquestación específica con 6+ fuentes de datos en orden determinista.
Dejárselo al LLM sería impredecible y lento.

### Manejo de las 2 bases de datos

```
Alias "monitoreo" → BAZ_CDMX (10.53.34.130:1533)
  ├─ BD Monitoreos → SPs de eventos PRTG y tickets históricos
  └─ BD ABCMASplus → SPs de templates, contactos y matrices

Los SPs *_EKT ya usan OPENDATASOURCE internamente.
Solo necesitamos UN alias de conexión.
AUTOCOMMIT ya configurado en Iris (fix previo) → compatible.

Fallback automático en AlertRepository:
  1. Intenta SP estándar (BAZ_CDMX)
  2. Sin resultados → intenta SP _EKT
  3. Marca resultados con "_origen": "BAZ_CDMX" | "EKT"
```

---

## Stored Procedures a usar

### BD Monitoreos (alias: monitoreo)

| SP | Parámetros | Retorna |
|----|-----------|---------|
| `PrtgObtenerEventosEnriquecidos` | ninguno | Eventos activos PRTG |
| `PrtgObtenerEventosEnriquecidosPerformance` | ninguno | Variante performance |
| `PrtgObtenerEventosEnriquecidos_EKT` | ninguno | Fallback EKT (OPENDATASOURCE) |
| `PrtgObtenerEventosEnriquecidosPerformance_EKT` | ninguno | Fallback EKT performance |
| `IABOT_ObtenerTicketsByAlerta` | `@ip`, `@sensor` | TOP 15 tickets históricos |
| `IABOT_ObtenerTicketsByAlerta_EKT` | `@ip`, `@sensor` | Fallback EKT |

### BD ABCMASplus (alias: monitoreo, prefix con schema)

| SP | Parámetros | Retorna |
|----|-----------|---------|
| `ABCMASplus.dbo.IDTemplateByIp` | `@ip` | `idTemplate`, `instancia` |
| `ABCMASplus.dbo.IDTemplateByUrl` | `@url` | `idTemplate`, `instancia` |
| `ABCMASplus.dbo.Template_GetById` | `@id` | Info del template + GerenciaDesarrollo |
| `ABCMASplus.dbo.Template_GetById_EKT` | `@id` | Fallback EKT |
| `ABCMASplus.dbo.ObtenerMatriz` | `@idTemplate` | Niveles de escalamiento |
| `ABCMASplus.dbo.ObtenerMatriz_EKT` | `@idTemplate` | Fallback EKT |
| `ABCMASplus.dbo.Contacto_GetByIdGerencia` | `@idGerencia` | Contacto del área |
| `ABCMASplus.dbo.Contacto_GetByIdGerencia_EKT` | `@idGerencia` | Fallback EKT |

---

## Fase 1: Infraestructura — BD multi-conexión para monitoreo

**Objetivo**: Configurar el alias `monitoreo` en Iris para que apunte
a la instancia BAZ_CDMX de monitoreo. Sin cambios de código — solo config.

**Dependencias**: Ninguna

### Tareas

- [ ] **Agregar variables de entorno** — Añadir en `.env` las vars del alias `monitoreo`
  - Variables:
    ```
    DB_CONNECTIONS=core,monitoreo
    DB_MONITOREO_HOST=10.53.34.130
    DB_MONITOREO_PORT=1533
    DB_MONITOREO_NAME=consolamonitoreo
    DB_MONITOREO_USER=<usuario>
    DB_MONITOREO_PASSWORD=<password>
    DB_MONITOREO_TYPE=mssql
    ```
  - Archivo: `.env` y `.env.example`

- [ ] **Verificar que DatabaseManager resuelve el alias** — Confirmar que
  `settings.get_db_connections()["monitoreo"]` retorna el `DbConnectionConfig` correcto.
  - Archivo: `src/config/settings.py` (no debería necesitar cambios)

- [ ] **Probar conectividad** — Script de prueba que ejecute un EXEC básico
  contra la instancia monitoreo y verifique AUTOCOMMIT con OPENDATASOURCE.
  - Archivo: `scripts/test_monitoreo_connection.py`

### Entregables
- [ ] `.env.example` actualizado con vars de monitoreo
- [ ] Script de prueba de conectividad ejecutado con éxito

---

## Fase 2: Dominio — Entidades y Repositorio de Alertas

**Objetivo**: Capa de dominio limpia para alertas, con repositorio que
encapsula toda la lógica de fallback BAZ→EKT.

**Dependencias**: Fase 1

### Tareas

- [ ] **Crear módulo de dominio** — Carpeta y `__init__.py`
  - Archivo: `src/domain/alerts/__init__.py`

- [ ] **Crear entidades Pydantic** — Modelos tipados para el dominio de alertas
  - Archivo: `src/domain/alerts/alert_entity.py`
  - Modelos:
    - `AlertEvent` — Evento activo de PRTG (Equipo, IP, Sensor, Status, Prioridad, idArea*, _origen)
    - `HistoricalTicket` — Ticket previo (Ticket, alerta, detalle, accionCorrectiva)
    - `Template` — Info del template (idTemplate, Aplicacion, GerenciaDesarrollo, instancia)
    - `EscalationLevel` — Nivel de matriz (nivel, Nombre, puesto, Extension, celular, correo, TiempoEscalacion)
    - `AreaContacto` — Contacto de gerencia (Gerencia, direccion_correo, extensiones)
    - `AlertContext` — Agregado con todo el contexto enriquecido de un evento

- [ ] **Crear AlertRepository** — Acceso a datos con fallback automático
  - Archivo: `src/domain/alerts/alert_repository.py`
  - Métodos:
    - `get_active_events(ip=None, equipo=None, solo_down=False) → list[AlertEvent]`
    - `get_historical_tickets(ip, sensor) → list[HistoricalTicket]`
    - `get_template_id(ip, url=None) → dict | None`
    - `get_template_info(template_id) → Template | None`
    - `get_escalation_matrix(template_id) → list[EscalationLevel]`
    - `get_contacto_gerencia(id_gerencia, usar_ekt=False) → AreaContacto | None`
  - Lógica de fallback:
    - Cada método intenta SP estándar primero
    - Si retorna vacío → intenta versión _EKT
    - Usa `execute_query_async` del `DatabaseManager` del alias `monitoreo`
    - Maneja excepciones sin fallar (retorna `[]` o `None`)
    - Marca `_origen` en `AlertEvent` para que el prompt sepa qué etiqueta usar

- [ ] **Método privado `_run_with_fallback`** — Helper genérico para patrón fallback
  ```python
  async def _run_with_fallback(sp_principal, sp_ekt, params) -> list[dict]
  ```
  - Evita duplicar el patrón try/fallback en cada método

- [ ] **Tests del repositorio** — Con mock de DatabaseManager
  - Archivo: `tests/domain/test_alert_repository.py`
  - Casos: evento encontrado en BAZ, fallback a EKT, ambos vacíos

### Entregables
- [ ] `src/domain/alerts/` con entidades y repositorio
- [ ] Tests unitarios pasando

---

## Fase 3: Alert Prompt Builder

**Objetivo**: Construir el prompt enriquecido multi-sección que el LLM
analiza para generar el diagnóstico de alerta.

**Dependencias**: Fase 2

### Tareas

- [ ] **Crear AlertPromptBuilder** — Adaptar de GS-prod a Iris
  - Archivo: `src/domain/alerts/alert_prompt_builder.py`
  - Método principal: `build(context: AlertContext) → str`
  - Secciones del prompt:
    1. **Datos del evento** — Template, Equipo, IP, Sensor, Áreas responsables
    2. **Tickets históricos** — TOP 15, con `[Salto]` → `\n`
    3. **Template + Matriz** — GerenciaDesarrollo + niveles con contactos
    4. **Instrucción al LLM** — Estructura Markdown esperada:
       - 📌 Template # + Aplicacion + etiqueta (ABCMASplus/ABCEKT)
       - 🔴 ALERTA: Equipo (IP)
       - 📡 Sensor + resumen
       - 👥 Áreas (atendedora + administradora) con contactos
       - 💻 Gerencia de desarrollo
       - 📞 Matriz de escalamiento con niveles
       - 🛠 5 acciones recomendadas (basadas en tickets)
       - 🔍 Posible causa raíz
       - 📋 Contexto histórico (1 oración)
  - Adaptaciones vs GS-prod:
    - Usa entidades Pydantic (`AlertContext`) en lugar de dicts crudos
    - Sistema prompt separado del user prompt (para `generate_messages`)

- [ ] **Disclaimer** — Constante con el aviso de responsabilidad
  ```
  ⚠️ Las sugerencias son orientativas. La decisión es responsabilidad
  exclusiva del operador. Valide siempre el impacto antes de actuar.
  ```

### Entregables
- [ ] `src/domain/alerts/alert_prompt_builder.py`

---

## Fase 4: Alert Analysis Tool

**Objetivo**: Tool que encapsula el pipeline completo como una sola
acción del ReAct loop. El agente llama el tool una vez y recibe el
análisis completo formateado.

**Dependencias**: Fases 2 y 3

### Tareas

- [ ] **Crear AlertAnalysisTool** — Tool en el registry de Iris
  - Archivo: `src/agents/tools/alert_analysis_tool.py`
  - Clase: `AlertAnalysisTool(BaseTool)`
  - Metadata:
    ```python
    name = "alert_analysis"
    description = "Analiza alertas activas de monitoreo PRTG. Obtiene eventos, "
                  "enriquece con historial de tickets, template y matriz de "
                  "escalamiento, y genera diagnóstico con acciones recomendadas."
    parameters = [
        ToolParameter("ip", str, required=False, description="IP del equipo a analizar"),
        ToolParameter("equipo", str, required=False, description="Nombre del equipo"),
        ToolParameter("solo_down", bool, required=False, description="Solo equipos caídos"),
    ]
    ```

- [ ] **Implementar `execute`** — Pipeline interno completo
  - Extraer filtros de `action_input` (ip, equipo, solo_down)
  - También extraer filtros del texto de la query (regex IP, keywords down/caído)
  - `repo.get_active_events(...)` → lista de eventos
  - Selección: si filtro específico → TOP 1; si general → TOP 3 por Prioridad desc
  - Para cada evento:
    - `repo.get_historical_tickets(ip, sensor)`
    - Determinar `usar_ekt` desde `evento._origen`
    - `repo.get_contacto_gerencia(idAreaAtendedora, usar_ekt)`
    - `repo.get_contacto_gerencia(idAreaAdministradora, usar_ekt)`
    - `repo.get_template_id(ip, url)` → detecta si sensor es URL
    - `repo.get_template_info(template_id)` con fallback EKT si instancia='COMERCIO'
    - `repo.get_escalation_matrix(template_id)` con fallback EKT
    - Construir `AlertContext`
    - `builder.build(context)` → prompt
    - `llm.generate_messages(messages)` → análisis
    - Agregar disclaimer

- [ ] **LLM call secundario** — Usar `OpenAIProvider` del agente
  - El tool recibe `user_context` en `action_input`
  - Accede al LLM vía el mismo provider del agente (no instanciar nuevo)
  - Registrar costo en `CostTracker` activo (automático via `get_current_tracker`)
  - Modelo: `settings.openai_loop_model` (mismo del agente)

- [ ] **Registrar el tool** — Agregar al registry
  - Archivo: `src/agents/tools/registry.py` o donde se inicialicen los tools
  - Agregar `AlertAnalysisTool` con su `AlertRepository` inyectado

- [ ] **Actualizar `__init__.py` de tools**
  - Archivo: `src/agents/tools/__init__.py`

### Entregables
- [ ] `src/agents/tools/alert_analysis_tool.py`
- [ ] Tool registrado y visible en `tools.get_tools_prompt()`

---

## Fase 5: Agente Especializado en BD

**Objetivo**: Configurar en `BotIAv2_AgenteDef` un agente "alertas"
con tool scope reducido y system prompt especializado, para que el
orchestrator lo route automáticamente con el intent classifier.

**Dependencias**: Fase 4

### Tareas

- [ ] **Definir el agente en BD** — INSERT en `BotIAv2_AgenteDef`
  ```sql
  INSERT INTO abcmasplus..BotIAv2_AgenteDef (
      nombre, descripcion, systemPrompt, herramientas,
      esGeneralista, activo, temperatura, maxIteraciones
  ) VALUES (
      'alertas',
      'Análisis de alertas activas de monitoreo PRTG: diagnóstico, acciones recomendadas y matriz de escalamiento',
      '<system prompt especializado>',
      '["alert_analysis", "datetime", "finish"]',
      0,  -- especialista
      1,
      0.1,
      3   -- máximo 3 iteraciones (1 llamada al tool + finish)
  );
  ```

- [ ] **Escribir system prompt del agente alertas**
  ```
  Eres Iris, asistente especializada en análisis de alertas de monitoreo.
  Tu única función es analizar eventos activos de PRTG y presentar
  el diagnóstico completo al usuario.

  ## REGLA CRÍTICA
  Para cualquier consulta sobre alertas, usa la tool alert_analysis.
  No generes diagnósticos de memoria — siempre consulta los datos reales.

  ## Flujo
  1. Usa alert_analysis con los filtros que el usuario mencione (IP, equipo, solo_down)
  2. Presenta el resultado al usuario con finish

  ## Formato de Respuesta
  SIEMPRE responde con JSON:
  {"thought": "...", "action": "nombre_accion", "action_input": {}, "final_answer": null}
  ```

- [ ] **Verificar que el intent classifier enruta correctamente**
  - Probar consultas como:
    - "¿hay alertas activas?"
    - "qué pasa con 10.53.34.50"
    - "el servidor de producción está caído"
  - El classifier debe seleccionar "alertas" con confidence > 0.8

- [ ] **Ajustar description del agente** — La description es la que lee el classifier
  - Asegurarse de que incluya keywords: alertas, monitoreo, PRTG, caído, down, equipo, IP

### Entregables
- [ ] Agente "alertas" activo en BD
- [ ] Intent classifier routea correctamente en pruebas

---

## Fase 6: Integración y Validación

**Objetivo**: Prueba end-to-end, verificar observabilidad completa y
documentar el nuevo tool en los archivos de contexto.

**Dependencias**: Fase 5

### Tareas

- [ ] **Test end-to-end básico** — Consulta sin filtros (todas las alertas)
  - Verificar que llega respuesta con análisis formateado
  - Verificar step_traces: [0:classifier, 1:llm_call, 2:alert_analysis, 3:llm_call, 4:finish]
  - Verificar costo total incluye LLM secundario del tool

- [ ] **Test end-to-end con IP** — "¿qué pasa con 10.80.191.22?"
  - Verificar que filtra por IP correctamente
  - Verificar fallback EKT si el equipo está en instancia comercio

- [ ] **Test sin alertas activas** — Verificar mensaje gracioso cuando no hay eventos

- [ ] **Verificar observabilidad** — Confirmar en BD que:
  - `BotIAv2_InteractionSteps` registra el step `alert_analysis` con tokens y costo
  - `BotIAv2_InteractionLogs` registra costo total correcto

- [ ] **Actualizar `.claude/context/TOOLS.md`** — Documentar el nuevo tool
  - Nombre, descripción, parámetros, comportamiento de fallback BAZ/EKT

- [ ] **Actualizar `.claude/context/DATABASE.md`** — Documentar alias `monitoreo`
  - SPs usados, BDs accedidas, estrategia de fallback

- [ ] **Actualizar `.env.example`** — Ya hecho en Fase 1, verificar que está completo

### Entregables
- [ ] End-to-end funcionando con las 3 variantes de consulta
- [ ] Observabilidad completa en BD
- [ ] Documentación de contexto actualizada

---

## Riesgos y Mitigaciones

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|--------------|---------|------------|
| OPENDATASOURCE falla por DTC | Media | Alto | AUTOCOMMIT ya configurado; probar en Fase 1 |
| Columna `instancia` sin nombre en SP | Media | Medio | AlertRepository normaliza el dict igual que GS-prod |
| LLM no sigue el JSON ReAct al recibir el análisis | Baja | Medio | Fallback plain-text→finish ya implementado |
| Tiempo de respuesta alto (6+ queries + LLM) | Alta | Medio | Status message mantiene al usuario informado; tool retorna en 1 iteración |
| SP Performance vs estándar → datos distintos | Baja | Medio | Combinar ambos resultados y deduplicar por IP+Sensor |

---

## Criterios de Éxito

- [ ] Usuario puede preguntar "¿hay alertas activas?" y recibe análisis con acciones
- [ ] Usuario puede preguntar "¿qué pasa con 10.x.x.x?" y recibe diagnóstico específico
- [ ] Fallback EKT transparente — usuario no nota diferencia entre BAZ y EKT
- [ ] Costo del LLM secundario aparece en `BotIAv2_InteractionSteps`
- [ ] Tiempo de respuesta total < 30s (incluyendo 6 queries BD + 2 LLM calls)
- [ ] Disclaimer incluido en toda respuesta de alertas

---

## Historial de Cambios

| Fecha | Cambio | Autor |
|-------|--------|-------|
| 2026-04-10 | Creación del plan | Angel David Roque Ayala |
