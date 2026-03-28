# Estructura de Base de Datos - abcmasplus

## Información General
- **Base de Datos**: abcmasplus
- **Esquema**: dbo
- **SGBD**: SQL Server
- **Propósito**: Sistema de gestión de usuarios, gerencias, roles y permisos para operaciones via Telegram

---

## Tablas del Sistema

### 1. Roles
**Propósito**: Catálogo de roles del sistema

| Campo | Tipo | Descripción | Constraints |
|-------|------|-------------|-------------|
| idRol | INT (PK, IDENTITY) | Identificador único del rol | PRIMARY KEY |
| nombre | NVARCHAR(100) | Nombre del rol | NOT NULL, UNIQUE |
| fechaCreacion | DATETIME | Fecha de creación | DEFAULT GETDATE() |
| activo | BIT | Estado del rol | DEFAULT 1 |

**Relaciones**:
- Referenciado por: Usuarios.rol
- Referenciado por: RolesOperaciones.idRol

**Datos de Ejemplo**:
- 1: Administrador
- 2: Gerente
- 3: Supervisor
- 4: Analista
- 5: Usuario
- 6: Consulta
- 7: Coordinador
- 8: Especialista

---

### 2. RolesIA
**Propósito**: Roles específicos para funcionalidades de Inteligencia Artificial

| Campo | Tipo | Descripción | Constraints |
|-------|------|-------------|-------------|
| idRol | INT (PK, IDENTITY) | Identificador único del rol IA | PRIMARY KEY |
| nombre | NVARCHAR(100) | Nombre del rol IA | NOT NULL, UNIQUE |
| descripcion | NVARCHAR(500) | Descripción del rol | NULL |
| fechaCreacion | DATETIME | Fecha de creación | DEFAULT GETDATE() |
| activo | BIT | Estado del rol | DEFAULT 1 |

**Relaciones**:
- Referenciado por: GerenciasRolesIA.idRol
- Referenciado por: UsuariosRolesIA.idRol

**Datos de Ejemplo**:
- 1: Administrador IA
- 2: Analista IA Avanzado
- 3: Analista IA
- 4: Usuario IA Premium
- 5: Usuario IA
- 6: Consultor IA

---

### 3. Usuarios
**Propósito**: Usuarios del sistema

| Campo | Tipo | Descripción | Constraints |
|-------|------|-------------|-------------|
| idUsuario | INT (PK, IDENTITY) | Identificador único del usuario | PRIMARY KEY |
| idEmpleado | INT | ID del empleado | NOT NULL, UNIQUE |
| nombre | NVARCHAR(100) | Nombre del usuario | NOT NULL |
| apellido | NVARCHAR(100) | Apellido del usuario | NOT NULL |
| rol | INT | ID del rol asignado | NOT NULL, FK → Roles.idRol |
| email | NVARCHAR(150) | Correo electrónico | NOT NULL, UNIQUE |
| fechaCreacion | DATETIME | Fecha de creación | DEFAULT GETDATE() |
| fechaUltimoAcceso | DATETIME | Último acceso del usuario | NULL |
| activo | BIT | Estado del usuario | DEFAULT 1 |

**Relaciones**:
- Referencias: Roles.idRol
- Referenciado por: Gerencias.idResponsable
- Referenciado por: GerenciaUsuarios.idUsuario
- Referenciado por: UsuariosRolesIA.idUsuario
- Referenciado por: UsuariosOperaciones.idUsuario
- Referenciado por: LogOperaciones.idUsuario

**Índices**:
- IX_Usuarios_Email
- IX_Usuarios_IdEmpleado

---

### 4. Gerencias
**Propósito**: Catálogo de gerencias de la organización

| Campo | Tipo | Descripción | Constraints |
|-------|------|-------------|-------------|
| idGerencia | INT (PK, IDENTITY) | Identificador único de la gerencia | PRIMARY KEY |
| idResponsable | INT | ID del usuario responsable | NULL, FK → Usuarios.idUsuario |
| gerencia | NVARCHAR(200) | Nombre de la gerencia | NOT NULL |
| alias | NVARCHAR(50) | Alias corto de la gerencia | UNIQUE |
| correo | NVARCHAR(150) | Correo de la gerencia | NULL |
| fechaCreacion | DATETIME | Fecha de creación | DEFAULT GETDATE() |
| activo | BIT | Estado de la gerencia | DEFAULT 1 |

