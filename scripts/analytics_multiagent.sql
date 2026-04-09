-- ============================================================
-- OBS-36: Analytics Multi-Agente
-- Queries de análisis para el sistema de orquestación N-way.
-- Ejecutar en SSMS o herramienta de reporting.
-- ============================================================

USE abcmasplus;
GO

-- ------------------------------------------------------------
-- 1. Distribución de ruteo por agente (últimos 7 días)
-- ------------------------------------------------------------
SELECT
    agenteNombre,
    COUNT(*)                                    AS totalRequests,
    SUM(CASE WHEN exitoso = 1 THEN 1 ELSE 0 END) AS exitosos,
    SUM(CASE WHEN exitoso = 0 THEN 1 ELSE 0 END) AS errores,
    CAST(
        100.0 * SUM(CASE WHEN exitoso = 1 THEN 1 ELSE 0 END) / COUNT(*)
        AS DECIMAL(5,1)
    )                                           AS pctExito,
    SUM(CASE WHEN usedFallback = 1 THEN 1 ELSE 0 END) AS usedFallback
FROM abcmasplus..BotIAv2_InteractionLogs
WHERE fechaEjecucion >= DATEADD(DAY, -7, GETDATE())
  AND agenteNombre IS NOT NULL
GROUP BY agenteNombre
ORDER BY totalRequests DESC;
GO

-- ------------------------------------------------------------
-- 2. Latencia promedio por agente (classify + react)
-- ------------------------------------------------------------
SELECT
    agenteNombre,
    COUNT(*)                        AS totalRequests,
    AVG(classifyMs)                 AS avgClassifyMs,
    MIN(classifyMs)                 AS minClassifyMs,
    MAX(classifyMs)                 AS maxClassifyMs,
    AVG(reactMs)                    AS avgReactMs,
    AVG(duracionMs)                 AS avgTotalMs,
    PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY duracionMs)
        OVER (PARTITION BY agenteNombre) AS p95TotalMs
FROM abcmasplus..BotIAv2_InteractionLogs
WHERE fechaEjecucion >= DATEADD(DAY, -7, GETDATE())
  AND agenteNombre IS NOT NULL
  AND classifyMs IS NOT NULL
GROUP BY agenteNombre, duracionMs
ORDER BY agenteNombre;
GO

-- ------------------------------------------------------------
-- 3. Costo USD por agente (últimos 7 días)
-- ------------------------------------------------------------
SELECT
    agenteNombre,
    COUNT(*)                    AS totalRequests,
    SUM(costUSD)                AS totalCostUSD,
    AVG(costUSD)                AS avgCostUSD,
    MAX(costUSD)                AS maxCostUSD,
    SUM(totalInputTokens)       AS totalInputTokens,
    SUM(totalOutputTokens)      AS totalOutputTokens
FROM abcmasplus..BotIAv2_InteractionLogs
WHERE fechaEjecucion >= DATEADD(DAY, -7, GETDATE())
  AND agenteNombre IS NOT NULL
  AND costUSD IS NOT NULL
GROUP BY agenteNombre
ORDER BY totalCostUSD DESC;
GO

-- ------------------------------------------------------------
-- 4. Tasa de fallback por hora (últimas 24 horas)
-- ------------------------------------------------------------
SELECT
    DATEADD(HOUR, DATEDIFF(HOUR, 0, fechaEjecucion), 0) AS hora,
    COUNT(*)                                             AS totalRequests,
    SUM(CASE WHEN usedFallback = 1 THEN 1 ELSE 0 END)   AS fallbacks,
    CAST(
        100.0 * SUM(CASE WHEN usedFallback = 1 THEN 1 ELSE 0 END) / COUNT(*)
        AS DECIMAL(5,1)
    )                                                    AS pctFallback
FROM abcmasplus..BotIAv2_InteractionLogs
WHERE fechaEjecucion >= DATEADD(HOUR, -24, GETDATE())
GROUP BY DATEADD(HOUR, DATEDIFF(HOUR, 0, fechaEjecucion), 0)
ORDER BY hora DESC;
GO

-- ------------------------------------------------------------
-- 5. Confianza del clasificador por agente (últimos 7 días)
-- ------------------------------------------------------------
SELECT
    agenteSeleccionado,
    COUNT(*)                    AS totalClasificaciones,
    AVG(confianza)              AS avgConfianza,
    MIN(confianza)              AS minConfianza,
    SUM(CASE WHEN usedFallback = 1 THEN 1 ELSE 0 END) AS fallbacks,
    AVG(classifyMs)             AS avgClassifyMs
FROM abcmasplus..BotIAv2_AgentRouting
WHERE fechaCreacion >= DATEADD(DAY, -7, GETDATE())
GROUP BY agenteSeleccionado
ORDER BY totalClasificaciones DESC;
GO

-- ------------------------------------------------------------
-- 6. Requests con baja confianza de clasificación (candidatos a revisar)
-- ------------------------------------------------------------
SELECT TOP 50
    ar.correlationId,
    ar.query,
    ar.agenteSeleccionado,
    ar.confianza,
    ar.alternativas,
    ar.classifyMs,
    ar.fechaCreacion
FROM abcmasplus..BotIAv2_AgentRouting ar
WHERE ar.confianza < 0.70
  AND ar.fechaCreacion >= DATEADD(DAY, -7, GETDATE())
ORDER BY ar.confianza ASC, ar.fechaCreacion DESC;
GO

-- ------------------------------------------------------------
-- 7. Iteraciones LLM por agente (profundidad de razonamiento)
-- ------------------------------------------------------------
SELECT
    agenteNombre,
    COUNT(*)                    AS totalRequests,
    AVG(llmIteraciones)         AS avgIteraciones,
    MAX(llmIteraciones)         AS maxIteraciones,
    SUM(CASE WHEN llmIteraciones >= 8 THEN 1 ELSE 0 END) AS requestsConMuchasIter
FROM abcmasplus..BotIAv2_InteractionLogs
WHERE fechaEjecucion >= DATEADD(DAY, -7, GETDATE())
  AND llmIteraciones IS NOT NULL
GROUP BY agenteNombre
ORDER BY avgIteraciones DESC;
GO

-- ------------------------------------------------------------
-- 8. Vista completa del último request (debug)
-- ------------------------------------------------------------
DECLARE @lastCid VARCHAR(50);
SELECT TOP 1 @lastCid = correlationId
FROM abcmasplus..BotIAv2_InteractionLogs
ORDER BY fechaEjecucion DESC;

SELECT
    il.correlationId,
    il.agenteNombre,
    il.query,
    il.exitoso,
    il.duracionMs,
    il.reactMs,
    il.classifyMs,
    il.agentConfidence,
    il.usedFallback,
    il.llmIteraciones,
    il.totalInputTokens,
    il.totalOutputTokens,
    il.costUSD,
    il.stepsTomados
FROM abcmasplus..BotIAv2_InteractionLogs il
WHERE il.correlationId = @lastCid;

SELECT
    ar.agenteSeleccionado,
    ar.confianza,
    ar.alternativas,
    ar.classifyMs,
    ar.usedFallback
FROM abcmasplus..BotIAv2_AgentRouting ar
WHERE ar.correlationId = @lastCid;

SELECT
    s.stepNum,
    s.tipo,
    s.nombre,
    s.tokensIn,
    s.tokensOut,
    s.costoUSD,
    s.duracionMs
FROM abcmasplus..BotIAv2_InteractionSteps s
WHERE s.correlationId = @lastCid
ORDER BY s.stepNum;
GO
