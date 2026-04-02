# Plan: SEC-01 — Rediseño Completo del Sistema de Permisos

> **Estado**: ⚪ No iniciado
> **Última actualización**: 2026-04-01
> **Rama Git**: `feature/sec-01-permisos`

## Resumen de Progreso

| Fase | Progreso | Estado |
|------|----------|--------|
| Fase 1: Nuevo Esquema BD | ░░░░░░░░░░ 0% | ⏳ Pendiente |
| Fase 2: Capa de Dominio | ░░░░░░░░░░ 0% | ⏳ Pendiente |
| Fase 3: UserContext con Roles y Gerencias | ░░░░░░░░░░ 0% | ⏳ Pendiente |
| Fase 4: Permisos en Tools del Agente | ░░░░░░░░░░ 0% | ⏳ Pendiente |
| Fase 5: Migrar Middleware y Handlers | ░░░░░░░░░░ 0% | ⏳ Pendiente |
| Fase 6: Tests y Cleanup | ░░░░░░░░░░ 0% | ⏳ Pendiente |

**Progreso Total**: ░░░░░░░░░░ 0% (0/28 tareas)

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
- Jerarquía de resolución: usuario > autenticado > gerencia > dirección > público
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
  nombre           VARCHAR(50) UNIQUE NOT NULL   -- 'usuario', 'autenticado', 'gerencia', 'direccion', 'publico'
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
| publico | 99 | permisivo | Sin autenticación requerida, idRolRequerido no aplica |

> **Regla de resolución**: Si `tipoResolucion='definitivo'` y existe una entrada → es la respuesta final.
> Si `tipoResolucion='permisivo'` → si ALGUNA entrada permite, se permite (más permisivo gana).
> `idRolRequerido`: aplica a `autenticado`, `gerencia` y `direccion`. No aplica a `usuario` ni `publico`.

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
| cmd:/start | cmd | Inicio del bot (público) |
| cmd:/help | cmd | Ayuda (público) |
| cmd:/costo | cmd | Ver costos (admin) |

---

### Tabla principal de permisos

