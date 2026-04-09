# Plan: AUTH-SP — Migración Auth a Stored Procedures

> **Estado**: ⚪ No iniciado
> **Última actualización**: 2026-04-09
> **Rama Git**: master

## Resumen de Progreso

| Fase | Progreso | Estado |
|------|----------|--------|
| Fase 1: SPs en base de datos | ░░░░░░░░░░ 0% | ⏳ Pendiente |
| Fase 2: .env + Settings | ░░░░░░░░░░ 0% | ⏳ Pendiente |
| Fase 3: Repositorios | ░░░░░░░░░░ 0% | ⏳ Pendiente |
| Fase 4: Tests | ░░░░░░░░░░ 0% | ⏳ Pendiente |

**Progreso Total**: ░░░░░░░░░░ 0% (0/24 tareas)

---

## Descripción

Migrar todas las consultas SQL directas de los repositorios de autenticación
(usuarios, roles, gerencias, permisos) a Stored Procedures. Agregar un parámetro
`.env` (`AUTH_DB_ALIAS`) que indica qué alias de BD contiene dichos SPs, permitiendo
que auth viva en una BD diferente a `core` si se requiere.

### Motivación
- Centralizar la lógica de acceso a datos de auth en la BD (más fácil de versionar y auditar)
- Desacoplar el alias de BD de auth del alias `core`
- Seguir el patrón ya establecido con `sp_RegistrarLogOperacion`

### Alcance
- **Incluye**: `user_repository.py`, `user_query_repository.py`, `permission_repository.py`, `telegram_account_repository.py`
- **Excluye**: `memory_repository.py` (tiene lógica de negocio propia que no es auth pura), `reload_permissions_tool.py` (no toca BD directamente)

---

## Fase 1: SPs en Base de Datos

**Objetivo**: Crear todos los stored procedures en un script de migración
**Dependencias**: Ninguna

### Tareas

- [ ] **sp_BotAuth_GetUsuarioByChatId** — Reemplaza query en `user_query_repository.get_by_chat_id`
  - Input: `@telegramChatId BIGINT`
  - Output: idUsuario, nombre, email, idRol, puesto, empresa, estado, verificado

- [ ] **sp_BotAuth_GetPerfilUsuario** — Reemplaza query en `user_query_repository.get_profile_for_permissions`
  - Input: `@telegramChatId BIGINT`
  - Output: idUsuario, nombre, rol_id, gerencia_ids (lista), estado, verificado
  - Incluye JOIN a GerenciasUsuarios (agrega los gerencia_ids como string separado por coma o via cursor)

- [ ] **sp_BotAuth_GetAdminChatIds** — Reemplaza query en `user_query_repository.get_admin_chat_ids`
  - Input: ninguno
  - Output: telegramChatId de todos los admins activos verificados

- [ ] **sp_BotAuth_GetUsuarioById** — Reemplaza query en `user_repository.get_user_by_id`
  - Input: `@idUsuario INT`
  - Output: idUsuario, nombre, email, idRol, puesto, empresa, estado

- [ ] **sp_BotAuth_InsertarCuentaTelegram** — Reemplaza lógica en `telegram_account_repository`
  - Input: idUsuario, telegramChatId, telegramUsername, codigoVerificacion
  - Output: idUsuarioTelegram nuevo (o error si ya existe)

- [ ] **sp_BotAuth_MarcarCuentaVerificada** — Reemplaza `mark_account_verified`
  - Input: `@telegramChatId BIGINT`
  - Output: rows affected

- [ ] **sp_BotAuth_BloquearCuenta** — Reemplaza `block_account`
  - Input: `@telegramChatId BIGINT`, `@motivo NVARCHAR(255)`
  - Output: rows affected

- [ ] **sp_BotAuth_ActualizarActividad** — Reemplaza `update_last_activity`
  - Input: `@telegramChatId BIGINT`
  - Output: rows affected

- [ ] **sp_BotAuth_GetPermisosUsuario** — Reemplaza la query UNION en `permission_repository`
  - Input: `@idUsuario INT`, `@gerenciaIds NVARCHAR(MAX)` (CSV), `@recursos NVARCHAR(MAX)` (CSV, opcional)
  - Output: recurso, tipoRecurso, idRolRequerido, permitido, prioridad
  - Lógica: UNION de permisos por usuario / por rol / por gerencia + recursos públicos

- [ ] **Agregar script** `scripts/migrations/006_auth_stored_procedures.sql`
  - Crear todos los SPs anteriores con `CREATE OR ALTER PROCEDURE`
  - Documentar cada SP con comentario de propósito

### Entregables
- [ ] `scripts/migrations/006_auth_stored_procedures.sql` con los 9 SPs

---

