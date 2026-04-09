-- ============================================================
-- Migración 006: Stored Procedures de Autenticación (BotIAv2_sp_*)
-- Propósito: Centralizar en BD todas las queries de usuarios, roles y gerencias.
--            Los repositorios Python llaman estos SPs en lugar de SQL directo.
-- BD destino: abcmasplus
-- ============================================================

-- ============================================================
-- 1. BotIAv2_sp_GetUsuarioByChatId
--    Reemplaza: user_query_repository.get_by_chat_id
--               user_repository.get_user_by_chat_id
-- ============================================================
CREATE OR ALTER PROCEDURE abcmasplus..BotIAv2_sp_GetUsuarioByChatId
    @telegramChatId BIGINT
AS
BEGIN
    SET NOCOUNT ON;
    SELECT
        u.idUsuario,
        u.Nombre,
        u.email,
        u.idRol,
        u.puesto,
        u.Empresa,
        u.Activa,
        r.nombre              AS rolNombre,
        ut.idUsuarioTelegram,
        ut.telegramChatId,
        ut.telegramUsername,
        ut.telegramFirstName,
        ut.telegramLastName,
        ut.alias,
        ut.esPrincipal,
        ut.estado,
        ut.verificado,
        ut.fechaUltimaActividad
    FROM abcmasplus..BotIAv2_UsuariosTelegram ut
    INNER JOIN abcmasplus..Usuarios u ON ut.idUsuario = u.idUsuario
    LEFT  JOIN abcmasplus..Roles    r ON u.idRol      = r.idRol
    WHERE ut.telegramChatId = @telegramChatId
      AND ut.activo = 1;
END;
GO

-- ============================================================
-- 2. BotIAv2_sp_GetUsuarioById
--    Reemplaza: user_query_repository.get_by_user_id
--               user_repository.get_user_by_id
--               telegram_account_repository.find_user_by_employee_id
-- ============================================================
CREATE OR ALTER PROCEDURE abcmasplus..BotIAv2_sp_GetUsuarioById
    @idUsuario INT
AS
BEGIN
    SET NOCOUNT ON;
    SELECT
        u.idUsuario,
        u.Nombre,
        u.email,
        u.idRol,
        u.puesto,
        u.Empresa,
        u.Activa,
        r.nombre              AS rolNombre,
        ut.idUsuarioTelegram,
        ut.telegramChatId,
        ut.telegramUsername,
        ut.telegramFirstName,
        ut.telegramLastName,
        ut.alias,
        ut.esPrincipal,
        ut.estado,
        ut.verificado,
        ut.fechaUltimaActividad
    FROM abcmasplus..Usuarios u
    LEFT JOIN abcmasplus..Roles r ON u.idRol = r.idRol
    LEFT JOIN abcmasplus..BotIAv2_UsuariosTelegram ut
        ON u.idUsuario = ut.idUsuario AND ut.esPrincipal = 1 AND ut.activo = 1
    WHERE u.idUsuario = @idUsuario;
END;
GO

-- ============================================================
-- 3. BotIAv2_sp_GetPerfilUsuario
--    Reemplaza: user_query_repository.get_profile_for_permissions
--    Retorna: user_id, role_id, gerencia_ids_csv (CSV de IDs)
-- ============================================================
CREATE OR ALTER PROCEDURE abcmasplus..BotIAv2_sp_GetPerfilUsuario
    @telegramChatId BIGINT
AS
BEGIN
    SET NOCOUNT ON;
    SELECT
        u.idUsuario AS user_id,
        u.idRol     AS role_id,
        STUFF((
            SELECT ',' + CAST(gu.idGerencia AS VARCHAR)
            FROM abcmasplus..GerenciasUsuarios gu
            WHERE gu.idUsuario = u.idUsuario
            FOR XML PATH('')
        ), 1, 1, '') AS gerencia_ids_csv
    FROM abcmasplus..BotIAv2_UsuariosTelegram ut
    INNER JOIN abcmasplus..Usuarios u ON ut.idUsuario = u.idUsuario
    WHERE ut.telegramChatId = @telegramChatId
      AND ut.activo = 1;
