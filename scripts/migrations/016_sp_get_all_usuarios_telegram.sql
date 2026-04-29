-- Migración 016: SP para listar todos los usuarios Telegram activos (panel admin)
-- Usado por: GET /api/admin/users en dashboard_api.py

CREATE OR ALTER PROCEDURE abcmasplus..BotIAv2_sp_GetAllUsuariosTelegram
AS
BEGIN
    SET NOCOUNT ON;
    SELECT
        u.idUsuario,
        u.Nombre,
        u.idRol,
        r.rol               AS rolNombre,
        ut.telegramChatId,
        ut.telegramUsername,
        ut.estado,
        ut.verificado,
        ut.fechaUltimaActividad
    FROM abcmasplus..BotIAv2_UsuariosTelegram ut
    INNER JOIN abcmasplus..Usuarios u ON ut.idUsuario = u.idUsuario
    LEFT  JOIN abcmasplus..Roles    r ON u.idRol = r.idRol
    WHERE ut.activo = 1
    ORDER BY ut.fechaUltimaActividad DESC;
END;
GO
