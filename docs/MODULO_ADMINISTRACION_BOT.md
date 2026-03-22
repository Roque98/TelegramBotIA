# Módulo de Administración del Bot - Requerimientos y Queries

## Información General

- **Proyecto**: Agente de Base de Datos con Telegram (IRIS)
- **Base de Datos**: abcmasplus
- **Esquema**: dbo
- **Fecha**: 2025-12-01
- **Versión**: 1.0

---

## 1. Descripción General

El **Módulo de Administración del Bot** es una interfaz web que permitirá gestionar de forma centralizada todos los aspectos del bot de Telegram, incluyendo usuarios, permisos, operaciones, knowledge base, auditoría y configuración.

---

## 2. Objetivos del Módulo

1. **Centralizar la administración** de todos los componentes del bot
2. **Facilitar la gestión de usuarios y permisos** sin necesidad de modificar la base de datos directamente
3. **Monitorear el uso del bot** mediante dashboards y reportes
4. **Gestionar el conocimiento** (Knowledge Base) de forma dinámica
5. **Auditar todas las operaciones** realizadas por los usuarios
6. **Configurar y mantener** el sistema de forma segura

---

## 3. Módulos Funcionales

### 3.1 Dashboard Principal

**Descripción**: Panel de control con métricas clave y estado del sistema.

**Funcionalidades**:
- Total de usuarios activos/inactivos
- Total de operaciones ejecutadas (hoy, semana, mes)
- Operaciones más utilizadas
- Usuarios más activos
- Tasa de éxito de operaciones
- Alertas y notificaciones del sistema

**Queries**:

```sql
-- Total de usuarios activos
SELECT COUNT(*) as TotalUsuarios
FROM Usuarios
WHERE activo = 1;

-- Usuarios con cuentas de Telegram
SELECT
    COUNT(DISTINCT ut.idUsuario) as UsuariosConTelegram
FROM UsuariosTelegram ut
WHERE ut.activo = 1 AND ut.verificado = 1;

-- Operaciones ejecutadas hoy
SELECT COUNT(*) as OperacionesHoy
FROM LogOperaciones
WHERE CAST(fechaEjecucion AS DATE) = CAST(GETDATE() AS DATE);

-- Operaciones por resultado (hoy)
SELECT
    resultado,
    COUNT(*) as cantidad
FROM LogOperaciones
WHERE CAST(fechaEjecucion AS DATE) = CAST(GETDATE() AS DATE)
GROUP BY resultado;

-- Top 5 operaciones más utilizadas
SELECT TOP 5
    o.nombre as Operacion,
    o.comando,
    COUNT(*) as TotalEjecuciones
FROM LogOperaciones l
INNER JOIN Operaciones o ON l.idOperacion = o.idOperacion
GROUP BY o.idOperacion, o.nombre, o.comando
ORDER BY TotalEjecuciones DESC;

-- Top 5 usuarios más activos
SELECT TOP 5
    u.nombre + ' ' + u.apellido as Usuario,
    COUNT(*) as TotalOperaciones,
    MAX(l.fechaEjecucion) as UltimaActividad
FROM LogOperaciones l
INNER JOIN Usuarios u ON l.idUsuario = u.idUsuario
GROUP BY u.idUsuario, u.nombre, u.apellido
ORDER BY TotalOperaciones DESC;

-- Tasa de éxito últimos 7 días
SELECT
    CAST(fechaEjecucion AS DATE) as Fecha,
    COUNT(*) as Total,
    SUM(CASE WHEN resultado = 'EXITOSO' THEN 1 ELSE 0 END) as Exitosas,
    CAST(SUM(CASE WHEN resultado = 'EXITOSO' THEN 1.0 ELSE 0 END) / COUNT(*) * 100 AS DECIMAL(5,2)) as PorcentajeExito
FROM LogOperaciones
WHERE fechaEjecucion >= DATEADD(day, -7, GETDATE())
GROUP BY CAST(fechaEjecucion AS DATE)
ORDER BY Fecha DESC;
```

---

### 3.2 Gestión de Usuarios

**Descripción**: CRUD completo de usuarios del sistema.

**Funcionalidades**:
- Listar todos los usuarios con filtros (rol, gerencia, estado)
- Crear nuevo usuario
- Editar información del usuario
- Activar/desactivar usuario
- Ver cuentas de Telegram asociadas
- Ver historial de operaciones del usuario
- Gestionar permisos específicos del usuario

**Queries**:

```sql
-- Listar todos los usuarios con su información completa
SELECT
    u.idUsuario,
    u.idEmpleado,
    u.nombre,
    u.apellido,
    u.nombre + ' ' + u.apellido as NombreCompleto,
    u.email,
    r.nombre as Rol,
    u.fechaCreacion,
    u.fechaUltimoAcceso,
    u.activo,
    (SELECT COUNT(*) FROM UsuariosTelegram ut WHERE ut.idUsuario = u.idUsuario AND ut.activo = 1) as CuentasTelegram,
    (SELECT COUNT(*) FROM LogOperaciones lo WHERE lo.idUsuario = u.idUsuario) as TotalOperaciones
FROM Usuarios u
INNER JOIN Roles r ON u.rol = r.idRol
ORDER BY u.nombre, u.apellido;

-- Obtener usuario por ID con detalles completos
SELECT
    u.idUsuario,
    u.idEmpleado,
    u.nombre,
    u.apellido,
    u.email,
    u.rol,
    r.nombre as RolNombre,
    u.fechaCreacion,
    u.fechaUltimoAcceso,
    u.activo
FROM Usuarios u
INNER JOIN Roles r ON u.rol = r.idRol
WHERE u.idUsuario = @idUsuario;

-- Crear nuevo usuario
INSERT INTO Usuarios (idEmpleado, nombre, apellido, rol, email, activo)
VALUES (@idEmpleado, @nombre, @apellido, @rol, @email, 1);
SELECT SCOPE_IDENTITY() as idUsuario;

-- Actualizar usuario
UPDATE Usuarios
SET
    nombre = @nombre,
    apellido = @apellido,
    email = @email,
    rol = @rol,
    activo = @activo
WHERE idUsuario = @idUsuario;

-- Desactivar usuario
UPDATE Usuarios
SET activo = 0
WHERE idUsuario = @idUsuario;

-- Obtener cuentas de Telegram del usuario
SELECT
    ut.idUsuarioTelegram,
    ut.telegramChatId,
    ut.telegramUsername,
    ut.telegramFirstName,
    ut.telegramLastName,
    ut.alias,
    ut.esPrincipal,
    ut.estado,
    ut.verificado,
    ut.fechaRegistro,
    ut.fechaUltimaActividad,
    ut.notificacionesActivas
FROM UsuariosTelegram ut
WHERE ut.idUsuario = @idUsuario AND ut.activo = 1
ORDER BY ut.esPrincipal DESC, ut.fechaRegistro DESC;

-- Obtener gerencias del usuario
SELECT
    g.idGerencia,
    g.gerencia,
    g.alias,
    gu.fechaAsignacion
FROM GerenciaUsuarios gu
INNER JOIN Gerencias g ON gu.idGerencia = g.idGerencia
WHERE gu.idUsuario = @idUsuario AND gu.activo = 1;

-- Obtener roles IA del usuario
SELECT
    ri.idRol,
    ri.nombre,
    ri.descripcion,
    uri.fechaAsignacion
FROM UsuariosRolesIA uri
INNER JOIN RolesIA ri ON uri.idRol = ri.idRol
WHERE uri.idUsuario = @idUsuario AND uri.activo = 1;
```

---

### 3.3 Gestión de Cuentas de Telegram

**Descripción**: Administrar las cuentas de Telegram vinculadas a usuarios.

**Funcionalidades**:
- Listar todas las cuentas de Telegram
- Ver cuentas pendientes de verificación
- Verificar/rechazar cuentas manualmente
- Establecer cuenta principal
- Suspender/bloquear cuentas
- Ver historial de actividad por cuenta

**Queries**:

```sql
-- Listar todas las cuentas de Telegram
SELECT
    ut.idUsuarioTelegram,
    u.nombre + ' ' + u.apellido as Usuario,
    ut.telegramChatId,
    ut.telegramUsername,
    ut.telegramFirstName,
    ut.telegramLastName,
    ut.alias,
    ut.esPrincipal,
    ut.estado,
    ut.verificado,
    ut.fechaRegistro,
    ut.fechaUltimaActividad,
    DATEDIFF(hour, ut.fechaUltimaActividad, GETDATE()) as HorasInactivo
FROM UsuariosTelegram ut
INNER JOIN Usuarios u ON ut.idUsuario = u.idUsuario
WHERE ut.activo = 1
ORDER BY ut.fechaUltimaActividad DESC;

-- Cuentas pendientes de verificación
SELECT
    ut.idUsuarioTelegram,
    u.nombre + ' ' + u.apellido as Usuario,
    u.email,
    ut.telegramChatId,
    ut.telegramUsername,
    ut.codigoVerificacion,
    ut.intentosVerificacion,
    ut.fechaRegistro,
    DATEDIFF(hour, ut.fechaRegistro, GETDATE()) as HorasSinVerificar
FROM UsuariosTelegram ut
INNER JOIN Usuarios u ON ut.idUsuario = u.idUsuario
WHERE ut.verificado = 0
  AND ut.activo = 1
  AND ut.estado = 'ACTIVO'
ORDER BY ut.fechaRegistro DESC;

-- Verificar cuenta manualmente
UPDATE UsuariosTelegram
SET
    verificado = 1,
    fechaVerificacion = GETDATE(),
    codigoVerificacion = NULL
WHERE idUsuarioTelegram = @idUsuarioTelegram;

-- Establecer cuenta como principal
-- Primero quitar principal de otras cuentas
UPDATE UsuariosTelegram
SET esPrincipal = 0
WHERE idUsuario = @idUsuario AND activo = 1;

-- Luego establecer la nueva principal
UPDATE UsuariosTelegram
SET esPrincipal = 1
WHERE idUsuarioTelegram = @idUsuarioTelegram;

-- Suspender cuenta
UPDATE UsuariosTelegram
SET estado = 'SUSPENDIDO'
WHERE idUsuarioTelegram = @idUsuarioTelegram;

-- Bloquear cuenta
UPDATE UsuariosTelegram
SET estado = 'BLOQUEADO'
WHERE idUsuarioTelegram = @idUsuarioTelegram;

-- Reactivar cuenta
UPDATE UsuariosTelegram
SET estado = 'ACTIVO'
WHERE idUsuarioTelegram = @idUsuarioTelegram;

-- Usuarios con múltiples cuentas
SELECT
    u.idUsuario,
    u.nombre + ' ' + u.apellido as Usuario,
    COUNT(ut.idUsuarioTelegram) as TotalCuentas,
    SUM(CASE WHEN ut.verificado = 1 THEN 1 ELSE 0 END) as Verificadas,
    SUM(CASE WHEN ut.estado = 'ACTIVO' THEN 1 ELSE 0 END) as Activas
FROM Usuarios u
INNER JOIN UsuariosTelegram ut ON u.idUsuario = ut.idUsuario
WHERE u.activo = 1
GROUP BY u.idUsuario, u.nombre, u.apellido
HAVING COUNT(ut.idUsuarioTelegram) > 1
ORDER BY TotalCuentas DESC;
```

---

### 3.4 Gestión de Roles y Permisos

**Descripción**: Administrar roles del sistema y sus permisos asociados.

**Funcionalidades**:
- Listar todos los roles
- Crear/editar roles
- Ver operaciones permitidas por rol
- Asignar/revocar permisos a roles
- Gestionar permisos específicos de usuarios (excepciones)
- Ver matriz de permisos completa

