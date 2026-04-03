# Plan: SEC-01 — Rediseño Completo del Sistema de Permisos

> **Estado**: ⚪ No iniciado
> **Última actualización**: 2026-04-01
> **Rama Git**: `feature/sec-01-permisos`

## Resumen de Progreso

| Fase | Progreso | Estado |
|------|----------|--------|
| Fase 1: Nuevo Esquema BD | ██████████ 100% | ✅ Completada |
| Fase 2: Capa de Dominio | ░░░░░░░░░░ 0% | ⏳ Pendiente |
| Fase 3: UserContext con Roles y Gerencias | ░░░░░░░░░░ 0% | ⏳ Pendiente |
| Fase 4: Permisos en Tools del Agente | ░░░░░░░░░░ 0% | ⏳ Pendiente |
| Fase 5: Migrar Middleware y Handlers | ░░░░░░░░░░ 0% | ⏳ Pendiente |
| Fase 6: Tests y Cleanup | ░░░░░░░░░░ 0% | ⏳ Pendiente |

**Progreso Total**: ██░░░░░░░░ 11% (5/46 tareas)

---

## Contexto: Problemas del Sistema Legacy

### Críticos (bugs reales)
- **Explicit deny no funciona**: `sp_VerificarPermisoOperacion` tiene bug — si el rol permite pero el usuario tiene deny, el rol gana. Debería ser al revés.
- **Sistema de roles duplicado**: Existen `Roles` y `RolesIA` desconectados. `sp_VerificarPermisoOperacion` solo consulta `Roles`, ignorando `RolesIA` completamente.
- **Defaults inseguros**: `TelegramUser` defaultea `activo=1` y `estado='ACTIVO'` cuando el valor de BD es NULL → usuario nulo queda activo.
- **UserContext.roles siempre vacío**: El campo existe pero ningún código lo popula. El agente nunca sabe el rol del usuario.

### Importantes
- **N+1 queries sin cache**: Cada check de permiso ejecuta 4-5 queries al SP sin ningún caching.
- **Lógica dispersa**: Checks de autenticación duplicados en middleware, handlers y service.
- **Magic strings hardcodeados**: `'/ia'`, `'ACTIVO'`, `'EXITOSO'`, `'DENEGADO'` en 5+ archivos.
- **God Repository**: `UserRepository` tiene 30+ métodos mezclando queries, mutaciones y lógica de negocio.
- **Gerencias no integradas**: El modelo organizacional (Gerencias, Direcciones) existe en BD pero no se usa para permisos.

### Deuda técnica
- Stored procedures difíciles de testear
- Sin audit trail para cambios de permisos
- Convención de nombres inconsistente (camelCase en BD, snake_case en Python, mezclados)
- `RolesIA` y `GerenciasRolesIA` son un sistema paralelo nunca integrado al flujo principal

---

## Decisiones de Diseño

### Lo que se CONSERVA
- Concepto RBAC con overrides por usuario ✅
- Soft-delete (`activo = 0`) en todas las tablas ✅
- `LogOperaciones` como audit trail de ejecuciones ✅
- Agrupación de operaciones por módulo ✅
- Soporte multi-cuenta Telegram por usuario ✅

### Lo que se REESCRIBE
- Sistema de roles unificado (eliminar `RolesIA` separado)
- Lógica de permisos en Python con cache (eliminar SPs del flujo principal)
- Jerarquía de resolución: usuario > autenticado > gerencia > dirección (recursos públicos via `esPublico` en `BotRecurso`)
- Catálogos de entidades y recursos administrables desde BD
- Capa de dominio con responsabilidades separadas

### Lo que se AGREGA
- Soporte de Gerencias y Direcciones en permisos
- `tipoResolucion` por tipo de entidad (definitivo vs permisivo)
- Audit trail para cambios de permisos (`PermisosAudit`)
- Tools del agente como recursos controlables desde BD

---

## Nuevo Esquema de BD

### Catálogo de tipos de entidad

