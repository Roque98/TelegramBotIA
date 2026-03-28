-- ============================================================================
-- Script: Gestión de Cuentas de Telegram
-- Base de Datos: abcmasplus
-- Esquema: dbo
-- Descripción: Sistema para administrar múltiples cuentas de Telegram por usuario
-- ============================================================================

USE abcmasplus;
GO

PRINT '============================================================================';
PRINT 'Creando estructura para gestión de cuentas de Telegram';
PRINT '============================================================================';
PRINT '';

-- ============================================================================
-- 1. TABLA: UsuariosTelegram
-- Descripción: Almacena las cuentas de Telegram asociadas a cada usuario
-- ============================================================================
IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[UsuariosTelegram]') AND type in (N'U'))
BEGIN
    CREATE TABLE [dbo].[UsuariosTelegram] (
        [idUsuarioTelegram] INT IDENTITY(1,1) NOT NULL,
        [idUsuario] INT NOT NULL,
        [telegramChatId] BIGINT NOT NULL,
        [telegramUsername] NVARCHAR(100) NULL,
        [telegramFirstName] NVARCHAR(100) NULL,
        [telegramLastName] NVARCHAR(100) NULL,
        [alias] NVARCHAR(50) NULL, -- Alias personalizado para identificar la cuenta
        [esPrincipal] BIT NOT NULL DEFAULT 0, -- Indica si es la cuenta principal
        [estado] NVARCHAR(20) NOT NULL DEFAULT 'ACTIVO', -- ACTIVO, SUSPENDIDO, BLOQUEADO
        [fechaRegistro] DATETIME NOT NULL DEFAULT GETDATE(),
        [fechaUltimaActividad] DATETIME NULL,
        [fechaVerificacion] DATETIME NULL, -- Fecha en que se verificó la cuenta
        [codigoVerificacion] NVARCHAR(10) NULL, -- Código temporal para verificación
        [verificado] BIT NOT NULL DEFAULT 0,
        [intentosVerificacion] INT NOT NULL DEFAULT 0,
        [notificacionesActivas] BIT NOT NULL DEFAULT 1,
        [observaciones] NVARCHAR(500) NULL,
        [activo] BIT NOT NULL DEFAULT 1,
        [fechaCreacion] DATETIME NOT NULL DEFAULT GETDATE(),
        [usuarioCreacion] INT NULL,
        [fechaModificacion] DATETIME NULL,
        [usuarioModificacion] INT NULL,
        CONSTRAINT [PK_UsuariosTelegram] PRIMARY KEY CLUSTERED ([idUsuarioTelegram] ASC),
        CONSTRAINT [UQ_UsuariosTelegram_ChatId] UNIQUE ([telegramChatId]),
        CONSTRAINT [FK_UsuariosTelegram_Usuarios] FOREIGN KEY ([idUsuario]) 
            REFERENCES [dbo].[Usuarios]([idUsuario]),
        CONSTRAINT [FK_UsuariosTelegram_UsuarioCreacion] FOREIGN KEY ([usuarioCreacion]) 
            REFERENCES [dbo].[Usuarios]([idUsuario]),
        CONSTRAINT [FK_UsuariosTelegram_UsuarioModificacion] FOREIGN KEY ([usuarioModificacion]) 
            REFERENCES [dbo].[Usuarios]([idUsuario]),
        CONSTRAINT [CK_UsuariosTelegram_Estado] CHECK ([estado] IN ('ACTIVO', 'SUSPENDIDO', 'BLOQUEADO'))
    );
    
    CREATE NONCLUSTERED INDEX [IX_UsuariosTelegram_IdUsuario] ON [dbo].[UsuariosTelegram]([idUsuario]);
    CREATE NONCLUSTERED INDEX [IX_UsuariosTelegram_ChatId] ON [dbo].[UsuariosTelegram]([telegramChatId]);
    CREATE NONCLUSTERED INDEX [IX_UsuariosTelegram_Username] ON [dbo].[UsuariosTelegram]([telegramUsername]);
    CREATE NONCLUSTERED INDEX [IX_UsuariosTelegram_Estado] ON [dbo].[UsuariosTelegram]([estado]);
    
    PRINT 'Tabla UsuariosTelegram creada exitosamente';
END
ELSE
    PRINT 'Tabla UsuariosTelegram ya existe';
GO