**Queries**:

```sql
-- Listar todos los roles con estadísticas
SELECT
    r.idRol,
    r.nombre,
    r.fechaCreacion,
    r.activo,
    (SELECT COUNT(*) FROM Usuarios u WHERE u.rol = r.idRol AND u.activo = 1) as TotalUsuarios,
    (SELECT COUNT(*) FROM RolesOperaciones ro WHERE ro.idRol = r.idRol AND ro.permitido = 1 AND ro.activo = 1) as PermisosAsignados
FROM Roles r
ORDER BY r.nombre;

-- Obtener permisos de un rol específico
SELECT
    m.nombre as Modulo,
    m.icono as IconoModulo,
    o.idOperacion,
    o.nombre as Operacion,
    o.comando,
    o.descripcion,
    o.nivelCriticidad,
    ro.permitido,
    ro.fechaAsignacion
FROM Operaciones o
INNER JOIN Modulos m ON o.idModulo = m.idModulo
LEFT JOIN RolesOperaciones ro ON o.idOperacion = ro.idOperacion AND ro.idRol = @idRol AND ro.activo = 1
WHERE o.activo = 1 AND m.activo = 1
ORDER BY m.orden, o.orden;

-- Asignar permiso a rol
IF NOT EXISTS (SELECT 1 FROM RolesOperaciones WHERE idRol = @idRol AND idOperacion = @idOperacion)
BEGIN
    INSERT INTO RolesOperaciones (idRol, idOperacion, permitido, usuarioAsignacion)
    VALUES (@idRol, @idOperacion, @permitido, @usuarioAsignacion);
END
ELSE
BEGIN
    UPDATE RolesOperaciones
    SET permitido = @permitido,
        fechaAsignacion = GETDATE(),
        usuarioAsignacion = @usuarioAsignacion,
        activo = 1
    WHERE idRol = @idRol AND idOperacion = @idOperacion;
END

-- Revocar permiso de rol
UPDATE RolesOperaciones
SET activo = 0
WHERE idRol = @idRol AND idOperacion = @idOperacion;

-- Permisos específicos de usuario (excepciones)
SELECT
    u.idUsuario,
    u.nombre + ' ' + u.apellido as Usuario,
    r.nombre as Rol,
    o.nombre as Operacion,
    o.comando,
    uo.permitido,
    uo.fechaAsignacion,
    uo.fechaExpiracion,
    uo.observaciones
FROM UsuariosOperaciones uo
INNER JOIN Usuarios u ON uo.idUsuario = u.idUsuario
INNER JOIN Roles r ON u.rol = r.idRol
INNER JOIN Operaciones o ON uo.idOperacion = o.idOperacion
WHERE uo.activo = 1
  AND (uo.fechaExpiracion IS NULL OR uo.fechaExpiracion > GETDATE())
ORDER BY u.nombre, u.apellido, o.nombre;

-- Asignar permiso específico a usuario
INSERT INTO UsuariosOperaciones
    (idUsuario, idOperacion, permitido, fechaExpiracion, usuarioAsignacion, observaciones)
VALUES
    (@idUsuario, @idOperacion, @permitido, @fechaExpiracion, @usuarioAsignacion, @observaciones);

-- Matriz completa de permisos (Vista consolidada)
SELECT
    r.nombre as Rol,
    m.nombre as Modulo,
    o.nombre as Operacion,
    o.comando,
    CASE WHEN ro.permitido = 1 THEN '✓' ELSE '✗' END as Permitido,
    o.nivelCriticidad
FROM Roles r
CROSS JOIN Operaciones o
INNER JOIN Modulos m ON o.idModulo = m.idModulo
LEFT JOIN RolesOperaciones ro ON r.idRol = ro.idRol AND o.idOperacion = ro.idOperacion AND ro.activo = 1
WHERE r.activo = 1 AND o.activo = 1 AND m.activo = 1
ORDER BY r.nombre, m.orden, o.orden;
```

---

### 3.5 Gestión de Operaciones y Módulos

**Descripción**: Administrar las operaciones (comandos) disponibles en el bot.

**Funcionalidades**:
- Listar todos los módulos
- Crear/editar/desactivar módulos
- Listar todas las operaciones por módulo
- Crear/editar/desactivar operaciones
- Configurar comandos de Telegram
- Establecer nivel de criticidad
- Ver uso de cada operación

**Queries**:

```sql
-- Listar todos los módulos
SELECT
    m.idModulo,
    m.nombre,
    m.descripcion,
    m.icono,
    m.orden,
    m.activo,
    m.fechaCreacion,
    (SELECT COUNT(*) FROM Operaciones o WHERE o.idModulo = m.idModulo AND o.activo = 1) as TotalOperaciones
FROM Modulos m
ORDER BY m.orden, m.nombre;

-- Crear módulo
INSERT INTO Modulos (nombre, descripcion, icono, orden, activo)
VALUES (@nombre, @descripcion, @icono, @orden, 1);
SELECT SCOPE_IDENTITY() as idModulo;

-- Actualizar módulo
UPDATE Modulos
SET
    nombre = @nombre,
    descripcion = @descripcion,
    icono = @icono,
    orden = @orden,
    activo = @activo
WHERE idModulo = @idModulo;

-- Listar operaciones por módulo
SELECT
    o.idOperacion,
    o.nombre,
    o.descripcion,
    o.comando,
    o.requiereParametros,
    o.parametrosEjemplo,
    o.nivelCriticidad,
    o.orden,
    o.activo,
    m.nombre as Modulo,
    m.icono as IconoModulo,
    (SELECT COUNT(*) FROM LogOperaciones lo WHERE lo.idOperacion = o.idOperacion) as TotalUsos
FROM Operaciones o
INNER JOIN Modulos m ON o.idModulo = m.idModulo
WHERE m.idModulo = @idModulo
ORDER BY o.orden, o.nombre;

-- Todas las operaciones con estadísticas
SELECT
    o.idOperacion,
    m.nombre as Modulo,
    m.icono as IconoModulo,
    o.nombre,
    o.comando,
    o.descripcion,
    o.nivelCriticidad,
    o.activo,
    COUNT(DISTINCT ro.idRol) as RolesConPermiso,
    (SELECT COUNT(*) FROM LogOperaciones lo WHERE lo.idOperacion = o.idOperacion) as TotalEjecuciones,
    (SELECT COUNT(*) FROM LogOperaciones lo WHERE lo.idOperacion = o.idOperacion AND lo.resultado = 'EXITOSO') as Exitosas,
    (SELECT COUNT(*) FROM LogOperaciones lo WHERE lo.idOperacion = o.idOperacion AND lo.resultado = 'ERROR') as Errores
FROM Operaciones o
INNER JOIN Modulos m ON o.idModulo = m.idModulo
LEFT JOIN RolesOperaciones ro ON o.idOperacion = ro.idOperacion AND ro.permitido = 1 AND ro.activo = 1
WHERE o.activo = 1 AND m.activo = 1
GROUP BY o.idOperacion, m.nombre, m.icono, o.nombre, o.comando, o.descripcion, o.nivelCriticidad, o.activo
ORDER BY m.nombre, o.nombre;

-- Crear operación
INSERT INTO Operaciones
    (idModulo, nombre, descripcion, comando, requiereParametros, parametrosEjemplo, nivelCriticidad, orden)
VALUES
    (@idModulo, @nombre, @descripcion, @comando, @requiereParametros, @parametrosEjemplo, @nivelCriticidad, @orden);
SELECT SCOPE_IDENTITY() as idOperacion;

-- Actualizar operación
UPDATE Operaciones
SET
    nombre = @nombre,
    descripcion = @descripcion,
    comando = @comando,
    requiereParametros = @requiereParametros,
    parametrosEjemplo = @parametrosEjemplo,
    nivelCriticidad = @nivelCriticidad,
    orden = @orden,
    activo = @activo
WHERE idOperacion = @idOperacion;
```

---

### 3.6 Gestión de Gerencias

**Descripción**: Administrar las gerencias de la organización.

**Funcionalidades**:
- Listar todas las gerencias
- Crear/editar gerencias
- Asignar responsables
- Asignar usuarios a gerencias
- Ver áreas atendedoras
- Asignar roles IA a gerencias

**Queries**:

```sql
-- Listar todas las gerencias
SELECT
    g.idGerencia,
    g.gerencia,
    g.alias,
    g.correo,
    g.idResponsable,
    u.nombre + ' ' + u.apellido as Responsable,
    g.fechaCreacion,
    g.activo,
    (SELECT COUNT(*) FROM GerenciaUsuarios gu WHERE gu.idGerencia = g.idGerencia AND gu.activo = 1) as TotalUsuarios,
    (SELECT COUNT(*) FROM AreaAtendedora aa WHERE aa.idGerencia = g.idGerencia AND aa.activo = 1) as EsAreaAtendedora
FROM Gerencias g
LEFT JOIN Usuarios u ON g.idResponsable = u.idUsuario
ORDER BY g.gerencia;

-- Crear gerencia
INSERT INTO Gerencias (gerencia, alias, correo, idResponsable, activo)
VALUES (@gerencia, @alias, @correo, @idResponsable, 1);
SELECT SCOPE_IDENTITY() as idGerencia;

-- Actualizar gerencia
UPDATE Gerencias
SET
    gerencia = @gerencia,
    alias = @alias,
    correo = @correo,
    idResponsable = @idResponsable,
    activo = @activo
WHERE idGerencia = @idGerencia;

-- Usuarios de una gerencia
SELECT
    u.idUsuario,
    u.nombre + ' ' + u.apellido as Usuario,
    u.email,
    r.nombre as Rol,
    gu.fechaAsignacion
FROM GerenciaUsuarios gu
INNER JOIN Usuarios u ON gu.idUsuario = u.idUsuario
INNER JOIN Roles r ON u.rol = r.idRol
WHERE gu.idGerencia = @idGerencia AND gu.activo = 1
ORDER BY u.nombre, u.apellido;

-- Asignar usuario a gerencia
INSERT INTO GerenciaUsuarios (idUsuario, idGerencia, activo)
VALUES (@idUsuario, @idGerencia, 1);

-- Remover usuario de gerencia
UPDATE GerenciaUsuarios
SET activo = 0
WHERE idUsuario = @idUsuario AND idGerencia = @idGerencia;

-- Áreas atendedoras
SELECT
    g.idGerencia,
    g.gerencia,
    g.alias,
    aa.fechaCreacion,
    aa.activo
FROM AreaAtendedora aa
INNER JOIN Gerencias g ON aa.idGerencia = g.idGerencia
WHERE aa.activo = 1
ORDER BY g.gerencia;

-- Marcar gerencia como área atendedora
INSERT INTO AreaAtendedora (idGerencia, activo)
VALUES (@idGerencia, 1);
```

---

### 3.7 Auditoría y Logs

**Descripción**: Sistema de auditoría completo de todas las operaciones.

**Funcionalidades**:
- Ver log completo de operaciones
- Filtrar por usuario, operación, fecha, resultado
- Ver detalles de cada operación (parámetros, duración, errores)
- Exportar logs a CSV/Excel
- Dashboard de auditoría con gráficos
- Alertas de operaciones fallidas

**Queries**:

```sql
-- Log completo de operaciones con paginación
SELECT
    l.idLog,
    l.fechaEjecucion,
    u.nombre + ' ' + u.apellido as Usuario,
    o.nombre as Operacion,
    o.comando,
    m.nombre as Modulo,
    l.resultado,
    l.duracionMs,
    l.telegramChatId,
    l.telegramUsername
FROM LogOperaciones l
INNER JOIN Usuarios u ON l.idUsuario = u.idUsuario
INNER JOIN Operaciones o ON l.idOperacion = o.idOperacion
INNER JOIN Modulos m ON o.idModulo = m.idModulo
ORDER BY l.fechaEjecucion DESC
OFFSET @offset ROWS FETCH NEXT @pageSize ROWS ONLY;

-- Log con filtros avanzados
SELECT
    l.idLog,
    l.fechaEjecucion,
    u.nombre + ' ' + u.apellido as Usuario,
    o.nombre as Operacion,
    o.comando,
    m.nombre as Modulo,
    l.resultado,
    l.duracionMs,
    l.parametros,
    l.mensajeError
FROM LogOperaciones l
INNER JOIN Usuarios u ON l.idUsuario = u.idUsuario
INNER JOIN Operaciones o ON l.idOperacion = o.idOperacion
INNER JOIN Modulos m ON o.idModulo = m.idModulo
WHERE
    (@idUsuario IS NULL OR l.idUsuario = @idUsuario)
    AND (@idOperacion IS NULL OR l.idOperacion = @idOperacion)
    AND (@resultado IS NULL OR l.resultado = @resultado)
    AND (@fechaDesde IS NULL OR l.fechaEjecucion >= @fechaDesde)
    AND (@fechaHasta IS NULL OR l.fechaEjecucion <= @fechaHasta)
ORDER BY l.fechaEjecucion DESC;

-- Detalle de una operación específica
SELECT
    l.idLog,
    l.fechaEjecucion,
    u.idUsuario,
    u.nombre + ' ' + u.apellido as Usuario,
    u.email,
    o.idOperacion,
    o.nombre as Operacion,
    o.comando,
    o.descripcion as DescripcionOperacion,
    m.nombre as Modulo,
    l.telegramChatId,
    l.telegramUsername,
    l.parametros,
    l.resultado,
    l.mensajeError,
    l.duracionMs,
    l.ipOrigen
FROM LogOperaciones l
INNER JOIN Usuarios u ON l.idUsuario = u.idUsuario
INNER JOIN Operaciones o ON l.idOperacion = o.idOperacion
INNER JOIN Modulos m ON o.idModulo = m.idModulo
WHERE l.idLog = @idLog;

-- Operaciones fallidas recientes (últimas 24 horas)
SELECT TOP 100
    l.idLog,
    l.fechaEjecucion,
    u.nombre + ' ' + u.apellido as Usuario,
    o.comando,
    l.mensajeError,
    l.telegramUsername
FROM LogOperaciones l
INNER JOIN Usuarios u ON l.idUsuario = u.idUsuario
INNER JOIN Operaciones o ON l.idOperacion = o.idOperacion
WHERE l.resultado IN ('ERROR', 'DENEGADO')
  AND l.fechaEjecucion >= DATEADD(hour, -24, GETDATE())
ORDER BY l.fechaEjecucion DESC;

-- Estadísticas por usuario
SELECT
    u.idUsuario,
    u.nombre + ' ' + u.apellido as Usuario,
    COUNT(*) as TotalOperaciones,
    SUM(CASE WHEN l.resultado = 'EXITOSO' THEN 1 ELSE 0 END) as Exitosas,
    SUM(CASE WHEN l.resultado = 'ERROR' THEN 1 ELSE 0 END) as Errores,
    SUM(CASE WHEN l.resultado = 'DENEGADO' THEN 1 ELSE 0 END) as Denegadas,
    AVG(CAST(l.duracionMs AS FLOAT)) as DuracionPromedio,
    MIN(l.fechaEjecucion) as PrimeraOperacion,
    MAX(l.fechaEjecucion) as UltimaOperacion
FROM LogOperaciones l
INNER JOIN Usuarios u ON l.idUsuario = u.idUsuario
WHERE l.fechaEjecucion >= @fechaDesde
GROUP BY u.idUsuario, u.nombre, u.apellido
ORDER BY TotalOperaciones DESC;

-- Operaciones por día (últimos 30 días)
SELECT
    CAST(l.fechaEjecucion AS DATE) as Fecha,
    COUNT(*) as Total,
    SUM(CASE WHEN l.resultado = 'EXITOSO' THEN 1 ELSE 0 END) as Exitosas,
    SUM(CASE WHEN l.resultado = 'ERROR' THEN 1 ELSE 0 END) as Errores,
    SUM(CASE WHEN l.resultado = 'DENEGADO' THEN 1 ELSE 0 END) as Denegadas
FROM LogOperaciones l
WHERE l.fechaEjecucion >= DATEADD(day, -30, GETDATE())
GROUP BY CAST(l.fechaEjecucion AS DATE)
ORDER BY Fecha DESC;

-- Duración promedio por operación
SELECT
    o.nombre as Operacion,
    o.comando,
    COUNT(*) as TotalEjecuciones,
    AVG(CAST(l.duracionMs AS FLOAT)) as DuracionPromedio,
    MIN(l.duracionMs) as DuracionMinima,
    MAX(l.duracionMs) as DuracionMaxima
FROM LogOperaciones l
INNER JOIN Operaciones o ON l.idOperacion = o.idOperacion
WHERE l.duracionMs IS NOT NULL
  AND l.fechaEjecucion >= DATEADD(day, -7, GETDATE())
GROUP BY o.idOperacion, o.nombre, o.comando
ORDER BY DuracionPromedio DESC;
```

---

### 3.8 Gestión de Knowledge Base

**Descripción**: Administrar el conocimiento del bot (preguntas y respuestas).

**Funcionalidades**:
- Listar todas las entradas de conocimiento
- Crear/editar/eliminar entradas
- Organizar por categorías
- Gestionar keywords para búsqueda
- Asignar prioridades
- Ver estadísticas de uso
- Importar/exportar knowledge base