```sql
BotTipoEntidad
  idTipoEntidad    INT IDENTITY PK
  nombre           VARCHAR(50) UNIQUE NOT NULL   -- 'usuario', 'autenticado', 'gerencia', 'direccion'
  prioridad        TINYINT UNIQUE NOT NULL        -- 1=más alta, mayor número=menor prioridad
  tipoResolucion   VARCHAR(20) NOT NULL           -- 'definitivo' | 'permisivo'
  descripcion      VARCHAR(255) NULL
  activo           BIT DEFAULT 1
  fechaCreacion    DATETIME DEFAULT GETDATE()
```

Datos iniciales:
| nombre | prioridad | tipoResolucion | descripcion |
|--------|-----------|----------------|-------------|
| usuario | 1 | definitivo | Override individual, pisa todo |
| autenticado | 2 | permisivo | Cualquier usuario autenticado, filtrable por rol via idRolRequerido |
| gerencia | 3 | permisivo | Gerencia(s) del usuario, filtrable por rol via idRolRequerido |
| direccion | 4 | permisivo | Dirección del usuario, filtrable por rol via idRolRequerido |

> **Nota**: No existe entidad `publico`. Los recursos públicos se marcan con `esPublico=1` en `BotRecurso` y se cortocircuitan antes de consultar permisos.

> **Regla de resolución**: Si `tipoResolucion='definitivo'` y existe una entrada → es la respuesta final.
> Si `tipoResolucion='permisivo'` → si ALGUNA entrada permite, se permite (más permisivo gana).
> `idRolRequerido`: aplica a `autenticado`, `gerencia` y `direccion`. No aplica a `usuario`.

---

### Catálogo de recursos

```sql
BotRecurso
  idRecurso        INT IDENTITY PK
  recurso          VARCHAR(100) UNIQUE NOT NULL   -- 'tool:database_query', 'cmd:/ia'
  tipoRecurso      VARCHAR(20) NOT NULL           -- 'tool' | 'cmd'
  esPublico        BIT DEFAULT 0                  -- shortcut: skip check si true
  descripcion      VARCHAR(255) NULL
  activo           BIT DEFAULT 1
  fechaCreacion    DATETIME DEFAULT GETDATE()
```

Recursos iniciales (tools del agente):
| recurso | tipoRecurso | descripcion |
|---------|-------------|-------------|
| tool:database_query | tool | Consultas SQL a la BD |
| tool:calculate | tool | Cálculos matemáticos |
| tool:knowledge_search | tool | Búsqueda en base de conocimiento |
| tool:save_preference | tool | Guardar preferencias del usuario |
| tool:save_memory | tool | Guardar notas de sesión |
| tool:datetime | tool | Consultar fecha y hora |
| cmd:/ia | cmd | Comando principal del agente |
| cmd:/start | cmd | Inicio del bot (público) — `esPublico=1` |
| cmd:/help | cmd | Ayuda (público) — `esPublico=1` |
| cmd:/costo | cmd | Ver costos |
| cmd:/recargar_permisos | cmd | Recargar permisos del usuario — `esPublico=1` |
| tool:reload_permissions | tool | Tool del agente para recargar permisos — `esPublico=1` |

---

### Tabla principal de permisos

```sql
BotPermisos
  idPermiso            INT IDENTITY PK
  idTipoEntidad        INT NOT NULL FK → BotTipoEntidad
  idEntidad            INT NOT NULL               -- ID del usuario/gerencia/direccion según tipo. 0 para autenticado
  idRecurso            INT NOT NULL FK → BotRecurso
  idRolRequerido       INT NULL FK → Roles        -- NULL=cualquier rol. Aplica a autenticado/gerencia/direccion
  permitido            BIT NOT NULL DEFAULT 1
  fechaExpiracion      DATETIME NULL              -- NULL = permanente
  activo               BIT DEFAULT 1
  descripcion          VARCHAR(255) NULL
  fechaCreacion        DATETIME DEFAULT GETDATE()
  usuarioCreacion      VARCHAR(100) NULL
  fechaModificacion    DATETIME NULL
  usuarioModificacion  VARCHAR(100) NULL

  -- idRolRequerido es nullable: no usar UNIQUE directo (NULL != NULL en SQL Server)
  -- En su lugar, índice único filtrado para filas con rol + índice único filtrado para NULL
  INDEX UX_BotPermisos_conRol    (idTipoEntidad, idEntidad, idRecurso, idRolRequerido)
    WHERE idRolRequerido IS NOT NULL
  INDEX UX_BotPermisos_sinRol    (idTipoEntidad, idEntidad, idRecurso)
    WHERE idRolRequerido IS NULL
  INDEX IX_BotPermisos_lookup    (idTipoEntidad, idEntidad, idRecurso)
```

