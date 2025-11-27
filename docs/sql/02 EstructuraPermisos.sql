-- ============================================================================
-- Script: Gestión de Operaciones y Permisos por Rol
-- Base de Datos: abcmasplus
-- Esquema: dbo
-- Descripción: Sistema de permisos basado en roles para operaciones de Telegram
-- ============================================================================

USE abcmasplus;
GO

PRINT '============================================================================';
PRINT 'Creando estructura de permisos y operaciones';
PRINT '============================================================================';
PRINT '';

-- ============================================================================
-- 1. TABLA: Modulos
-- Descripción: Módulos principales del sistema (agrupadores de operaciones)
-- ============================================================================
IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[Modulos]') AND type in (N'U'))
BEGIN
    CREATE TABLE [dbo].[Modulos] (
        [idModulo] INT IDENTITY(1,1) NOT NULL,
        [nombre] NVARCHAR(100) NOT NULL,
        [descripcion] NVARCHAR(500) NULL,
        [icono] NVARCHAR(50) NULL, -- Emoji o código de icono para Telegram
        [orden] INT NOT NULL DEFAULT 0,
        [activo] BIT NOT NULL DEFAULT 1,
        [fechaCreacion] DATETIME NOT NULL DEFAULT GETDATE(),
        CONSTRAINT [PK_Modulos] PRIMARY KEY CLUSTERED ([idModulo] ASC),
        CONSTRAINT [UQ_Modulos_Nombre] UNIQUE ([nombre])
    );
    
    PRINT 'Tabla Modulos creada exitosamente';
END
ELSE
    PRINT 'Tabla Modulos ya existe';
GO

-- ============================================================================
-- 2. TABLA: Operaciones
-- Descripción: Operaciones/Acciones disponibles en el sistema
-- ============================================================================
IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[Operaciones]') AND type in (N'U'))
BEGIN
    CREATE TABLE [dbo].[Operaciones] (
        [idOperacion] INT IDENTITY(1,1) NOT NULL,
        [idModulo] INT NOT NULL,
        [nombre] NVARCHAR(100) NOT NULL,
        [descripcion] NVARCHAR(500) NULL,
        [comando] NVARCHAR(100) NULL, -- Comando de Telegram (ej: /crear_ticket, /consultar_status)
        [requiereParametros] BIT NOT NULL DEFAULT 0,
        [parametrosEjemplo] NVARCHAR(500) NULL,
        [nivelCriticidad] INT NOT NULL DEFAULT 1, -- 1=Baja, 2=Media, 3=Alta, 4=Crítica
        [orden] INT NOT NULL DEFAULT 0,
        [activo] BIT NOT NULL DEFAULT 1,
        [fechaCreacion] DATETIME NOT NULL DEFAULT GETDATE(),
        CONSTRAINT [PK_Operaciones] PRIMARY KEY CLUSTERED ([idOperacion] ASC),
        CONSTRAINT [UQ_Operaciones_Comando] UNIQUE ([comando]),
        CONSTRAINT [FK_Operaciones_Modulos] FOREIGN KEY ([idModulo]) 
            REFERENCES [dbo].[Modulos]([idModulo])
    );
    
    CREATE NONCLUSTERED INDEX [IX_Operaciones_IdModulo] ON [dbo].[Operaciones]([idModulo]);
    CREATE NONCLUSTERED INDEX [IX_Operaciones_Comando] ON [dbo].[Operaciones]([comando]);
    
    PRINT 'Tabla Operaciones creada exitosamente';
END
ELSE
    PRINT 'Tabla Operaciones ya existe';
GO

-- ============================================================================
-- 3. TABLA: RolesOperaciones
-- Descripción: Relación muchos a muchos entre Roles y Operaciones (PERMISOS)
-- ============================================================================
IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[RolesOperaciones]') AND type in (N'U'))
BEGIN
    CREATE TABLE [dbo].[RolesOperaciones] (
        [idRolOperacion] INT IDENTITY(1,1) NOT NULL,
        [idRol] INT NOT NULL,
        [idOperacion] INT NOT NULL,
        [permitido] BIT NOT NULL DEFAULT 1, -- Permite denegar explícitamente
        [fechaAsignacion] DATETIME NOT NULL DEFAULT GETDATE(),
        [usuarioAsignacion] INT NULL, -- Quién otorgó el permiso
        [observaciones] NVARCHAR(500) NULL,
        [activo] BIT NOT NULL DEFAULT 1,
        CONSTRAINT [PK_RolesOperaciones] PRIMARY KEY CLUSTERED ([idRolOperacion] ASC),
        CONSTRAINT [UQ_RolesOperaciones] UNIQUE ([idRol], [idOperacion]),
        CONSTRAINT [FK_RolesOperaciones_Roles] FOREIGN KEY ([idRol]) 
            REFERENCES [dbo].[Roles]([idRol]),
        CONSTRAINT [FK_RolesOperaciones_Operaciones] FOREIGN KEY ([idOperacion]) 
            REFERENCES [dbo].[Operaciones]([idOperacion]),
        CONSTRAINT [FK_RolesOperaciones_Usuario] FOREIGN KEY ([usuarioAsignacion]) 
            REFERENCES [dbo].[Usuarios]([idUsuario])
    );
    
    CREATE NONCLUSTERED INDEX [IX_RolesOperaciones_IdRol] ON [dbo].[RolesOperaciones]([idRol]);
    CREATE NONCLUSTERED INDEX [IX_RolesOperaciones_IdOperacion] ON [dbo].[RolesOperaciones]([idOperacion]);
    
    PRINT 'Tabla RolesOperaciones creada exitosamente';
