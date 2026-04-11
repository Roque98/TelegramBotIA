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

---

## Migraciones

Los scripts están en `database/migrations/` y deben ejecutarse en orden numérico:

| Script | Descripción |
|--------|-------------|
| `09_PreMigracionCheck.sql` | Verificaciones pre-migración |
| `10_BotPermisos.sql` | Crea BotIAv2_TipoEntidad, BotIAv2_Recurso, BotIAv2_Permisos |
| `11_BotPermisos_DatosIniciales.sql` | Datos iniciales de permisos por rol |
| `20_DropLegacyPermisosSPs.sql` | Elimina stored procedures legacy |
| `21_DropLegacyPermisosTablas.sql` | Elimina tablas legacy de permisos |

---

**← Anterior** [Infraestructura](infraestructura.md) · [Índice](README.md) · **Siguiente →** [Cómo extender](como-extender.md)
