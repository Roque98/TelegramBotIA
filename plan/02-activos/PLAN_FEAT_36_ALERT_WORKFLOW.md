# Plan: FEAT-36 — Workflow de Análisis de Alertas

> **Estado**: 🟡 En progreso
> **Última actualización**: 2026-04-09
> **Rama Git**: `feature/feat-36-alert-workflow`

## Resumen de Progreso

| Fase | Progreso | Estado |
|------|----------|--------|
| Fase 1: Infraestructura BD multi-conexión | ██████████ 100% | ✅ Completada |
| Fase 2: Dominio — entidades y repositorio | ██████████ 100% | ✅ Completada |
| Fase 3: Prompt Builder | ██████████ 100% | ✅ Completada |
| Fase 4: Alert Tool (orquestador interno) | ██████████ 100% | ✅ Completada |
| Fase 5: Agente especializado en BD | ████░░░░░░ 40% | 🔄 En progreso |
| Fase 6: Integración y validación | ░░░░░░░░░░ 0% | ⏳ Pendiente |

**Progreso Total**: ████████░░ 80% (pendiente: ejecutar migración 008 + validar routing)

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

## Fase 1: Infraestructura — BD multi-conexión para monitoreo ✅

**Objetivo**: Configurar el alias `monitoreo` en Iris para que apunte
a la instancia BAZ_CDMX de monitoreo. Sin cambios de código — solo config.

**Dependencias**: Ninguna

### Tareas

- [x] **Agregar variables de entorno** — Añadir en `.env` las vars del alias `monitoreo`
  - Archivo: `.env` y `.env.example`
  - Commit: `568a1d8`

- [x] **`Settings.extra="ignore"`** — Permite que `DB_MONITOREO_*` no rompa
  la validación de Pydantic Settings (las lee `get_db_connections()` directo de `os.environ`)
  - Archivo: `src/config/settings.py`
  - Commit: `568a1d8`

- [ ] **Probar conectividad** — Script de prueba contra la instancia monitoreo
  - Archivo: `scripts/test_monitoreo_connection.py` (pendiente)

### Entregables
- [x] `.env.example` actualizado con vars de monitoreo
- [ ] Script de prueba de conectividad ejecutado con éxito

---

## Fase 2: Dominio — Entidades y Repositorio de Alertas ✅

**Objetivo**: Capa de dominio limpia para alertas, con repositorio que
encapsula toda la lógica de fallback BAZ→EKT.

**Dependencias**: Fase 1

### Tareas

- [x] **Crear módulo de dominio** — `src/domain/alerts/__init__.py`
  - Commit: `568a1d8`

- [x] **Crear entidades Pydantic** — `src/domain/alerts/alert_entity.py`
  - `AlertEvent`, `HistoricalTicket`, `Template`, `EscalationLevel`, `AreaContacto`, `AlertContext`
  - Commit: `568a1d8`

- [x] **Crear AlertRepository** — `src/domain/alerts/alert_repository.py`
  - Todos los métodos implementados con fallback BAZ→EKT
  - Helpers `_run_sp_with_fallback` y `_run_sps_with_fallback`
  - Commit: `568a1d8`

### Entregables
- [x] `src/domain/alerts/` con entidades y repositorio

---

## Fase 3: Alert Prompt Builder ✅

**Objetivo**: Construir el prompt enriquecido multi-sección que el LLM
analiza para generar el diagnóstico de alerta.

**Dependencias**: Fase 2

### Tareas

- [x] **Crear AlertPromptBuilder** — `src/domain/alerts/alert_prompt_builder.py`
  - `build(context) → (system_prompt, user_prompt)` para `generate_messages()`
  - 4 secciones: evento, tickets históricos, template/escalamiento, instrucción
  - Constante `DISCLAIMER` con aviso de responsabilidad
  - Commit: `568a1d8`

### Entregables
- [x] `src/domain/alerts/alert_prompt_builder.py`

---

