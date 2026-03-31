-- Migración 002: Tabla TransactionLogs
-- Una fila por request con los tiempos de cada etapa del pipeline.
-- Ejecutar manualmente en SQL Server Management Studio.

CREATE TABLE abcmasplus..TransactionLogs (
    id            BIGINT IDENTITY PRIMARY KEY,
    correlationId NVARCHAR(8)    NOT NULL,
    userId        NVARCHAR(50),
    username      NVARCHAR(100),
    query         NVARCHAR(500),
    channel       NVARCHAR(20)   DEFAULT 'telegram',
    memoryMs      INT,
    reactMs       INT,
    saveMs        INT,
    totalMs       INT,
    success       BIT            NOT NULL,
    errorMessage  NVARCHAR(1000),
    toolsUsed     NVARCHAR(500),             -- JSON: ["database_query", "knowledge_search"]
    stepsCount    INT,
    createdAt     DATETIME       DEFAULT GETDATE()
);

CREATE INDEX IX_TransactionLogs_userId    ON abcmasplus..TransactionLogs (userId);
CREATE INDEX IX_TransactionLogs_createdAt ON abcmasplus..TransactionLogs (createdAt DESC);

-- Consultas útiles de ejemplo:
--
-- Latencia promedio de LLM (reactMs) por día:
-- SELECT CAST(createdAt AS DATE) dia, AVG(reactMs) avg_react_ms, COUNT(*) requests
-- FROM abcmasplus..TransactionLogs
-- GROUP BY CAST(createdAt AS DATE)
-- ORDER BY dia DESC
--
-- Requests más lentos de la última semana:
-- SELECT TOP 20 correlationId, userId, query, totalMs, createdAt
-- FROM abcmasplus..TransactionLogs
-- WHERE createdAt > DATEADD(DAY, -7, GETDATE())
-- ORDER BY totalMs DESC
--
-- Tasa de error por día:
-- SELECT CAST(createdAt AS DATE) dia,
--        SUM(CASE WHEN success=1 THEN 1 ELSE 0 END) exitosos,
--        SUM(CASE WHEN success=0 THEN 1 ELSE 0 END) errores
-- FROM abcmasplus..TransactionLogs
-- GROUP BY CAST(createdAt AS DATE)
-- ORDER BY dia DESC

-- Retención: borrar registros con más de 90 días
-- DELETE FROM abcmasplus..TransactionLogs WHERE createdAt < DATEADD(DAY, -90, GETDATE());