END;
GO

-- ============================================================
-- 4. BotIAv2_sp_GetAdminChatIds
--    Reemplaza: user_query_repository.get_admin_chat_ids
-- ============================================================
CREATE OR ALTER PROCEDURE abcmasplus..BotIAv2_sp_GetAdminChatIds
    @idRolAdmin INT = 1
AS
BEGIN
    SET NOCOUNT ON;
    SELECT ut.telegramChatId
    FROM abcmasplus..BotIAv2_UsuariosTelegram ut
    INNER JOIN abcmasplus..Usuarios u ON ut.idUsuario = u.idUsuario
    WHERE u.idRol    = @idRolAdmin
      AND u.Activa   = 1
      AND ut.verificado = 1
      AND ut.activo  = 1
      AND ut.estado  = 'ACTIVO';
END;
GO

-- ============================================================
-- 5. BotIAv2_sp_ActualizarActividad
--    Reemplaza: user_query_repository.update_last_activity
--               user_repository.update_last_activity
-- ============================================================
CREATE OR ALTER PROCEDURE abcmasplus..BotIAv2_sp_ActualizarActividad
    @telegramChatId BIGINT
AS
BEGIN
    SET NOCOUNT ON;
    UPDATE abcmasplus..BotIAv2_UsuariosTelegram
    SET    fechaUltimaActividad = GETDATE()
    WHERE  telegramChatId = @telegramChatId
      AND  activo = 1;
    SELECT @@ROWCOUNT AS filasAfectadas;
END;
GO

-- ============================================================
-- 6. BotIAv2_sp_BuscarPorEmail
--    Reemplaza: telegram_account_repository.find_user_by_email
--               user_repository.find_user_by_email
-- ============================================================
CREATE OR ALTER PROCEDURE abcmasplus..BotIAv2_sp_BuscarPorEmail
    @email NVARCHAR(255)
AS
BEGIN
    SET NOCOUNT ON;
    SELECT idUsuario, Nombre, email, idRol, puesto, Activa
    FROM   abcmasplus..Usuarios
    WHERE  email = @email
      AND  Activa = 1;
END;
GO

-- ============================================================
-- 7. BotIAv2_sp_EstaRegistrado
--    Reemplaza: user_repository.is_user_registered
--    Retorna: 1 si tiene cuenta activa, 0 si no
-- ============================================================
CREATE OR ALTER PROCEDURE abcmasplus..BotIAv2_sp_EstaRegistrado
    @telegramChatId BIGINT
AS
BEGIN
    SET NOCOUNT ON;
    SELECT CAST(
        CASE WHEN EXISTS (
            SELECT 1 FROM abcmasplus..BotIAv2_UsuariosTelegram
            WHERE telegramChatId = @telegramChatId AND activo = 1
        ) THEN 1 ELSE 0 END
    AS BIT) AS estaRegistrado;
END;
GO

-- ============================================================
-- 8. BotIAv2_sp_GetInfoRegistro
--    Reemplaza: user_repository.get_registration_info
-- ============================================================
CREATE OR ALTER PROCEDURE abcmasplus..BotIAv2_sp_GetInfoRegistro
    @telegramChatId BIGINT
AS
BEGIN
    SET NOCOUNT ON;
    SELECT idUsuario, verificado, estado
    FROM   abcmasplus..BotIAv2_UsuariosTelegram
    WHERE  telegramChatId = @telegramChatId
      AND  activo = 1;
END;
GO

-- ============================================================
-- 9. BotIAv2_sp_GetEstadoRegistro
--    Reemplaza: telegram_account_repository.get_registration_status
--               user_repository.get_registration_status
-- ============================================================
CREATE OR ALTER PROCEDURE abcmasplus..BotIAv2_sp_GetEstadoRegistro
    @telegramChatId BIGINT