## Fase 4: Alert Analysis Tool ✅

**Objetivo**: Tool que encapsula el pipeline completo como una sola
acción del ReAct loop. El agente llama el tool una vez y recibe el
análisis completo formateado.

**Dependencias**: Fases 2 y 3

### Tareas

- [x] **`ToolCategory.MONITORING`** — Agregado a `src/agents/tools/base.py`
  - Commit: `568a1d8`

- [x] **Crear AlertAnalysisTool** — `src/agents/tools/alert_analysis_tool.py`
  - Parámetros: `query` (required), `ip`, `equipo`, `solo_down` (optional)
  - Enriquecimiento en paralelo con `asyncio.gather`
  - LLM call con `data_llm.generate_messages()` — costo se registra automáticamente vía `CostTracker`
  - Commit: `568a1d8`

- [x] **Registrar en factory** — `src/pipeline/factory.py`
  - Solo activa si `db_registry.is_configured("monitoreo")` — sin monitoreo en `.env` la tool se omite silenciosamente
  - Commit: `568a1d8`

- [x] **`to_observation(max_length=8000)`** — `src/agents/react/agent.py`
  - Evita truncar el análisis completo de alertas
  - Commit: `568a1d8`

- [x] **Lazy import en `__init__.py`** — `src/agents/tools/__init__.py`
  - Commit: `568a1d8`

### Entregables
- [x] `src/agents/tools/alert_analysis_tool.py`
- [x] Tool registrado en `factory._build_tool_catalog()`

---

## Fase 5: Registros en BD (migración 008)

**Objetivo**: Ejecutar los 3 INSERTs necesarios para activar la tool
y el agente en el sistema dinámico del orquestador.

**Dependencias**: Fase 4

**Archivo**: `scripts/migrations/008_feat36_alert_analysis_tool.sql`

### Tareas

- [x] **Migración 008 creada** — `scripts/migrations/008_feat36_alert_analysis_tool.sql`
  - Commit: `8f1468f`

- [ ] **Ejecutar INSERT 1 — `BotIAv2_Recurso`**
  ```sql
  -- Registra la tool en el catálogo de recursos del sistema.
  -- El factory.py lee esta tabla al arrancar para saber qué tools instanciar.
  INSERT INTO ABCMASplus.dbo.BotIAv2_Recurso
      (recurso, tipoRecurso, descripcion, esPublico, activo)
  VALUES
      ('tool:alert_analysis', 'tool',
       'Análisis de alertas activas PRTG con diagnóstico, acciones recomendadas y matriz de escalamiento',
       0,   -- esPublico=0: requiere autenticación
       1);  -- activo=1: habilitada
  ```
  > Columnas reales de la tabla: `idRecurso`, `recurso`, `tipoRecurso`, `esPublico`, `descripcion`, `activo`, `fechaCreacion`

- [ ] **Ejecutar INSERT 2 — `BotIAv2_Permisos`**
  ```sql
  -- Permisos por rol (mismos que las demás tools: roles 1,2,3,4,7,8).
  -- esPublico=0 en Recurso → el sistema valida permisos antes de ejecutar.
  DECLARE @idRecurso     INT = (SELECT idRecurso     FROM ABCMASplus.dbo.BotIAv2_Recurso    WHERE recurso = 'tool:alert_analysis');
  DECLARE @idTipoEntidad INT = (SELECT idTipoEntidad FROM ABCMASplus.dbo.BotIAv2_TipoEntidad WHERE nombre  = 'autenticado');

  INSERT INTO ABCMASplus.dbo.BotIAv2_Permisos
      (idTipoEntidad, idEntidad, idRecurso, idRolRequerido, permitido, activo)
  SELECT @idTipoEntidad, 0, @idRecurso, idRol, 1, 1
  FROM (VALUES (1),(2),(3),(4),(7),(8)) AS roles(idRol)
  WHERE NOT EXISTS (
      SELECT 1 FROM ABCMASplus.dbo.BotIAv2_Permisos
      WHERE idRecurso = @idRecurso AND idRolRequerido = roles.idRol AND activo = 1
  );
  ```