**Queries**:

```sql
-- Listar todas las categorías de conocimiento
SELECT
    c.id,
    c.name,
    c.display_name,
    c.description,
    c.icon,
    c.active,
    COUNT(e.id) as TotalEntradas
FROM knowledge_categories c
LEFT JOIN knowledge_entries e ON c.id = e.category_id AND e.active = 1
WHERE c.active = 1
GROUP BY c.id, c.name, c.display_name, c.description, c.icon, c.active
ORDER BY c.display_name;

-- Crear categoría
INSERT INTO knowledge_categories (name, display_name, description, icon, active)
VALUES (@name, @display_name, @description, @icon, 1);
SELECT SCOPE_IDENTITY() as id;

-- Listar todas las entradas de conocimiento
SELECT
    e.id,
    e.question,
    e.answer,
    e.keywords,
    e.related_commands,
    e.priority,
    c.name as category,
    c.display_name as category_display_name,
    c.icon as category_icon,
    e.created_at,
    e.updated_at
FROM knowledge_entries e
INNER JOIN knowledge_categories c ON e.category_id = c.id
WHERE e.active = 1 AND c.active = 1
ORDER BY e.priority DESC, e.id;

-- Entradas por categoría
SELECT
    e.id,
    e.question,
    e.answer,
    e.keywords,
    e.related_commands,
    e.priority,
    e.created_at
FROM knowledge_entries e
WHERE e.category_id = @category_id AND e.active = 1
ORDER BY e.priority DESC, e.id;

-- Crear entrada de conocimiento
INSERT INTO knowledge_entries
    (category_id, question, answer, keywords, related_commands, priority, active, created_by)
VALUES
    (@category_id, @question, @answer, @keywords, @related_commands, @priority, 1, @created_by);
SELECT SCOPE_IDENTITY() as id;

-- Actualizar entrada
UPDATE knowledge_entries
SET
    category_id = @category_id,
    question = @question,
    answer = @answer,
    keywords = @keywords,
    related_commands = @related_commands,
    priority = @priority,
    updated_at = GETDATE()
WHERE id = @id;

-- Eliminar entrada (soft delete)
UPDATE knowledge_entries
SET active = 0
WHERE id = @id;

-- Buscar en knowledge base
EXEC sp_search_knowledge
    @query = @searchTerm,
    @category = @categoryFilter,
    @top_k = 10;

-- Entradas más consultadas (basado en logs)
SELECT TOP 10
    ke.id,
    ke.question,
    ke.priority,
    c.display_name as categoria,
    COUNT(*) as ConsultasRelacionadas
FROM knowledge_entries ke
INNER JOIN knowledge_categories c ON ke.category_id = c.id
LEFT JOIN LogOperaciones lo ON lo.parametros LIKE '%' + ke.question + '%'
WHERE ke.active = 1
  AND lo.fechaEjecucion >= DATEADD(day, -30, GETDATE())
GROUP BY ke.id, ke.question, ke.priority, c.display_name
ORDER BY ConsultasRelacionadas DESC;
```

---

### 3.9 Gestión de Roles IA

**Descripción**: Administrar roles específicos para funcionalidades de IA.

**Funcionalidades**:
- Listar roles IA
- Crear/editar roles IA
- Asignar roles IA a usuarios
- Asignar roles IA a gerencias
- Ver capacidades por rol IA

**Queries**:

```sql
-- Listar todos los roles IA
SELECT
    ri.idRol,
    ri.nombre,
    ri.descripcion,
    ri.fechaCreacion,
    ri.activo,
    (SELECT COUNT(*) FROM UsuariosRolesIA uri WHERE uri.idRol = ri.idRol AND uri.activo = 1) as TotalUsuarios,
    (SELECT COUNT(*) FROM GerenciasRolesIA gri WHERE gri.idRol = ri.idRol AND gri.activo = 1) as TotalGerencias
FROM RolesIA ri
ORDER BY ri.nombre;

-- Crear rol IA
INSERT INTO RolesIA (nombre, descripcion, activo)
VALUES (@nombre, @descripcion, 1);
SELECT SCOPE_IDENTITY() as idRol;

-- Actualizar rol IA
UPDATE RolesIA
SET
    nombre = @nombre,
    descripcion = @descripcion,
    activo = @activo
WHERE idRol = @idRol;

-- Usuarios con un rol IA específico
SELECT
    u.idUsuario,
    u.nombre + ' ' + u.apellido as Usuario,
    u.email,
    r.nombre as Rol,
    uri.fechaAsignacion
FROM UsuariosRolesIA uri
INNER JOIN Usuarios u ON uri.idUsuario = u.idUsuario
INNER JOIN Roles r ON u.rol = r.idRol
WHERE uri.idRol = @idRol AND uri.activo = 1
ORDER BY u.nombre, u.apellido;

-- Asignar rol IA a usuario
INSERT INTO UsuariosRolesIA (idRol, idUsuario, activo)
VALUES (@idRol, @idUsuario, 1);

-- Remover rol IA de usuario
UPDATE UsuariosRolesIA
SET activo = 0
WHERE idRol = @idRol AND idUsuario = @idUsuario;

-- Gerencias con un rol IA específico
SELECT
    g.idGerencia,
    g.gerencia,
    g.alias,
    gri.fechaAsignacion
FROM GerenciasRolesIA gri
INNER JOIN Gerencias g ON gri.idGerencia = g.idGerencia
WHERE gri.idRol = @idRol AND gri.activo = 1
ORDER BY g.gerencia;

-- Asignar rol IA a gerencia
INSERT INTO GerenciasRolesIA (idRol, idGerencia, activo)
VALUES (@idRol, @idGerencia, 1);
```

---

### 3.10 Configuración del Sistema

**Descripción**: Configuraciones generales del bot.