---

### Audit trail de cambios de permisos

```sql
BotPermisosAudit
  idAudit              BIGINT IDENTITY PK
  idPermiso            INT NOT NULL               -- FK a BotPermisos (sin CASCADE)
  accion               VARCHAR(20) NOT NULL       -- 'INSERT' | 'UPDATE' | 'DELETE'
  valorAnterior        NVARCHAR(MAX) NULL         -- JSON del estado anterior
  valorNuevo           NVARCHAR(MAX) NULL         -- JSON del estado nuevo
  usuario              VARCHAR(100) NOT NULL
  fechaAccion          DATETIME DEFAULT GETDATE()
  ip                   VARCHAR(50) NULL
```

> Poblado via trigger en `BotPermisos` para capturar cualquier cambio, incluyendo los hechos directamente en BD.

---

## Jerarquía de Resolución

```
Request: usuario X quiere ejecutar recurso Y

1. ¿esPublico=1 en BotRecurso? → PERMITIDO inmediatamente (sin consultar BotPermisos)

2. Cargar todas las filas de BotPermisos donde:
   - (tipoEntidad='usuario'      AND idEntidad = idUsuario)
   - (tipoEntidad='autenticado'  AND (idRolRequerido IS NULL OR idRolRequerido = idRol))
   - (tipoEntidad='gerencia'     AND idEntidad IN gerencias del usuario
                                 AND (idRolRequerido IS NULL OR idRolRequerido = idRol))
   - (tipoEntidad='direccion'    AND idEntidad IN direcciones del usuario
                                 AND (idRolRequerido IS NULL OR idRolRequerido = idRol))
   - idRecurso = Y
   - activo = 1
   - fechaExpiracion IS NULL OR fechaExpiracion > NOW()

3. Aplicar resolución por tipoResolucion:
   a. Buscar entradas 'definitivo' (usuario) → si existe, es la respuesta final
   b. Entre entradas 'permisivo' → si ALGUNA tiene permitido=1, PERMITIDO
   c. Sin ninguna fila → DENEGADO (default deny)
```

---

## Permisos por Defecto (datos iniciales `BotPermisos`)

Usando `tipoEntidad='autenticado'` con `idRolRequerido` para cada rol:

| tipoEntidad | idRolRequerido | Recurso | Permitido |
|-------------|----------------|---------|-----------|
| autenticado | 1 (Administrador) | tool:* | ✅ todos |
| autenticado | 2 (Gerente) | tool:* | ✅ todos |
| autenticado | 3 (Supervisor) | tool:database_query, tool:calculate, tool:knowledge_search | ✅ |
| autenticado | 7 (Coordinador) | tool:database_query, tool:calculate, tool:knowledge_search | ✅ |
| autenticado | 8 (Especialista) | tool:database_query, tool:calculate, tool:knowledge_search | ✅ |
| autenticado | 4 (Analista) | tool:database_query, tool:calculate, tool:knowledge_search | ✅ |
| autenticado | 5 (Usuario) | tool:knowledge_search, tool:calculate | ✅ |
| autenticado | 6 (Consulta) | tool:knowledge_search | ✅ |
| autenticado | NULL (todos) | tool:save_preference, tool:save_memory, tool:datetime | ✅ |
| autenticado | NULL (todos) | cmd:/ia | ✅ |
| autenticado | 1 (Administrador) | cmd:/costo | ✅ |

