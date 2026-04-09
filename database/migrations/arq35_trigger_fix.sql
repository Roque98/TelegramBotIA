-- ============================================================
-- ARQ-35: Trigger para versionado automático de prompts
-- Ejecutar dentro de la base de datos abcmasplus.
-- El CREATE/ALTER TRIGGER NO permite prefijo de BD, por eso está separado.
-- ============================================================

USE abcmasplus;
GO

IF OBJECT_ID('TR_AgenteDef_VersionHistorial', 'TR') IS NOT NULL
    DROP TRIGGER TR_AgenteDef_VersionHistorial;
GO

CREATE TRIGGER TR_AgenteDef_VersionHistorial
ON BotIAv2_AgenteDef
AFTER UPDATE
AS
BEGIN
    SET NOCOUNT ON;

    -- Solo actuar si systemPrompt cambió
    IF NOT UPDATE(systemPrompt)
        RETURN;

    -- Insertar la versión ANTERIOR en historial (DELETED tiene el prompt viejo)
    INSERT INTO BotIAv2_AgentePromptHistorial
        (idAgente, systemPrompt, version, razonCambio, modificadoPor)
    SELECT
        d.idAgente,
        d.systemPrompt,
        d.version,
        N'Actualización automática vía trigger',
        SYSTEM_USER
    FROM DELETED d;

    -- Incrementar version en la fila actualizada
    UPDATE ad
    SET ad.version            = ad.version + 1,
        ad.fechaActualizacion = GETDATE()
    FROM BotIAv2_AgenteDef ad
    INNER JOIN INSERTED i ON ad.idAgente = i.idAgente;

END;
GO

PRINT 'Trigger TR_AgenteDef_VersionHistorial creado exitosamente.';
GO