**Relaciones**:
- Referencias: Usuarios.idUsuario (idResponsable)
- Referenciado por: GerenciaUsuarios.idGerencia
- Referenciado por: AreaAtendedora.idGerencia
- Referenciado por: GerenciasRolesIA.idGerencia

**Datos de Ejemplo**:
- 1: Gerencia General (GG)
- 2: Gerencia de Tecnología (GTECH)
- 3: Gerencia de Recursos Humanos (GRH)
- 4: Gerencia de Finanzas (GFIN)
- 5: Gerencia de Operaciones (GOPE)

---

### 5. GerenciaUsuarios
**Propósito**: Relación muchos a muchos entre Usuarios y Gerencias

| Campo | Tipo | Descripción | Constraints |
|-------|------|-------------|-------------|
| idGerenciaUsuario | INT (PK, IDENTITY) | Identificador único | PRIMARY KEY |
| idUsuario | INT | ID del usuario | NOT NULL, FK → Usuarios.idUsuario |
| idGerencia | INT | ID de la gerencia | NOT NULL, FK → Gerencias.idGerencia |
| fechaAsignacion | DATETIME | Fecha de asignación | DEFAULT GETDATE() |
| activo | BIT | Estado de la relación | DEFAULT 1 |

**Relaciones**:
- Referencias: Usuarios.idUsuario
- Referencias: Gerencias.idGerencia

**Índices**:
- IX_GerenciaUsuarios_IdUsuario
- IX_GerenciaUsuarios_IdGerencia
- UNIQUE (idUsuario, idGerencia)

---

### 6. AreaAtendedora
**Propósito**: Gerencias que funcionan como áreas atendedoras

| Campo | Tipo | Descripción | Constraints |
|-------|------|-------------|-------------|
| idAreaAtendedora | INT (PK, IDENTITY) | Identificador único | PRIMARY KEY |
| idGerencia | INT | ID de la gerencia | NOT NULL, UNIQUE, FK → Gerencias.idGerencia |
| fechaCreacion | DATETIME | Fecha de creación | DEFAULT GETDATE() |
| activo | BIT | Estado del área | DEFAULT 1 |

**Relaciones**:
- Referencias: Gerencias.idGerencia

**Datos de Ejemplo**:
- Tecnología, RRHH, Finanzas, Logística, Calidad, Atención al Cliente

---

### 7. GerenciasRolesIA
**Propósito**: Relación muchos a muchos entre Gerencias y RolesIA

| Campo | Tipo | Descripción | Constraints |
|-------|------|-------------|-------------|
| idGerenciaRolIA | INT (PK, IDENTITY) | Identificador único | PRIMARY KEY |
| idRol | INT | ID del rol IA | NOT NULL, FK → RolesIA.idRol |
| idGerencia | INT | ID de la gerencia | NOT NULL, FK → Gerencias.idGerencia |
| fechaAsignacion | DATETIME | Fecha de asignación | DEFAULT GETDATE() |
| activo | BIT | Estado de la relación | DEFAULT 1 |

**Relaciones**:
- Referencias: RolesIA.idRol
- Referencias: Gerencias.idGerencia

**Índices**:
- IX_GerenciasRolesIA_IdRol
- IX_GerenciasRolesIA_IdGerencia
- UNIQUE (idRol, idGerencia)

---

### 8. UsuariosRolesIA
**Propósito**: Relación muchos a muchos entre Usuarios y RolesIA

| Campo | Tipo | Descripción | Constraints |
|-------|------|-------------|-------------|
| idUsuarioRolIA | INT (PK, IDENTITY) | Identificador único | PRIMARY KEY |
| idRol | INT | ID del rol IA | NOT NULL, FK → RolesIA.idRol |
| idUsuario | INT | ID del usuario | NOT NULL, FK → Usuarios.idUsuario |
| fechaAsignacion | DATETIME | Fecha de asignación | DEFAULT GETDATE() |
| activo | BIT | Estado de la relación | DEFAULT 1 |

**Relaciones**:
- Referencias: RolesIA.idRol
- Referencias: Usuarios.idUsuario

**Índices**:
- IX_UsuariosRolesIA_IdRol
- IX_UsuariosRolesIA_IdUsuario
- UNIQUE (idRol, idUsuario)

---

### 9. Modulos
**Propósito**: Módulos principales del sistema (agrupadores de operaciones)

