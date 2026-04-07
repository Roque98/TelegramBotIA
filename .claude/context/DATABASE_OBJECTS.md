# Inventario de Objetos de Base de Datos

**Base de datos**: `abcmasplus`
**Motor**: SQL Server
**ORM**: SQLAlchemy 2.0 (sólo como driver — los modelos de dominio son dataclasses Python)
**Última actualización**: 2026-04-07

---

## 1. TABLAS (30 total)

### Usuarios y Autenticación

| Tabla | PK | Columnas relevantes | FK | Archivo |
|---|---|---|---|---|
| **Usuarios** | idUsuario (IDENTITY) | idEmpleado (UNIQUE), nombre, apellido, rol, email (UNIQUE), fechaCreacion, fechaUltimoAcceso, activo | rol → Roles.idRol | `01_EstructuraUsuarios.sql` |
| **Roles** | idRol (IDENTITY) | nombre (UNIQUE), fechaCreacion, activo | — | `01_EstructuraUsuarios.sql` |
| **Gerencias** | idGerencia (IDENTITY) | idResponsable (FK), gerencia, alias (UNIQUE), correo, fechaCreacion, activo | idResponsable → Usuarios.idUsuario | `01_EstructuraUsuarios.sql` |
| **Direcciones** | idDireccion (IDENTITY) | nombre, activo | — | `10_BotPermisos.sql` |
| **UsuariosTelegram** | idUsuarioTelegram (IDENTITY) | idUsuario (FK, UNIQUE), telegramChatId (UNIQUE), telegramUsername, telegramFirstName, telegramLastName, alias, esPrincipal, estado (CHECK), fechaRegistro, fechaUltimaActividad, verificado, codigoVerificacion, intentosVerificacion, notificacionesActivas, observaciones, activo, usuarioCreacion, usuarioModificacion | idUsuario → Usuarios | `03_EstructuraVerificacion.sql` |
| **UserMemoryProfiles** | idMemoryProfile (IDENTITY) | idUsuario (FK, UNIQUE), resumenContextoLaboral, resumenTemasRecientes, resumenHistorialBreve, numInteracciones, ultimaActualizacion, fechaCreacion, version | idUsuario → Usuarios | `002_create_user_memory_profiles.sql` |

**Constraints** en UsuariosTelegram:
- `CHECK estado IN ('ACTIVO', 'SUSPENDIDO', 'BLOQUEADO')`

---

### Relaciones Usuario ↔ Grupos

| Tabla | PK | Columnas relevantes | FK | Archivo |
|---|---|---|---|---|
| **GerenciaUsuarios** | idGerenciaUsuario (IDENTITY) | idUsuario, idGerencia, fechaAsignacion, activo | UNIQUE(idUsuario, idGerencia) | `01_EstructuraUsuarios.sql` |
| **AreaAtendedora** | idAreaAtendedora (IDENTITY) | idGerencia (FK, UNIQUE), fechaCreacion, activo | idGerencia → Gerencias | `01_EstructuraUsuarios.sql` |

---

### Roles IA — LEGACY (pendiente de drop)

| Tabla | Estado | Archivo |
|---|---|---|
| **RolesIA** | legacy — drop en fase 6 | `01_EstructuraUsuarios.sql` |
| **UsuariosRolesIA** | legacy — drop | `01_EstructuraUsuarios.sql` |
| **GerenciasRolesIA** | legacy — drop | `01_EstructuraUsuarios.sql` |

---

### Permisos y Operaciones — LEGACY (pendiente de drop)

| Tabla | PK | Columnas relevantes | FK | Archivo |
|---|---|---|---|---|
| **Modulos** | idModulo (IDENTITY) | nombre (UNIQUE), descripcion, icono, orden, activo | — | `02_EstructuraPermisos.sql` |
| **Operaciones** | idOperacion (IDENTITY) | idModulo (FK), nombre, descripcion, comando (UNIQUE), requiereParametros, parametrosEjemplo, nivelCriticidad, orden, activo | idModulo → Modulos | `02_EstructuraPermisos.sql` |
| **RolesOperaciones** | idRolOperacion (IDENTITY) | idRol, idOperacion, permitido, fechaAsignacion, usuarioAsignacion, activo | UNIQUE(idRol, idOperacion) — **drop pendiente** | `02_EstructuraPermisos.sql` |
| **UsuariosOperaciones** | idUsuarioOperacion (IDENTITY) | idUsuario, idOperacion, permitido, fechaAsignacion, fechaExpiracion, activo | UNIQUE(idUsuario, idOperacion) — **drop pendiente** | `02_EstructuraPermisos.sql` |
| **LogOperaciones** | idLog (BIGINT, IDENTITY) | idUsuario, idOperacion, telegramChatId, telegramUsername, parametros (JSON), resultado, mensajeError, duracionMs, ipOrigen, fechaEjecucion | idUsuario → Usuarios, idOperacion → Operaciones | `02_EstructuraPermisos.sql` |

