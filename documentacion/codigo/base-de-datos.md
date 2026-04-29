[Docs](../index.md) › [Código](README.md) › Base de datos

# Base de datos

La base de datos es `abcmasplus` en SQL Server. Las tablas del bot tienen prefijo `BotIAv2_`.
Las tablas sin prefijo son del sistema legacy empresarial que el bot consulta (solo lectura).

---

## Configuración de conexión

| Parámetro | Valor por defecto | Variable de entorno |
|-----------|-------------------|---------------------|
| Motor | SQL Server (mssql) | `DB_TYPE` |
| Host | localhost | `DB_HOST` |
| Puerto | 1433 | `DB_PORT` |
| Instancia | *(vacío)* | `DB_INSTANCE` |
| Base de datos | — | `DB_NAME` |
| Driver | ODBC Driver 17 for SQL Server | — |
| Pool size | 5 + 10 overflow | — |
| Timeout | 20 segundos | — |

---

## Tablas del bot (BotIAv2_*)

### BotIAv2_UsuariosTelegram — cuentas Telegram registradas

| Columna | Tipo | Descripción |
|---------|------|-------------|
| `idTelegramUsuario` | INT PK | — |
| `idUsuario` | INT FK → Usuarios | — |
| `telegramChatId` | BIGINT UNIQUE | Chat ID de Telegram |
| `telegramUsername` | VARCHAR(100) | @username (puede ser null) |
| `verificado` | BIT | 1=cuenta verificada |
| `codigoVerificacion` | VARCHAR(10) | Código temporal de 6 dígitos |
| `activo` | BIT | 1=puede usar el bot |
| `fechaRegistro` | DATETIME | — |

### BotIAv2_UserMemoryProfiles — perfil de memoria del usuario

| Columna | Tipo | Descripción |
|---------|------|-------------|
| `idMemoryProfile` | INT PK | — |
| `idUsuario` | INT FK UNIQUE | — |
| `preferencias` | NVARCHAR(MAX) | JSON: `{"alias": "Ángel", "idioma": "español"}` |
| `resumenContextoLaboral` | NVARCHAR(MAX) | Resumen del contexto laboral |
| `resumenTemasRecientes` | NVARCHAR(MAX) | Resumen de temas recurrentes |
| `resumenHistorialBreve` | NVARCHAR(MAX) | Estadísticas de uso |
| `numInteracciones` | INT | Contador total de interacciones |
| `ultimaActualizacion` | DATETIME2 | — |
| `fechaCreacion` | DATETIME2 | — |
| `version` | INT | Para control de concurrencia |

### BotIAv2_InteractionLogs — registro de interacciones

| Columna | Tipo | Descripción |
|---------|------|-------------|
| `idInteraction` | BIGINT PK | — |
| `correlationId` | UNIQUEIDENTIFIER | UUID de la interacción |
| `userId` | VARCHAR(50) | Telegram chat_id o numero_empleado |
| `canal` | VARCHAR(20) | `telegram`, `api` |
| `mensajeUsuario` | NVARCHAR(MAX) | Consulta original |
| `respuestaBot` | NVARCHAR(MAX) | Respuesta enviada |
| `exitoso` | BIT | 1=sin errores |
| `duracionMs` | INT | Tiempo total de la respuesta |
| `pasosTomados` | INT | Iteraciones del loop ReAct |
| `error` | NVARCHAR(MAX) | Descripción del error si exitoso=0 |
| `fechaInteraccion` | DATETIME2 | — |
| `agenteNombre` | VARCHAR(100) NULL | Agente LLM que procesó la interacción (ARQ-35) |
| `totalInputTokens` | INT NULL | Tokens enviados al LLM en el request (OBS-36) |
| `totalOutputTokens` | INT NULL | Tokens recibidos del LLM en el request (OBS-36) |
| `llmIteraciones` | INT NULL | Cantidad de iteraciones del loop ReAct (OBS-36) |
| `usedFallback` | BIT DEFAULT 0 | 1=el orchestrator usó el agente generalista como fallback (OBS-36) |
| `classifyMs` | INT NULL | Latencia del IntentClassifier en ms (OBS-36) |
| `agentConfidence` | DECIMAL(5,4) NULL | Confianza del clasificador, rango 0.0–1.0 (OBS-36) |
| `costUSD` | DECIMAL(10,6) NULL | Costo total del request en USD (OBS-36) |

### BotIAv2_InteractionSteps — pasos del loop ReAct