| Campo | Tipo | Descripción | Constraints |
|-------|------|-------------|-------------|
| idModulo | INT (PK, IDENTITY) | Identificador único del módulo | PRIMARY KEY |
| nombre | NVARCHAR(100) | Nombre del módulo | NOT NULL, UNIQUE |
| descripcion | NVARCHAR(500) | Descripción del módulo | NULL |
| icono | NVARCHAR(50) | Emoji o código de icono | NULL |
| orden | INT | Orden de visualización | DEFAULT 0 |
| activo | BIT | Estado del módulo | DEFAULT 1 |
| fechaCreacion | DATETIME | Fecha de creación | DEFAULT GETDATE() |

**Relaciones**:
- Referenciado por: Operaciones.idModulo

**Datos de Ejemplo**:
- 1: Tickets 🎫
- 2: Reportes 📊
- 3: Usuarios 👥
- 4: Configuración ⚙️
- 5: Notificaciones 🔔
- 6: Consultas 🔍
- 7: Aprobaciones ✅
- 8: IA 🤖

---

### 10. Operaciones
**Propósito**: Operaciones/Acciones disponibles en el sistema (comandos de Telegram)

| Campo | Tipo | Descripción | Constraints |
|-------|------|-------------|-------------|
| idOperacion | INT (PK, IDENTITY) | Identificador único de la operación | PRIMARY KEY |
| idModulo | INT | ID del módulo al que pertenece | NOT NULL, FK → Modulos.idModulo |
| nombre | NVARCHAR(100) | Nombre de la operación | NOT NULL |
| descripcion | NVARCHAR(500) | Descripción de la operación | NULL |
| comando | NVARCHAR(100) | Comando de Telegram | UNIQUE |
| requiereParametros | BIT | Indica si requiere parámetros | DEFAULT 0 |
| parametrosEjemplo | NVARCHAR(500) | Ejemplo de uso del comando | NULL |
| nivelCriticidad | INT | Nivel crítico (1=Baja, 2=Media, 3=Alta, 4=Crítica) | DEFAULT 1 |
| orden | INT | Orden de visualización | DEFAULT 0 |
| activo | BIT | Estado de la operación | DEFAULT 1 |
| fechaCreacion | DATETIME | Fecha de creación | DEFAULT GETDATE() |

**Relaciones**:
- Referencias: Modulos.idModulo
- Referenciado por: RolesOperaciones.idOperacion
- Referenciado por: UsuariosOperaciones.idOperacion
- Referenciado por: LogOperaciones.idOperacion

**Índices**:
- IX_Operaciones_IdModulo
- IX_Operaciones_Comando

**Ejemplos de Comandos**:
- /crear_ticket - Crear un nuevo ticket
- /ver_ticket - Ver detalles de un ticket
- /mis_tickets - Ver todos mis tickets
- /reporte_diario - Generar reporte diario
- /listar_usuarios - Ver lista de usuarios
- /ia - Hacer consulta con IA

---

### 11. RolesOperaciones
**Propósito**: Relación muchos a muchos entre Roles y Operaciones (PERMISOS)

| Campo | Tipo | Descripción | Constraints |
|-------|------|-------------|-------------|
| idRolOperacion | INT (PK, IDENTITY) | Identificador único | PRIMARY KEY |
| idRol | INT | ID del rol | NOT NULL, FK → Roles.idRol |
| idOperacion | INT | ID de la operación | NOT NULL, FK → Operaciones.idOperacion |
| permitido | BIT | Permiso concedido (1) o denegado (0) | DEFAULT 1 |
| fechaAsignacion | DATETIME | Fecha de asignación | DEFAULT GETDATE() |
| usuarioAsignacion | INT | Usuario que otorgó el permiso | NULL, FK → Usuarios.idUsuario |
| observaciones | NVARCHAR(500) | Notas sobre el permiso | NULL |
| activo | BIT | Estado del permiso | DEFAULT 1 |

**Relaciones**:
- Referencias: Roles.idRol
- Referencias: Operaciones.idOperacion
- Referencias: Usuarios.idUsuario (usuarioAsignacion)

**Índices**:
- IX_RolesOperaciones_IdRol
- IX_RolesOperaciones_IdOperacion
- UNIQUE (idRol, idOperacion)

**Nota**: Esta es la tabla PRINCIPAL para gestionar qué operaciones puede realizar cada rol.

---

### 12. UsuariosOperaciones
**Propósito**: Permisos específicos por usuario (excepciones a los permisos del rol)

