-- Migración 025: Caché de análisis de tickets por IP/sensor
-- Propósito: evitar llamadas redundantes al LLM cuando los tickets no han cambiado.
-- Invalidación: si cambia total_tickets o la accionCorrectiva del último ticket → nuevo análisis.

IF NOT EXISTS (
    SELECT 1 FROM sys.tables
    WHERE name = 'BotIAv2_TicketAnalysisCache'
      AND SCHEMA_NAME(schema_id) = 'dbo'
)
BEGIN
    CREATE TABLE abcmasplus..BotIAv2_TicketAnalysisCache (
        id               INT IDENTITY(1,1) PRIMARY KEY,
        ip               VARCHAR(50)    NOT NULL,
        sensor           VARCHAR(100)   NOT NULL,
        total_tickets    INT            NOT NULL,
        ultima_accion    NVARCHAR(500)  NOT NULL,
        analisis         NVARCHAR(MAX)  NOT NULL,
        fechaCreacion    DATETIME       NOT NULL DEFAULT GETDATE()
    );

    CREATE UNIQUE INDEX UX_TicketAnalysisCache_Key
        ON abcmasplus..BotIAv2_TicketAnalysisCache (ip, sensor, total_tickets, ultima_accion);

    PRINT 'Tabla BotIAv2_TicketAnalysisCache creada.';
END
ELSE
    PRINT 'Tabla BotIAv2_TicketAnalysisCache ya existe — sin cambios.';
