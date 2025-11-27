-- ============================================================================
-- Script: Stored Procedures para Sistema de Permisos
-- Base de Datos: abcmasplus
-- Esquema: dbo
-- Descripción: Stored procedures para autenticación y autorización
-- ============================================================================

USE abcmasplus;
GO

PRINT '============================================================================';
PRINT 'Creando stored procedures para sistema de permisos';
PRINT '============================================================================';
PRINT '';

-- ============================================================================
-- sp_VerificarPermisoOperacion
-- Descripción: Verificar si un usuario tiene permiso para ejecutar una operación
-- ============================================================================
IF EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[sp_VerificarPermisoOperacion]') AND type in (N'P'))
    DROP PROCEDURE [dbo].[sp_VerificarPermisoOperacion];
GO

CREATE PROCEDURE [dbo].[sp_VerificarPermisoOperacion]
    @idUsuario INT,
    @comando NVARCHAR(100)
AS
BEGIN
    SET NOCOUNT ON;

    DECLARE @tienePermiso BIT = 0;
    DECLARE @mensaje NVARCHAR(500);
    DECLARE @idOperacion INT;
    DECLARE @nombreOperacion NVARCHAR(100);
    DECLARE @descripcionOperacion NVARCHAR(500);
    DECLARE @requiereParametros BIT;
    DECLARE @parametrosEjemplo NVARCHAR(500);
    DECLARE @rolUsuario INT;

    -- Verificar que el usuario existe y está activo
    IF NOT EXISTS (SELECT 1 FROM Usuarios WHERE idUsuario = @idUsuario AND activo = 1)
    BEGIN
        SELECT
            0 AS TienePermiso,
            'Usuario no encontrado o inactivo' AS Mensaje,
            NULL AS NombreOperacion,
            NULL AS DescripcionOperacion,
            NULL AS RequiereParametros,
            NULL AS ParametrosEjemplo;
        RETURN;
    END

    -- Obtener rol del usuario
    SELECT @rolUsuario = rol FROM Usuarios WHERE idUsuario = @idUsuario;

    -- Buscar la operación por comando
    SELECT
        @idOperacion = idOperacion,
        @nombreOperacion = nombre,
        @descripcionOperacion = descripcion,
        @requiereParametros = requiereParametros,
        @parametrosEjemplo = parametrosEjemplo
    FROM Operaciones
    WHERE comando = @comando AND activo = 1;

    -- Verificar que la operación existe
    IF @idOperacion IS NULL
    BEGIN
        SELECT
            0 AS TienePermiso,
            'Operación no encontrada' AS Mensaje,
            NULL AS NombreOperacion,
            NULL AS DescripcionOperacion,
            NULL AS RequiereParametros,
            NULL AS ParametrosEjemplo;
        RETURN;
    END

    -- Verificar permisos específicos del usuario (prioridad alta)
    IF EXISTS (
        SELECT 1
        FROM UsuariosOperaciones
        WHERE idUsuario = @idUsuario
            AND idOperacion = @idOperacion
            AND activo = 1
            AND (fechaExpiracion IS NULL OR fechaExpiracion > GETDATE())
    )
    BEGIN
        SELECT @tienePermiso = permitido
        FROM UsuariosOperaciones
        WHERE idUsuario = @idUsuario
            AND idOperacion = @idOperacion
            AND activo = 1
            AND (fechaExpiracion IS NULL OR fechaExpiracion > GETDATE());

        SET @mensaje = CASE
            WHEN @tienePermiso = 1 THEN 'Permiso concedido (permiso específico de usuario)'
            ELSE 'Permiso denegado (permiso específico de usuario)'
        END;
    END
    ELSE
    BEGIN
        -- Verificar permisos del rol
        IF EXISTS (
            SELECT 1
            FROM RolesOperaciones
            WHERE idRol = @rolUsuario
                AND idOperacion = @idOperacion
                AND activo = 1
        )
        BEGIN
            SELECT @tienePermiso = permitido
            FROM RolesOperaciones
            WHERE idRol = @rolUsuario
                AND idOperacion = @idOperacion
                AND activo = 1;

            SET @mensaje = CASE
                WHEN @tienePermiso = 1 THEN 'Permiso concedido (permiso de rol)'
                ELSE 'Permiso denegado (permiso de rol)'
            END;
        END
        ELSE
        BEGIN
            SET @tienePermiso = 0;
            SET @mensaje = 'Permiso no configurado para este usuario o rol';
        END
    END

    -- Retornar resultado
    SELECT
        @tienePermiso AS TienePermiso,
        @mensaje AS Mensaje,
        @nombreOperacion AS NombreOperacion,
        @descripcionOperacion AS DescripcionOperacion,
        @requiereParametros AS RequiereParametros,
        @parametrosEjemplo AS ParametrosEjemplo;
END
GO

PRINT 'Stored procedure sp_VerificarPermisoOperacion creado exitosamente';

-- ============================================================================
-- sp_ObtenerOperacionesUsuario
-- Descripción: Obtener todas las operaciones disponibles para un usuario
-- ============================================================================
IF EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[sp_ObtenerOperacionesUsuario]') AND type in (N'P'))
    DROP PROCEDURE [dbo].[sp_ObtenerOperacionesUsuario];
GO

CREATE PROCEDURE [dbo].[sp_ObtenerOperacionesUsuario]
    @idUsuario INT