| Campo | Tipo | Descripción | Constraints |
|-------|------|-------------|-------------|
| idUsuarioOperacion | INT (PK, IDENTITY) | Identificador único | PRIMARY KEY |
| idUsuario | INT | ID del usuario | NOT NULL, FK → Usuarios.idUsuario |
| idOperacion | INT | ID de la operación | NOT NULL, FK → Operaciones.idOperacion |
| permitido | BIT | Permiso concedido (1) o denegado (0) | DEFAULT 1 |
| fechaAsignacion | DATETIME | Fecha de asignación | DEFAULT GETDATE() |
| fechaExpiracion | DATETIME | Fecha de expiración del permiso | NULL |
| usuarioAsignacion | INT | Usuario que otorgó el permiso | NULL, FK → Usuarios.idUsuario |
| observaciones | NVARCHAR(500) | Notas sobre el permiso | NULL |
| activo | BIT | Estado del permiso | DEFAULT 1 |

**Relaciones**:
- Referencias: Usuarios.idUsuario
- Referencias: Operaciones.idOperacion
- Referencias: Usuarios.idUsuario (usuarioAsignacion)

**Índices**:
- IX_UsuariosOperaciones_IdUsuario
- IX_UsuariosOperaciones_IdOperacion
- UNIQUE (idUsuario, idOperacion)

**Nota**: Los permisos de usuario SOBRESCRIBEN los permisos del rol. Útil para conceder o denegar permisos temporales.

---

### 13. LogOperaciones
**Propósito**: Auditoría de operaciones ejecutadas por usuarios

| Campo | Tipo | Descripción | Constraints |
|-------|------|-------------|-------------|
| idLog | BIGINT (PK, IDENTITY) | Identificador único del log | PRIMARY KEY |
| idUsuario | INT | ID del usuario que ejecutó | NOT NULL, FK → Usuarios.idUsuario |
| idOperacion | INT | ID de la operación ejecutada | NOT NULL, FK → Operaciones.idOperacion |
| telegramChatId | BIGINT | Chat ID de Telegram | NULL |
| telegramUsername | NVARCHAR(100) | Username de Telegram | NULL |
| parametros | NVARCHAR(MAX) | Parámetros enviados (JSON) | NULL |
| resultado | NVARCHAR(50) | Resultado: EXITOSO, ERROR, DENEGADO | NOT NULL |
| mensajeError | NVARCHAR(MAX) | Mensaje de error si aplica | NULL |
| duracionMs | INT | Duración en milisegundos | NULL |
| ipOrigen | NVARCHAR(50) | IP de origen | NULL |
| fechaEjecucion | DATETIME | Fecha y hora de ejecución | DEFAULT GETDATE() |

**Relaciones**:
- Referencias: Usuarios.idUsuario
- Referencias: Operaciones.idOperacion

**Índices**:
- IX_LogOperaciones_IdUsuario
- IX_LogOperaciones_IdOperacion
- IX_LogOperaciones_FechaEjecucion (DESC)
- IX_LogOperaciones_Resultado

---

## Stored Procedures

### sp_VerificarPermisoOperacion
**Propósito**: Verificar si un usuario tiene permiso para ejecutar una operación

**Parámetros**:
- @idUsuario INT - ID del usuario
- @comando NVARCHAR(100) - Comando a verificar (ej: '/crear_ticket')

**Retorna**:
- TienePermiso (BIT) - 1 si tiene permiso, 0 si no
- Mensaje (NVARCHAR) - Descripción del resultado
- NombreOperacion (NVARCHAR) - Nombre de la operación
- DescripcionOperacion (NVARCHAR) - Descripción de la operación
- RequiereParametros (BIT) - Si requiere parámetros
- ParametrosEjemplo (NVARCHAR) - Ejemplo de uso

**Lógica**:
1. Verifica si el usuario existe y está activo
2. Busca la operación por comando
3. Verifica primero permisos específicos del usuario (prioridad alta)
4. Si no hay permiso específico, verifica permisos del rol
5. Retorna el resultado

**Ejemplo de Uso**:
```sql
EXEC sp_VerificarPermisoOperacion @idUsuario = 5, @comando = '/crear_ticket'
```

---

### sp_ObtenerOperacionesUsuario
**Propósito**: Obtener todas las operaciones disponibles para un usuario

**Parámetros**:
- @idUsuario INT - ID del usuario