AS
BEGIN
    SET NOCOUNT ON;
    SELECT
        ut.verificado,
        ut.estado,
        ut.intentosVerificacion,
        ut.fechaRegistro,
        u.Nombre,
        u.email
    FROM abcmasplus..BotIAv2_UsuariosTelegram ut
    INNER JOIN abcmasplus..Usuarios u ON ut.idUsuario = u.idUsuario
    WHERE ut.telegramChatId = @telegramChatId
      AND ut.activo = 1;
END;
GO

-- ============================================================
-- 10. BotIAv2_sp_GetCuentasTelegram
--     Reemplaza: user_repository.get_all_user_telegram_accounts
-- ============================================================
CREATE OR ALTER PROCEDURE abcmasplus..BotIAv2_sp_GetCuentasTelegram
    @idUsuario INT
AS
BEGIN
    SET NOCOUNT ON;
    SELECT
        idUsuarioTelegram,
        telegramChatId,
        telegramUsername,
        alias,
        esPrincipal,
        estado,
        verificado,
        fechaRegistro,
        fechaUltimaActividad
    FROM abcmasplus..BotIAv2_UsuariosTelegram
    WHERE idUsuario = @idUsuario
      AND activo = 1
    ORDER BY esPrincipal DESC, fechaRegistro DESC;
END;
GO

-- ============================================================
-- 11. BotIAv2_sp_TieneCuentaTelegram
--     Reemplaza: telegram_account_repository.has_telegram_account
--                user_repository.has_telegram_account
-- ============================================================
CREATE OR ALTER PROCEDURE abcmasplus..BotIAv2_sp_TieneCuentaTelegram
    @telegramChatId BIGINT
AS
BEGIN
    SET NOCOUNT ON;
    SELECT CAST(
        CASE WHEN EXISTS (
            SELECT 1 FROM abcmasplus..BotIAv2_UsuariosTelegram
            WHERE telegramChatId = @telegramChatId AND activo = 1
        ) THEN 1 ELSE 0 END
    AS BIT) AS tieneCuenta;
END;
GO

-- ============================================================
-- 12. BotIAv2_sp_TieneCuentaPrincipal
--     Reemplaza: telegram_account_repository.has_principal_account
--                user_repository.has_principal_account
-- ============================================================
CREATE OR ALTER PROCEDURE abcmasplus..BotIAv2_sp_TieneCuentaPrincipal
    @idUsuario INT
AS
BEGIN
    SET NOCOUNT ON;
    SELECT CAST(
        CASE WHEN EXISTS (
            SELECT 1 FROM abcmasplus..BotIAv2_UsuariosTelegram
            WHERE idUsuario = @idUsuario AND esPrincipal = 1 AND activo = 1
        ) THEN 1 ELSE 0 END
    AS BIT) AS tienePrincipal;
END;
GO

-- ============================================================
-- 13. BotIAv2_sp_InsertarCuentaTelegram
--     Reemplaza: telegram_account_repository.insert_telegram_account
--                user_repository.insert_telegram_account
-- ============================================================
CREATE OR ALTER PROCEDURE abcmasplus..BotIAv2_sp_InsertarCuentaTelegram
    @idUsuario          INT,
    @telegramChatId     BIGINT,
    @telegramUsername   NVARCHAR(100)  = NULL,
    @telegramFirstName  NVARCHAR(100)  = NULL,
    @telegramLastName   NVARCHAR(100)  = NULL,
    @alias              NVARCHAR(100)  = NULL,
    @esPrincipal        BIT,
    @estado             NVARCHAR(20)   = 'ACTIVO',
    @codigoVerificacion NVARCHAR(50)
AS
BEGIN
    SET NOCOUNT ON;
    INSERT INTO abcmasplus..BotIAv2_UsuariosTelegram (
        idUsuario, telegramChatId, telegramUsername,
        telegramFirstName, telegramLastName, alias,
        esPrincipal, estado, codigoVerificacion,
        verificado, intentosVerificacion, fechaRegistro, activo
    ) VALUES (
        @idUsuario, @telegramChatId, @telegramUsername,
        @telegramFirstName, @telegramLastName, @alias,
        @esPrincipal, @estado, @codigoVerificacion,
        0, 0, GETDATE(), 1
    );
    SELECT SCOPE_IDENTITY() AS idUsuarioTelegram;