**Funcionalidades**:
- Ver estado de conexión a base de datos
- Configurar límites de rate limiting
- Configurar mensajes del sistema
- Ver versión del bot y componentes
- Gestionar logs del sistema
- Backup y restore de configuración

**Queries**:

```sql
-- Estado del sistema
SELECT
    (SELECT COUNT(*) FROM Usuarios WHERE activo = 1) as UsuariosActivos,
    (SELECT COUNT(*) FROM UsuariosTelegram WHERE verificado = 1 AND activo = 1) as CuentasVerificadas,
    (SELECT COUNT(*) FROM Operaciones WHERE activo = 1) as OperacionesDisponibles,
    (SELECT COUNT(*) FROM knowledge_entries WHERE active = 1) as EntradasConocimiento,
    (SELECT COUNT(*) FROM LogOperaciones WHERE CAST(fechaEjecucion AS DATE) = CAST(GETDATE() AS DATE)) as OperacionesHoy,
    (SELECT TOP 1 fechaEjecucion FROM LogOperaciones ORDER BY fechaEjecucion DESC) as UltimaActividad;

-- Versiones de tablas
SELECT
    t.name AS TableName,
    p.rows AS RowCount,
    SUM(a.total_pages) * 8 AS TotalSpaceKB,
    SUM(a.used_pages) * 8 AS UsedSpaceKB
FROM sys.tables t
INNER JOIN sys.indexes i ON t.object_id = i.object_id
INNER JOIN sys.partitions p ON i.object_id = p.object_id AND i.index_id = p.index_id
INNER JOIN sys.allocation_units a ON p.partition_id = a.container_id
WHERE t.name IN ('Usuarios', 'Operaciones', 'LogOperaciones', 'knowledge_entries')
  AND i.index_id <= 1
GROUP BY t.name, p.rows
ORDER BY t.name;

-- Estadísticas de uso últimos 7 días
SELECT
    CAST(fechaEjecucion AS DATE) as Fecha,
    COUNT(*) as TotalOperaciones,
    COUNT(DISTINCT idUsuario) as UsuariosActivos,
    AVG(CAST(duracionMs AS FLOAT)) as DuracionPromedio
FROM LogOperaciones
WHERE fechaEjecucion >= DATEADD(day, -7, GETDATE())
GROUP BY CAST(fechaEjecucion AS DATE)
ORDER BY Fecha DESC;
```

---

## 4. Stored Procedures Utilizados

El sistema utiliza los siguientes stored procedures ya implementados:

### 4.1 sp_VerificarPermisoOperacion
**Propósito**: Verificar si un usuario tiene permiso para ejecutar una operación.

**Parámetros**:
- `@idUsuario INT` - ID del usuario
- `@comando NVARCHAR(100)` - Comando a verificar

**Retorna**:
- TienePermiso (BIT)
- Mensaje (NVARCHAR)
- NombreOperacion (NVARCHAR)
- DescripcionOperacion (NVARCHAR)
- RequiereParametros (BIT)
- ParametrosEjemplo (NVARCHAR)

**Uso**:
```sql
EXEC sp_VerificarPermisoOperacion @idUsuario = 5, @comando = '/crear_ticket';
```

---

### 4.2 sp_ObtenerOperacionesUsuario
**Propósito**: Obtener todas las operaciones disponibles para un usuario.

**Parámetros**:
- `@idUsuario INT` - ID del usuario

**Retorna**: Lista de operaciones con permisos del usuario.

**Uso**:
```sql
EXEC sp_ObtenerOperacionesUsuario @idUsuario = 5;
```

---

### 4.3 sp_RegistrarLogOperacion
**Propósito**: Registrar la ejecución de una operación para auditoría.

**Parámetros**:
- `@idUsuario INT`
- `@comando NVARCHAR(100)`
- `@telegramChatId BIGINT` (opcional)
- `@telegramUsername NVARCHAR(100)` (opcional)
- `@parametros NVARCHAR(MAX)` (opcional)
- `@resultado NVARCHAR(50)` - EXITOSO, ERROR, DENEGADO
- `@mensajeError NVARCHAR(MAX)` (opcional)
- `@duracionMs INT` (opcional)
- `@ipOrigen NVARCHAR(50)` (opcional)

**Uso**:
```sql
EXEC sp_RegistrarLogOperacion
    @idUsuario = 5,
    @comando = '/ia',
    @telegramChatId = 123456789,
    @resultado = 'EXITOSO',
    @duracionMs = 234;
```

---

### 4.4 sp_ActualizarActividadTelegram
**Propósito**: Actualizar la última actividad de una cuenta de Telegram.

**Parámetros**:
- `@telegramChatId BIGINT`

**Uso**:
```sql
EXEC sp_ActualizarActividadTelegram @telegramChatId = 123456789;
```

---

### 4.5 sp_search_knowledge
**Propósito**: Buscar en la knowledge base.

**Parámetros**:
- `@query NVARCHAR(500)` - Texto de búsqueda
- `@category VARCHAR(50)` (opcional) - Filtro de categoría
- `@top_k INT` - Número de resultados (default: 3)

**Uso**:
```sql
EXEC sp_search_knowledge
    @query = 'horario',
    @category = 'PROCESOS',
    @top_k = 5;
```

---

## 5. Estructura de Tablas Principal

### 5.1 Tablas de Usuarios y Autenticación
- **Usuarios** - Información de usuarios del sistema
- **Roles** - Catálogo de roles
- **UsuariosTelegram** - Cuentas de Telegram vinculadas
- **RolesIA** - Roles específicos para IA
- **UsuariosRolesIA** - Relación usuarios-roles IA

### 5.2 Tablas de Gerencias
- **Gerencias** - Catálogo de gerencias
- **GerenciaUsuarios** - Usuarios por gerencia
- **AreaAtendedora** - Gerencias que atienden solicitudes
- **GerenciasRolesIA** - Roles IA por gerencia