> **Nota**: `cmd:/start`, `cmd:/help`, `cmd:/recargar_permisos` y `tool:reload_permissions` se marcan `esPublico=1` en `BotRecurso` — no necesitan fila en `BotPermisos`.
> `esPublico=1` en `cmd:/recargar_permisos` y `tool:reload_permissions` garantiza que cualquier usuario autenticado pueda recargar sus permisos incluso si su cache está vacío o corrupto.

---

## Fases de Implementación

---

### Fase 1: Nuevo Esquema BD

**Objetivo**: Crear las nuevas tablas y poblar datos iniciales
**Dependencias**: Ninguna — las tablas legacy siguen funcionando en paralelo

#### Tareas

- [x] **Script SQL: crear `BotTipoEntidad`, `BotRecurso`, `BotPermisos`, `BotPermisosAudit`**
  - Archivo: `database/migrations/10_BotPermisos.sql`
  - Incluir índices y unique constraints
  - Idempotente (IF NOT EXISTS)

- [x] **Script SQL: insertar datos iniciales**
  - Archivo: `database/migrations/11_BotPermisos_DatosIniciales.sql`
  - TipoEntidades, Recursos (tools + cmds), permisos por rol
  - Usa MERGE — idempotente

- [ ] ~~**Script SQL: trigger de audit**~~ — **diferido** (no es bloqueante para la migración)
  - Archivo: `database/migrations/12_BotPermisos_Audit.sql`
  - Trigger AFTER INSERT/UPDATE/DELETE en `BotPermisos`

- [x] **Script de verificación pre-migración**
  - Archivo: `database/migrations/09_PreMigracionCheck.sql`
  - Query: usuarios activos sin gerencia asignada
  - Query: roles en uso vs datos iniciales

- [x] **Verificar en staging antes de prod**

#### Entregables
- [ ] 4 tablas nuevas creadas
- [ ] Datos iniciales por rol configurados
- [ ] ~~Trigger de audit~~ — diferido
- [ ] Todos los roles en uso cubiertos por datos iniciales de `BotPermisos`

---

### Fase 2: Capa de Dominio Nueva

**Objetivo**: Python limpio que reemplaza los stored procedures
**Dependencias**: Fase 1

#### Tareas

- [ ] **Crear `PermissionRepository`**
  - Archivo: `src/domain/auth/permission_repository.py`
  - `get_all_permissions(user_id, role_id, gerencia_ids, direccion_ids) -> list[dict]`
  - La query usa UNION de dos partes:
    1. Filas de `BotPermisos` que aplican al usuario (por rol, gerencia, dirección, usuario)
    2. `SELECT recurso, 1 AS permitido FROM BotRecurso WHERE esPublico=1 AND activo=1` — siempre incluidos como `True`
  - Así `get_all_for_user()` retorna un dict completo que incluye recursos públicos, y `get_tools_prompt()` los muestra correctamente

- [ ] **Crear `PermissionService`**
  - Archivo: `src/domain/auth/permission_service.py`
  - `can(user_id, recurso, context) -> bool` — método principal
  - `get_all_for_user(user_id, role_id, gerencia_ids, direccion_ids) -> dict[str, bool]`
  - Cache LRU con TTL de 60s por usuario
  - `invalidate(user_id)` — forzar recarga inmediata para un usuario específico
  - `invalidate_all()` — forzar recarga de todo el cache (para admins)
  - Lee `tipoResolucion` de BD (no hardcodeado)

- [ ] **Crear enums para magic strings**
  - Archivo: `src/domain/auth/constants.py`
  - `AccountState`, `OperationResult`, `EntityType`, `ResolutionType`

- [ ] **Separar `UserRepository` en 3**
  - `UserQueryRepository`: get_user_by_chat_id, get_user_by_id
  - `TelegramAccountRepository`: registro, verificación, bloqueo
  - `PermissionRepository`: consultas de permisos (ya definido arriba)

