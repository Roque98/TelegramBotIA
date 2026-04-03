-- ============================================================================
-- Script: SEC-01 — Trigger de audit para BotPermisos
-- Base de Datos: abcmasplus
-- Descripción: Captura INSERT/UPDATE/DELETE en BotPermisos → BotPermisosAudit
-- Idempotente: DROP + CREATE
-- ============================================================================

USE abcmasplus;
GO

PRINT '============================================================================';
PRINT 'SEC-01: Creando trigger de audit para BotPermisos';
PRINT '============================================================================';

IF OBJECT_ID('dbo.TR_BotPermisos_Audit', 'TR') IS NOT NULL
    DROP TRIGGER dbo.TR_BotPermisos_Audit;
GO

CREATE TRIGGER dbo.TR_BotPermisos_Audit
ON dbo.BotPermisos
AFTER INSERT, UPDATE, DELETE
AS
BEGIN
    SET NOCOUNT ON;

    DECLARE @usuario VARCHAR(100) = ORIGINAL_LOGIN();

    -- INSERT
    IF EXISTS (SELECT 1 FROM inserted) AND NOT EXISTS (SELECT 1 FROM deleted)
    BEGIN
        INSERT INTO dbo.BotPermisosAudit (idPermiso, accion, valorAnterior, valorNuevo, usuario)
        SELECT
            i.idPermiso,
            'INSERT',
            NULL,
            (SELECT
                i.idPermiso       AS idPermiso,
                i.idTipoEntidad   AS idTipoEntidad,
                i.idEntidad       AS idEntidad,
                i.idRecurso       AS idRecurso,
                i.idRolRequerido  AS idRolRequerido,
                i.permitido       AS permitido,
                i.activo          AS activo,
                i.fechaExpiracion AS fechaExpiracion
             FOR JSON PATH, WITHOUT_ARRAY_WRAPPER),
            @usuario
        FROM inserted i;
    END

    -- DELETE
    IF EXISTS (SELECT 1 FROM deleted) AND NOT EXISTS (SELECT 1 FROM inserted)
    BEGIN
        INSERT INTO dbo.BotPermisosAudit (idPermiso, accion, valorAnterior, valorNuevo, usuario)
        SELECT
            d.idPermiso,
            'DELETE',
            (SELECT
                d.idPermiso       AS idPermiso,
                d.idTipoEntidad   AS idTipoEntidad,
                d.idEntidad       AS idEntidad,
                d.idRecurso       AS idRecurso,
                d.idRolRequerido  AS idRolRequerido,
                d.permitido       AS permitido,
                d.activo          AS activo,
                d.fechaExpiracion AS fechaExpiracion
             FOR JSON PATH, WITHOUT_ARRAY_WRAPPER),
            NULL,
            @usuario
        FROM deleted d;
    END

    -- UPDATE
    IF EXISTS (SELECT 1 FROM inserted) AND EXISTS (SELECT 1 FROM deleted)
    BEGIN
        INSERT INTO dbo.BotPermisosAudit (idPermiso, accion, valorAnterior, valorNuevo, usuario)
        SELECT
            i.idPermiso,
            'UPDATE',
            (SELECT
                d.idPermiso       AS idPermiso,
                d.idTipoEntidad   AS idTipoEntidad,
                d.idEntidad       AS idEntidad,
                d.idRecurso       AS idRecurso,
                d.idRolRequerido  AS idRolRequerido,
                d.permitido       AS permitido,
                d.activo          AS activo,
                d.fechaExpiracion AS fechaExpiracion
             FOR JSON PATH, WITHOUT_ARRAY_WRAPPER),
            (SELECT
                i.idPermiso       AS idPermiso,
                i.idTipoEntidad   AS idTipoEntidad,
                i.idEntidad       AS idEntidad,
                i.idRecurso       AS idRecurso,
                i.idRolRequerido  AS idRolRequerido,
                i.permitido       AS permitido,
                i.activo          AS activo,
                i.fechaExpiracion AS fechaExpiracion
             FOR JSON PATH, WITHOUT_ARRAY_WRAPPER),
            @usuario
        FROM inserted i
        INNER JOIN deleted d ON i.idPermiso = d.idPermiso;
    END
END;
GO

PRINT 'Trigger TR_BotPermisos_Audit creado.';
PRINT '';
PRINT 'SEC-01 Fase 1c completada: audit trigger activo.';
PRINT 'Fase 1 completa. Continuar con Fase 2: capa de dominio en Python.';
GO