```sql
BotPermisos
  idPermiso            INT IDENTITY PK
  idTipoEntidad        INT NOT NULL FK → BotTipoEntidad
  idEntidad            INT NOT NULL               -- ID del usuario/gerencia/direccion según tipo. 0 para autenticado/publico
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

  UNIQUE (idTipoEntidad, idEntidad, idRecurso, idRolRequerido)
  INDEX IX_BotPermisos_lookup (idTipoEntidad, idEntidad, idRecurso)
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

1. ¿esPublico=1 en BotRecurso? → PERMITIDO (sin consultar permisos)

2. Cargar todas las filas de BotPermisos donde:
   - (tipoEntidad='usuario'      AND idEntidad = idUsuario)
   - (tipoEntidad='autenticado'  AND (idRolRequerido IS NULL OR idRolRequerido = idRol))
   - (tipoEntidad='gerencia'     AND idEntidad IN gerencias del usuario
                                 AND (idRolRequerido IS NULL OR idRolRequerido = idRol))
   - (tipoEntidad='direccion'    AND idEntidad IN direcciones del usuario
                                 AND (idRolRequerido IS NULL OR idRolRequerido = idRol))
   - (tipoEntidad='publico')
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
| publico | NULL | cmd:/start, cmd:/help | ✅ |

---

## Fases de Implementación

---

### Fase 1: Nuevo Esquema BD

**Objetivo**: Crear las nuevas tablas y poblar datos iniciales
**Dependencias**: Ninguna — las tablas legacy siguen funcionando en paralelo

#### Tareas

- [ ] **Script SQL: crear `BotTipoEntidad`, `BotRecurso`, `BotPermisos`, `BotPermisosAudit`**
  - Archivo: `database/migrations/10_BotPermisos.sql`
  - Incluir índices y unique constraints
  - Idempotente (IF NOT EXISTS)

- [ ] **Script SQL: insertar datos iniciales**
  - Archivo: `database/migrations/11_BotPermisos_DatosIniciales.sql`
  - TipoEntidades, Recursos (tools + cmds), permisos por rol

- [ ] **Script SQL: trigger de audit**
  - Archivo: `database/migrations/12_BotPermisos_Audit.sql`
  - Trigger AFTER INSERT/UPDATE/DELETE en `BotPermisos`

- [ ] **Verificar en staging antes de prod**

#### Entregables
- [ ] 4 tablas nuevas creadas
- [ ] Datos iniciales por rol configurados
- [ ] Trigger de audit activo

---

### Fase 2: Capa de Dominio Nueva

**Objetivo**: Python limpio que reemplaza los stored procedures
**Dependencias**: Fase 1

#### Tareas

- [ ] **Crear `PermissionRepository`**
  - Archivo: `src/domain/auth/permission_repository.py`
  - `get_all_permissions(user_id, role_id, gerencia_ids, direccion_ids) -> list[dict]`
  - Una sola query con todos los JOINs necesarios

- [ ] **Crear `PermissionService`**
  - Archivo: `src/domain/auth/permission_service.py`
  - `can(user_id, recurso) -> bool` — método principal
  - Cache LRU con TTL de 60s por usuario
  - `invalidate(user_id)` — para forzar recarga tras cambio en BD
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

#### Entregables
- [ ] `PermissionService` con cache y tests
- [ ] 3 repositories con responsabilidades separadas
- [ ] Enums reemplazando magic strings

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
  - Agregar JOIN con `Usuarios`, `Roles`, `GerenciasUsuarios`, `Gerencias`
  - Una sola query que trae todo
  - Archivo: `src/domain/memory/memory_repository.py`

- [ ] **Poblar `UserContext` completo**
  - `roles = [profile.role_name]`
  - `role_id = profile.role_id`
  - `gerencia_ids = profile.gerencia_ids`
  - `direccion_ids = profile.direccion_ids`
  - Archivo: `src/domain/memory/memory_service.py`

- [ ] **Verificar prompt con rol visible**
  - `<memory type="user">` debe mostrar rol y gerencia
  - El agente adapta respuestas según el contexto organizacional

#### Entregables
- [ ] `UserContext` con contexto organizacional completo
- [ ] Rol y gerencia visibles en el prompt del agente

---

### Fase 4: Permisos en Tools del Agente

**Objetivo**: Cada tool verifica permisos antes de ejecutarse
**Dependencias**: Fases 2 y 3

#### Tareas

- [ ] **Inyectar `PermissionService` en `ToolRegistry`**
  - Archivo: `src/agents/tools/registry.py`
  - `ToolRegistry.__init__` recibe `permission_service: Optional[PermissionService]`

- [ ] **Check de permiso en `ToolRegistry` antes de ejecutar**
  - Si `permission_service` disponible: verificar `can(user_id, f"tool:{tool_name}")`
  - Si deniega: retornar `ToolResult.error_result("No tenés permiso para usar esta herramienta")`
  - Log del intento denegado

- [ ] **Wiring en factory**
  - `create_tool_registry()` recibe y pasa `permission_service`
  - Archivo: `src/pipeline/factory.py`

- [ ] **Tests de permisos en tools**
  - Test: tool bloqueado retorna observation de error
  - Test: tool permitido ejecuta normalmente
  - Test: sin `permission_service` → ejecuta sin restricciones (backward compat)

#### Entregables
- [ ] Tools con control de acceso desde BD
- [ ] Mensaje claro al usuario cuando no tiene acceso

---

### Fase 5: Migrar Middleware y Handlers

**Objetivo**: Reemplazar lógica legacy con el nuevo `PermissionService`
**Dependencias**: Fase 2

#### Tareas

- [ ] **Refactorizar `AuthMiddleware`**
  - Reemplazar llamadas a SP por `PermissionService.can(user_id, comando)`
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

#### Entregables
- [ ] Un solo punto de autorización (middleware)
- [ ] Sin magic strings en handlers
- [ ] Defaults seguros en entidades

---

### Fase 6: Tests y Cleanup

**Objetivo**: Cobertura completa y eliminación de código muerto
**Dependencias**: Todas las anteriores

#### Tareas

- [ ] **Actualizar tests existentes**
  - `tests/domain/test_user_service.py`
  - `tests/auth/test_auth_middleware.py`

- [ ] **Test de integración del flujo completo**
  - Archivo: `tests/integration/test_permission_flow.py`
  - Flujo: request → middleware → permiso verificado → tool ejecutado

- [ ] **Eliminar stored procedures del flujo Python**
  - Remover todas las llamadas a `sp_VerificarPermisoOperacion` y `sp_ObtenerOperacionesUsuario`
  - Los SPs se quedan en BD como documentación/fallback pero no se llaman

- [ ] **Documentar el nuevo sistema**
  - Cómo agregar un nuevo permiso desde BD
  - Cómo agregar una nueva entidad (ej: equipo)
  - Actualizar `.claude/context/DATABASE.md`

#### Entregables
- [ ] Suite de tests completa
- [ ] Sin llamadas a SPs de permisos desde Python
- [ ] Documentación actualizada

---

## Riesgos y Mitigaciones

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|--------------|---------|------------|
| Cache desactualizado tras cambio en BD | Media | Medio | TTL de 60s + comando `/recargar_permisos` para admins |
| Tool nuevo sin configurar en BotRecurso | Alta | Bajo | Log WARNING explícito + default deny con mensaje claro |
| Migración rompe auth existente | Media | Alto | Fases paralelas — legacy sigue funcionando hasta Fase 5 |
| Usuario sin rol asignado | Baja | Medio | Default a rol "Consulta" (más restrictivo) + log |
| Orphan rows en BotPermisos tras borrar rol/gerencia | Media | Bajo | Trigger o job nocturno de limpieza |

---

## Criterios de Éxito

- [ ] `UserContext` tiene rol, gerencias y direcciones en el 100% de los requests
- [ ] Todos los tools verifican permisos antes de ejecutarse
- [ ] Admin puede cambiar permiso en BD → efecto en ≤60s (TTL cache)
- [ ] Explicit deny de usuario siempre pisa permisos de rol/gerencia
- [ ] Sin llamadas a `sp_VerificarPermisoOperacion` desde código Python
- [ ] Tests cubren los 8 roles con sus permisos esperados

---

## Historial de Cambios

| Fecha | Cambio | Autor |
|-------|--------|-------|
| 2026-04-01 | Creación del plan — análisis completo del sistema legacy | Roque98 |
| 2026-04-01 | Rediseño completo con catálogos, audit trail y resolución configurable | Roque98 |
| 2026-04-02 | Diseño final: entidad 'autenticado' + idRolRequerido en gerencia/direccion | Roque98 |