**Retorna**:
- Modulo - Nombre del módulo
- IconoModulo - Icono del módulo
- idOperacion - ID de la operación
- Operacion - Nombre de la operación
- descripcion - Descripción
- comando - Comando de Telegram
- requiereParametros - Si requiere parámetros
- parametrosEjemplo - Ejemplo de uso
- nivelCriticidad - Nivel de criticidad
- OrigenPermiso - 'Usuario' o 'Rol'
- Permitido - 1 si está permitido

**Lógica**:
1. Obtiene el rol del usuario
2. Consulta operaciones del rol
3. Consulta permisos específicos del usuario
4. Combina ambos resultados
5. Filtra solo operaciones permitidas

**Ejemplo de Uso**:
```sql
EXEC sp_ObtenerOperacionesUsuario @idUsuario = 5
```

---

### sp_RegistrarLogOperacion
**Propósito**: Registrar la ejecución de una operación para auditoría

**Parámetros**:
- @idUsuario INT - ID del usuario
- @comando NVARCHAR(100) - Comando ejecutado
- @telegramChatId BIGINT - Chat ID de Telegram (opcional)
- @telegramUsername NVARCHAR(100) - Username de Telegram (opcional)
- @parametros NVARCHAR(MAX) - Parámetros en formato JSON (opcional)
- @resultado NVARCHAR(50) - EXITOSO, ERROR, DENEGADO
- @mensajeError NVARCHAR(MAX) - Mensaje de error (opcional)
- @duracionMs INT - Duración en milisegundos (opcional)
- @ipOrigen NVARCHAR(50) - IP de origen (opcional)

**Ejemplo de Uso**:
```sql
EXEC sp_RegistrarLogOperacion
    @idUsuario = 5,
    @comando = '/crear_ticket',
    @telegramChatId = 123456789,
    @telegramUsername = 'usuario_telegram',
    @parametros = '{"descripcion":"Problema con servidor"}',
    @resultado = 'EXITOSO',
    @duracionMs = 234
```

---

## Vistas

### vw_PermisosUsuarios
**Propósito**: Vista consolidada de todos los permisos por usuario

**Columnas**:
- idUsuario
- idEmpleado
- NombreCompleto
- email
- Rol
- Modulo
- Operacion
- comando
- descripcion
- TienePermiso (BIT)
- TipoPermiso ('Permiso Usuario', 'Permiso Rol', 'Sin Permiso')

**Uso**:
```sql
SELECT * FROM vw_PermisosUsuarios WHERE idUsuario = 5
```

---

### 14. UsuariosTelegram
**Propósito**: Almacena las cuentas de Telegram asociadas a cada usuario

| Campo | Tipo | Descripción | Constraints |
|-------|------|-------------|-------------|
| idUsuarioTelegram | INT (PK, IDENTITY) | Identificador único de la cuenta | PRIMARY KEY |
| idUsuario | INT | ID del usuario propietario | NOT NULL, FK → Usuarios.idUsuario |
| telegramChatId | BIGINT | Chat ID único de Telegram | NOT NULL, UNIQUE |
| telegramUsername | NVARCHAR(100) | Username de Telegram (@usuario) | NULL |
| telegramFirstName | NVARCHAR(100) | Nombre en Telegram | NULL |
| telegramLastName | NVARCHAR(100) | Apellido en Telegram | NULL |
| alias | NVARCHAR(50) | Alias personalizado para la cuenta | NULL |
| esPrincipal | BIT | Indica si es la cuenta principal | DEFAULT 0 |
| estado | NVARCHAR(20) | Estado de la cuenta | DEFAULT 'ACTIVO', CHECK IN ('ACTIVO', 'SUSPENDIDO', 'BLOQUEADO') |
| fechaRegistro | DATETIME | Fecha de registro de la cuenta | DEFAULT GETDATE() |
| fechaUltimaActividad | DATETIME | Última actividad registrada | NULL |
| fechaVerificacion | DATETIME | Fecha de verificación | NULL |
| codigoVerificacion | NVARCHAR(10) | Código temporal para verificación | NULL |
| verificado | BIT | Indica si la cuenta está verificada | DEFAULT 0 |
| intentosVerificacion | INT | Contador de intentos fallidos | DEFAULT 0 |
| notificacionesActivas | BIT | Control de notificaciones | DEFAULT 1 |
| observaciones | NVARCHAR(500) | Notas adicionales | NULL |
| activo | BIT | Estado del registro | DEFAULT 1 |
| fechaCreacion | DATETIME | Fecha de creación del registro | DEFAULT GETDATE() |
| usuarioCreacion | INT | Usuario que creó el registro | NULL, FK → Usuarios.idUsuario |
| fechaModificacion | DATETIME | Fecha de última modificación | NULL |
| usuarioModificacion | INT | Usuario que modificó | NULL, FK → Usuarios.idUsuario |

