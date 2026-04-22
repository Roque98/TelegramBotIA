-- ============================================================
-- Migración 018: Registrar tool template_search_by_name
--
-- Cambios:
--   1. INSERT en BotIAv2_Recurso
--   2. Copiar permisos desde get_template_by_id
--   3. Asignar tool al agente alertas en BotIAv2_AgenteTools
--
-- Idempotente: usa IF NOT EXISTS en cada paso.
-- ============================================================

USE abcmasplus;
GO

-- ── 1. Registrar recurso ─────────────────────────────────────────────────────
IF NOT EXISTS (
    SELECT 1 FROM abcmasplus..BotIAv2_Recurso
    WHERE recurso = 'tool:template_search_by_name'
)
BEGIN
    INSERT INTO abcmasplus..BotIAv2_Recurso
        (recurso, tipoRecurso, esPublico, descripcion, activo)
    VALUES
        (
            'tool:template_search_by_name',
            'tool',
            0,
            N'Busca templates por nombre de aplicación en banco (BAZ) y EKT en paralelo. '
            + N'Retorna lista con id, aplicación e instancia para que el agente sepa '
            + N'si usar usar_ekt=true en consultas posteriores (escalamiento, detalle).',
            1
        );
    PRINT 'OK: Recurso tool:template_search_by_name creado.';
END
ELSE
    PRINT 'INFO: Recurso tool:template_search_by_name ya existe.';
GO

-- ── 2. Copiar permisos desde get_template_by_id ──────────────────────────────
DECLARE @idRecursoNuevo INT = (
    SELECT idRecurso FROM abcmasplus..BotIAv2_Recurso
    WHERE recurso = 'tool:template_search_by_name'
);
DECLARE @idRecursoRef INT = (
    SELECT idRecurso FROM abcmasplus..BotIAv2_Recurso
    WHERE recurso = 'tool:get_template_by_id'
);

IF @idRecursoRef IS NOT NULL AND @idRecursoNuevo IS NOT NULL
BEGIN
    INSERT INTO abcmasplus..BotIAv2_Permisos
        (idTipoEntidad, idEntidad, idRecurso, idRolRequerido, permitido, activo)
    SELECT
        p.idTipoEntidad,
        p.idEntidad,
        @idRecursoNuevo,
        p.idRolRequerido,
        1,
        1
    FROM abcmasplus..BotIAv2_Permisos p
    WHERE p.idRecurso = @idRecursoRef
      AND NOT EXISTS (
          SELECT 1 FROM abcmasplus..BotIAv2_Permisos
          WHERE idRecurso      = @idRecursoNuevo
            AND idRolRequerido = p.idRolRequerido
            AND idTipoEntidad  = p.idTipoEntidad
            AND activo         = 1
      );

    PRINT 'OK: Permisos copiados desde get_template_by_id.';
END
ELSE
    PRINT 'ADVERTENCIA: No se encontró recurso de referencia get_template_by_id — permisos no copiados.';
GO

-- ── 3. Asignar tool al agente alertas ────────────────────────────────────────
DECLARE @idAgente INT = (
    SELECT idAgente FROM abcmasplus..BotIAv2_AgenteDef
    WHERE nombre = 'alertas'
);

IF @idAgente IS NOT NULL
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM abcmasplus..BotIAv2_AgenteTools
        WHERE idAgente    = @idAgente
          AND nombreTool  = 'template_search_by_name'
    )
    BEGIN
        INSERT INTO abcmasplus..BotIAv2_AgenteTools (idAgente, nombreTool, activo)
        VALUES (@idAgente, 'template_search_by_name', 1);
        PRINT 'OK: Tool template_search_by_name asignada al agente alertas.';
    END
    ELSE
        PRINT 'INFO: Tool template_search_by_name ya estaba asignada al agente alertas.';
END
ELSE
    PRINT 'ADVERTENCIA: No se encontró el agente alertas.';
GO

-- ── 4. Verificación ──────────────────────────────────────────────────────────
SELECT
    r.recurso,
    r.activo                        AS recurso_activo,
    r.descripcion                   AS descripcion_corta,
    (
        SELECT COUNT(*)
        FROM abcmasplus..BotIAv2_Permisos p
        WHERE p.idRecurso = r.idRecurso AND p.activo = 1
    )                               AS permisos_activos,
    (
        SELECT COUNT(*)
        FROM abcmasplus..BotIAv2_AgenteTools at2
        JOIN abcmasplus..BotIAv2_AgenteDef   ad ON ad.idAgente = at2.idAgente
        WHERE at2.nombreTool = 'template_search_by_name'
          AND ad.nombre      = 'alertas'
          AND at2.activo     = 1
    )                               AS asignada_alertas
FROM abcmasplus..BotIAv2_Recurso r
WHERE r.recurso = 'tool:template_search_by_name';
GO