| Columna | Tipo | Descripción |
|---------|------|-------------|
| `idStep` | BIGINT PK | — |
| `correlationId` | UNIQUEIDENTIFIER FK | Enlaza con InteractionLogs |
| `stepNumber` | INT | Orden del paso (1, 2, ...) |
| `stepType` | VARCHAR(50) | `llm_call`, `tool_call:database_query`, etc. |
| `duracionMs` | INT | Duración de este paso |
| `exitoso` | BIT | — |
| `metadata` | NVARCHAR(MAX) | JSON con detalles del paso |
| `timestamp` | DATETIME2 | — |

### BotIAv2_ApplicationLogs — logs de la aplicación

| Columna | Tipo | Descripción |
|---------|------|-------------|
| `idLog` | BIGINT PK | — |
| `nivel` | VARCHAR(20) | `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL` |
| `mensaje` | NVARCHAR(MAX) | — |
| `modulo` | VARCHAR(200) | Módulo Python que generó el log |
| `excepcion` | NVARCHAR(MAX) | Stack trace si hay excepción |
| `correlationId` | VARCHAR(50) | UUID de la interacción (si aplica) |
| `timestamp` | DATETIME2 | — |

### BotIAv2_CostSesiones — costos de uso del LLM

| Columna | Tipo | Descripción |
|---------|------|-------------|
| `idCosto` | BIGINT PK | — |
| `correlationId` | VARCHAR(50) | Enlaza con InteractionLogs |
| `userId` | VARCHAR(50) | — |
| `llamadasLLM` | INT | Número de llamadas al LLM en esta sesión |
| `tokensPrompt` | INT | Tokens enviados |
| `tokensCompletion` | INT | Tokens recibidos |
| `costoUSD` | DECIMAL(10,6) | Costo calculado en dólares |
| `modelo` | VARCHAR(100) | Modelo LLM usado |
| `fechaCreacion` | DATETIME2 | — |

---

## Tablas de orquestación multi-agente (ARQ-35 / OBS-36)

### BotIAv2_AgenteDef — definición de agentes LLM

Catálogo de agentes disponibles. El orchestrator carga esta tabla al iniciar para construir los agentes dinámicamente.

| Columna | Tipo | Descripción |
|---------|------|-------------|
| `idAgente` | INT PK | — |
| `nombre` | VARCHAR(100) UNIQUE | Identificador del agente: `datos`, `conocimiento`, `casual`, `generalista` |
| `descripcion` | VARCHAR(500) | Texto usado por el IntentClassifier para rutear |
| `systemPrompt` | NVARCHAR(MAX) | System prompt; debe contener `{tools_description}` y `{usage_hints}` |
| `temperatura` | DECIMAL(3,2) | Temperatura del LLM; default 0.1 |
| `maxIteraciones` | INT | Máximo de iteraciones del loop ReAct; default 10 |
| `modeloOverride` | VARCHAR(100) NULL | NULL = usa `openai_loop_model` del sistema |
| `esGeneralista` | BIT | 1 = ignora `tool_scope`, usa permisos directos del usuario |
| `activo` | BIT | 1 = habilitado |
| `version` | INT | Auto-incrementado por trigger al cambiar `systemPrompt` |
| `fechaActualizacion` | DATETIME2 | — |

### BotIAv2_AgenteTools — tools en el scope de cada agente

Asociación entre agentes y las tools que pueden usar. Los agentes con `esGeneralista=1` no tienen filas aquí.

| Columna | Tipo | Descripción |
|---------|------|-------------|
| `idAgenteTools` | INT PK | — |
| `idAgente` | INT FK → AgenteDef | — |
| `nombreTool` | VARCHAR(100) | Nombre de la tool: `database_query`, `knowledge_search`, etc. |
| `activo` | BIT | 1 = tool habilitada para este agente |

### BotIAv2_AgentePromptHistorial — auditoría de cambios de prompt

Tabla append-only. El trigger `TR_AgenteDef_VersionHistorial` inserta automáticamente la versión anterior cada vez que se modifica `systemPrompt` en `AgenteDef`.

| Columna | Tipo | Descripción |
|---------|------|-------------|
| `idHistorial` | INT PK | — |
| `idAgente` | INT FK → AgenteDef | — |
| `systemPrompt` | NVARCHAR(MAX) | Texto del prompt anterior al cambio |
| `version` | INT | Número de versión del prompt guardado |
| `razonCambio` | VARCHAR(500) | Descripción del motivo del cambio |
| `modificadoPor` | VARCHAR(100) | Usuario de BD que realizó el UPDATE (`SYSTEM_USER`) |
| `fechaCreacion` | DATETIME2 | — |

### BotIAv2_TicketAnalysisCache — caché de análisis LLM de tickets