**Relaciones**:
- Referencias: Usuarios.idUsuario (propietario de la cuenta)
- Referencias: Usuarios.idUsuario (usuarioCreacion)
- Referencias: Usuarios.idUsuario (usuarioModificacion)
- Referenciado por: LogOperaciones.telegramChatId (relación lógica, no FK)

**Índices**:
- IX_UsuariosTelegram_IdUsuario
- IX_UsuariosTelegram_ChatId
- IX_UsuariosTelegram_Username
- IX_UsuariosTelegram_Estado

**Reglas de Negocio**:
- Un usuario puede tener múltiples cuentas de Telegram
- Solo una cuenta puede ser principal (esPrincipal = 1) por usuario
- El telegramChatId debe ser único en todo el sistema
- Máximo 5 intentos de verificación antes de bloqueo automático
- Código de verificación es de 6 dígitos numéricos

**Estados Posibles**:
- **ACTIVO**: Cuenta operativa y en uso
- **SUSPENDIDO**: Cuenta temporalmente suspendida
- **BLOQUEADO**: Cuenta bloqueada por seguridad (ej: exceso de intentos)

**Datos de Ejemplo**:
```
idUsuario=1, chatId=1001234567, username='juanperez_admin', 
esPrincipal=1, verificado=1, notificacionesActivas=1
```

---

## Diagrama de Relaciones Simplificado

```
Roles (1) ─────< (N) Usuarios (N) >───── (N) Gerencias
  │                    │    │                   │
  │                    │    │                   │
  └──< RolesOperaciones  │    └──< UsuariosOperaciones  └──< AreaAtendedora
           │             │              │
           │             │              │
      Operaciones <──────┘              │
           │                            │
           │                            │
      Modulos                    UsuariosTelegram (1) ──< (N) Usuarios
                                      │
                                      └─── telegramChatId (usado en LogOperaciones)

RolesIA (1) ─────< (N) UsuariosRolesIA (N) >───── (N) Usuarios
   │
   └────< GerenciasRolesIA (N) >───── (N) Gerencias
```

**Nota sobre UsuariosTelegram**: 
- Un Usuario puede tener múltiples cuentas de Telegram (relación 1:N)
- Solo una puede ser principal (esPrincipal = 1)
- El telegramChatId se usa en LogOperaciones para auditoría

---

## Flujo de Validación de Permisos

```
1. Usuario ejecuta comando en Telegram (ej: /crear_ticket)
   ↓
2. Sistema llama: sp_VerificarPermisoOperacion(@idUsuario, '/crear_ticket')
   ↓
3. Stored Procedure verifica en este orden:
   a. ¿Existe permiso específico en UsuariosOperaciones? → Usar ese
   b. Si no, ¿existe permiso en RolesOperaciones para su rol? → Usar ese
   c. Si no, → DENEGAR
   ↓
4. Si tiene permiso:
   - Ejecutar operación
   - Registrar en LogOperaciones con sp_RegistrarLogOperacion
5. Si no tiene permiso:
   - Retornar mensaje de error
   - Registrar intento en LogOperaciones (resultado='DENEGADO')
```

---

## Niveles de Criticidad de Operaciones

- **Nivel 1 (Baja)**: Consultas, lecturas, operaciones sin impacto
- **Nivel 2 (Media)**: Creación y modificación de registros
- **Nivel 3 (Alta)**: Asignaciones, reasignaciones, cambios importantes
- **Nivel 4 (Crítica)**: Eliminaciones, backups, cambios de configuración

---

## Ejemplos de Consultas Útiles

### Obtener todos los permisos de un usuario
```sql
SELECT * FROM vw_PermisosUsuarios 
WHERE idUsuario = 5 AND TienePermiso = 1
ORDER BY Modulo, Operacion
```

