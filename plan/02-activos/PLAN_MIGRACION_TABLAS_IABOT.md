# Plan: Migración de Tablas - Prefijo IABOT_ y Reubicación a consolamonitoreo

## Información General

| Campo | Valor |
|-------|-------|
| **Fecha** | 2026-02-16 |
| **Estado** | En progreso |
| **Rama** | feature/react-fase6-polish |
| **Prioridad** | Alta |

---

## Objetivo

1. Renombrar todas las tablas del bot con el prefijo `IABOT_`
2. Mover las tablas renombradas a la base de datos `consolamonitoreo`
3. Actualizar la tabla `Usuarios` con la nueva estructura (columnas de ABCMASplus)
4. Las tablas `Usuarios`, `Gerencias` y `GerenciasUsuarios` **permanecen en ABCMASplus sin renombrar**
5. Actualizar todo el código Python que referencia las tablas afectadas

---

## Contexto

Las tablas del bot actualmente residen en `ABCMASplus.dbo`. Se necesita separarlas porque:
- `Usuarios`, `Gerencias` y `GerenciasUsuarios` son tablas compartidas del sistema ABCMASplus
- Las tablas propias del bot deben vivir en `consolamonitoreo` con prefijo `IABOT_` para evitar colisiones

### Nueva estructura de Usuarios (ABCMASplus)

```sql
-- Permanece en ABCMASplus.dbo.Usuarios (sin cambios de ubicación)
SELECT [idUsuario], [Nombre], [Password], [idRol], [email],
       [puesto], [UltimoAcceso], [EstatusLDAP], [TipoCuentaLDAP],
       [Empresa], [Activa]
FROM [ABCMASplus].[dbo].[Usuarios]
```

### Nueva estructura de Gerencias (ABCMASplus)

```sql
-- Permanece en ABCMASplus.dbo.Gerencias (sin cambios de ubicación)
SELECT [idGerencia], [idGerente], [idResponsable], [Gerencia],
       [CentroCostos], [idDireccion], [GrupoDeCorreo],
       [id_ChatTelegram], [Nickname]
FROM [ABCMASplus].[dbo].[Gerencias]
```

### Nueva estructura de GerenciasUsuarios (ABCMASplus)

```sql
-- Permanece en ABCMASplus.dbo.GerenciasUsuarios (sin cambios de ubicación)
SELECT [IdGerencia], [IdUsuario]
FROM [ABCMASplus].[dbo].[GerenciasUsuarios]
```

---

## Mapeo de Tablas

### Tablas que NO se mueven (permanecen en ABCMASplus.dbo)

| Tabla actual | Tabla nueva | Base de datos |
|---|---|---|
| Usuarios | Usuarios (misma) | ABCMASplus |
| Gerencias | Gerencias (misma) | ABCMASplus |
| GerenciasUsuarios | GerenciasUsuarios (misma) | ABCMASplus |

### Tablas que se renombran y mueven a consolamonitoreo.dbo

| Tabla actual (ABCMASplus) | Tabla nueva (consolamonitoreo) |
|---|---|
| Roles | IABOT_Roles |
| RolesIA | IABOT_RolesIA |
| UsuariosTelegram | IABOT_UsuariosTelegram |
| AreaAtendedora | IABOT_AreaAtendedora |
| GerenciasRolesIA | IABOT_GerenciasRolesIA |
| UsuariosRolesIA | IABOT_UsuariosRolesIA |
| Modulos | IABOT_Modulos |
| Operaciones | IABOT_Operaciones |
| RolesOperaciones | IABOT_RolesOperaciones |
| UsuariosOperaciones | IABOT_UsuariosOperaciones |
| LogOperaciones | IABOT_LogOperaciones |
| knowledge_categories | IABOT_knowledge_categories |
| knowledge_entries | IABOT_knowledge_entries |
| RolesCategoriesKnowledge | IABOT_RolesCategoriesKnowledge |
| table_documentation | IABOT_table_documentation |
| column_documentation | IABOT_column_documentation |
| UserMemoryProfiles | IABOT_UserMemoryProfiles |
| ChatConversaciones | IABOT_ChatConversaciones |
| ChatMensajes | IABOT_ChatMensajes |

### Stored Procedures a migrar a consolamonitoreo

| SP actual | SP nuevo |
|---|---|
| sp_VerificarPermisoOperacion | IABOT_sp_VerificarPermisoOperacion |
| sp_ObtenerOperacionesUsuario | IABOT_sp_ObtenerOperacionesUsuario |
| sp_RegistrarLogOperacion | IABOT_sp_RegistrarLogOperacion |
| sp_ActualizarActividadTelegram | IABOT_sp_ActualizarActividadTelegram |
| sp_search_knowledge | IABOT_sp_search_knowledge |

### Vistas a migrar a consolamonitoreo

| Vista actual | Vista nueva |
|---|---|
| vw_PermisosUsuarios | IABOT_vw_PermisosUsuarios |
| vw_knowledge_base | IABOT_vw_knowledge_base |

---

## Fases de Implementación

### Fase 1: Scripts SQL de Migración
- [ ] Crear script para crear tablas IABOT_* en consolamonitoreo con estructura idéntica
- [ ] Crear script para migrar datos de ABCMASplus a consolamonitoreo
- [ ] Crear script para recrear SPs en consolamonitoreo con referencias cross-database a ABCMASplus (Usuarios, Gerencias, GerenciasUsuarios)
- [ ] Crear script para recrear vistas en consolamonitoreo
- [ ] Crear script de rollback

