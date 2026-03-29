# Sistema de Autenticación y Autorización

## Índice

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

### Características

- Registro por número de empleado con verificación por código de 6 dígitos
- Códigos consultables desde portal web (sin envío por Telegram)
- Permisos basados en roles con excepciones por usuario
- Auditoría completa de operaciones
- Soporte para múltiples cuentas de Telegram por empleado

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
│  ┌──────────────┐  ┌───────────────┐                        │
│  │  Middleware  │  │   Handlers    │                        │
│  │              │  │               │                        │
│  │ - Logging    │  │ - Register    │                        │
│  │ - Auth       │  │ - Verify      │                        │
│  └──────────────┘  └───────────────┘                        │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│                 Módulos de Autenticación                     │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────────────────────────────────────────────┐  │
│  │   UserService  (src/domain/auth/user_service.py)     │  │
│  │                                                      │  │
│  │ - get_user_by_chat_id()   - validate_employee()      │  │
│  │ - is_registered()         - check_permission()       │  │
│  │ - create_registration()   - verify_account()         │  │
│  │ - resend_verification()   - update_last_activity()   │  │
│  └──────────────────────────────────────────────────────┘  │
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

### 1. UserService (`src/domain/auth/user_service.py`)

Concentra toda la lógica de negocio de autenticación y permisos.

**Métodos principales:**
- `get_user_by_chat_id(chat_id)`: Obtiene usuario por su Chat ID
- `is_registered(chat_id)`: Verifica si un chat_id está registrado y activo
- `check_permission(user_id, command)`: Verifica si tiene permiso para un comando
- `validate_employee(employee_id)`: Busca usuario por ID de empleado
- `create_registration(user_id, chat_id)`: Inicia el proceso de registro
- `verify_account(chat_id, code)`: Verifica con código
- `resend_verification(chat_id)`: Genera nuevo código de verificación
- `update_last_activity(chat_id)`: Actualiza la última actividad

### 2. Entidades (`src/domain/auth/user_entity.py`)

- `TelegramUser`: Usuario registrado con chat_id, rol, permisos y estado
- `PermissionResult`: Resultado de verificación de permiso (allowed, reason)
- `Operation`: Operación/comando con su nivel de criticidad

### 3. UserRepository (`src/domain/auth/user_repository.py`)

Acceso a datos para usuarios — encapsula todas las queries SQL contra tablas de autenticación.

### 4. Middleware de Autenticación (`src/bot/middleware/auth_middleware.py`)

Intercepta todas las actualizaciones de Telegram antes de los handlers. Usa `UserService` para verificar registro y cachea el `TelegramUser` en `context.user_data`.

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

En orden (desde `database/migrations/`):

```bash
01_EstructuraUsuarios.sql     # tablas de usuarios y roles
02_EstructuraPermisos.sql     # operaciones y permisos
03_EstructuraVerificacion.sql # cuentas de Telegram
04_StoredProcedures.sql       # stored procedures
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

## Archivos del Módulo

### Domain (lógica de negocio)
- `src/domain/auth/user_entity.py` — TelegramUser, PermissionResult, Operation
- `src/domain/auth/user_repository.py` — acceso a datos
- `src/domain/auth/user_service.py` — orquestador de autenticación

### Bot (entrypoints Telegram)
- `src/bot/middleware/auth_middleware.py` — intercepta y valida cada update
- `src/bot/handlers/registration_handlers.py` — flujo /register, /verify, /resend

### SQL
- `database/migrations/` — Scripts SQL de estructura de tablas y stored procedures

---

**Última actualización:** 2026-03-28
**Estado:** ✅ Módulo activo — arquitectura domain-driven
