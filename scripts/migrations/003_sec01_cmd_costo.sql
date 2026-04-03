-- Migración 003: Registrar cmd:/costo en SEC-01
-- Reemplaza el control por admin_chat_ids hardcodeado en settings.
-- Idempotente — se puede ejecutar más de una vez sin errores.
-- Ejecutar manualmente en SQL Server Management Studio.

-- 1. Registrar en BotRecurso
IF NOT EXISTS (SELECT 1 FROM abcmasplus..BotRecurso WHERE recurso = 'cmd:/costo')
BEGIN
    INSERT INTO abcmasplus..BotRecurso
        (recurso, descripcion, tipoRecurso, esPublico, activo)
    VALUES
        ('cmd:/costo', 'Comando /costo — ver costo diario de tokens por usuario', 'cmd', 0, 1);
END

-- 2. Permiso para rol Administrador
DECLARE @idRecurso    INT = (SELECT idRecurso    FROM abcmasplus..BotRecurso    WHERE recurso = 'cmd:/costo');
DECLARE @idTipoEntidad INT = (SELECT idTipoEntidad FROM abcmasplus..BotTipoEntidad WHERE nombre  = 'autenticado');
DECLARE @idRolAdmin   INT = (SELECT idRol         FROM abcmasplus..Roles          WHERE nombre  = 'Administrador');

IF NOT EXISTS (
    SELECT 1 FROM abcmasplus..BotPermisos
    WHERE idRecurso = @idRecurso AND idRolRequerido = @idRolAdmin AND activo = 1
)
BEGIN
    INSERT INTO abcmasplus..BotPermisos
        (idTipoEntidad, idEntidad, idRecurso, idRolRequerido, permitido, activo)
    VALUES
        (@idTipoEntidad, 0, @idRecurso, @idRolAdmin, 1, 1);
END

SELECT 'cmd:/costo registrado en SEC-01 para rol Administrador' AS resultado;
