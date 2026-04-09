-- ============================================================
-- OBS-36: Observabilidad para Multi-Agente
-- Extiende InteractionLogs y crea BotIAv2_AgentRouting.
-- Ejecutar una sola vez. Idempotente (IF NOT EXISTS).
-- ============================================================

USE abcmasplus;
GO

-- ------------------------------------------------------------
-- 1. ALTERs en BotIAv2_InteractionLogs
-- ------------------------------------------------------------

-- Tokens agregados por request
IF NOT EXISTS (
    SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_NAME = 'BotIAv2_InteractionLogs' AND COLUMN_NAME = 'totalInputTokens'
)
BEGIN
    ALTER TABLE abcmasplus..BotIAv2_InteractionLogs
    ADD totalInputTokens INT NULL;
    PRINT 'Columna totalInputTokens agregada.';
END
ELSE PRINT 'totalInputTokens ya existe, omitida.';
GO

IF NOT EXISTS (
    SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_NAME = 'BotIAv2_InteractionLogs' AND COLUMN_NAME = 'totalOutputTokens'
)
BEGIN
    ALTER TABLE abcmasplus..BotIAv2_InteractionLogs
    ADD totalOutputTokens INT NULL;
    PRINT 'Columna totalOutputTokens agregada.';
END
ELSE PRINT 'totalOutputTokens ya existe, omitida.';
GO

-- Cantidad de iteraciones LLM dentro del loop ReAct
IF NOT EXISTS (
    SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_NAME = 'BotIAv2_InteractionLogs' AND COLUMN_NAME = 'llmIteraciones'
)
BEGIN
    ALTER TABLE abcmasplus..BotIAv2_InteractionLogs
    ADD llmIteraciones INT NULL;
    PRINT 'Columna llmIteraciones agregada.';
END
ELSE PRINT 'llmIteraciones ya existe, omitida.';
GO

-- Flag: el orchestrator usó el agente generalista como fallback
IF NOT EXISTS (
    SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_NAME = 'BotIAv2_InteractionLogs' AND COLUMN_NAME = 'usedFallback'
)
BEGIN
    ALTER TABLE abcmasplus..BotIAv2_InteractionLogs
    ADD usedFallback BIT NOT NULL DEFAULT 0;
    PRINT 'Columna usedFallback agregada.';
END
ELSE PRINT 'usedFallback ya existe, omitida.';
GO

-- Latencia del IntentClassifier (ms)
IF NOT EXISTS (
    SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_NAME = 'BotIAv2_InteractionLogs' AND COLUMN_NAME = 'classifyMs'
)
BEGIN
    ALTER TABLE abcmasplus..BotIAv2_InteractionLogs
    ADD classifyMs INT NULL;
    PRINT 'Columna classifyMs agregada.';
END
ELSE PRINT 'classifyMs ya existe, omitida.';
GO

-- Confianza del clasificador (0.0 – 1.0)
IF NOT EXISTS (
    SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_NAME = 'BotIAv2_InteractionLogs' AND COLUMN_NAME = 'agentConfidence'
)
BEGIN
    ALTER TABLE abcmasplus..BotIAv2_InteractionLogs
    ADD agentConfidence DECIMAL(5,4) NULL;
    PRINT 'Columna agentConfidence agregada.';
END
ELSE PRINT 'agentConfidence ya existe, omitida.';
GO

-- Costo total del request en USD
IF NOT EXISTS (
    SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_NAME = 'BotIAv2_InteractionLogs' AND COLUMN_NAME = 'costUSD'
)
BEGIN
    ALTER TABLE abcmasplus..BotIAv2_InteractionLogs
    ADD costUSD DECIMAL(10,6) NULL;
    PRINT 'Columna costUSD agregada.';
END
ELSE PRINT 'costUSD ya existe, omitida.';
GO

-- ------------------------------------------------------------
-- 2. Nueva tabla: BotIAv2_AgentRouting
--    Una fila por request — auditoría de decisiones de ruteo.
-- ------------------------------------------------------------
IF NOT EXISTS (
    SELECT 1 FROM INFORMATION_SCHEMA.TABLES
    WHERE TABLE_NAME = 'BotIAv2_AgentRouting'
)
BEGIN
    CREATE TABLE abcmasplus..BotIAv2_AgentRouting (
        idRouting           INT PRIMARY KEY IDENTITY,
        correlationId       VARCHAR(50)     NOT NULL,
        query               NVARCHAR(1000)  NULL,           -- texto de la consulta (truncado)
        agenteSeleccionado  VARCHAR(100)    NOT NULL,
        confianza           DECIMAL(5,4)    NULL,           -- 0.0–1.0; NULL si no disponible
        alternativas        NVARCHAR(500)   NULL,           -- JSON: [{"agente":"x","score":0.3}]
        classifyMs          INT             NOT NULL,
        usedFallback        BIT             NOT NULL DEFAULT 0,
        fechaCreacion       DATETIME2               DEFAULT GETDATE()
    );

    CREATE NONCLUSTERED INDEX IX_AgentRouting_CorrelationId
        ON abcmasplus..BotIAv2_AgentRouting (correlationId);

    CREATE NONCLUSTERED INDEX IX_AgentRouting_Agente
        ON abcmasplus..BotIAv2_AgentRouting (agenteSeleccionado, fechaCreacion DESC);

    PRINT 'BotIAv2_AgentRouting creada.';
END
ELSE PRINT 'BotIAv2_AgentRouting ya existe, omitida.';
GO

-- ------------------------------------------------------------
-- Verificación final
-- ------------------------------------------------------------
SELECT
    COLUMN_NAME,
    DATA_TYPE,
    IS_NULLABLE
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_NAME = 'BotIAv2_InteractionLogs'
ORDER BY ORDINAL_POSITION;
GO

SELECT
    COLUMN_NAME,
    DATA_TYPE,
    IS_NULLABLE
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_NAME = 'BotIAv2_AgentRouting'
ORDER BY ORDINAL_POSITION;
GO