### Listar usuarios con acceso a una operación específica
```sql
SELECT DISTINCT u.idUsuario, u.nombre, u.apellido, u.email, r.nombre AS Rol
FROM Usuarios u
INNER JOIN Roles r ON u.rol = r.idRol
LEFT JOIN RolesOperaciones ro ON r.idRol = ro.idRol
LEFT JOIN UsuariosOperaciones uo ON u.idUsuario = uo.idUsuario
WHERE (ro.idOperacion = 1 OR uo.idOperacion = 1)
  AND (ro.permitido = 1 OR uo.permitido = 1)
  AND u.activo = 1
```

### Ver auditoría de operaciones de un usuario
```sql
SELECT 
    l.fechaEjecucion,
    o.comando,
    o.nombre AS Operacion,
    l.resultado,
    l.duracionMs,
    l.parametros
FROM LogOperaciones l
INNER JOIN Operaciones o ON l.idOperacion = o.idOperacion
WHERE l.idUsuario = 5
ORDER BY l.fechaEjecucion DESC
```

### Operaciones más usadas
```sql
SELECT TOP 10
    o.comando,
    o.nombre,
    COUNT(*) AS TotalEjecuciones,
    SUM(CASE WHEN l.resultado = 'EXITOSO' THEN 1 ELSE 0 END) AS Exitosas,
    SUM(CASE WHEN l.resultado = 'ERROR' THEN 1 ELSE 0 END) AS Errores,
    SUM(CASE WHEN l.resultado = 'DENEGADO' THEN 1 ELSE 0 END) AS Denegadas
FROM LogOperaciones l
INNER JOIN Operaciones o ON l.idOperacion = o.idOperacion
GROUP BY o.idOperacion, o.comando, o.nombre
ORDER BY TotalEjecuciones DESC
```

### Usuarios de una gerencia específica
```sql
SELECT 
    u.idUsuario,
    u.nombre + ' ' + u.apellido AS NombreCompleto,
    u.email,
    r.nombre AS Rol,
    g.gerencia,
    g.alias
FROM Usuarios u
INNER JOIN Roles r ON u.rol = r.idRol
INNER JOIN GerenciaUsuarios gu ON u.idUsuario = gu.idUsuario
INNER JOIN Gerencias g ON gu.idGerencia = g.idGerencia
WHERE g.idGerencia = 2 -- Tecnología
  AND u.activo = 1
  AND gu.activo = 1
```

### Obtener cuentas de Telegram de un usuario
```sql
SELECT 
    ut.idUsuarioTelegram,
    ut.telegramChatId,
    ut.telegramUsername,
    ut.alias,
    CASE WHEN ut.esPrincipal = 1 THEN '⭐ Principal' ELSE 'Secundaria' END AS Tipo,
    CASE WHEN ut.verificado = 1 THEN '✅ Verificada' ELSE '⏳ Pendiente' END AS Estado,
    ut.fechaUltimaActividad
FROM UsuariosTelegram ut
WHERE ut.idUsuario = 5 
  AND ut.activo = 1
ORDER BY ut.esPrincipal DESC, ut.fechaRegistro DESC
```

### Usuarios con múltiples cuentas de Telegram
```sql
SELECT 
    u.idUsuario,
    u.nombre + ' ' + u.apellido AS Usuario,
    COUNT(ut.idUsuarioTelegram) AS TotalCuentas,
    SUM(CASE WHEN ut.verificado = 1 THEN 1 ELSE 0 END) AS Verificadas,
    SUM(CASE WHEN ut.estado = 'ACTIVO' THEN 1 ELSE 0 END) AS Activas
FROM Usuarios u
INNER JOIN UsuariosTelegram ut ON u.idUsuario = ut.idUsuario
WHERE u.activo = 1
GROUP BY u.idUsuario, u.nombre, u.apellido
HAVING COUNT(ut.idUsuarioTelegram) > 1
ORDER BY TotalCuentas DESC
```

### Cuentas de Telegram pendientes de verificación
```sql
SELECT 
    u.idUsuario,
    u.nombre + ' ' + u.apellido AS Usuario,
    ut.telegramChatId,
    ut.telegramUsername,
    ut.codigoVerificacion,
    ut.intentosVerificacion,
    DATEDIFF(hour, ut.fechaRegistro, GETDATE()) AS HorasSinVerificar
FROM UsuariosTelegram ut
INNER JOIN Usuarios u ON ut.idUsuario = u.idUsuario
WHERE ut.verificado = 0 
  AND ut.activo = 1
  AND ut.estado = 'ACTIVO'
ORDER BY ut.fechaRegistro DESC
```