Evita llamadas redundantes al LLM cuando los datos de tickets no han cambiado.
La clave de caché es la combinación `(ip, sensor, total_tickets, ultima_accion)`.

| Columna | Tipo | Descripción |
|---------|------|-------------|
| `ip` | VARCHAR(50) | IP del equipo en PRTG |
| `sensor` | VARCHAR(500) | Nombre del sensor |
| `total_tickets` | INT | Cantidad total de tickets históricos |
| `ultima_accion` | VARCHAR(500) | `accionCorrectiva` del ticket más reciente (truncado a 500 chars) |
| `analisis` | NVARCHAR(MAX) | Texto del análisis generado por el LLM |
| `fechaCreacion` | DATETIME | Fecha de creación o última actualización |

**Estrategia de invalidación**: si cambia `total_tickets` o `ultima_accion`, hay un cache miss
y se genera un nuevo análisis LLM. El upsert usa `MERGE` — si la clave ya existe, solo actualiza
`analisis` y `fechaCreacion`. Repositorio: `TicketAnalysisCacheRepository` en
`src/domain/alerts/ticket_cache_repository.py`.

---

### BotIAv2_AgentRouting — auditoría de decisiones de ruteo

Una fila por request. Registra qué agente eligió el orchestrator y con qué confianza.

| Columna | Tipo | Descripción |
|---------|------|-------------|
| `idRouting` | INT PK | — |
| `correlationId` | VARCHAR(50) | Correlación con `InteractionLogs` |
| `query` | NVARCHAR(1000) NULL | Texto de la consulta (truncado) |
| `agenteSeleccionado` | VARCHAR(100) | Nombre del agente elegido |
| `confianza` | DECIMAL(5,4) NULL | Score 0.0–1.0; NULL si no disponible |
| `alternativas` | NVARCHAR(500) NULL | JSON: `[{"agente":"x","score":0.3}]` |
| `classifyMs` | INT | Latencia del clasificador en ms |
| `usedFallback` | BIT DEFAULT 0 | 1 = se usó el agente generalista como fallback |
| `fechaCreacion` | DATETIME2 | — |

---

## Tablas del sistema de permisos (SEC-01)

### BotIAv2_TipoEntidad — tipos de entidad para permisos

| nombre | prioridad | tipoResolucion |
|--------|-----------|----------------|
| `usuario` | 1 | definitivo — override individual, pisa todo |
| `autenticado` | 2 | permisivo — cualquier usuario autenticado |
| `gerencia` | 3 | permisivo — por gerencia del usuario |
| `direccion` | 4 | permisivo — por dirección del usuario |

### BotIAv2_Recurso — catálogo de recursos controlables

| Columna | Tipo | Descripción |
|---------|------|-------------|
| `idRecurso` | INT PK | — |
| `recurso` | VARCHAR(100) UNIQUE | `tool:database_query`, `cmd:/ia`, etc. |
| `tipoRecurso` | VARCHAR(20) | `tool`, `cmd` |
| `descripcion` | VARCHAR(500) | — |
| `esPublico` | BIT | 1=acceso universal sin verificar |

### BotIAv2_Permisos — reglas de acceso

| Columna | Tipo | Descripción |
|---------|------|-------------|
| `idPermiso` | INT PK | — |
| `idTipoEntidad` | INT FK | Tipo de entidad (usuario/autenticado/etc.) |
| `idEntidad` | INT | ID del usuario/gerencia (0 para autenticado) |
| `idRecurso` | INT FK | Recurso controlado |
| `idRolRequerido` | INT NULL | NULL=cualquier rol, valor=rol específico |
| `permitido` | BIT | 1=permitido, 0=denegado |
| `fechaExpiracion` | DATETIME2 NULL | NULL=permanente |

---

## Tablas del sistema legacy

El bot consulta estas tablas en modo solo lectura:

| Tabla | Descripción |
|-------|-------------|
| `Usuarios` | Empleados de la empresa |
| `Roles` | Roles del sistema |
| `knowledge_categories` | Categorías de la base de conocimiento |
| `knowledge_entries` | Artículos de la base de conocimiento |
| `LogOperaciones` | Log heredado de operaciones |

---

## Stored procedures

### sp_search_knowledge

Búsqueda en la base de conocimiento con filtros opcionales:

```sql
EXEC sp_search_knowledge
    @query = 'política devoluciones',
    @category = NULL,        -- o 'POLITICAS'
    @top_k = 3,
    @min_priority = 1
```

### BotIAv2_sp_GetAllUsuariosTelegram

Lista todos los usuarios Telegram activos con su rol. Usado por el panel admin (`GET /api/admin/users`).