END
ELSE
    PRINT 'Tabla RolesOperaciones ya existe';
GO

-- ============================================================================
-- 4. TABLA: UsuariosOperaciones (OPCIONAL)
-- Descripción: Permisos específicos por usuario (excepciones a los permisos del rol)
-- ============================================================================
IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[UsuariosOperaciones]') AND type in (N'U'))
BEGIN
    CREATE TABLE [dbo].[UsuariosOperaciones] (
        [idUsuarioOperacion] INT IDENTITY(1,1) NOT NULL,
        [idUsuario] INT NOT NULL,
        [idOperacion] INT NOT NULL,
        [permitido] BIT NOT NULL DEFAULT 1,
        [fechaAsignacion] DATETIME NOT NULL DEFAULT GETDATE(),
        [fechaExpiracion] DATETIME NULL, -- Permiso temporal
        [usuarioAsignacion] INT NULL,
        [observaciones] NVARCHAR(500) NULL,
        [activo] BIT NOT NULL DEFAULT 1,
        CONSTRAINT [PK_UsuariosOperaciones] PRIMARY KEY CLUSTERED ([idUsuarioOperacion] ASC),
        CONSTRAINT [UQ_UsuariosOperaciones] UNIQUE ([idUsuario], [idOperacion]),
        CONSTRAINT [FK_UsuariosOperaciones_Usuarios] FOREIGN KEY ([idUsuario]) 
            REFERENCES [dbo].[Usuarios]([idUsuario]),
        CONSTRAINT [FK_UsuariosOperaciones_Operaciones] FOREIGN KEY ([idOperacion]) 
            REFERENCES [dbo].[Operaciones]([idOperacion]),
        CONSTRAINT [FK_UsuariosOperaciones_Usuario] FOREIGN KEY ([usuarioAsignacion]) 
            REFERENCES [dbo].[Usuarios]([idUsuario])
    );
    
    CREATE NONCLUSTERED INDEX [IX_UsuariosOperaciones_IdUsuario] ON [dbo].[UsuariosOperaciones]([idUsuario]);
    CREATE NONCLUSTERED INDEX [IX_UsuariosOperaciones_IdOperacion] ON [dbo].[UsuariosOperaciones]([idOperacion]);
    
    PRINT 'Tabla UsuariosOperaciones creada exitosamente';
END
ELSE
    PRINT 'Tabla UsuariosOperaciones ya existe';
GO

-- ============================================================================
-- 5. TABLA: LogOperaciones
-- Descripción: Auditoría de operaciones ejecutadas por usuarios
-- ============================================================================
IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[LogOperaciones]') AND type in (N'U'))
BEGIN
    CREATE TABLE [dbo].[LogOperaciones] (
        [idLog] BIGINT IDENTITY(1,1) NOT NULL,
        [idUsuario] INT NOT NULL,
        [idOperacion] INT NOT NULL,
        [telegramChatId] BIGINT NULL,
        [telegramUsername] NVARCHAR(100) NULL,
        [parametros] NVARCHAR(MAX) NULL, -- JSON con los parámetros enviados
        [resultado] NVARCHAR(50) NOT NULL, -- 'EXITOSO', 'ERROR', 'DENEGADO'
        [mensajeError] NVARCHAR(MAX) NULL,
        [duracionMs] INT NULL,
        [ipOrigen] NVARCHAR(50) NULL,
        [fechaEjecucion] DATETIME NOT NULL DEFAULT GETDATE(),
        CONSTRAINT [PK_LogOperaciones] PRIMARY KEY CLUSTERED ([idLog] ASC),
        CONSTRAINT [FK_LogOperaciones_Usuarios] FOREIGN KEY ([idUsuario]) 
            REFERENCES [dbo].[Usuarios]([idUsuario]),
        CONSTRAINT [FK_LogOperaciones_Operaciones] FOREIGN KEY ([idOperacion]) 
            REFERENCES [dbo].[Operaciones]([idOperacion])
    );
    
    CREATE NONCLUSTERED INDEX [IX_LogOperaciones_IdUsuario] ON [dbo].[LogOperaciones]([idUsuario]);
    CREATE NONCLUSTERED INDEX [IX_LogOperaciones_IdOperacion] ON [dbo].[LogOperaciones]([idOperacion]);
    CREATE NONCLUSTERED INDEX [IX_LogOperaciones_FechaEjecucion] ON [dbo].[LogOperaciones]([fechaEjecucion] DESC);
    CREATE NONCLUSTERED INDEX [IX_LogOperaciones_Resultado] ON [dbo].[LogOperaciones]([resultado]);
    
    PRINT 'Tabla LogOperaciones creada exitosamente';
END
ELSE
    PRINT 'Tabla LogOperaciones ya existe';
GO