## Fase 2: .env + Settings

**Objetivo**: Agregar parámetro `AUTH_DB_ALIAS` para indicar qué BD tiene los SPs de auth
**Dependencias**: Ninguna (puede hacerse en paralelo con Fase 1)

### Tareas

- [ ] **Agregar `AUTH_DB_ALIAS` a `.env.example`**
  - Valor por defecto: `core`
  - Comentario: alias de la BD que contiene los SPs de autenticación (sp_BotAuth_*)

- [ ] **Agregar `auth_db_alias` a `AppSettings` en `src/config/settings.py`**
  - Tipo: `str`, default `"core"`
  - Leer de env var `AUTH_DB_ALIAS`
  - Validar que el alias esté registrado en `db_connections` al inicializar

### Entregables
- [ ] `.env.example` actualizado
- [ ] `settings.py` con campo `auth_db_alias` validado

---

## Fase 3: Repositorios

**Objetivo**: Reemplazar SQL directo por llamadas a SPs en todos los repositorios de auth
**Dependencias**: Fase 1 (SPs creados), Fase 2 (alias disponible en settings)

### Tareas

- [ ] **Actualizar `UserQueryRepository`** — 3 métodos
  - `get_by_chat_id` → `EXEC sp_BotAuth_GetUsuarioByChatId @telegramChatId`
  - `get_profile_for_permissions` → `EXEC sp_BotAuth_GetPerfilUsuario @telegramChatId`
  - `get_admin_chat_ids` → `EXEC sp_BotAuth_GetAdminChatIds`
  - Usar `auth_db_alias` del settings para elegir la conexión via `db_manager`

- [ ] **Actualizar `UserRepository`** — 1 método
  - `get_user_by_id` → `EXEC sp_BotAuth_GetUsuarioById @idUsuario`

- [ ] **Actualizar `TelegramAccountRepository`** — 3 métodos
  - `insert_telegram_account` → `EXEC sp_BotAuth_InsertarCuentaTelegram ...`
  - `mark_account_verified` → `EXEC sp_BotAuth_MarcarCuentaVerificada @telegramChatId`
  - `block_account` → `EXEC sp_BotAuth_BloquearCuenta @telegramChatId, @motivo`

- [ ] **Actualizar `PermissionRepository`** — 1 método principal
  - Query UNION de permisos → `EXEC sp_BotAuth_GetPermisosUsuario @idUsuario, @gerenciaIds`
  - Los gerencia_ids se pasan como CSV (ya vienen como lista desde el perfil)

- [ ] **Inyectar `auth_db_alias`** en los repositorios que lo necesiten
  - Via constructor o via `settings.auth_db_alias` directamente

### Entregables
- [ ] 4 repositorios actualizados sin SQL directo para operaciones de auth

---

## Fase 4: Tests

**Objetivo**: Verificar que el comportamiento es idéntico al anterior
**Dependencias**: Fase 3

### Tareas

- [ ] **Actualizar tests existentes** en `tests/` que mockeen queries de auth
  - Cambiar mocks de SQL text a mocks de EXEC sp_*

- [ ] **Test de integración** `tests/auth/test_auth_sp_integration.py`
  - Verificar que `sp_BotAuth_GetPerfilUsuario` retorna los campos esperados
  - Verificar que `sp_BotAuth_GetPermisosUsuario` resuelve permisos correctamente

- [ ] **Test de configuración** — verificar que `AUTH_DB_ALIAS` inválido lanza error al iniciar

### Entregables
- [ ] Tests actualizados pasando
- [ ] Test de integración documentado

---

## Criterios de Éxito

- [ ] Ningún repositorio de auth usa `text()` con SQL directo para usuarios/roles/gerencias
- [ ] `AUTH_DB_ALIAS` en `.env` controla qué BD se usa para auth
- [ ] Si `AUTH_DB_ALIAS=core` (default), el bot funciona igual que antes
- [ ] Si `AUTH_DB_ALIAS=otro_alias`, el bot usa esa BD para todos los SPs de auth
- [ ] Tests de integración pasan contra BD real

---

## Riesgos y Mitigaciones

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|--------------|---------|------------|
| SP de permisos (UNION) es complejo de migrar | Media | Medio | Crear SP gradualmente, testear con datos reales |
| `get_profile_for_permissions` retorna gerencia_ids como lista Python | Alta | Medio | SP retorna CSV, repositorio hace split — documentar contrato |
| Multi-database: `auth_db_alias` apunta a BD sin los SPs | Baja | Alto | Validar alias en settings.py al iniciar la app |

---

## Historial de Cambios

| Fecha | Cambio | Autor |
|-------|--------|-------|
| 2026-04-09 | Creación del plan | Roque98 |
