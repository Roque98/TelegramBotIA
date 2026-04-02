# Plan: SEC-01 — Migración del Sistema de Permisos

> **Estado**: ⚪ No iniciado
> **Última actualización**: 2026-04-01
> **Rama Git**: `feature/sec-01-permisos`
> **Motivación**: El sistema legacy usa stored procedures para todo, no tiene cache, los roles nunca se cargan en UserContext, y los tools del agente no tienen ningún control de acceso.

## Resumen de Progreso

| Fase | Progreso | Estado |
|------|----------|--------|
| Fase 1: Diagnóstico y DB | ░░░░░░░░░░ 0% | ⏳ Pendiente |
| Fase 2: Capa de Dominio | ░░░░░░░░░░ 0% | ⏳ Pendiente |
| Fase 3: Cargar Roles en Contexto | ░░░░░░░░░░ 0% | ⏳ Pendiente |
| Fase 4: Permisos en Tools del Agente | ░░░░░░░░░░ 0% | ⏳ Pendiente |
| Fase 5: Migrar Middleware y Handlers | ░░░░░░░░░░ 0% | ⏳ Pendiente |
| Fase 6: Tests y Cleanup | ░░░░░░░░░░ 0% | ⏳ Pendiente |

**Progreso Total**: ░░░░░░░░░░ 0% (0/24 tareas)

---

## Descripción

Reemplazar el sistema de permisos legacy (stored procedures + checks dispersos en handlers)
por una capa de dominio limpia que:

1. Carga roles desde BD y los inyecta en `UserContext`
2. Registra los tools del agente como operaciones en `Operaciones`
3. Controla acceso a tools via `RolesOperaciones` (administrable desde BD)
4. Unifica toda la lógica de permisos en `PermissionService`
5. Elimina los stored procedures del flujo principal (mantener como fallback)

---

## Estado Actual (Legacy)

### Lo que funciona bien
- Esquema de BD sólido: `Roles`, `Operaciones`, `RolesOperaciones`, `UsuariosOperaciones`
- Jerarquía: permisos de usuario sobreescriben los de rol
- `UsuariosOperaciones.fechaExpiracion` para permisos temporales
- `LogOperaciones` como audit trail completo

### Problemas a corregir
- `sp_VerificarPermisoOperacion` hace 3-4 queries sin cache → lento
- `UserContext.roles` siempre vacío — los agentes no saben el rol del usuario
- Tools del agente (`database_query`, `calculate`, etc.) no están en `Operaciones` → sin control
- Lógica de permisos dispersa en handlers con hard-coded strings (`'/ia'`)
- `UserService` abre sesión DB en cada check sin pool ni cache
- Stored procedures difíciles de testear

---

## Fase 1: Diagnóstico y BD

**Objetivo**: Extender el esquema existente para soportar tools del agente
**Dependencias**: Ninguna

### Tareas

- [ ] **Registrar tools del agente en tabla `Operaciones`**
  - Agregar un módulo "Agente IA" en `Modulos`
  - Insertar operaciones: `tool:database_query`, `tool:calculate`, `tool:knowledge_search`, `tool:save_preference`, `tool:save_memory`, `tool:datetime`
  - Convención de nombre: prefijo `tool:` para distinguir de comandos `/comando`

- [ ] **Configurar permisos default en `RolesOperaciones`**
  - Administrador (1): todos los tools permitidos
  - Gerente (2): todos los tools permitidos
  - Supervisor (3): todos los tools permitidos
  - Coordinador (7): database_query, calculate, knowledge_search
  - Especialista (8): database_query, calculate, knowledge_search
  - Analista (4): database_query, calculate, knowledge_search
  - Usuario (5): knowledge_search, calculate
  - Consulta (6): knowledge_search únicamente

- [ ] **Script SQL de migración**
  - Archivo: `database/migrations/10_AgentToolsPermisos.sql`
  - Idempotente (puede ejecutarse múltiples veces sin errores)