AS
BEGIN
    SET NOCOUNT ON;

    DECLARE @rolUsuario INT;

    -- Obtener rol del usuario
    SELECT @rolUsuario = rol
    FROM Usuarios
    WHERE idUsuario = @idUsuario AND activo = 1;

    IF @rolUsuario IS NULL
    BEGIN
        -- Usuario no encontrado
        SELECT
            NULL AS Modulo,
            NULL AS IconoModulo,
            NULL AS idOperacion,
            NULL AS Operacion,
            NULL AS descripcion,
            NULL AS comando,
            NULL AS requiereParametros,
            NULL AS parametrosEjemplo,
            NULL AS nivelCriticidad,
            NULL AS OrigenPermiso,
            0 AS Permitido
        WHERE 1 = 0; -- Retornar resultado vacío
        RETURN;
    END

    -- Obtener operaciones combinando permisos de rol y usuario
    SELECT DISTINCT
        m.nombre AS Modulo,
        m.icono AS IconoModulo,
        m.orden AS OrdenModulo,
        o.idOperacion,
        o.nombre AS Operacion,
        o.descripcion,
        o.comando,
        o.requiereParametros,
        o.parametrosEjemplo,
        o.nivelCriticidad,
        o.orden AS OrdenOperacion,
        CASE
            WHEN uo.idUsuarioOperacion IS NOT NULL THEN 'Usuario'
            ELSE 'Rol'
        END AS OrigenPermiso,
        CASE
            WHEN uo.idUsuarioOperacion IS NOT NULL THEN uo.permitido
            ELSE ro.permitido
        END AS Permitido
    FROM Operaciones o
    INNER JOIN Modulos m ON o.idModulo = m.idModulo
    LEFT JOIN RolesOperaciones ro ON o.idOperacion = ro.idOperacion
        AND ro.idRol = @rolUsuario
        AND ro.activo = 1
    LEFT JOIN UsuariosOperaciones uo ON o.idOperacion = uo.idOperacion
        AND uo.idUsuario = @idUsuario
        AND uo.activo = 1
        AND (uo.fechaExpiracion IS NULL OR uo.fechaExpiracion > GETDATE())
    WHERE o.activo = 1
        AND m.activo = 1
        AND (
            (uo.idUsuarioOperacion IS NOT NULL AND uo.permitido = 1)
            OR (uo.idUsuarioOperacion IS NULL AND ro.idRolOperacion IS NOT NULL AND ro.permitido = 1)
        )
    ORDER BY m.orden, o.orden, o.nombre;
END
GO

PRINT 'Stored procedure sp_ObtenerOperacionesUsuario creado exitosamente';

-- ============================================================================
-- sp_RegistrarLogOperacion
-- Descripción: Registrar la ejecución de una operación para auditoría
-- ============================================================================
IF EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[sp_RegistrarLogOperacion]') AND type in (N'P'))
    DROP PROCEDURE [dbo].[sp_RegistrarLogOperacion];
GO

CREATE PROCEDURE [dbo].[sp_RegistrarLogOperacion]
    @idUsuario INT,
    @comando NVARCHAR(100),
    @telegramChatId BIGINT = NULL,
    @telegramUsername NVARCHAR(100) = NULL,
    @parametros NVARCHAR(MAX) = NULL,
    @resultado NVARCHAR(50) = 'EXITOSO',
    @mensajeError NVARCHAR(MAX) = NULL,
    @duracionMs INT = NULL,
    @ipOrigen NVARCHAR(50) = NULL
AS
BEGIN
    SET NOCOUNT ON;

    DECLARE @idOperacion INT;

    -- Buscar la operación por comando
    SELECT @idOperacion = idOperacion
    FROM Operaciones
    WHERE comando = @comando;

    -- Si no encuentra la operación, buscar una operación genérica o crear un log sin idOperacion
    IF @idOperacion IS NULL
    BEGIN
        -- Intentar encontrar una operación genérica para "comando desconocido"
        SELECT @idOperacion = idOperacion
        FROM Operaciones
        WHERE nombre = 'Operación Desconocida' OR comando IS NULL
        ORDER BY idOperacion
        OFFSET 0 ROWS FETCH NEXT 1 ROWS ONLY;
    END

    -- Insertar log
    INSERT INTO LogOperaciones (
        idUsuario,
        idOperacion,
        telegramChatId,
        telegramUsername,
        parametros,
        resultado,
        mensajeError,
        duracionMs,
        ipOrigen,
        fechaEjecucion
    )
    VALUES (
        @idUsuario,
        @idOperacion,
        @telegramChatId,
        @telegramUsername,
        @parametros,
        @resultado,
        @mensajeError,
        @duracionMs,
        @ipOrigen,
        GETDATE()
    );

    -- Retornar el ID del log insertado
    SELECT SCOPE_IDENTITY() AS idLog;
END
GO

PRINT 'Stored procedure sp_RegistrarLogOperacion creado exitosamente';

-- ============================================================================
-- sp_ActualizarActividadTelegram
-- Descripción: Actualizar la última actividad de una cuenta de Telegram
-- ============================================================================
IF EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[sp_ActualizarActividadTelegram]') AND type in (N'P'))
    DROP PROCEDURE [dbo].[sp_ActualizarActividadTelegram];
GO

CREATE PROCEDURE [dbo].[sp_ActualizarActividadTelegram]
    @telegramChatId BIGINT
AS
BEGIN
    SET NOCOUNT ON;

    UPDATE UsuariosTelegram
    SET fechaUltimaActividad = GETDATE()
    WHERE telegramChatId = @telegramChatId
        AND activo = 1;

    SELECT @@ROWCOUNT AS FilasActualizadas;
END
GO

PRINT 'Stored procedure sp_ActualizarActividadTelegram creado exitosamente';

-- ============================================================================
PRINT '';
PRINT '============================================================================';
PRINT 'Stored procedures creados exitosamente';
PRINT '============================================================================';