### 5.3 Tablas de Operaciones y Permisos
- **Modulos** - Agrupación de operaciones
- **Operaciones** - Comandos disponibles
- **RolesOperaciones** - Permisos por rol
- **UsuariosOperaciones** - Permisos específicos de usuario

### 5.4 Tablas de Auditoría
- **LogOperaciones** - Log de todas las operaciones ejecutadas

### 5.5 Tablas de Knowledge Base
- **knowledge_categories** - Categorías de conocimiento
- **knowledge_entries** - Entradas de conocimiento
- **table_documentation** - Documentación de tablas
- **column_documentation** - Documentación de columnas

---

## 6. Casos de Uso Principales

### 6.1 Crear Nuevo Usuario y Asignar Permisos
1. Crear usuario en tabla `Usuarios`
2. Asignar rol base
3. Crear cuenta de Telegram en `UsuariosTelegram`
4. Asignar a gerencia(s) en `GerenciaUsuarios`
5. Asignar permisos específicos si es necesario en `UsuariosOperaciones`

### 6.2 Verificar Permiso de Usuario
1. Recibir comando de Telegram
2. Ejecutar `sp_VerificarPermisoOperacion`
3. Si tiene permiso, ejecutar operación
4. Registrar log con `sp_RegistrarLogOperacion`

### 6.3 Modificar Permisos de un Rol
1. Obtener operaciones actuales del rol
2. Actualizar `RolesOperaciones` (INSERT/UPDATE)
3. Los cambios aplican inmediatamente a todos los usuarios con ese rol

### 6.4 Auditar Actividad de Usuario
1. Consultar `LogOperaciones` filtrando por `idUsuario`
2. Ver detalles: operaciones, resultados, errores
3. Generar reportes de actividad

---

## 7. Consideraciones de Seguridad

1. **Autenticación**: Verificar identidad del usuario administrador
2. **Autorización**: Solo administradores pueden acceder al módulo
3. **Auditoría**: Registrar todas las acciones del módulo de administración
4. **Validación**: Validar todos los inputs para prevenir SQL injection
5. **Encriptación**: Datos sensibles deben estar encriptados
6. **Backup**: Realizar backups regulares de la configuración
7. **Rate Limiting**: Limitar peticiones para prevenir abuso

---

## 8. Tecnologías Recomendadas

### Backend
- **Python** con FastAPI o Flask
- **SQLAlchemy** para ORM
- **pyodbc** para conexión a SQL Server

### Frontend
- **React** o **Vue.js**
- **Material-UI** o **Ant Design** para componentes
- **Chart.js** o **Recharts** para gráficos
- **Axios** para peticiones HTTP

### Extras
- **JWT** para autenticación
- **WebSocket** para notificaciones en tiempo real
- **Redis** para caché
- **Celery** para tareas asíncronas

---

## 9. Endpoints API Sugeridos

```
GET    /api/dashboard/stats
GET    /api/users
POST   /api/users
GET    /api/users/:id
PUT    /api/users/:id
DELETE /api/users/:id
GET    /api/users/:id/operations
GET    /api/users/:id/telegram-accounts
GET    /api/roles
POST   /api/roles
GET    /api/roles/:id/permissions
PUT    /api/roles/:id/permissions
GET    /api/operations
POST   /api/operations
GET    /api/modules
POST   /api/modules
GET    /api/gerencias
POST   /api/gerencias
GET    /api/logs
GET    /api/logs/:id
GET    /api/knowledge/categories
GET    /api/knowledge/entries
POST   /api/knowledge/entries
PUT    /api/knowledge/entries/:id
DELETE /api/knowledge/entries/:id
GET    /api/telegram-accounts
POST   /api/telegram-accounts/:id/verify
PUT    /api/telegram-accounts/:id/status
```

---

## 10. Mockups y Wireframes Sugeridos

### 10.1 Dashboard Principal
- Cards con métricas clave
- Gráfico de operaciones por día
- Lista de operaciones recientes
- Alertas y notificaciones

### 10.2 Gestión de Usuarios
- Tabla con filtros y búsqueda
- Modal para crear/editar usuario
- Vista detalle con tabs (Info, Telegram, Permisos, Logs)

### 10.3 Gestión de Permisos
- Matriz de permisos (Roles x Operaciones)
- Drag & drop para asignar permisos
- Indicadores visuales (colores por nivel de criticidad)

### 10.4 Auditoría
- Timeline de operaciones
- Filtros avanzados
- Exportación a CSV/Excel
- Gráficos de tendencias

---

## 11. Prioridades de Implementación

### Fase 1 (MVP)
1. Dashboard básico
2. Gestión de usuarios (CRUD)
3. Gestión de permisos por rol
4. Log de auditoría básico

### Fase 2
1. Gestión de cuentas de Telegram
2. Gestión de operaciones y módulos
3. Dashboard avanzado con gráficos
4. Filtros y búsquedas avanzadas

### Fase 3
1. Gestión de Knowledge Base
2. Gestión de gerencias
3. Reportes y exportaciones
4. Notificaciones en tiempo real

### Fase 4
1. Configuración avanzada
2. Backup y restore
3. Integración con otros sistemas
4. API pública

---

## 12. Métricas de Éxito

- **Reducción del tiempo** de gestión de usuarios en un 70%
- **Aumento de la visibilidad** de uso del bot
- **Reducción de errores** por mala configuración
- **Mejora en la auditoría** y trazabilidad
- **Facilidad de uso** (menos de 5 clics para tareas comunes)

---

## Conclusión

Este documento proporciona una base completa para el desarrollo del módulo de administración del bot. Todas las queries SQL están documentadas y probadas, y la estructura permite una implementación incremental siguiendo las fases propuestas.

El módulo permitirá una gestión eficiente y profesional del bot, reduciendo la necesidad de acceso directo a la base de datos y mejorando la trazabilidad y seguridad del sistema.