---

### Sistema de Permisos SEC-01 (activo)

| Tabla | PK | Columnas relevantes | FK / Constraints | Archivo |
|---|---|---|---|---|
| **BotTipoEntidad** | idTipoEntidad (IDENTITY) | nombre (UNIQUE), prioridad (TINYINT, UNIQUE), tipoResolucion (CHECK), descripcion, activo | CHECK tipoResolucion IN ('definitivo','permisivo') | `10_BotPermisos.sql` |
| **BotRecurso** | idRecurso (IDENTITY) | recurso (UNIQUE), tipoRecurso (CHECK), esPublico, descripcion, activo | CHECK tipoRecurso IN ('tool','cmd') | `10_BotPermisos.sql` |
| **BotPermisos** | idPermiso (IDENTITY) | idTipoEntidad, idEntidad (0 = autenticado), idRecurso, idRolRequerido (nullable), permitido, fechaExpiracion, activo, descripcion, usuarioCreacion, usuarioModificacion | FK: idTipoEntidad, idRecurso, idRolRequerido → Roles | `10_BotPermisos.sql` |
| **BotPermisosAudit** | idAudit (BIGINT, IDENTITY) | idPermiso, accion (CHECK), valorAnterior (JSON), valorNuevo (JSON), usuario, fechaAccion, ip | CHECK accion IN ('INSERT','UPDATE','DELETE') | `12_BotPermisos_Audit.sql` |

---

### Base de Conocimiento

| Tabla | PK | Columnas relevantes | FK / Constraints | Archivo |
|---|---|---|---|---|
| **knowledge_categories** | id (IDENTITY) | name (UNIQUE, VARCHAR 50), display_name, description, icon (emoji), active | — | `001_create_knowledge_base_tables.sql` |
| **knowledge_entries** | id (IDENTITY) | category_id (FK), question, answer, keywords (JSON), related_commands (JSON), priority (CHECK 1-3), active, created_by | FK: category_id → knowledge_categories; CHECK priority BETWEEN 1 AND 3 | `001_create_knowledge_base_tables.sql` |
| **table_documentation** | id (IDENTITY) | schema_name (DEFAULT 'dbo'), table_name, display_name, description, usage_examples (JSON), common_queries (JSON), category, active | UNIQUE(schema_name, table_name) | `001_create_knowledge_base_tables.sql` |
| **column_documentation** | id (IDENTITY) | table_doc_id (FK, CASCADE), column_name, display_name, description, data_type, example_value, icon, is_key | FK: table_doc_id → table_documentation (CASCADE); UNIQUE(table_doc_id, column_name) | `001_create_knowledge_base_tables.sql` |

---

### Logging de Aplicación

| Tabla | PK | Columnas relevantes | Archivo |
|---|---|---|---|
| **ApplicationLogs** | id (BIGINT, IDENTITY) | correlationId (NVARCHAR 8), userId, level (WARNING/ERROR), event, message, module, durationMs, extra (JSON), createdAt (DEFAULT GETDATE()) | `scripts/migrations/001_add_application_logs.sql` |

---

## 2. VISTAS (2)

| Vista | Tablas origen | Archivo |
|---|---|---|
| **vw_knowledge_base** | knowledge_entries, knowledge_categories | `001_create_knowledge_base_tables.sql` |
| *(vistas del sistema legacy chatbot)* | ChatConversaciones, BibliotecaPrompts | `ChatBot_mysql.sql` |

---

## 3. STORED PROCEDURES (4)

| Nombre | Parámetros de entrada | Retorna | Estado | Archivo |
|---|---|---|---|---|
| **sp_search_knowledge** | @query NVARCHAR(500), @category VARCHAR(50), @top_k INT, @min_priority INT | id, question, answer, keywords, related_commands, priority, category, score | **Activo** | `001_create_knowledge_base_tables.sql` |
| **sp_VerificarPermisoOperacion** | @idUsuario INT, @comando NVARCHAR(100) | TienePermiso (BIT), Mensaje, NombreOperacion, RequiereParametros | Legacy — drop pendiente | `04_StoredProcedures.sql` |
| **sp_ObtenerOperacionesUsuario** | @idUsuario INT | Modulo, IconoModulo, idOperacion, Operacion, OrigenPermiso, Permitido | Legacy — drop pendiente | `04_StoredProcedures.sql` |
| **sp_RegistrarLogOperacion** | @idUsuario, @comando, @telegramChatId, @telegramUsername, @parametros (JSON), @resultado, @mensajeError, @duracionMs, @ipOrigen | idLog (BIGINT) | Legacy — drop pendiente | `04_StoredProcedures.sql` |