```sql
EXEC abcmasplus..BotIAv2_sp_GetAllUsuariosTelegram
```

Retorna: `idUsuario`, `Nombre`, `idRol`, `rolNombre`, `telegramChatId`, `telegramUsername`, `estado`, `verificado`, `fechaUltimaActividad`.

---

## Migraciones

### `database/migrations/` — migraciones por feature

| Script | Descripción |
|--------|-------------|
| `09_PreMigracionCheck.sql` | Verificaciones pre-migración |
| `10_BotPermisos.sql` | Crea BotIAv2_TipoEntidad, BotIAv2_Recurso, BotIAv2_Permisos |
| `11_BotPermisos_DatosIniciales.sql` | Datos iniciales de permisos por rol |
| `20_DropLegacyPermisosSPs.sql` | Elimina stored procedures legacy |
| `21_DropLegacyPermisosTablas.sql` | Elimina tablas legacy de permisos |
| `arq35_dynamic_orchestrator.sql` | ARQ-35: crea AgenteDef, AgenteTools, AgentePromptHistorial; agrega columna `agenteNombre` a InteractionLogs; trigger de versionado; 4 agentes iniciales |
| `arq35_trigger_fix.sql` | ARQ-35: versión corregida del trigger `TR_AgenteDef_VersionHistorial` (sin prefijo de BD para compatibilidad con SQL Server) |
| `obs36_multiagent_observability.sql` | OBS-36: agrega columnas de observabilidad a InteractionLogs (`totalInputTokens`, `totalOutputTokens`, `llmIteraciones`, `usedFallback`, `classifyMs`, `agentConfidence`, `costUSD`); crea BotIAv2_AgentRouting |
| `obs36_sp_ultima_interaccion.sql` | OBS-36: actualiza `BotIAv2_sp_UltimaInteraccion` para incluir datos de AgentRouting y columnas OBS-36 |

### `scripts/migrations/` — migraciones numeradas

| Script | Descripción |
|--------|-------------|
| `001_add_application_logs.sql` | Crea BotIAv2_ApplicationLogs |
| `002_add_transaction_logs.sql` | Crea BotIAv2_InteractionSteps |
| `003_sec01_cmd_costo.sql` | Registra `cmd:/costo` en SEC-01 (reemplaza admin_chat_ids hardcodeados) |
| `004_sec01_tool_read_attachment.sql` | Registra `tool:read_attachment` en SEC-01 |
| `005_tool_catalog_in_recurso.sql` | Registra todas las tools del catálogo en BotIAv2_Recurso |
| `006_auth_stored_procedures.sql` | Stored procedures de autenticación (BotIAv2_sp_*) |
| `007_auth_sp_extended.sql` | SPs extendidos de auth: memoria, preferencias, costos, observabilidad |
| `008_feat36_alert_analysis_tool.sql` | FEAT-36: tool de análisis de alertas PRTG |
| `009_fix_alertas_system_prompt.sql` | Corrige el system prompt del agente `alertas` |
| `010_feat37_alert_tools_refactor.sql` | FEAT-37: refactor de alert tools (4 tools estructuradas) |
| `016_sp_get_all_usuarios_telegram.sql` | Crea `BotIAv2_sp_GetAllUsuariosTelegram` — lista todos los usuarios Telegram activos con rol (usado por panel admin) |
| `017_fix_alertas_prompt_cleanup.sql` | Limpia el system prompt del agente alertas |
| `018_template_search_by_name_tool.sql` | Agrega SP `BotIAv2_sp_SearchTemplatesByNombre` y registra `tool:template_search_by_name` en SEC-01 |
| `019_fix_alertas_template_search_format.sql` | Ajusta formato de resultados de template search |
| `020_fix_alertas_seleccion_template.sql` | Corrige lógica de selección de template en agente alertas |
| `021_fix_alertas_no_pedir_ip_con_template.sql` | Evita pedir IP cuando ya hay template seleccionado |
| `022_fix_alertas_template_search_truncado.sql` | Maneja resultados truncados en template search |
| `023_fix_alertas_present_templates.sql` | Mejora presentación de templates encontrados |
| `024_pass_id_gerencia_en_escalamiento.sql` | Pasa `id_gerencia_atendedora` en escalamiento para evitar llamada redundante a `get_template_info` |
| `025_ticket_analysis_cache.sql` | Crea tabla `BotIAv2_TicketAnalysisCache` para caché de análisis LLM de tickets |

---

**← Anterior** [Infraestructura](infraestructura.md) · [Índice](README.md) · **Siguiente →** [Cómo extender](como-extender.md)
