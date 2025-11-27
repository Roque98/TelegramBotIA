# 🔐 Sistema de Autenticación y Autorización

## 📋 Índice

1. [Descripción General](#descripción-general)
2. [Arquitectura](#arquitectura)
3. [Componentes del Sistema](#componentes-del-sistema)
4. [Flujo de Registro](#flujo-de-registro)
5. [Flujo de Verificación](#flujo-de-verificación)
6. [Sistema de Permisos](#sistema-de-permisos)
7. [Comandos de Telegram](#comandos-de-telegram)
8. [Stored Procedures](#stored-procedures)
9. [Configuración](#configuración)
10. [Troubleshooting](#troubleshooting)

---

## Descripción General

El sistema de autenticación y autorización garantiza que solo usuarios autorizados puedan usar el bot de Telegram y que tengan acceso únicamente a las operaciones permitidas según su rol.

### Características Principales

- ✅ **Registro por número de empleado**: Los usuarios se registran usando su ID de empleado
- ✅ **Verificación con código**: Sistema de códigos de 6 dígitos almacenados en BD
- ✅ **Portal de administración**: Códigos consultables desde portal web
- ✅ **Sistema de permisos basado en roles**: Control granular de operaciones
- ✅ **Permisos específicos por usuario**: Excepciones a los permisos del rol
- ✅ **Auditoría completa**: Registro de todas las operaciones
- ✅ **Soporte para múltiples cuentas**: Un usuario puede tener varias cuentas de Telegram

---

## Arquitectura

```
┌─────────────────────────────────────────────────────────────┐
│                       Usuario Telegram                       │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│              Telegram Bot (telegram_bot.py)                 │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌───────────────┐  ┌─────────────────┐  │
│  │  Middleware  │  │   Handlers    │  │  Decoradores    │  │
│  │              │  │               │  │                 │  │
│  │ - Logging    │  │ - Register    │  │ - @require_auth │  │
│  │ - Auth       │  │ - Verify      │  │ - @require_perm │  │
│  └──────────────┘  └───────────────┘  └─────────────────┘  │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│                 Módulos de Autenticación                     │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────────┐  ┌────────────────────────────────┐  │
│  │  UserManager     │  │   PermissionChecker            │  │
│  │                  │  │                                │  │
│  │ - get_user       │  │ - check_permission()           │  │
│  │ - is_registered  │  │ - get_user_operations()        │  │
│  │ - update_activity│  │ - log_operation()              │  │
│  └──────────────────┘  └────────────────────────────────┘  │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐  │
│  │   RegistrationManager                                  │  │
│  │                                                        │  │
│  │ - start_registration()                                │  │
│  │ - verify_account()                                    │  │
│  │ - resend_verification_code()                          │  │
│  └────────────────────────────────────────────────────────┘  │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│                   Base de Datos (SQL Server)                 │
├─────────────────────────────────────────────────────────────┤
│  Tablas:                                                     │
│  - Usuarios                                                  │
│  - UsuariosTelegram                                          │
│  - Roles                                                     │
│  - Operaciones                                               │
│  - RolesOperaciones                                          │
│  - UsuariosOperaciones                                       │
│  - LogOperaciones                                            │
│                                                              │
│  Stored Procedures:                                          │
│  - sp_VerificarPermisoOperacion                             │
│  - sp_ObtenerOperacionesUsuario                             │
│  - sp_RegistrarLogOperacion                                 │
│  - sp_ActualizarActividadTelegram                           │
└─────────────────────────────────────────────────────────────┘
```

---

## Componentes del Sistema

### 1. UserManager (`src/auth/user_manager.py`)

Gestiona los usuarios de Telegram.

**Métodos principales:**
- `get_user_by_chat_id(chat_id)`: Obtiene usuario por su Chat ID
- `get_user_by_id(user_id)`: Obtiene usuario por su ID en BD
- `is_user_registered(chat_id)`: Verifica si un chat_id está registrado
- `update_last_activity(chat_id)`: Actualiza la última actividad
- `get_user_stats(user_id)`: Obtiene estadísticas de uso

### 2. PermissionChecker (`src/auth/permission_checker.py`)

Verifica permisos y registra operaciones.

**Métodos principales:**
- `check_permission(user_id, comando)`: Verifica si tiene permiso
- `get_user_operations(user_id)`: Obtiene todas las operaciones permitidas
- `log_operation(...)`: Registra la ejecución de una operación
- `is_operation_critical(user_id, comando)`: Verifica si es crítica

### 3. RegistrationManager (`src/auth/registration.py`)

Maneja el proceso de registro.

**Métodos principales:**
- `find_user_by_employee_id(employee_id)`: Busca usuario por ID empleado
- `start_registration(...)`: Inicia el proceso de registro
- `verify_account(chat_id, code)`: Verifica con código
- `resend_verification_code(chat_id)`: Genera nuevo código

### 4. Middleware de Autenticación (`src/bot/middleware/auth_middleware.py`)

**Decoradores:**
- `@require_auth`: Requiere que el usuario esté autenticado
- `@require_permission(comando)`: Requiere permiso específico

---

## Flujo de Registro

### Diagrama de Flujo

```
┌─────────────┐
│  Usuario    │
│  Telegram   │
└──────┬──────┘
       │
       │ /register
       ▼
┌──────────────────────────┐
│  Bot solicita número     │
│  de empleado             │
└──────┬───────────────────┘
       │
       │ 12345
       ▼
┌──────────────────────────┐
│  Buscar en BD por        │
│  idEmpleado = 12345      │
└──────┬───────────────────┘
       │
       ├─ No existe ──> ❌ "Usuario no encontrado"
       │
       └─ Existe
          │
          ▼
┌──────────────────────────┐
│  Generar código (123456) │
│  Guardar en              │
│  UsuariosTelegram        │
└──────┬───────────────────┘
       │
       ▼
┌──────────────────────────┐
│  "Código generado.       │
│   Consulta el portal"    │
└──────────────────────────┘
       │
       ▼
┌──────────────────────────┐
│  Usuario consulta portal │
│  y ve código: 123456     │
└──────┬───────────────────┘
       │
       │ /verify 123456
       ▼
┌──────────────────────────┐
│  Verificar código        │
└──────┬───────────────────┘
       │
       ├─ Incorrecto ──> ❌ "Código incorrecto"
       │
       └─ Correcto
          │
          ▼
┌──────────────────────────┐
│  Marcar verificado=1     │
│  fechaVerificacion=NOW() │
└──────┬───────────────────┘
       │
       ▼
┌──────────────────────────┐
│  ✅ "Cuenta verificada"  │
│  Usuario puede usar bot  │
└──────────────────────────┘
```

### Pasos Detallados

1. **Usuario inicia registro**
   ```
   /register
   ```

2. **Bot solicita ID de empleado**
   ```
   Por favor, envía tu número de empleado:
   ```

3. **Usuario envía ID**
   ```
   12345
   ```

4. **Sistema busca usuario en BD**
   - Busca en tabla `Usuarios` por `idEmpleado = 12345`
   - Si no existe: Error "Usuario no encontrado"
   - Si existe: Continúa

5. **Genera código y guarda en BD**
   ```sql
   INSERT INTO UsuariosTelegram (
       idUsuario, telegramChatId, codigoVerificacion, ...
   ) VALUES (
       @idUsuario, @chatId, '123456', ...
   )
   ```

6. **Informa al usuario**
   ```
   ✅ Registro iniciado.
   Consulta tu código en el Portal de Consola de Monitoreo.
   ```

7. **Usuario consulta portal web**
   - Portal muestra: Código de verificación: `123456`

8. **Usuario verifica en Telegram**
   ```
   /verify 123456
   ```

9. **Sistema valida y activa cuenta**
   ```sql
   UPDATE UsuariosTelegram
   SET verificado = 1, fechaVerificacion = GETDATE()
   WHERE telegramChatId = @chatId
   AND codigoVerificacion = '123456'
   ```

---

## Flujo de Verificación de Permisos

### Diagrama

```
Usuario envía mensaje
        │
        ▼
┌───────────────────────┐
│  ¿Está autenticado?   │
└────┬──────────┬───────┘
     │          │
     NO         SÍ
     │          │
     ▼          ▼
   ❌ Error   ┌─────────────────────┐
              │ Obtener permisos    │
              │ sp_VerificarPermiso │
              └─────┬───────────────┘
                    │
              ┌─────┴──────┐
              │            │
            PERMITIDO   DENEGADO
              │            │
              ▼            ▼
      ┌─────────────┐   ❌ Acceso
      │ Ejecutar    │      Denegado
      │ operación   │
      └─────┬───────┘
            │
            ▼
      ┌─────────────┐
      │ Registrar   │
      │ en Log      │
      └─────────────┘
```

---

## Sistema de Permisos

### Jerarquía de Permisos

1. **Permisos específicos de usuario** (UsuariosOperaciones)
   - Prioridad ALTA
   - Sobrescriben permisos del rol
   - Pueden tener fecha de expiración

2. **Permisos del rol** (RolesOperaciones)
   - Prioridad MEDIA
   - Se aplican a todos los usuarios del rol

### Niveles de Criticidad

| Nivel | Nombre | Descripción | Ejemplos |
|-------|--------|-------------|----------|
| 1 | Baja | Consultas, lecturas | /ia, /help, /stats |
| 2 | Media | Crear/modificar registros | /crear_ticket |
| 3 | Alta | Asignaciones importantes | /asignar_ticket |
| 4 | Crítica | Eliminaciones, config | /eliminar_usuario |

### Tabla de Roles de Ejemplo

| Rol | Descripción | Operaciones Típicas |
|-----|-------------|---------------------|
| Administrador | Control total | Todas las operaciones |
| Gerente | Gestión de equipos | Consultas, reportes, asignaciones |
| Analista | Operaciones diarias | Consultas, crear tickets |
| Usuario | Solo consultas | /ia, /help |

---

## Comandos de Telegram

### Comandos Públicos (No requieren autenticación)

#### `/register`
Inicia el proceso de registro.

**Flujo:**
1. Usuario: `/register`
2. Bot: "Envía tu número de empleado:"
3. Usuario: `12345`
4. Bot: "Código generado. Consulta el portal."

#### `/verify <codigo>`
Verifica la cuenta con el código.

**Ejemplo:**
```
/verify 123456
```

**Respuesta:**
```
🎉 ¡Verificación exitosa!
Bienvenido, Juan Pérez
Rol: Analista
```

#### `/resend`
Genera un nuevo código de verificación.

**Ejemplo:**
```
/resend
```

**Respuesta:**
```
✅ Nuevo código generado.
Consulta el portal para ver tu código.
```

### Comandos que Requieren Autenticación

#### `/help`
Muestra ayuda y comandos disponibles.

#### `/stats`
Muestra estadísticas de uso del usuario.

---

## Stored Procedures

### sp_VerificarPermisoOperacion

Verifica si un usuario tiene permiso para ejecutar una operación.

**Parámetros:**
- `@idUsuario INT`: ID del usuario
- `@comando NVARCHAR(100)`: Comando a verificar

**Retorna:**
| Campo | Tipo | Descripción |
|-------|------|-------------|
| TienePermiso | BIT | 1 si tiene permiso |
| Mensaje | NVARCHAR | Descripción del resultado |
| NombreOperacion | NVARCHAR | Nombre de la operación |
| RequiereParametros | BIT | Si requiere parámetros |

**Ejemplo:**
```sql
EXEC sp_VerificarPermisoOperacion
    @idUsuario = 5,
    @comando = '/ia'
```

### sp_ObtenerOperacionesUsuario

Obtiene todas las operaciones disponibles para un usuario.

**Parámetros:**
- `@idUsuario INT`: ID del usuario

**Retorna:**
Lista de operaciones con módulos, comandos, permisos, etc.

**Ejemplo:**
```sql
EXEC sp_ObtenerOperacionesUsuario @idUsuario = 5
```

### sp_RegistrarLogOperacion

Registra la ejecución de una operación para auditoría.

**Parámetros:**
- `@idUsuario INT`: ID del usuario
- `@comando NVARCHAR(100)`: Comando ejecutado
- `@telegramChatId BIGINT`: Chat ID (opcional)
- `@resultado NVARCHAR(50)`: EXITOSO, ERROR, DENEGADO
- `@duracionMs INT`: Duración en milisegundos (opcional)

**Ejemplo:**
```sql
EXEC sp_RegistrarLogOperacion
    @idUsuario = 5,
    @comando = '/ia',
    @resultado = 'EXITOSO',
    @duracionMs = 1250
```

---

## Configuración

### 1. Ejecutar Scripts SQL

En orden:
```sql
-- 1. Estructura de usuarios y roles
docs/sql/01 EstructuraUsuarios.sql

-- 2. Estructura de permisos y operaciones
docs/sql/02 EstructuraPermisos.sql

-- 3. Gestión de cuentas de Telegram
docs/sql/03 EstructuraVerificacion.sql

-- 4. Stored Procedures
docs/sql/04 StoredProcedures.sql
```

### 2. Configurar Variables de Entorno

Asegúrate de tener configurado en `.env`:
```env
# Base de datos
DB_TYPE=sqlserver
DB_HOST=localhost
DB_PORT=1433
DB_NAME=abcmasplus
DB_USER=tu_usuario
DB_PASSWORD=tu_password

# Telegram
TELEGRAM_BOT_TOKEN=tu_token_aqui
```

### 3. Crear Operaciones Iniciales

Crear al menos la operación `/ia` para consultas:

```sql
-- Módulo IA
INSERT INTO Modulos (nombre, descripcion, icono, orden)
VALUES ('IA', 'Consultas con Inteligencia Artificial', '🤖', 8);

-- Operación de consulta IA
INSERT INTO Operaciones (
    idModulo, nombre, descripcion, comando,
    requiereParametros, nivelCriticidad
)
VALUES (
    (SELECT idModulo FROM Modulos WHERE nombre = 'IA'),
    'Consulta IA',
    'Realizar consultas en lenguaje natural a la base de datos',
    '/ia',
    0,
    1 -- Baja criticidad
);

-- Asignar permiso a un rol (ej: Analista)
INSERT INTO RolesOperaciones (idRol, idOperacion, permitido)
VALUES (
    (SELECT idRol FROM Roles WHERE nombre = 'Analista'),
    (SELECT idOperacion FROM Operaciones WHERE comando = '/ia'),
    1
);
```

---

## Troubleshooting

### Problema: "No estás registrado en el sistema"

**Causa:** El chat_id no está en la tabla `UsuariosTelegram`.

**Solución:**
1. Verificar que usaste `/register`
2. Verificar que el número de empleado existe en tabla `Usuarios`
3. Consultar:
   ```sql
   SELECT * FROM UsuariosTelegram WHERE telegramChatId = <tu_chat_id>
   ```

### Problema: "Tu cuenta no está verificada"

**Causa:** El campo `verificado` está en 0.

**Solución:**
1. Consultar código en el portal
2. Usar `/verify <codigo>`
3. Si perdiste el código, usa `/resend`

### Problema: "No tienes permiso para realizar consultas con IA"

**Causa:** No hay permiso configurado para `/ia`.

**Solución:**
1. Verificar permisos del rol:
   ```sql
   SELECT * FROM RolesOperaciones ro
   INNER JOIN Operaciones o ON ro.idOperacion = o.idOperacion
   WHERE ro.idRol = <tu_rol> AND o.comando = '/ia'
   ```

2. Agregar permiso si no existe:
   ```sql
   INSERT INTO RolesOperaciones (idRol, idOperacion, permitido)
   VALUES (<tu_rol>, <id_operacion_ia>, 1)
   ```

### Problema: "Demasiados intentos fallidos"

**Causa:** Más de 5 intentos de verificación incorrectos.

**Solución:**
Contactar al administrador para desbloquear la cuenta:
```sql
UPDATE UsuariosTelegram
SET intentosVerificacion = 0,
    estado = 'ACTIVO'
WHERE telegramChatId = <tu_chat_id>
```

---

## Consultas Útiles para Administradores

### Ver usuarios registrados
```sql
SELECT
    u.idEmpleado,
    u.nombre + ' ' + u.apellido AS NombreCompleto,
    ut.telegramUsername,
    ut.verificado,
    ut.estado,
    ut.fechaRegistro
FROM UsuariosTelegram ut
INNER JOIN Usuarios u ON ut.idUsuario = u.idUsuario
WHERE ut.activo = 1
ORDER BY ut.fechaRegistro DESC
```

### Ver códigos de verificación pendientes
```sql
SELECT
    u.idEmpleado,
    u.nombre + ' ' + u.apellido AS NombreCompleto,
    ut.codigoVerificacion,
    ut.intentosVerificacion,
    ut.fechaRegistro
FROM UsuariosTelegram ut
INNER JOIN Usuarios u ON ut.idUsuario = u.idUsuario
WHERE ut.verificado = 0
    AND ut.activo = 1
ORDER BY ut.fechaRegistro DESC
```

### Auditoría de operaciones
```sql
SELECT TOP 100
    u.nombre + ' ' + u.apellido AS Usuario,
    o.comando,
    l.resultado,
    l.duracionMs,
    l.fechaEjecucion
FROM LogOperaciones l
INNER JOIN Usuarios u ON l.idUsuario = u.idUsuario
INNER JOIN Operaciones o ON l.idOperacion = o.idOperacion
ORDER BY l.fechaEjecucion DESC
```

---

## Resumen de Archivos Creados

### Módulos de Autenticación
- ✅ `src/auth/__init__.py`
- ✅ `src/auth/user_manager.py`
- ✅ `src/auth/permission_checker.py`
- ✅ `src/auth/registration.py`

### Middleware
- ✅ `src/bot/middleware/auth_middleware.py`

### Handlers
- ✅ `src/bot/handlers/registration_handlers.py`

### SQL
- ✅ `docs/sql/04 StoredProcedures.sql`

### Documentación
- ✅ `docs/SISTEMA_AUTENTICACION.md` (este archivo)

---

**Última actualización:** 2025-11-07
**Versión:** 1.0
**Estado:** ✅ Implementación completa del TODO #1