---

## 4. FUNCIONES

Ninguna definida. Se usan Stored Procedures en su lugar.

---

## 5. TRIGGERS (1)

| Nombre | Tabla | Eventos | Acción | Archivo |
|---|---|---|---|---|
| **TR_BotPermisos_Audit** | BotPermisos | INSERT, UPDATE, DELETE | Inserta en BotPermisosAudit el estado anterior/nuevo en JSON + usuario que ejecutó | `12_BotPermisos_Audit.sql` |

---

## 6. ÍNDICES (35+)

### Tablas de Usuarios

| Índice | Tabla | Columnas | Tipo |
|---|---|---|---|
| IX_Usuarios_Email | Usuarios | email | NONCLUSTERED |
| IX_Usuarios_IdEmpleado | Usuarios | idEmpleado | NONCLUSTERED |
| IX_GerenciaUsuarios_IdUsuario | GerenciaUsuarios | idUsuario | NONCLUSTERED |
| IX_GerenciaUsuarios_IdGerencia | GerenciaUsuarios | idGerencia | NONCLUSTERED |
| IX_UsuariosRolesIA_IdRol | UsuariosRolesIA | idRol | NONCLUSTERED |
| IX_UsuariosRolesIA_IdUsuario | UsuariosRolesIA | idUsuario | NONCLUSTERED |
| IX_GerenciasRolesIA_IdRol | GerenciasRolesIA | idRol | NONCLUSTERED |
| IX_GerenciasRolesIA_IdGerencia | GerenciasRolesIA | idGerencia | NONCLUSTERED |
| IX_UsuariosTelegram_IdUsuario | UsuariosTelegram | idUsuario | NONCLUSTERED |
| IX_UsuariosTelegram_ChatId | UsuariosTelegram | telegramChatId | NONCLUSTERED |
| IX_UsuariosTelegram_Username | UsuariosTelegram | telegramUsername | NONCLUSTERED |
| IX_UsuariosTelegram_Estado | UsuariosTelegram | estado | NONCLUSTERED |
| IX_UserMemoryProfiles_Usuario | UserMemoryProfiles | idUsuario | NONCLUSTERED |
| IX_UserMemoryProfiles_UltimaActualizacion | UserMemoryProfiles | ultimaActualizacion DESC | NONCLUSTERED |

### Tablas de Permisos Legacy

| Índice | Tabla | Columnas | Tipo |
|---|---|---|---|
| IX_RolesOperaciones_IdRol | RolesOperaciones | idRol | NONCLUSTERED |
| IX_RolesOperaciones_IdOperacion | RolesOperaciones | idOperacion | NONCLUSTERED |
| IX_UsuariosOperaciones_IdUsuario | UsuariosOperaciones | idUsuario | NONCLUSTERED |
| IX_UsuariosOperaciones_IdOperacion | UsuariosOperaciones | idOperacion | NONCLUSTERED |
| IX_LogOperaciones_IdUsuario | LogOperaciones | idUsuario | NONCLUSTERED |
| IX_LogOperaciones_IdOperacion | LogOperaciones | idOperacion | NONCLUSTERED |
| IX_LogOperaciones_FechaEjecucion | LogOperaciones | fechaEjecucion DESC | NONCLUSTERED |
| IX_LogOperaciones_Resultado | LogOperaciones | resultado | NONCLUSTERED |
| IX_Operaciones_IdModulo | Operaciones | idModulo | NONCLUSTERED |
| IX_Operaciones_Comando | Operaciones | comando | NONCLUSTERED |

### BotPermisos (SEC-01)

| Índice | Tabla | Columnas | Tipo |
|---|---|---|---|
| UX_BotPermisos_ConRol | BotPermisos | (idTipoEntidad, idEntidad, idRecurso, idRolRequerido) WHERE idRolRequerido IS NOT NULL | UNIQUE NONCLUSTERED |
| UX_BotPermisos_SinRol | BotPermisos | (idTipoEntidad, idEntidad, idRecurso) WHERE idRolRequerido IS NULL | UNIQUE NONCLUSTERED |
| IX_BotPermisos_Lookup | BotPermisos | (idTipoEntidad, idEntidad, idRecurso) INCLUDE (idRolRequerido, permitido, activo, fechaExpiracion) | NONCLUSTERED |
| IX_BotPermisosAudit_Permiso | BotPermisosAudit | (idPermiso, fechaAccion DESC) | NONCLUSTERED |

