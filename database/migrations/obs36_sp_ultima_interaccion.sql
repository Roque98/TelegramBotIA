-- ============================================================
-- OBS-36: Actualización de BotIAv2_sp_UltimaInteraccion
-- Agrega resultado de BotIAv2_AgentRouting y columnas OBS-36.
-- ============================================================

USE abcmasplus;
GO

ALTER PROCEDURE dbo.BotIAv2_sp_UltimaInteraccion
AS
BEGIN
    SET NOCOUNT ON;

    -- Obtener el último correlationId insertado
    DECLARE @lastCorrelationId NVARCHAR(100);

    SELECT TOP 1 @lastCorrelationId = il.correlationId
    FROM abcmasplus..BotIAv2_InteractionLogs il
    ORDER BY il.fechaEjecucion DESC;

    IF @lastCorrelationId IS NULL
    BEGIN
        RAISERROR('No se encontraron registros en BotIAv2_InteractionLogs.', 16, 1);
        RETURN;
    END;

    -- 1. Última interacción (vista general)
    SELECT
        il.correlationId,
        il.telegramUsername,
        il.query,
        il.respuesta,
        il.exitoso,
        il.agenteNombre,
        il.stepsTomados,
        il.llmIteraciones,
        il.memoryMs,
        il.reactMs,
        il.duracionMs,
        il.classifyMs,
        il.agentConfidence,
        il.usedFallback,
        il.totalInputTokens,
        il.totalOutputTokens,
        il.costUSD,
        il.toolsUsadas,
        il.mensajeError,
        il.channel,
        il.fechaEjecucion
    FROM abcmasplus..BotIAv2_InteractionLogs il
    WHERE il.correlationId = @lastCorrelationId
    ORDER BY il.fechaEjecucion DESC;

    -- 2. Decisión de ruteo (OBS-36)
    SELECT
        ar.agenteSeleccionado,
        ar.confianza,
        ar.alternativas,
        ar.classifyMs,
        ar.usedFallback,
        ar.fechaCreacion
    FROM abcmasplus..BotIAv2_AgentRouting ar
    WHERE ar.correlationId = @lastCorrelationId;

    -- 3. Steps del último registro
    SELECT *
    FROM abcmasplus..BotIAv2_InteractionSteps s
    WHERE s.correlationId = @lastCorrelationId
    ORDER BY s.stepNum;

    -- 4. Costo del último registro (detalle por sesión)
    SELECT ut.telegramUsername, cs.*
    FROM abcmasplus..BotIAv2_CostSesiones cs
    LEFT JOIN abcmasplus..BotIAv2_UsuariosTelegram ut
        ON cs.telegramChatId = ut.telegramChatId
    WHERE cs.correlationId = @lastCorrelationId
    ORDER BY cs.fechaSesion DESC;

    -- 5. Validación: suma de InteractionSteps vs suma de CostSesiones
    SELECT
        s.sumStepsUSD,
        cs.sumCostSesionesUSD,
        s.sumStepsUSD - cs.sumCostSesionesUSD          AS diferencia,
        CASE
            WHEN ABS(s.sumStepsUSD - cs.sumCostSesionesUSD) < 0.000001
            THEN 'OK'
            ELSE 'DISCREPANCIA'
        END                                             AS estatus
    FROM (
        SELECT ISNULL(SUM(costoUSD), 0) AS sumStepsUSD
        FROM abcmasplus..BotIAv2_InteractionSteps
        WHERE correlationId = @lastCorrelationId
    ) s
    CROSS JOIN (
        SELECT ISNULL(SUM(costoUSD), 0) AS sumCostSesionesUSD
        FROM abcmasplus..BotIAv2_CostSesiones
        WHERE correlationId = @lastCorrelationId
    ) cs;

END;
GO