- [ ] **Tests de `PermissionService`**
  - Archivo: `tests/domain/test_permission_service.py`
  - Test: rol permite → OK
  - Test: usuario deniega sobre rol que permite → DENEGADO
  - Test: gerencia permite, rol no tiene regla → OK (permisivo)
  - Test: permiso expirado → DENEGADO
  - Test: recurso público → siempre OK
  - Test: sin ninguna regla → DENEGADO (default deny)
  - Test: cache hit no hace query a BD
  - Test: `invalidate(user_id)` fuerza re-query en el siguiente acceso

- [ ] **`create_permission_service()` en factory**
  - Archivo: `src/pipeline/factory.py`
  - Recibe `db_manager`, crea `PermissionRepository` y `PermissionService`
  - Llamado en `create_main_handler()` antes de crear `MemoryService`
  - Pasado también a `create_tool_registry()` para que `ReloadPermissionsTool` pueda llamar `invalidate()`

#### Entregables
- [ ] `PermissionService` con cache TTL y métodos de invalidación con tests
- [ ] 3 repositories con responsabilidades separadas
- [ ] Enums reemplazando magic strings
- [ ] Factory function para `PermissionService`

---

### Fase 3: UserContext con Roles y Gerencias

**Objetivo**: Que cada request cargue el contexto organizacional completo del usuario
**Dependencias**: Fase 2

#### Tareas

- [ ] **Agregar campos a `UserProfile`**
  - Archivo: `src/domain/memory/memory_entity.py`
  - `role_id: Optional[int]`
  - `role_name: Optional[str]`
  - `gerencia_ids: list[int]`
  - `direccion_ids: list[int]`

- [ ] **Actualizar `MemoryRepository.get_profile()`**
  - Agregar JOINs con `Usuarios`, `Roles`, `GerenciasUsuarios`, `Gerencias`, `DireccionesUsuarios`, `Direcciones`
  - Una sola query que trae todo
  - Archivo: `src/domain/memory/memory_repository.py`

- [ ] **Poblar `UserContext` completo**
  - `roles = [profile.role_name]`
  - `role_id = profile.role_id`
  - `gerencia_ids = profile.gerencia_ids`
  - `direccion_ids = profile.direccion_ids`
  - Archivo: `src/domain/memory/memory_service.py`

- [ ] **Inyectar `PermissionService` en `MemoryService`**
  - `MemoryService.__init__` recibe `permission_service: PermissionService`
  - Archivo: `src/domain/memory/memory_service.py`

- [ ] **Cargar `permisos` al inicio de cada request (siempre frescos)**
  - Campo: `permisos: dict[str, bool]` — clave = nombre del recurso, valor = permitido
  - Ejemplo: `{"tool:database_query": True, "tool:calculate": True, "tool:knowledge_search": False}`
  - **Importante**: `MemoryService` cachea `UserContext` con TTL 300s, pero `permisos` NO debe venir del cache del contexto. En `get_or_create_context()`, siempre llamar `permission_service.get_all_for_user()` al final y setear `context.permisos` antes de retornar, aunque el resto del contexto venga de cache.
  - Esto garantiza que el TTL de `PermissionService` (60s) se respeta independientemente del cache de `MemoryService` (300s).
  - Archivo: `src/domain/memory/memory_service.py`

- [ ] **Verificar prompt con rol y capacidades visibles**
  - `<memory type="user">` debe mostrar rol, gerencia y lista de capacidades disponibles
  - El agente adapta respuestas según el contexto organizacional (comportamiento proactivo)

#### Entregables
- [ ] `UserContext` con contexto organizacional completo (rol, gerencias, direcciones)
- [ ] `PermissionService` inyectado en `MemoryService`
- [ ] `permisos` cargados (con TTL) al inicio de cada request
- [ ] Rol, gerencia y capacidades visibles en el prompt del agente

---

### Fase 4: Permisos en Tools del Agente (Proactivo)

