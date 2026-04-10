-- ============================================================
-- Migración 010b: Fix — insertar permisos faltantes para las 4 tools de alertas
--
-- Problema: La migración 010 no insertó permisos en BotIAv2_Permisos
-- para las tools get_active_alerts, get_historical_tickets,
-- get_escalation_matrix y get_alert_detail.
--
-- Solución: Copiar los mismos permisos que ya existen para otras tools
-- de monitoreo (tool:alert_analysis), usando esos registros como plantilla.
-- ============================================================

USE abcmasplus;
GO

-- Verificar qué roles tienen permisos en otras tools (usamos alert_analysis como referencia)
-- SELECT DISTINCT idTipoEntidad, idEntidad, idRolRequerido
-- FROM abcmasplus..BotIAv2_Permisos
-- WHERE idRecurso = (SELECT idRecurso FROM BotIAv2_Recurso WHERE recurso = 'tool:alert_analysis');

DECLARE @idTipoEntidad INT = (
    SELECT TOP 1 idTipoEntidad FROM abcmasplus..BotIAv2_Permisos
    WHERE idRecurso = (
        SELECT idRecurso FROM abcmasplus..BotIAv2_Recurso WHERE recurso = 'tool:alert_analysis'
    )
);
DECLARE @idEntidad INT = 0;

PRINT 'idTipoEntidad de referencia: ' + ISNULL(CAST(@idTipoEntidad AS VARCHAR), 'NULL');

-- ── get_active_alerts ──────────────────────────────────────────────────────
DECLARE @idR1 INT = (SELECT idRecurso FROM abcmasplus..BotIAv2_Recurso WHERE recurso = 'tool:get_active_alerts');

INSERT INTO abcmasplus..BotIAv2_Permisos (idTipoEntidad, idEntidad, idRecurso, idRolRequerido, permitido, activo)
SELECT @idTipoEntidad, @idEntidad, @idR1, p.idRolRequerido, 1, 1
FROM abcmasplus..BotIAv2_Permisos p
JOIN abcmasplus..BotIAv2_Recurso r ON p.idRecurso = r.idRecurso
WHERE r.recurso = 'tool:alert_analysis'
  AND NOT EXISTS (
    SELECT 1 FROM abcmasplus..BotIAv2_Permisos
    WHERE idRecurso = @idR1 AND idRolRequerido = p.idRolRequerido AND activo = 1
  );

PRINT 'get_active_alerts: ' + CAST(@@ROWCOUNT AS VARCHAR) + ' permisos insertados';

-- ── get_historical_tickets ─────────────────────────────────────────────────
DECLARE @idR2 INT = (SELECT idRecurso FROM abcmasplus..BotIAv2_Recurso WHERE recurso = 'tool:get_historical_tickets');

INSERT INTO abcmasplus..BotIAv2_Permisos (idTipoEntidad, idEntidad, idRecurso, idRolRequerido, permitido, activo)
SELECT @idTipoEntidad, @idEntidad, @idR2, p.idRolRequerido, 1, 1
FROM abcmasplus..BotIAv2_Permisos p
JOIN abcmasplus..BotIAv2_Recurso r ON p.idRecurso = r.idRecurso
WHERE r.recurso = 'tool:alert_analysis'
  AND NOT EXISTS (
    SELECT 1 FROM abcmasplus..BotIAv2_Permisos
    WHERE idRecurso = @idR2 AND idRolRequerido = p.idRolRequerido AND activo = 1
  );

PRINT 'get_historical_tickets: ' + CAST(@@ROWCOUNT AS VARCHAR) + ' permisos insertados';

-- ── get_escalation_matrix ──────────────────────────────────────────────────
DECLARE @idR3 INT = (SELECT idRecurso FROM abcmasplus..BotIAv2_Recurso WHERE recurso = 'tool:get_escalation_matrix');

INSERT INTO abcmasplus..BotIAv2_Permisos (idTipoEntidad, idEntidad, idRecurso, idRolRequerido, permitido, activo)
SELECT @idTipoEntidad, @idEntidad, @idR3, p.idRolRequerido, 1, 1
FROM abcmasplus..BotIAv2_Permisos p
JOIN abcmasplus..BotIAv2_Recurso r ON p.idRecurso = r.idRecurso
WHERE r.recurso = 'tool:alert_analysis'
  AND NOT EXISTS (
    SELECT 1 FROM abcmasplus..BotIAv2_Permisos
    WHERE idRecurso = @idR3 AND idRolRequerido = p.idRolRequerido AND activo = 1
  );

PRINT 'get_escalation_matrix: ' + CAST(@@ROWCOUNT AS VARCHAR) + ' permisos insertados';

-- ── get_alert_detail ───────────────────────────────────────────────────────
DECLARE @idR4 INT = (SELECT idRecurso FROM abcmasplus..BotIAv2_Recurso WHERE recurso = 'tool:get_alert_detail');

INSERT INTO abcmasplus..BotIAv2_Permisos (idTipoEntidad, idEntidad, idRecurso, idRolRequerido, permitido, activo)
SELECT @idTipoEntidad, @idEntidad, @idR4, p.idRolRequerido, 1, 1
FROM abcmasplus..BotIAv2_Permisos p
JOIN abcmasplus..BotIAv2_Recurso r ON p.idRecurso = r.idRecurso
WHERE r.recurso = 'tool:alert_analysis'
  AND NOT EXISTS (
    SELECT 1 FROM abcmasplus..BotIAv2_Permisos
    WHERE idRecurso = @idR4 AND idRolRequerido = p.idRolRequerido AND activo = 1
  );

PRINT 'get_alert_detail: ' + CAST(@@ROWCOUNT AS VARCHAR) + ' permisos insertados';
GO

-- ── Verificación ─────────────────────────────────────────────────────────────
SELECT r.recurso, r.activo AS recurso_activo, p.idRolRequerido, p.permitido, p.activo AS permiso_activo
FROM abcmasplus..BotIAv2_Recurso r
LEFT JOIN abcmasplus..BotIAv2_Permisos p ON p.idRecurso = r.idRecurso
WHERE r.recurso IN (
    'tool:get_active_alerts', 'tool:get_historical_tickets',
    'tool:get_escalation_matrix', 'tool:get_alert_detail'
)
ORDER BY r.recurso, p.idRolRequerido;
GO