### Entregables
- [ ] Tools registrados en `Operaciones`
- [ ] Permisos default configurados por rol
- [ ] Script de migración documentado

---

## Fase 2: Capa de Dominio Nueva

**Objetivo**: Reemplazar los stored procedures con Python limpio y testeable
**Dependencias**: Fase 1

### Tareas

- [ ] **Crear `PermissionRepository`**
  - Archivo: `src/domain/auth/permission_repository.py`
  - `get_user_permissions(user_id) -> dict[str, bool]` — carga todos los permisos del usuario de una sola query (JOIN RolesOperaciones + UsuariosOperaciones)
  - `get_role_id(user_id) -> int` — obtiene el idRol del usuario

- [ ] **Crear `PermissionService`**
  - Archivo: `src/domain/auth/permission_service.py`
  - `can(user_id, operation) -> bool` — check principal
  - `get_user_role(user_id) -> str` — retorna nombre del rol
  - Cache en memoria con TTL de 60s (evita query en cada tool call)
  - Invalida cache cuando se modifica `UsuariosOperaciones`

- [ ] **Deprecar stored procedures del flujo principal**
  - `sp_VerificarPermisoOperacion` → reemplazado por `PermissionService.can()`
  - `sp_ObtenerOperacionesUsuario` → reemplazado por `PermissionRepository.get_user_permissions()`
  - Mantener SPs en BD pero no llamarlos desde código nuevo

- [ ] **Tests de `PermissionService`**
  - Archivo: `tests/domain/test_permission_service.py`
  - Test: permisos de rol base
  - Test: override de usuario sobreescribe rol
  - Test: permiso temporal expirado se deniega
  - Test: cache hit no hace query a BD

### Entregables
- [ ] `PermissionRepository` con tests
- [ ] `PermissionService` con cache y tests
- [ ] SPs como fallback (no eliminados)

---

## Fase 3: Cargar Roles en UserContext

**Objetivo**: Que el agente sepa el rol del usuario en cada request
**Dependencias**: Fase 2

### Tareas

- [ ] **Agregar `role_name` y `role_id` a `UserProfile`**
  - Archivo: `src/domain/memory/memory_entity.py`
  - Campos: `role_id: Optional[int]`, `role_name: Optional[str]`

- [ ] **Actualizar `MemoryRepository.get_profile()`**
  - Agregar JOIN con `Usuarios` y `Roles` para traer `idRol` y `rolNombre`
  - Archivo: `src/domain/memory/memory_repository.py`

- [ ] **Poblar `UserContext.roles`**
  - En `MemoryService.build_context()`: `roles=[profile.role_name]` si existe
  - Archivo: `src/domain/memory/memory_service.py`

- [ ] **Verificar que el rol aparece en el prompt**
  - `to_prompt_context()` ya incluye roles en `<memory type="user">`
  - El agente verá: `Roles: Gerente`

### Entregables
- [ ] `UserContext.roles` poblado en cada request
- [ ] Rol visible en el bloque `<memory type="user">` del prompt

---

## Fase 4: Permisos en Tools del Agente

**Objetivo**: Que cada tool verifique permisos antes de ejecutarse
**Dependencias**: Fases 2 y 3

### Tareas

- [ ] **Agregar `permission_service` al `ToolRegistry`**
  - Archivo: `src/agents/tools/registry.py`
  - El registry recibe `PermissionService` al construirse

- [ ] **Verificar permiso en `ToolRegistry.execute_tool()`**
  - Antes de llamar `tool.execute()`: `permission_service.can(user_id, f"tool:{tool_name}")`
  - Si no tiene permiso: retornar `ToolResult.error_result("No tienes permiso para usar esta herramienta")`
  - El agente recibe el error como observation y lo comunica al usuario

- [ ] **Inyectar `user_id` en el contexto de ejecución**
  - Ya se inyecta `user_context` en kwargs — usar `user_context.user_id`