### Actividad reciente en Telegram por usuario
```sql
SELECT 
    u.nombre + ' ' + u.apellido AS Usuario,
    ut.telegramUsername,
    ut.alias,
    ut.fechaUltimaActividad,
    DATEDIFF(hour, ut.fechaUltimaActividad, GETDATE()) AS HorasInactivo,
    CASE 
        WHEN DATEDIFF(day, ut.fechaUltimaActividad, GETDATE()) = 0 THEN '🟢 Hoy'
        WHEN DATEDIFF(day, ut.fechaUltimaActividad, GETDATE()) <= 7 THEN '🟡 Esta semana'
        ELSE '🔴 Más de una semana'
    END AS EstadoActividad
FROM UsuariosTelegram ut
INNER JOIN Usuarios u ON ut.idUsuario = u.idUsuario
WHERE ut.activo = 1 
  AND ut.verificado = 1
ORDER BY ut.fechaUltimaActividad DESC
```

---

## Notas Importantes para Integración con Telegram

1. **Validación de Comandos**: Siempre usar `sp_VerificarPermisoOperacion` antes de ejecutar cualquier operación
2. **Logging**: Registrar TODAS las operaciones con `sp_RegistrarLogOperacion` para auditoría
3. **Permisos Temporales**: Verificar `fechaExpiracion` en `UsuariosOperaciones`
4. **Comandos Únicos**: Cada comando debe ser único en la tabla `Operaciones`
5. **Parámetros**: Si `requiereParametros = 1`, validar que el usuario envíe los parámetros necesarios
6. **Criticidad**: Considerar agregar confirmación adicional para operaciones de nivel 3 y 4
7. **Chat ID**: Usar `telegramChatId` de la tabla `UsuariosTelegram` para identificar usuarios
8. **Verificación**: Siempre verificar que la cuenta esté verificada (`verificado = 1`) antes de permitir operaciones sensibles
9. **Cuenta Principal**: Para notificaciones importantes, usar la cuenta con `esPrincipal = 1`
10. **Actualizar Actividad**: Llamar a `sp_ActualizarActividadTelegram` en cada interacción para mantener el registro actualizado
11. **Múltiples Cuentas**: Un usuario puede tener varias cuentas, manejar correctamente este escenario
12. **Estado de Cuenta**: Verificar que `estado = 'ACTIVO'` y `activo = 1` antes de procesar comandos

---

## Estadísticas del Sistema

### Tablas por Categoría
- **Gestión de Usuarios**: 4 tablas (Usuarios, Roles, RolesIA, UsuariosTelegram)
- **Gestión de Gerencias**: 4 tablas (Gerencias, GerenciaUsuarios, AreaAtendedora, GerenciasRolesIA)
- **Sistema de Permisos**: 3 tablas (Modulos, Operaciones, RolesOperaciones)
- **Permisos Específicos**: 1 tabla (UsuariosOperaciones)
- **Auditoría**: 1 tabla (LogOperaciones)
- **Relaciones**: 2 tablas (UsuariosRolesIA, GerenciasRolesIA)

### Total de Tablas: 14

### Datos de Prueba Disponibles
- 8 Roles
- 6 Roles IA
- 20 Usuarios
- 10 Gerencias
- 8 Módulos
- 37 Operaciones
- 139 Permisos por Rol
- 3 Permisos específicos de Usuario
- 5 Logs de ejemplo

---

## Consideraciones de Seguridad

1. **Permisos en Cascada**: Los permisos de usuario sobrescriben los del rol
2. **Auditoría Completa**: Todos los intentos de operación se registran
3. **Permisos Temporales**: Usar `fechaExpiracion` para permisos temporales
4. **Desactivación**: Nunca eliminar registros, usar campo `activo = 0`
5. **Validación Doble**: Validar permisos tanto en aplicación como en base de datos
6. **Trazabilidad**: Campo `usuarioAsignacion` registra quién otorgó el permiso

---

## Extensiones Futuras Sugeridas

1. **Grupos de Usuarios**: Tabla adicional para agrupar usuarios
2. **Horarios de Acceso**: Restricciones por horario para operaciones críticas
3. **Geolocalización**: Restricciones por ubicación geográfica
4. **MFA**: Tabla para registro de autenticación multifactor
5. **Workflows**: Tabla para definir flujos de aprobación
6. **Notificaciones Automáticas**: Disparadores para envío automático de notificaciones
7. **Rate Limiting**: Control de frecuencia de ejecución por operación/usuario

---

Última actualización: 2025-10-29