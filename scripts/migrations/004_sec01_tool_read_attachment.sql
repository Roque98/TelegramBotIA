-- Migración 004: Registrar tool:read_attachment en SEC-01
-- Idempotente — se puede ejecutar más de una vez sin errores.
-- Ejecutar manualmente en SQL Server Management Studio.

-- 1. Insertar en BotRecurso si no existe
IF NOT EXISTS (SELECT 1 FROM abcmasplus..BotIAv2_Recurso WHERE recurso = 'tool:read_attachment')
BEGIN
    INSERT INTO abcmasplus..BotIAv2_Recurso
        (recurso, descripcion, tipoRecurso, esPublico, activo)
    VALUES
        ('tool:read_attachment', 'Herramienta para leer archivos adjuntos enviados por el usuario', 'tool', 0, 1);
END

-- 2. Actualizar para asegurar que los campos estén completos (por si se insertó parcialmente)
UPDATE abcmasplus..BotIAv2_Recurso
SET
    descripcion  = 'Herramienta para leer archivos adjuntos enviados por el usuario',
    tipoRecurso  = 'tool',
    esPublico    = 0,
    activo       = 1
WHERE recurso = 'tool:read_attachment';

-- 3. Permisos por rol (mismos que database_query: 1,2,3,4,7,8)
DECLARE @idRecurso    INT = (SELECT idRecurso    FROM abcmasplus..BotIAv2_Recurso    WHERE recurso = 'tool:read_attachment');
DECLARE @idTipoEntidad INT = (SELECT idTipoEntidad FROM abcmasplus..BotIAv2_TipoEntidad WHERE nombre  = 'autenticado');

INSERT INTO abcmasplus..BotIAv2_Permisos
    (idTipoEntidad, idEntidad, idRecurso, idRolRequerido, permitido, activo)
SELECT @idTipoEntidad, 0, @idRecurso, idRol, 1, 1
FROM (VALUES (1),(2),(3),(4),(7),(8)) AS roles(idRol)
WHERE NOT EXISTS (
    SELECT 1 FROM abcmasplus..BotIAv2_Permisos
    WHERE idRecurso = @idRecurso AND idRolRequerido = roles.idRol AND activo = 1
);

SELECT 'tool:read_attachment registrado en SEC-01' AS resultado;