END;
GO

-- ============================================================
-- 14. BotIAv2_sp_GetPendienteVerificacion
--     Reemplaza: telegram_account_repository.get_pending_verification
--                user_repository.get_pending_verification
-- ============================================================
CREATE OR ALTER PROCEDURE abcmasplus..BotIAv2_sp_GetPendienteVerificacion
    @telegramChatId BIGINT
AS
BEGIN
    SET NOCOUNT ON;
    SELECT
        idUsuarioTelegram,
        idUsuario,
        codigoVerificacion,
        intentosVerificacion,
        fechaRegistro,
        verificado
    FROM abcmasplus..BotIAv2_UsuariosTelegram
    WHERE telegramChatId = @telegramChatId
      AND activo = 1;
END;
GO

-- ============================================================
-- 15. BotIAv2_sp_MarcarCuentaVerificada
--     Reemplaza: telegram_account_repository.mark_account_verified
--                user_repository.mark_account_verified
-- ============================================================
CREATE OR ALTER PROCEDURE abcmasplus..BotIAv2_sp_MarcarCuentaVerificada
    @telegramChatId BIGINT
AS
BEGIN
    SET NOCOUNT ON;
    UPDATE abcmasplus..BotIAv2_UsuariosTelegram
    SET    verificado          = 1,
           fechaVerificacion   = GETDATE(),
           codigoVerificacion  = NULL
    WHERE  telegramChatId = @telegramChatId;
    SELECT @@ROWCOUNT AS filasAfectadas;
END;
GO

-- ============================================================
-- 16. BotIAv2_sp_IncrementarIntentos
--     Reemplaza: telegram_account_repository.increment_verification_attempts
--                user_repository.increment_verification_attempts
-- ============================================================
CREATE OR ALTER PROCEDURE abcmasplus..BotIAv2_sp_IncrementarIntentos
    @telegramChatId BIGINT
AS
BEGIN
    SET NOCOUNT ON;
    UPDATE abcmasplus..BotIAv2_UsuariosTelegram
    SET    intentosVerificacion = intentosVerificacion + 1
    WHERE  telegramChatId = @telegramChatId;
    SELECT @@ROWCOUNT AS filasAfectadas;
END;
GO

-- ============================================================
-- 17. BotIAv2_sp_ActualizarCodigoVerificacion
--     Reemplaza: telegram_account_repository.update_verification_code
--                user_repository.update_verification_code
-- ============================================================
CREATE OR ALTER PROCEDURE abcmasplus..BotIAv2_sp_ActualizarCodigoVerificacion
    @telegramChatId     BIGINT,
    @codigoVerificacion NVARCHAR(50)
AS
BEGIN
    SET NOCOUNT ON;
    UPDATE abcmasplus..BotIAv2_UsuariosTelegram
    SET    codigoVerificacion   = @codigoVerificacion,
           intentosVerificacion = 0,
           fechaRegistro        = GETDATE()
    WHERE  telegramChatId = @telegramChatId;
    SELECT @@ROWCOUNT AS filasAfectadas;
END;
GO

-- ============================================================
-- 18. BotIAv2_sp_BloquearCuenta
--     Reemplaza: telegram_account_repository.block_account
--                user_repository.block_account
-- ============================================================
CREATE OR ALTER PROCEDURE abcmasplus..BotIAv2_sp_BloquearCuenta
    @telegramChatId BIGINT
AS
BEGIN
    SET NOCOUNT ON;
    UPDATE abcmasplus..BotIAv2_UsuariosTelegram
    SET    estado = 'BLOQUEADO'
    WHERE  telegramChatId = @telegramChatId;
    SELECT @@ROWCOUNT AS filasAfectadas;
END;
GO

-- ============================================================
-- 19. BotIAv2_sp_GetPermisosUsuario
--     Reemplaza: permission_repository.get_all_for_user
--     Nota: usa SQL dinámico para los IN de gerencias/direcciones
-- ============================================================
CREATE OR ALTER PROCEDURE abcmasplus..BotIAv2_sp_GetPermisosUsuario
    @idUsuario      INT,
    @idRol          INT,
    @gerenciaIds    NVARCHAR(MAX) = NULL,   -- CSV: "1,2,3" o NULL
    @direccionIds   NVARCHAR(MAX) = NULL    -- CSV: "1,2,3" o NULL