### Knowledge Base

| Índice | Tabla | Columnas | Tipo |
|---|---|---|---|
| idx_knowledge_categories_active | knowledge_categories | active | NONCLUSTERED |
| idx_knowledge_entries_category | knowledge_entries | category_id | NONCLUSTERED |
| idx_knowledge_entries_priority | knowledge_entries | priority DESC | NONCLUSTERED |
| idx_knowledge_entries_active | knowledge_entries | active | NONCLUSTERED |
| idx_knowledge_entries_question | knowledge_entries | question | NONCLUSTERED |
| idx_table_documentation_active | table_documentation | active | NONCLUSTERED |
| idx_column_documentation_table | column_documentation | table_doc_id | NONCLUSTERED |

### ApplicationLogs

| Índice | Tabla | Columnas | Tipo |
|---|---|---|---|
| IX_ApplicationLogs_level | ApplicationLogs | level | NONCLUSTERED |
| IX_ApplicationLogs_correlationId | ApplicationLogs | correlationId | NONCLUSTERED |
| IX_ApplicationLogs_createdAt | ApplicationLogs | createdAt DESC | NONCLUSTERED |

---

## 7. SECUENCIAS

Ninguna. Todas las PKs usan `IDENTITY(1,1)`.

---

## 8. ENTIDADES DE DOMINIO PYTHON (no ORM)

Archivos en `src/domain/`:

| Clase | Archivo | Descripción |
|---|---|---|
| `TelegramUser` | `user_entity.py` | Datos del usuario de Telegram |
| `PermissionResult` | `user_entity.py` | Resultado de verificación de permiso |
| `Operation` | `user_entity.py` | Operación del sistema legacy |
| `UserProfile` | `memory_entity.py` | Perfil de memoria de usuario |
| `Interaction` | `memory_entity.py` | Interacción almacenada |
| `CacheEntry` | `memory_entity.py` | Entrada de caché LRU |
| `KnowledgeCategory` | `knowledge_entity.py` | Enum de categorías |
| `KnowledgeEntry` | `knowledge_entity.py` | Entrada de base de conocimiento |

---

## 9. ARCHIVOS DE MIGRACIÓN

```
database/migrations/
├── 00_ResumenEstructura.sql              — Documentación del esquema
├── 01_EstructuraUsuarios.sql             — Tablas: Usuarios, Roles, Gerencias, GerenciaUsuarios, etc.
├── 02_EstructuraPermisos.sql             — Tablas: Modulos, Operaciones, RolesOperaciones, LogOperaciones
├── 03_EstructuraVerificacion.sql         — Tabla: UsuariosTelegram
├── 04_StoredProcedures.sql               — 3 SPs legacy
├── 001_create_knowledge_base_tables.sql  — 4 tablas + vista + SP knowledge base
├── 002_create_user_memory_profiles.sql   — Tabla: UserMemoryProfiles
├── 002_seed_knowledge_base.sql           — Datos iniciales knowledge base
├── 09_PreMigracionCheck.sql              — Verificación pre-migración
├── 10_BotPermisos.sql                    — Tablas SEC-01: BotTipoEntidad, BotRecurso, BotPermisos
├── 11_BotPermisos_DatosIniciales.sql     — Datos iniciales SEC-01
├── 12_BotPermisos_Audit.sql              — Trigger: TR_BotPermisos_Audit
├── 20_DropLegacyPermisosSPs.sql          — Drop SPs legacy (pendiente)
└── 21_DropLegacyPermisosTablas.sql       — Drop tablas legacy (pendiente)

scripts/migrations/
├── 001_add_application_logs.sql          — Tabla: ApplicationLogs
├── 002_add_transaction_logs.sql          — Logging adicional
├── 003_sec01_cmd_costo.sql               — Registro recurso cmd:/costo en SEC-01
└── 004_sec01_tool_read_attachment.sql    — Registro recurso tool:read_attachment en SEC-01
```

---

## 10. RESUMEN

| Tipo | Cantidad | Notas |
|---|---|---|
| Tablas activas | ~22 | Sin contar las legacy |
| Tablas legacy (drop pendiente) | 8 | RolesIA, UsuariosRolesIA, GerenciasRolesIA, RolesOperaciones, UsuariosOperaciones + SPs |
| Vistas | 2+ | |
| Stored Procedures | 4 (3 legacy) | |
| Funciones | 0 | |
| Triggers | 1 | TR_BotPermisos_Audit |
| Índices | 35+ | |
| Secuencias | 0 | Se usa IDENTITY |
| Foreign Keys | 35+ | |
| Unique Constraints | 25+ | |