**Objetivo**: Filtrar tools disponibles según permisos cargados en `UserContext`, y que el agente responda proactivamente según lo que el usuario puede hacer
**Dependencias**: Fases 2 y 3

#### Tareas

- [ ] **Filtrar tools en `ToolRegistry.get_tools_prompt()`**
  - Recibe `user_context: Optional[UserContext]` como parámetro
  - Si `user_context.permisos` está cargado: solo incluir tools donde `permisos.get(f"tool:{name}", False) == True`
  - Si no hay contexto de permisos: incluir todas (backward compat)
  - El agente solo "ve" las tools a las que tiene acceso → no puede invocar lo que no aparece en el prompt
  - Archivo: `src/agents/tools/registry.py`

- [ ] **Check de permiso en `ToolRegistry` al ejecutar** (segunda línea de defensa)
  - Verificar `user_context.permisos.get(f"tool:{tool_name}", False)` antes de ejecutar
  - Si deniega: retornar `ToolResult.error_result("No tenés permiso para usar esta herramienta")`
  - Log del intento denegado (para detectar prompt injection o bypass)
  - Archivo: `src/agents/tools/registry.py`

- [ ] **Inyectar capacidades disponibles en `<memory type="user">`**
  - `UserContext.to_prompt_context()` agrega bloque "Capacidades disponibles:"
  - Lista las tools permitidas en lenguaje natural (e.g. "Consultas a base de datos, Cálculos matemáticos")
  - El agente puede responder proactivamente "Puedo ayudarte con X, Y, Z"
  - Archivo: `src/agents/base/events.py`

- [ ] **Wiring en factory**
  - `create_tool_registry()` ya no recibe `permission_service` — los permisos viven en `UserContext`
  - `ToolRegistry.execute()` y `get_tools_prompt()` reciben `user_context` que ya trae los permisos precargados
  - Archivo: `src/pipeline/factory.py`

- [ ] **Tests de permisos en tools**
  - Test: tool ausente en `permisos` no aparece en `get_tools_prompt()`
  - Test: tool denegada en ejecución retorna observation de error
  - Test: tool permitida ejecuta normalmente
  - Test: sin `permisos` en `user_context` → incluye todas (backward compat)

> **Nota — Scopes de tools (futuro)**: Control más granular de permisos dentro de una tool (ej: solo ciertas tablas de SQL, solo ciertos módulos de conocimiento) está **diferido a un plan separado**. En esta fase, el permiso es binario por tool.

#### Entregables
- [ ] Tools filtradas en prompt según `UserContext.permisos`
- [ ] Segunda verificación en ejecución como defensa en profundidad
- [ ] Agente responde proactivamente sobre sus capacidades disponibles

---

### Fase 5: Migrar Middleware y Handlers

**Objetivo**: Reemplazar lógica legacy con el nuevo `PermissionService`
**Dependencias**: Fase 2

#### Tareas

- [ ] **Refactorizar `AuthMiddleware`**
  - El middleware corre antes de que `UserContext` esté cargado, pero necesita `role_id` y `gerencia_ids` para resolver permisos de comando
  - Estrategia: `AuthMiddleware` inyecta `PermissionService` + `UserQueryRepository`. Antes del check, hace una query liviana para obtener `(user_id, role_id, gerencia_ids)` del usuario — query simple sin cargar historial ni memoria
  - Reemplazar llamadas a SP por `PermissionService.can(user_id, recurso, role_id, gerencia_ids, direccion_ids)`
  - Usar enums en lugar de magic strings
  - Archivo: `src/bot/middleware/auth_middleware.py`

- [ ] **Eliminar check duplicado en `query_handlers.py`**
  - El check de permiso en el handler es redundante si el middleware ya lo hace
  - Limpiar: una sola capa de autorización
  - Archivo: `src/bot/handlers/query_handlers.py`

- [ ] **Fix defaults inseguros en `TelegramUser`**
  - `activo` default → `False` (no `True`)
  - `estado` default → `'BLOQUEADO'` (no `'ACTIVO'`)
  - Archivo: `src/domain/auth/user_entity.py`