AS
BEGIN
    SET NOCOUNT ON;

    -- Normalizar NULLs a "0" para evitar IN () vacío
    IF @gerenciaIds  IS NULL OR LEN(LTRIM(RTRIM(@gerenciaIds)))  = 0 SET @gerenciaIds  = '0';
    IF @direccionIds IS NULL OR LEN(LTRIM(RTRIM(@direccionIds))) = 0 SET @direccionIds = '0';

    DECLARE @sql NVARCHAR(MAX) = N'
        SELECT br.recurso, bp.permitido, bte.tipoResolucion
        FROM abcmasplus..BotIAv2_Permisos      bp
        INNER JOIN abcmasplus..BotIAv2_Recurso     br  ON bp.idRecurso     = br.idRecurso
        INNER JOIN abcmasplus..BotIAv2_TipoEntidad bte ON bp.idTipoEntidad = bte.idTipoEntidad
        WHERE bp.activo = 1
          AND br.activo = 1
          AND (bp.fechaExpiracion IS NULL OR bp.fechaExpiracion > GETDATE())
          AND (
            (bte.nombre = ''usuario''
                AND bp.idEntidad = @idUsuario)
            OR (bte.nombre = ''autenticado''
                AND (bp.idRolRequerido IS NULL OR bp.idRolRequerido = @idRol))
            OR (bte.nombre = ''gerencia''
                AND bp.idEntidad IN (' + @gerenciaIds + N')
                AND (bp.idRolRequerido IS NULL OR bp.idRolRequerido = @idRol))
            OR (bte.nombre = ''direccion''
                AND bp.idEntidad IN (' + @direccionIds + N')
                AND (bp.idRolRequerido IS NULL OR bp.idRolRequerido = @idRol))
          )

        UNION ALL

        SELECT br.recurso, 1 AS permitido, ''permisivo'' AS tipoResolucion
        FROM abcmasplus..BotIAv2_Recurso br
        WHERE br.esPublico = 1
          AND br.activo    = 1
    ';

    EXEC sp_executesql @sql,
        N'@idUsuario INT, @idRol INT',
        @idUsuario = @idUsuario,
        @idRol     = @idRol;
END;
GO

-- ============================================================
-- 20. BotIAv2_sp_EsRecursoPublico
--     Reemplaza: permission_repository.is_public
-- ============================================================
CREATE OR ALTER PROCEDURE abcmasplus..BotIAv2_sp_EsRecursoPublico
    @recurso NVARCHAR(200)
AS
BEGIN
    SET NOCOUNT ON;
    SELECT ISNULL(esPublico, 0) AS esPublico
    FROM   abcmasplus..BotIAv2_Recurso
    WHERE  recurso = @recurso
      AND  activo  = 1;
END;
GO

-- ============================================================
-- 21. BotIAv2_sp_GetToolsActivas
--     Reemplaza: permission_repository.get_active_tool_names
-- ============================================================
CREATE OR ALTER PROCEDURE abcmasplus..BotIAv2_sp_GetToolsActivas
AS
BEGIN
    SET NOCOUNT ON;
    SELECT recurso
    FROM   abcmasplus..BotIAv2_Recurso
    WHERE  tipoRecurso = 'tool'
      AND  activo      = 1;
END;
GO

-- ============================================================
-- Verificación
-- ============================================================
SELECT
    name        AS sp_name,
    create_date,
    modify_date
FROM sys.procedures
WHERE name LIKE 'BotIAv2_sp_%'
ORDER BY name;

PRINT 'Migración 006 completada: ' + CAST((
    SELECT COUNT(*) FROM sys.procedures WHERE name LIKE 'BotIAv2_sp_%'
) AS VARCHAR) + ' SPs BotIAv2_sp_* disponibles.';
