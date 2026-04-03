-- Migración 003: Registrar cmd:/costo en SEC-01
-- Reemplaza el control por admin_chat_ids hardcodeado en settings.
-- Ejecutar manualmente en SQL Server Management Studio.

-- 1. Registrar el recurso cmd:/costo en BotRecurso (si no existe)
IF NOT EXISTS (
    SELECT 1 FROM abcmasplus..BotRecurso WHERE recurso = 'cmd:/costo'
)
BEGIN
    INSERT INTO abcmasplus..BotRecurso (recurso, descripcion, esPublico, activo)
    VALUES ('cmd:/costo', 'Comando /costo — ver costo diario de tokens por usuario', 0, 1);
END

-- 2. Obtener el idRecurso recién insertado (o existente)
DECLARE @idRecurso INT = (
    SELECT idRecurso FROM abcmasplus..BotRecurso WHERE recurso = 'cmd:/costo'
);

-- 3. Obtener idTipoEntidad para tipo 'autenticado' (aplica por rol)
DECLARE @idTipoEntidad INT = (
    SELECT idTipoEntidad FROM abcmasplus..BotTipoEntidad WHERE nombre = 'autenticado'
);

-- 4. Obtener idRol del Administrador
DECLARE @idRolAdmin INT = (
    SELECT idRol FROM abcmasplus..Roles WHERE nombre = 'Administrador'
);

-- 5. Registrar permiso para rol Administrador (si no existe)
IF NOT EXISTS (
    SELECT 1
    FROM abcmasplus..BotPermisos
    WHERE idRecurso = @idRecurso
      AND idTipoEntidad = @idTipoEntidad
      AND idRolRequerido = @idRolAdmin
)
BEGIN
    INSERT INTO abcmasplus..BotPermisos
        (idRecurso, idTipoEntidad, idEntidad, idRolRequerido, permitido, activo)
    VALUES
        (@idRecurso, @idTipoEntidad, NULL, @idRolAdmin, 1, 1);
END

SELECT 'cmd:/costo registrado en SEC-01 para rol Administrador' AS resultado;
