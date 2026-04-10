-- ============================================================
-- Migración 014: Registrar tool get_contacto_gerencia
--
-- Registra el recurso 'tool:get_contacto_gerencia' en BotIAv2_Recurso
-- y copia los permisos de las tools de alertas existentes.
-- ============================================================

USE abcmasplus;
GO

-- ── 1. Registrar el recurso ────────────────────────────────────────────────
IF NOT EXISTS (SELECT 1 FROM abcmasplus..BotIAv2_Recurso WHERE recurso = 'tool:get_contacto_gerencia')
BEGIN
    INSERT INTO abcmasplus..BotIAv2_Recurso (recurso, tipoRecurso, esPublico, descripcion, activo)
    VALUES ('tool:get_contacto_gerencia', 'tool', 0, 'Tool: Obtener contacto de gerencia por ID', 1);
    PRINT 'Recurso tool:get_contacto_gerencia insertado.';
END
ELSE
BEGIN
    PRINT 'Recurso tool:get_contacto_gerencia ya existe, omitiendo inserción.';
END
GO

-- ── 2. Copiar permisos desde get_escalation_matrix ────────────────────────
DECLARE @idRecursoNuevo INT = (
    SELECT idRecurso FROM abcmasplus..BotIAv2_Recurso WHERE recurso = 'tool:get_contacto_gerencia'
);
DECLARE @idTipoEntidad INT = (
    SELECT TOP 1 idTipoEntidad FROM abcmasplus..BotIAv2_Permisos
    WHERE idRecurso = (
        SELECT idRecurso FROM abcmasplus..BotIAv2_Recurso WHERE recurso = 'tool:get_escalation_matrix'
    )
);
DECLARE @idEntidad INT = 0;

INSERT INTO abcmasplus..BotIAv2_Permisos (idTipoEntidad, idEntidad, idRecurso, idRolRequerido, permitido, activo)
SELECT @idTipoEntidad, @idEntidad, @idRecursoNuevo, p.idRolRequerido, 1, 1
FROM abcmasplus..BotIAv2_Permisos p
JOIN abcmasplus..BotIAv2_Recurso r ON p.idRecurso = r.idRecurso
WHERE r.recurso = 'tool:get_escalation_matrix'
  AND NOT EXISTS (
    SELECT 1 FROM abcmasplus..BotIAv2_Permisos
    WHERE idRecurso = @idRecursoNuevo AND idRolRequerido = p.idRolRequerido AND activo = 1
  );

PRINT 'get_contacto_gerencia: ' + CAST(@@ROWCOUNT AS VARCHAR) + ' permisos insertados.';
GO

-- ── 3. Verificación ───────────────────────────────────────────────────────
SELECT r.recurso, r.activo AS recurso_activo, p.idRolRequerido, p.permitido, p.activo AS permiso_activo
FROM abcmasplus..BotIAv2_Recurso r
LEFT JOIN abcmasplus..BotIAv2_Permisos p ON p.idRecurso = r.idRecurso
WHERE r.recurso = 'tool:get_contacto_gerencia'
ORDER BY p.idRolRequerido;
GO