- [ ] **Ejecutar INSERT 3 — `BotIAv2_AgenteDef`**
  ```sql
  -- Registra el agente especialista. El intent classifier usa la descripción
  -- para decidir cuándo rutear al agente "alertas".
  INSERT INTO ABCMASplus.dbo.BotIAv2_AgenteDef
      (nombre, descripcion, systemPrompt, temperatura, maxIteraciones,
       modeloOverride, esGeneralista, activo)
  VALUES (
      'alertas',
      'Especialista en monitoreo PRTG. Maneja consultas sobre alertas activas, equipos caídos, '
      'problemas de red/infraestructura, análisis de incidentes y matriz de escalamiento.',
      N'Eres Iris, asistente de operaciones TI especializado en monitoreo de infraestructura PRTG.

Tus capacidades:
{tools_description}

{usage_hints}

Reglas:
- Usa alert_analysis para CUALQUIER consulta sobre alertas, equipos, sensores o incidentes de red.
- Si el usuario filtra por IP o equipo, pasa esos parámetros a la tool.
- Si pregunta solo por equipos caídos, usa solo_down=true.
- Presenta el análisis tal como lo retorna la tool — ya viene formateado en Markdown.
- No inventes datos de equipos ni IPs. Toda la información viene de la tool.',
      0.1,   -- temperatura
      5,     -- maxIteraciones
      NULL,  -- modeloOverride: usa openai_loop_model del sistema
      0,     -- esGeneralista=0: agente especialista
      1);    -- activo=1
  ```

- [ ] **Ejecutar INSERT 4 — `BotIAv2_AgenteTools`**
  ```sql
  -- Asigna alert_analysis al scope del agente alertas.
  -- Solo las tools en su scope aparecen en el prompt del agente.
  DECLARE @idAgente INT = (
      SELECT idAgente FROM ABCMASplus.dbo.BotIAv2_AgenteDef WHERE nombre = 'alertas'
  );
  INSERT INTO ABCMASplus.dbo.BotIAv2_AgenteTools (idAgente, nombreTool, activo)
  VALUES (@idAgente, 'alert_analysis', 1);
  ```

- [ ] **Verificar los 4 registros**
  ```sql
  SELECT recurso, tipoRecurso, esPublico, activo FROM ABCMASplus.dbo.BotIAv2_Recurso
  WHERE recurso = 'tool:alert_analysis';

  SELECT nombre, descripcion, temperatura, maxIteraciones, esGeneralista, activo
  FROM ABCMASplus.dbo.BotIAv2_AgenteDef WHERE nombre = 'alertas';

  SELECT at.nombreTool, at.activo FROM ABCMASplus.dbo.BotIAv2_AgenteTools at
  JOIN ABCMASplus.dbo.BotIAv2_AgenteDef ad ON at.idAgente = ad.idAgente
  WHERE ad.nombre = 'alertas';
  ```

- [ ] **Reiniciar bot o ejecutar `/reload_agent_config`** — Para que el orquestador
  cargue el nuevo agente sin reiniciar el proceso

### Entregables
- [ ] `BotIAv2_Recurso`: fila `tool:alert_analysis` con `activo=1`
- [ ] `BotIAv2_Permisos`: 6 filas (roles 1,2,3,4,7,8) con `permitido=1`
- [ ] `BotIAv2_AgenteDef`: agente `alertas` activo con system prompt
- [ ] `BotIAv2_AgenteTools`: scope `alert_analysis` asignado al agente

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
| 2026-04-09 | Fases 1-4 completadas; migración 008 creada | Claude Sonnet 4.6 |
| 2026-04-09 | Fase 5 actualizada con INSERTs correctos (Recurso + AgenteDef + AgenteTools) | Claude Sonnet 4.6 |
