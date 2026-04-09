-- Migración 001: Tabla ApplicationLogs
-- Persiste logs WARNING/ERROR con correlation_id para diagnóstico post-mortem.
-- Ejecutar manualmente en SQL Server Management Studio.

CREATE TABLE abcmasplus..ApplicationLogs (
    id            BIGINT IDENTITY PRIMARY KEY,
    correlationId NVARCHAR(8),
    userId        NVARCHAR(50),
    level         NVARCHAR(10)   NOT NULL,   -- WARNING, ERROR
    event         NVARCHAR(100)  NOT NULL,
    message       NVARCHAR(2000),
    module        NVARCHAR(100),
    durationMs    INT,
    extra         NVARCHAR(2000),            -- JSON con campos adicionales
    createdAt     DATETIME       DEFAULT GETDATE()
);

CREATE INDEX IX_ApplicationLogs_level         ON abcmasplus..ApplicationLogs (level);
CREATE INDEX IX_ApplicationLogs_correlationId ON abcmasplus..ApplicationLogs (correlationId);
CREATE INDEX IX_ApplicationLogs_createdAt     ON abcmasplus..ApplicationLogs (createdAt DESC);

-- Retención: borrar registros con más de 90 días
-- (ejecutar periódicamente o como job de SQL Agent)
-- DELETE FROM abcmasplus..ApplicationLogs WHERE createdAt < DATEADD(DAY, -90, GETDATE());