### Fase 2: Actualizar Configuración del Proyecto
- [ ] Actualizar `src/config/settings.py` - agregar configuración para segunda base de datos (`consolamonitoreo`)
- [ ] Actualizar `src/database/connection.py` - soporte para conexiones a ambas bases de datos
- [ ] Actualizar `.env` / variables de entorno con nueva conexión

### Fase 3: Actualizar Código Python - Tablas Renombradas
- [ ] `src/auth/registration.py` - Actualizar referencias a UsuariosTelegram → IABOT_UsuariosTelegram
- [ ] `src/auth/user_manager.py` - Actualizar referencias a UsuariosTelegram, Roles, LogOperaciones
- [ ] `src/auth/permission_checker.py` - Actualizar referencias a Operaciones, RolesOperaciones, SPs
- [ ] `src/memory/repository.py` - Actualizar referencias a UserMemoryProfiles, LogOperaciones
- [ ] `src/agent/memory/memory_repository.py` - Actualizar referencias a UserMemoryProfiles, LogOperaciones
- [ ] `src/agent/knowledge/knowledge_repository.py` - Actualizar referencias a knowledge_entries, knowledge_categories, RolesCategoriesKnowledge
- [ ] `src/agents/tools/preference_tool.py` - Actualizar referencias a UserMemoryProfiles, UsuariosTelegram
- [ ] `src/agents/tools/database_tool.py` - Actualizar queries genéricas

### Fase 4: Actualizar Código Python - Nueva Estructura de Usuarios
- [ ] Actualizar modelos/schemas que referencian columnas de Usuarios (nueva estructura: Nombre, Password, idRol, email, puesto, UltimoAcceso, EstatusLDAP, TipoCuentaLDAP, Empresa, Activa)
- [ ] Actualizar modelos/schemas de Gerencias (nueva estructura: idGerente, idResponsable, Gerencia, CentroCostos, idDireccion, GrupoDeCorreo, id_ChatTelegram, Nickname)
- [ ] Actualizar modelos/schemas de GerenciasUsuarios (estructura simplificada: IdGerencia, IdUsuario)
- [ ] Actualizar queries en `src/auth/user_manager.py` para usar nuevas columnas
- [ ] Actualizar queries en `src/auth/registration.py` para usar nuevas columnas

### Fase 5: Actualizar Referencias Cross-Database
- [ ] Las queries que JOINean tablas del bot con Usuarios/Gerencias deben usar referencia cross-database: `ABCMASplus.dbo.Usuarios`
- [ ] Las queries dentro de consolamonitoreo usan nombres directos: `IABOT_Roles`, `IABOT_Operaciones`, etc.
- [ ] Actualizar SPs para referenciar cross-database donde sea necesario

### Fase 6: Actualizar Documentación
- [ ] Actualizar `.claude/context/DATABASE.md` con nueva estructura
- [ ] Actualizar `docs/sql/00 ResumenEstructura.sql`
- [ ] Actualizar `docs/sql/01 EstructuraUsuarios.sql`
- [ ] Actualizar `docs/sql/02 EstructuraPermisos.sql`
- [ ] Actualizar `docs/sql/03 EstructuraVerificacion.sql`
- [ ] Actualizar `docs/sql/04 StoredProcedures.sql`
- [ ] Crear nueva migración en `database/migrations/`

### Fase 7: Testing
- [ ] Verificar que la conexión a ambas bases de datos funcione
- [ ] Verificar autenticación y registro de usuarios
- [ ] Verificar sistema de permisos
- [ ] Verificar knowledge base
- [ ] Verificar sistema de memoria
- [ ] Verificar logging de operaciones
- [ ] Ejecutar tests existentes y corregir los que fallen

---

## Archivos Afectados (Resumen)

### Configuración
- `src/config/settings.py`
- `src/database/connection.py`
- `.env`

### Autenticación y Permisos
- `src/auth/registration.py`
- `src/auth/user_manager.py`
- `src/auth/permission_checker.py`

### Repositorios
- `src/memory/repository.py`
- `src/agent/memory/memory_repository.py`
- `src/agent/knowledge/knowledge_repository.py`

### Tools
- `src/agents/tools/preference_tool.py`
- `src/agents/tools/database_tool.py`

### SQL
- `docs/sql/*.sql`
- `database/migrations/*.sql`

### Documentación
- `.claude/context/DATABASE.md`

---

## Consideraciones Importantes

1. **Cross-database queries**: Las tablas en `consolamonitoreo` que hacen JOIN con `Usuarios` deben usar `ABCMASplus.dbo.Usuarios`
2. **Permisos SQL Server**: El usuario de la aplicación necesita permisos en ambas bases de datos
3. **Transacciones cross-database**: SQL Server soporta transacciones distribuidas pero evaluar si es necesario
4. **Rollback**: Mantener script de rollback por si se necesita revertir
5. **Compatibilidad**: La tabla Usuarios de ABCMASplus tiene estructura diferente a la documentada - adaptar el código

---

## Notas

- La tabla `Usuarios` en ABCMASplus ya no tiene `idEmpleado`, `apellido`, `fechaCreacion` - tiene `Nombre`, `Password`, `puesto`, `EstatusLDAP`, `TipoCuentaLDAP`, `Empresa`
- La tabla `Gerencias` en ABCMASplus tiene campos adicionales: `idGerente`, `CentroCostos`, `idDireccion`, `GrupoDeCorreo`, `id_ChatTelegram`, `Nickname`
- La tabla `GerenciasUsuarios` es más simple: solo `IdGerencia` e `IdUsuario` (sin campos de auditoría)