- [ ] **Unificar `UserService`**
  - Remover métodos de permisos (ahora en `PermissionService`)
  - `UserService` queda solo para: registro, verificación, bloqueo
  - Archivo: `src/domain/auth/user_service.py`

- [ ] **Comando `/recargar_permisos` disponible para cualquier usuario**
  - Llama `PermissionService.invalidate(user_id)` → vacía el cache solo del usuario que lo ejecuta
  - Responde confirmación: "Tus permisos fueron recargados"
  - No requiere ser admin — cada usuario recarga los suyos propios
  - Archivo: `src/bot/handlers/command_handlers.py`

- [ ] **Tool `reload_permissions` para el agente**
  - El agente puede llamar esta tool cuando detecta que el usuario menciona problemas de acceso
  - Llama `PermissionService.invalidate(user_id)` y recarga `UserContext.permisos` en el request actual
  - Responde al usuario explicando qué cambió (qué tools están ahora disponibles)
  - Archivo: `src/agents/tools/reload_permissions_tool.py`

- [ ] **Registrar `ReloadPermissionsTool` en `create_tool_registry()`**
  - Recibe `permission_service` como dependencia (ya pasado desde `create_main_handler()`)
  - Archivo: `src/pipeline/factory.py`

#### Entregables
- [ ] Un solo punto de autorización (middleware)
- [ ] Sin magic strings en handlers
- [ ] Defaults seguros en entidades
- [ ] Comando `/recargar_permisos` disponible para todos los usuarios
- [ ] Tool `reload_permissions` registrada en el agente

---

### Fase 6: Tests, Cleanup y Eliminación de Objetos Legacy

**Objetivo**: Cobertura completa, eliminación de código muerto y drop de objetos BD que ya no se usan
**Dependencias**: Todas las anteriores

#### Tareas — Tests

- [ ] **Actualizar tests existentes**
  - `tests/domain/test_user_service.py`
  - `tests/auth/test_auth_middleware.py`

- [ ] **Test de integración del flujo completo**
  - Archivo: `tests/integration/test_permission_flow.py`
  - Flujo: request → middleware → permiso cargado en UserContext → tool filtrada → ejecutada

#### Tareas — Cleanup Python

- [ ] **Eliminar llamadas a stored procedures desde Python**
  - Remover todas las llamadas a `sp_VerificarPermisoOperacion` y `sp_ObtenerOperacionesUsuario`
  - Remover importaciones y referencias en: `auth_middleware.py`, `user_service.py`, `query_handlers.py`

- [ ] **Eliminar tablas legacy del código Python**
  - Remover accesos directos a `RolesOperaciones` desde el nuevo flujo
  - Verificar que ningún repositorio nuevo las referencie
  - Nota: `OperacionesIA` y `PerfilOperacion` no existen en BD (verificado en pre-migración)

#### Tareas — Eliminación de Objetos BD

> **Estrategia**: primero verificar que nadie más los consume (logs, reportes, otros sistemas), luego dropear en staging, luego en prod.

- [ ] **Script: DROP stored procedures de permisos**
  - Archivo: `database/migrations/20_DropLegacyPermisosSPs.sql`
  - SPs a eliminar: `sp_VerificarPermisoOperacion`, `sp_ObtenerOperacionesUsuario`, y dependientes
  - Idempotente (`IF OBJECT_ID(...) IS NOT NULL DROP PROCEDURE ...`)

- [ ] **Script: DROP tablas legacy de permisos**
  - Archivo: `database/migrations/21_DropLegacyPermisosTablas.sql`
  - Tablas confirmadas en BD: `RolesOperaciones`, `RolesIA`, `GerenciasRolesIA`
  - `OperacionesIA` y `PerfilOperacion` no existen — ignorar
  - **Verificar antes de dropear**: que no tengan FK activas hacia otras tablas usadas
  - Mover data histórica relevante a tabla de archivo antes del drop si aplica