- [ ] **Tests de permisos en tools**
  - Test: tool bloqueado retorna error observation
  - Test: tool permitido se ejecuta normalmente
  - Test: usuario sin rol configurado deniega por defecto

### Entregables
- [ ] Tools con verificación de permisos
- [ ] Error claro al usuario cuando no tiene acceso
- [ ] Tests pasando

---

## Fase 5: Migrar Middleware y Handlers

**Objetivo**: Reemplazar los checks legacy en handlers con el nuevo `PermissionService`
**Dependencias**: Fase 2

### Tareas

- [ ] **Refactorizar `AuthMiddleware`**
  - Reemplazar llamada a SP por `PermissionService.can(user_id, comando)`
  - Archivo: `src/bot/middleware/auth_middleware.py`
  - Eliminar el hard-coded `'/ia'` en `query_handlers.py`

- [ ] **Refactorizar decorador `@require_permission`**
  - Usar `PermissionService` en lugar de `UserService.check_permission()`
  - Archivo: `src/bot/middleware/auth_middleware.py`

- [ ] **Cargar `telegram_user` con rol en middleware**
  - Al autenticar, guardar `role_name` en `context.user_data`
  - Evitar segunda query en handlers que necesitan el rol

- [ ] **Limpiar `UserService`**
  - Mover lógica de permisos a `PermissionService`
  - `UserService` queda solo para gestión de usuarios (registro, verificación, bloqueo)

### Entregables
- [ ] Middleware usando nuevo `PermissionService`
- [ ] Sin strings hard-coded de comandos en handlers
- [ ] `UserService` con responsabilidad única

---

## Fase 6: Tests y Cleanup

**Objetivo**: Cobertura completa y eliminación de código muerto
**Dependencias**: Todas las anteriores

### Tareas

- [ ] **Tests de integración del flujo completo**
  - Request Telegram → middleware → handler → agente → tool → permiso verificado
  - Archivo: `tests/integration/test_permission_flow.py`

- [ ] **Actualizar tests existentes**
  - `tests/domain/test_user_service.py` — adaptar a nueva estructura
  - `tests/auth/test_auth_middleware.py` — usar nuevo `PermissionService`

- [ ] **Eliminar código dead**
  - Calls directas a SPs desde Python
  - Lógica de permisos duplicada en handlers

- [ ] **Documentar el nuevo sistema**
  - Actualizar `.claude/context/DATABASE.md`
  - README de cómo agregar un nuevo permiso desde BD

### Entregables
- [ ] Suite de tests completa
- [ ] Zero llamadas a SPs de permisos desde Python
- [ ] Documentación actualizada

---

## Riesgos y Mitigaciones

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|--------------|---------|------------|
| Cache desactualizado tras cambio en BD | Media | Medio | TTL de 60s + invalidación manual via comando admin |
| Tool nuevo no registrado en Operaciones → denegado por default | Alta | Bajo | Log explícito cuando se deniega un tool no configurado |
| Migración rompe permisos existentes de comandos | Media | Alto | Ejecutar en staging, verificar todos los roles antes de prod |
| Usuario sin rol asignado en Usuarios | Baja | Medio | Default a rol "Consulta" (más restrictivo) |

---

## Criterios de Éxito

- [ ] `UserContext.roles` poblado en el 100% de los requests
- [ ] Todos los tools del agente verifican permisos antes de ejecutarse
- [ ] Un admin puede cambiar permisos desde BD sin reiniciar el bot (cache se invalida en ≤60s)
- [ ] Zero llamadas a `sp_VerificarPermisoOperacion` desde el flujo del agente
- [ ] Tests cubren los 8 roles con sus permisos esperados

---

## Historial de Cambios

| Fecha | Cambio | Autor |
|-------|--------|-------|
| 2026-04-01 | Creación del plan tras análisis del sistema legacy | Roque98 |