- [ ] **Verificar integridad tras cleanup**
  - Correr suite de tests completa post-drop
  - Verificar que `LogOperaciones` siga funcionando (no depende de las tablas dropeadas)
  - Confirmar en staging antes de prod

#### Tareas — Documentación

- [ ] **Documentar el nuevo sistema**
  - Cómo agregar un nuevo permiso desde BD (INSERT en `BotPermisos`)
  - Cómo agregar una nueva entidad organizacional (ej: equipo)
  - Actualizar `.claude/context/DATABASE.md`

#### Entregables
- [ ] Suite de tests completa con integración
- [ ] Sin llamadas a SPs de permisos desde Python
- [ ] Scripts de drop versionados y ejecutados
- [ ] Tablas legacy eliminadas de BD
- [ ] Documentación actualizada

---

## Riesgos y Mitigaciones

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|--------------|---------|------------|
| Cache desactualizado tras cambio en BD | Media | Medio | TTL de 60s + comando `/recargar_permisos` para efecto inmediato |
| Tool nuevo sin configurar en BotRecurso | Alta | Bajo | Log WARNING explícito + default deny con mensaje claro |
| Migración rompe auth existente | Media | Alto | Fases paralelas — legacy sigue funcionando hasta Fase 5 |
| Usuario sin rol asignado | Baja | Medio | Default a rol "Consulta" (más restrictivo) + log |
| Drop de tabla legacy rompe otro sistema | Media | Alto | Verificar FK activas y consumidores externos antes de cada DROP |
| Orphan rows en BotPermisos tras borrar rol/gerencia | Media | Bajo | Trigger o job nocturno de limpieza |

---

## Criterios de Éxito

- [ ] `UserContext` tiene rol, gerencias y permisos en el 100% de los requests
- [ ] Admin puede cambiar permiso en BD → efecto en ≤60s (TTL) o inmediato con `/recargar_permisos`
- [ ] Todos los tools filtran su disponibilidad según `UserContext.permisos`
- [ ] Explicit deny de usuario siempre pisa permisos de rol/gerencia
- [ ] Sin llamadas a `sp_VerificarPermisoOperacion` desde código Python
- [ ] Tablas y SPs legacy dropeados y verificados en staging
- [ ] Tests cubren los 8 roles con sus permisos esperados

---

## Historial de Cambios

| Fecha | Cambio | Autor |
|-------|--------|-------|
| 2026-04-01 | Creación del plan — análisis completo del sistema legacy | Roque98 |
| 2026-04-01 | Rediseño completo con catálogos, audit trail y resolución configurable | Roque98 |
| 2026-04-02 | Diseño final: entidad 'autenticado' + idRolRequerido en gerencia/direccion | Roque98 |
| 2026-04-02 | Eliminar entidad 'publico' — reemplazada por esPublico en BotRecurso | Roque98 |
| 2026-04-02 | Agregar permisos proactivos: UserContext.permisos + filtro en ToolRegistry + capacidades en prompt | Roque98 |
| 2026-04-02 | Scopes de tools diferidos a plan futuro | Roque98 |
| 2026-04-02 | Cache TTL 60s + /recargar_permisos (cualquier usuario) + tool reload_permissions (agente) | Roque98 |
| 2026-04-02 | Fase 6: agregar DROP de tablas y SPs legacy como tareas explícitas | Roque98 |
| 2026-04-02 | Revisión completa: corregir inconsistencias 'publico', completar BotRecurso/BotPermisos iniciales, agregar wiring PermissionService→MemoryService, JOINs de direcciones, ciclo de vida de permisos | Roque98 |
| 2026-04-02 | Segunda revisión: fix UNIQUE nullable en BotPermisos, wiring ReloadPermissionsTool, permisos siempre frescos fuera del cache de MemoryService, AuthMiddleware con query liviana, verificación pre-migración | Roque98 |
| 2026-04-02 | Tercera revisión: PermissionRepository incluye esPublico=1 via UNION, registrar ReloadPermissionsTool en create_tool_registry() | Roque98 |
