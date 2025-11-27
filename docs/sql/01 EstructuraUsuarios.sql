-- ============================================================================
-- Script: Estructura de Base de Datos - Sistema de Usuarios
-- Base de Datos: abcmasplus
-- Esquema: dbo
-- Descripción: Creación de tablas para gestión de usuarios, gerencias y roles
-- ============================================================================

USE abcmasplus;
GO

-- ============================================================================
-- 1. TABLA: Roles
-- Descripción: Catálogo de roles del sistema
-- ============================================================================
IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[Roles]') AND type in (N'U'))
BEGIN
    CREATE TABLE [dbo].[Roles] (
        [idRol] INT IDENTITY(1,1) NOT NULL,
        [nombre] NVARCHAR(100) NOT NULL,
        [fechaCreacion] DATETIME NOT NULL DEFAULT GETDATE(),
        [activo] BIT NOT NULL DEFAULT 1,
        CONSTRAINT [PK_Roles] PRIMARY KEY CLUSTERED ([idRol] ASC),
        CONSTRAINT [UQ_Roles_Nombre] UNIQUE ([nombre])
    );
    
    PRINT 'Tabla Roles creada exitosamente';
END
ELSE
    PRINT 'Tabla Roles ya existe';
GO

-- ============================================================================
-- 2. TABLA: RolesIA
-- Descripción: Roles específicos para funcionalidades de IA
-- ============================================================================
IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[RolesIA]') AND type in (N'U'))
BEGIN
    CREATE TABLE [dbo].[RolesIA] (
        [idRol] INT IDENTITY(1,1) NOT NULL,
        [nombre] NVARCHAR(100) NOT NULL,
        [descripcion] NVARCHAR(500) NULL,
        [fechaCreacion] DATETIME NOT NULL DEFAULT GETDATE(),
        [activo] BIT NOT NULL DEFAULT 1,
        CONSTRAINT [PK_RolesIA] PRIMARY KEY CLUSTERED ([idRol] ASC),
        CONSTRAINT [UQ_RolesIA_Nombre] UNIQUE ([nombre])
    );
    
    PRINT 'Tabla RolesIA creada exitosamente';
END
ELSE
    PRINT 'Tabla RolesIA ya existe';
GO

-- ============================================================================
-- 3. TABLA: Gerencias
-- Descripción: Catálogo de gerencias de la organización
-- ============================================================================
IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[Gerencias]') AND type in (N'U'))
BEGIN
    CREATE TABLE [dbo].[Gerencias] (
        [idGerencia] INT IDENTITY(1,1) NOT NULL,
        [idResponsable] INT NULL,
        [gerencia] NVARCHAR(200) NOT NULL,
        [alias] NVARCHAR(50) NULL,
        [correo] NVARCHAR(150) NULL,
        [fechaCreacion] DATETIME NOT NULL DEFAULT GETDATE(),
        [activo] BIT NOT NULL DEFAULT 1,
        CONSTRAINT [PK_Gerencias] PRIMARY KEY CLUSTERED ([idGerencia] ASC),
        CONSTRAINT [UQ_Gerencias_Alias] UNIQUE ([alias])
    );
    
    PRINT 'Tabla Gerencias creada exitosamente';
END
ELSE
    PRINT 'Tabla Gerencias ya existe';
GO

-- ============================================================================
-- 4. TABLA: Usuarios
-- Descripción: Usuarios del sistema
-- ============================================================================
IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[Usuarios]') AND type in (N'U'))
BEGIN
    CREATE TABLE [dbo].[Usuarios] (
        [idUsuario] INT IDENTITY(1,1) NOT NULL,
        [idEmpleado] INT NOT NULL,
        [nombre] NVARCHAR(100) NOT NULL,
        [apellido] NVARCHAR(100) NOT NULL,
        [rol] INT NOT NULL,
        [email] NVARCHAR(150) NOT NULL,
        [fechaCreacion] DATETIME NOT NULL DEFAULT GETDATE(),
        [fechaUltimoAcceso] DATETIME NULL,
        [activo] BIT NOT NULL DEFAULT 1,
        CONSTRAINT [PK_Usuarios] PRIMARY KEY CLUSTERED ([idUsuario] ASC),
        CONSTRAINT [UQ_Usuarios_IdEmpleado] UNIQUE ([idEmpleado]),
        CONSTRAINT [UQ_Usuarios_Email] UNIQUE ([email]),
        CONSTRAINT [FK_Usuarios_Roles] FOREIGN KEY ([rol]) 
            REFERENCES [dbo].[Roles]([idRol])
    );
    
    CREATE NONCLUSTERED INDEX [IX_Usuarios_Email] ON [dbo].[Usuarios]([email]);
    CREATE NONCLUSTERED INDEX [IX_Usuarios_IdEmpleado] ON [dbo].[Usuarios]([idEmpleado]);
    
    PRINT 'Tabla Usuarios creada exitosamente';
END
ELSE
    PRINT 'Tabla Usuarios ya existe';
GO

-- ============================================================================
-- 5. TABLA: GerenciaUsuarios
-- Descripción: Relación muchos a muchos entre Usuarios y Gerencias
-- ============================================================================
IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[GerenciaUsuarios]') AND type in (N'U'))
BEGIN
    CREATE TABLE [dbo].[GerenciaUsuarios] (
        [idGerenciaUsuario] INT IDENTITY(1,1) NOT NULL,
        [idUsuario] INT NOT NULL,
        [idGerencia] INT NOT NULL,
        [fechaAsignacion] DATETIME NOT NULL DEFAULT GETDATE(),
        [activo] BIT NOT NULL DEFAULT 1,
        CONSTRAINT [PK_GerenciaUsuarios] PRIMARY KEY CLUSTERED ([idGerenciaUsuario] ASC),
        CONSTRAINT [UQ_GerenciaUsuarios] UNIQUE ([idUsuario], [idGerencia]),
        CONSTRAINT [FK_GerenciaUsuarios_Usuarios] FOREIGN KEY ([idUsuario]) 
            REFERENCES [dbo].[Usuarios]([idUsuario]),
        CONSTRAINT [FK_GerenciaUsuarios_Gerencias] FOREIGN KEY ([idGerencia]) 
            REFERENCES [dbo].[Gerencias]([idGerencia])
    );
    
    CREATE NONCLUSTERED INDEX [IX_GerenciaUsuarios_IdUsuario] ON [dbo].[GerenciaUsuarios]([idUsuario]);
    CREATE NONCLUSTERED INDEX [IX_GerenciaUsuarios_IdGerencia] ON [dbo].[GerenciaUsuarios]([idGerencia]);
    
    PRINT 'Tabla GerenciaUsuarios creada exitosamente';
END
ELSE
    PRINT 'Tabla GerenciaUsuarios ya existe';
GO

-- ============================================================================
-- 6. TABLA: AreaAtendedora
-- Descripción: Gerencias que funcionan como áreas atendedoras
-- ============================================================================
IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[AreaAtendedora]') AND type in (N'U'))
BEGIN
    CREATE TABLE [dbo].[AreaAtendedora] (
        [idAreaAtendedora] INT IDENTITY(1,1) NOT NULL,
        [idGerencia] INT NOT NULL,
        [fechaCreacion] DATETIME NOT NULL DEFAULT GETDATE(),
        [activo] BIT NOT NULL DEFAULT 1,
        CONSTRAINT [PK_AreaAtendedora] PRIMARY KEY CLUSTERED ([idAreaAtendedora] ASC),
        CONSTRAINT [UQ_AreaAtendedora_IdGerencia] UNIQUE ([idGerencia]),
        CONSTRAINT [FK_AreaAtendedora_Gerencias] FOREIGN KEY ([idGerencia]) 
            REFERENCES [dbo].[Gerencias]([idGerencia])
    );
    
    PRINT 'Tabla AreaAtendedora creada exitosamente';
END
ELSE
    PRINT 'Tabla AreaAtendedora ya existe';
GO

-- ============================================================================
-- 7. TABLA: GerenciasRolesIA
-- Descripción: Relación muchos a muchos entre Gerencias y RolesIA
-- ============================================================================
IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[GerenciasRolesIA]') AND type in (N'U'))
BEGIN
    CREATE TABLE [dbo].[GerenciasRolesIA] (
        [idGerenciaRolIA] INT IDENTITY(1,1) NOT NULL,
        [idRol] INT NOT NULL,
        [idGerencia] INT NOT NULL,
        [fechaAsignacion] DATETIME NOT NULL DEFAULT GETDATE(),
        [activo] BIT NOT NULL DEFAULT 1,
        CONSTRAINT [PK_GerenciasRolesIA] PRIMARY KEY CLUSTERED ([idGerenciaRolIA] ASC),
        CONSTRAINT [UQ_GerenciasRolesIA] UNIQUE ([idRol], [idGerencia]),
        CONSTRAINT [FK_GerenciasRolesIA_RolesIA] FOREIGN KEY ([idRol]) 
            REFERENCES [dbo].[RolesIA]([idRol]),
        CONSTRAINT [FK_GerenciasRolesIA_Gerencias] FOREIGN KEY ([idGerencia]) 
            REFERENCES [dbo].[Gerencias]([idGerencia])
    );
    
    CREATE NONCLUSTERED INDEX [IX_GerenciasRolesIA_IdRol] ON [dbo].[GerenciasRolesIA]([idRol]);
    CREATE NONCLUSTERED INDEX [IX_GerenciasRolesIA_IdGerencia] ON [dbo].[GerenciasRolesIA]([idGerencia]);
    
    PRINT 'Tabla GerenciasRolesIA creada exitosamente';
END
ELSE
    PRINT 'Tabla GerenciasRolesIA ya existe';
GO

-- ============================================================================
-- 8. TABLA: UsuariosRolesIA
-- Descripción: Relación muchos a muchos entre Usuarios y RolesIA
-- ============================================================================
IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[UsuariosRolesIA]') AND type in (N'U'))
BEGIN
    CREATE TABLE [dbo].[UsuariosRolesIA] (
        [idUsuarioRolIA] INT IDENTITY(1,1) NOT NULL,
        [idRol] INT NOT NULL,
        [idUsuario] INT NOT NULL,
        [fechaAsignacion] DATETIME NOT NULL DEFAULT GETDATE(),
        [activo] BIT NOT NULL DEFAULT 1,
        CONSTRAINT [PK_UsuariosRolesIA] PRIMARY KEY CLUSTERED ([idUsuarioRolIA] ASC),
        CONSTRAINT [UQ_UsuariosRolesIA] UNIQUE ([idRol], [idUsuario]),
        CONSTRAINT [FK_UsuariosRolesIA_RolesIA] FOREIGN KEY ([idRol]) 
            REFERENCES [dbo].[RolesIA]([idRol]),
        CONSTRAINT [FK_UsuariosRolesIA_Usuarios] FOREIGN KEY ([idUsuario]) 
            REFERENCES [dbo].[Usuarios]([idUsuario])
    );
    
    CREATE NONCLUSTERED INDEX [IX_UsuariosRolesIA_IdRol] ON [dbo].[UsuariosRolesIA]([idRol]);
    CREATE NONCLUSTERED INDEX [IX_UsuariosRolesIA_IdUsuario] ON [dbo].[UsuariosRolesIA]([idUsuario]);
    
    PRINT 'Tabla UsuariosRolesIA creada exitosamente';
END
ELSE
    PRINT 'Tabla UsuariosRolesIA ya existe';
GO

-- ============================================================================
-- FOREIGN KEY ADICIONAL: Gerencias.idResponsable -> Usuarios.idUsuario
-- ============================================================================
IF NOT EXISTS (SELECT * FROM sys.foreign_keys WHERE name = 'FK_Gerencias_Usuarios')
BEGIN
    ALTER TABLE [dbo].[Gerencias]
    ADD CONSTRAINT [FK_Gerencias_Usuarios] FOREIGN KEY ([idResponsable]) 
        REFERENCES [dbo].[Usuarios]([idUsuario]);
    
    PRINT 'Foreign Key FK_Gerencias_Usuarios creada exitosamente';
END
ELSE
    PRINT 'Foreign Key FK_Gerencias_Usuarios ya existe';
GO

-- ============================================================================
-- DATOS INICIALES (OPCIONAL)
-- ============================================================================

-- Insertar roles básicos
IF NOT EXISTS (SELECT 1 FROM [dbo].[Roles])
BEGIN
    INSERT INTO [dbo].[Roles] ([nombre]) VALUES 
        ('Administrador'),
        ('Usuario'),
        ('Supervisor'),
        ('Consulta');
    
    PRINT 'Roles iniciales insertados';
END
GO

-- Insertar roles IA básicos
IF NOT EXISTS (SELECT 1 FROM [dbo].[RolesIA])
BEGIN
    INSERT INTO [dbo].[RolesIA] ([nombre], [descripcion]) VALUES 
        ('Administrador IA', 'Acceso completo a funcionalidades de IA'),
        ('Analista IA', 'Puede usar herramientas de análisis con IA'),
        ('Usuario IA', 'Acceso básico a funcionalidades de IA');
    
    PRINT 'Roles IA iniciales insertados';
END
GO

PRINT '';
PRINT '============================================================================';
PRINT 'Script ejecutado exitosamente';
PRINT 'Base de datos: abcmasplus';
PRINT 'Esquema: dbo';
PRINT 'Total de tablas creadas: 8';
PRINT '============================================================================';
GO



-- ============================================================================
-- Script: Datos de Prueba - Sistema de Usuarios
-- Base de Datos: abcmasplus
-- Esquema: dbo
-- Descripción: Inserción de datos de prueba para todas las tablas
-- ============================================================================

USE abcmasplus;
GO

PRINT '============================================================================';
PRINT 'Iniciando inserción de datos de prueba';
PRINT '============================================================================';
PRINT '';

-- ============================================================================
-- 1. ROLES
-- ============================================================================
PRINT '1. Insertando Roles...';

SET IDENTITY_INSERT [dbo].[Roles] ON;

INSERT INTO [dbo].[Roles] ([idRol], [nombre], [fechaCreacion], [activo]) VALUES 
    (1, 'Administrador', GETDATE(), 1),
    (2, 'Gerente', GETDATE(), 1),
    (3, 'Supervisor', GETDATE(), 1),
    (4, 'Analista', GETDATE(), 1),
    (5, 'Usuario', GETDATE(), 1),
    (6, 'Consulta', GETDATE(), 1),
    (7, 'Coordinador', GETDATE(), 1),
    (8, 'Especialista', GETDATE(), 1);

SET IDENTITY_INSERT [dbo].[Roles] OFF;

PRINT '   - 8 roles insertados';
GO

-- ============================================================================
-- 2. ROLES IA
-- ============================================================================
PRINT '2. Insertando Roles IA...';

SET IDENTITY_INSERT [dbo].[RolesIA] ON;

INSERT INTO [dbo].[RolesIA] ([idRol], [nombre], [descripcion], [fechaCreacion], [activo]) VALUES 
    (1, 'Administrador IA', 'Acceso completo a funcionalidades de IA y configuración', GETDATE(), 1),
    (2, 'Analista IA Avanzado', 'Puede usar herramientas avanzadas de análisis con IA', GETDATE(), 1),
    (3, 'Analista IA', 'Puede usar herramientas de análisis con IA', GETDATE(), 1),
    (4, 'Usuario IA Premium', 'Acceso a funcionalidades premium de IA', GETDATE(), 1),
    (5, 'Usuario IA', 'Acceso básico a funcionalidades de IA', GETDATE(), 1),
    (6, 'Consultor IA', 'Solo consulta de resultados generados por IA', GETDATE(), 1);

SET IDENTITY_INSERT [dbo].[RolesIA] OFF;

PRINT '   - 6 roles IA insertados';
GO

-- ============================================================================
-- 3. USUARIOS (sin idResponsable en Gerencias aún)
-- ============================================================================
PRINT '3. Insertando Usuarios...';

SET IDENTITY_INSERT [dbo].[Usuarios] ON;

INSERT INTO [dbo].[Usuarios] ([idUsuario], [idEmpleado], [nombre], [apellido], [rol], [email], [fechaCreacion], [fechaUltimoAcceso], [activo]) VALUES 
    (1, 1001, 'Juan', 'Pérez González', 1, 'juan.perez@abcmasplus.com', DATEADD(day, -90, GETDATE()), GETDATE(), 1),
    (2, 1002, 'María', 'López Hernández', 2, 'maria.lopez@abcmasplus.com', DATEADD(day, -85, GETDATE()), DATEADD(hour, -2, GETDATE()), 1),
    (3, 1003, 'Carlos', 'Martínez Silva', 2, 'carlos.martinez@abcmasplus.com', DATEADD(day, -80, GETDATE()), DATEADD(day, -1, GETDATE()), 1),
    (4, 1004, 'Ana', 'García Rodríguez', 3, 'ana.garcia@abcmasplus.com', DATEADD(day, -75, GETDATE()), DATEADD(hour, -5, GETDATE()), 1),
    (5, 1005, 'Luis', 'Fernández Torres', 3, 'luis.fernandez@abcmasplus.com', DATEADD(day, -70, GETDATE()), DATEADD(day, -2, GETDATE()), 1),
    (6, 1006, 'Patricia', 'Sánchez Morales', 4, 'patricia.sanchez@abcmasplus.com', DATEADD(day, -65, GETDATE()), GETDATE(), 1),
    (7, 1007, 'Roberto', 'Ramírez Cruz', 4, 'roberto.ramirez@abcmasplus.com', DATEADD(day, -60, GETDATE()), DATEADD(hour, -3, GETDATE()), 1),
    (8, 1008, 'Laura', 'Torres Jiménez', 5, 'laura.torres@abcmasplus.com', DATEADD(day, -55, GETDATE()), DATEADD(hour, -1, GETDATE()), 1),
    (9, 1009, 'Miguel', 'Flores Vargas', 5, 'miguel.flores@abcmasplus.com', DATEADD(day, -50, GETDATE()), DATEADD(day, -3, GETDATE()), 1),
    (10, 1010, 'Carmen', 'Ruiz Mendoza', 6, 'carmen.ruiz@abcmasplus.com', DATEADD(day, -45, GETDATE()), DATEADD(hour, -6, GETDATE()), 1),
    (11, 1011, 'Jorge', 'Díaz Castro', 7, 'jorge.diaz@abcmasplus.com', DATEADD(day, -40, GETDATE()), DATEADD(hour, -4, GETDATE()), 1),
    (12, 1012, 'Sofía', 'Moreno Ortiz', 7, 'sofia.moreno@abcmasplus.com', DATEADD(day, -35, GETDATE()), GETDATE(), 1),
    (13, 1013, 'Fernando', 'Vázquez Luna', 8, 'fernando.vazquez@abcmasplus.com', DATEADD(day, -30, GETDATE()), DATEADD(hour, -2, GETDATE()), 1),
    (14, 1014, 'Isabel', 'Romero Ríos', 8, 'isabel.romero@abcmasplus.com', DATEADD(day, -25, GETDATE()), DATEADD(day, -1, GETDATE()), 1),
    (15, 1015, 'Ricardo', 'Herrera Peña', 5, 'ricardo.herrera@abcmasplus.com', DATEADD(day, -20, GETDATE()), DATEADD(hour, -8, GETDATE()), 1),
    (16, 1016, 'Gabriela', 'Aguilar Medina', 5, 'gabriela.aguilar@abcmasplus.com', DATEADD(day, -15, GETDATE()), DATEADD(hour, -12, GETDATE()), 1),
    (17, 1017, 'Andrés', 'Castillo Ramos', 4, 'andres.castillo@abcmasplus.com', DATEADD(day, -10, GETDATE()), GETDATE(), 1),
    (18, 1018, 'Valentina', 'Guerrero Salazar', 4, 'valentina.guerrero@abcmasplus.com', DATEADD(day, -8, GETDATE()), DATEADD(hour, -1, GETDATE()), 1),
    (19, 1019, 'Daniel', 'Mendoza Fuentes', 5, 'daniel.mendoza@abcmasplus.com', DATEADD(day, -5, GETDATE()), DATEADD(hour, -3, GETDATE()), 1),
    (20, 1020, 'Mónica', 'Cruz Navarro', 6, 'monica.cruz@abcmasplus.com', DATEADD(day, -3, GETDATE()), DATEADD(day, -2, GETDATE()), 1);

SET IDENTITY_INSERT [dbo].[Usuarios] OFF;

PRINT '   - 20 usuarios insertados';
GO

-- ============================================================================
-- 4. GERENCIAS
-- ============================================================================
PRINT '4. Insertando Gerencias...';

SET IDENTITY_INSERT [dbo].[Gerencias] ON;

INSERT INTO [dbo].[Gerencias] ([idGerencia], [idResponsable], [gerencia], [alias], [correo], [fechaCreacion], [activo]) VALUES 
    (1, 1, 'Gerencia General', 'GG', 'gerencia.general@abcmasplus.com', DATEADD(day, -100, GETDATE()), 1),
    (2, 2, 'Gerencia de Tecnología', 'GTECH', 'tecnologia@abcmasplus.com', DATEADD(day, -95, GETDATE()), 1),
    (3, 3, 'Gerencia de Recursos Humanos', 'GRH', 'rrhh@abcmasplus.com', DATEADD(day, -90, GETDATE()), 1),
    (4, 4, 'Gerencia de Finanzas', 'GFIN', 'finanzas@abcmasplus.com', DATEADD(day, -85, GETDATE()), 1),
    (5, 5, 'Gerencia de Operaciones', 'GOPE', 'operaciones@abcmasplus.com', DATEADD(day, -80, GETDATE()), 1),
    (6, 11, 'Gerencia de Marketing', 'GMKT', 'marketing@abcmasplus.com', DATEADD(day, -75, GETDATE()), 1),
    (7, 12, 'Gerencia de Ventas', 'GVTA', 'ventas@abcmasplus.com', DATEADD(day, -70, GETDATE()), 1),
    (8, NULL, 'Gerencia de Logística', 'GLOG', 'logistica@abcmasplus.com', DATEADD(day, -65, GETDATE()), 1),
    (9, NULL, 'Gerencia de Calidad', 'GCAL', 'calidad@abcmasplus.com', DATEADD(day, -60, GETDATE()), 1),
    (10, NULL, 'Gerencia de Atención al Cliente', 'GACL', 'atencion.cliente@abcmasplus.com', DATEADD(day, -55, GETDATE()), 1);

SET IDENTITY_INSERT [dbo].[Gerencias] OFF;

PRINT '   - 10 gerencias insertadas';
GO

-- ============================================================================
-- 5. GERENCIA USUARIOS (Relación Usuarios-Gerencias)
-- ============================================================================
PRINT '5. Insertando GerenciaUsuarios...';

SET IDENTITY_INSERT [dbo].[GerenciaUsuarios] ON;

INSERT INTO [dbo].[GerenciaUsuarios] ([idGerenciaUsuario], [idUsuario], [idGerencia], [fechaAsignacion], [activo]) VALUES 
    -- Usuario 1 (Admin) - Acceso a todas las gerencias
    (1, 1, 1, DATEADD(day, -90, GETDATE()), 1),
    (2, 1, 2, DATEADD(day, -90, GETDATE()), 1),
    
    -- Usuario 2 (Gerente de Tecnología)
    (3, 2, 2, DATEADD(day, -85, GETDATE()), 1),
    (4, 2, 8, DATEADD(day, -85, GETDATE()), 1),
    
    -- Usuario 3 (Gerente de RRHH)
    (5, 3, 3, DATEADD(day, -80, GETDATE()), 1),
    
    -- Usuario 4 (Supervisor de Finanzas)
    (6, 4, 4, DATEADD(day, -75, GETDATE()), 1),
    
    -- Usuario 5 (Supervisor de Operaciones)
    (7, 5, 5, DATEADD(day, -70, GETDATE()), 1),
    (8, 5, 8, DATEADD(day, -70, GETDATE()), 1),
    
    -- Usuario 6 (Analista de Tecnología)
    (9, 6, 2, DATEADD(day, -65, GETDATE()), 1),
    
    -- Usuario 7 (Analista de Finanzas)
    (10, 7, 4, DATEADD(day, -60, GETDATE()), 1),
    
    -- Usuario 8 (Usuario de RRHH)
    (11, 8, 3, DATEADD(day, -55, GETDATE()), 1),
    
    -- Usuario 9 (Usuario de Marketing)
    (12, 9, 6, DATEADD(day, -50, GETDATE()), 1),
    
    -- Usuario 10 (Consulta múltiple)
    (13, 10, 1, DATEADD(day, -45, GETDATE()), 1),
    (14, 10, 4, DATEADD(day, -45, GETDATE()), 1),
    (15, 10, 7, DATEADD(day, -45, GETDATE()), 1),
    
    -- Usuario 11 (Coordinador de Marketing)
    (16, 11, 6, DATEADD(day, -40, GETDATE()), 1),
    
    -- Usuario 12 (Coordinador de Ventas)
    (17, 12, 7, DATEADD(day, -35, GETDATE()), 1),
    (18, 12, 10, DATEADD(day, -35, GETDATE()), 1),
    
    -- Usuario 13 (Especialista de Calidad)
    (19, 13, 9, DATEADD(day, -30, GETDATE()), 1),
    
    -- Usuario 14 (Especialista de Logística)
    (20, 14, 8, DATEADD(day, -25, GETDATE()), 1),
    
    -- Usuario 15 (Usuario de Operaciones)
    (21, 15, 5, DATEADD(day, -20, GETDATE()), 1),
    
    -- Usuario 16 (Usuario de Atención al Cliente)
    (22, 16, 10, DATEADD(day, -15, GETDATE()), 1),
    
    -- Usuario 17 (Analista de Ventas)
    (23, 17, 7, DATEADD(day, -10, GETDATE()), 1),
    
    -- Usuario 18 (Analista de Marketing)
    (24, 18, 6, DATEADD(day, -8, GETDATE()), 1),
    
    -- Usuario 19 (Usuario de Tecnología)
    (25, 19, 2, DATEADD(day, -5, GETDATE()), 1),
    
    -- Usuario 20 (Consulta de Calidad)
    (26, 20, 9, DATEADD(day, -3, GETDATE()), 1);

SET IDENTITY_INSERT [dbo].[GerenciaUsuarios] OFF;

PRINT '   - 26 relaciones Usuario-Gerencia insertadas';
GO

-- ============================================================================
-- 6. AREA ATENDEDORA
-- ============================================================================
PRINT '6. Insertando AreaAtendedora...';

SET IDENTITY_INSERT [dbo].[AreaAtendedora] ON;

INSERT INTO [dbo].[AreaAtendedora] ([idAreaAtendedora], [idGerencia], [fechaCreacion], [activo]) VALUES 
    (1, 2, DATEADD(day, -95, GETDATE()), 1),  -- Tecnología
    (2, 3, DATEADD(day, -90, GETDATE()), 1),  -- RRHH
    (3, 4, DATEADD(day, -85, GETDATE()), 1),  -- Finanzas
    (4, 8, DATEADD(day, -65, GETDATE()), 1),  -- Logística
    (5, 9, DATEADD(day, -60, GETDATE()), 1),  -- Calidad
    (6, 10, DATEADD(day, -55, GETDATE()), 1); -- Atención al Cliente

SET IDENTITY_INSERT [dbo].[AreaAtendedora] OFF;

PRINT '   - 6 áreas atendedoras insertadas';
GO

-- ============================================================================
-- 7. GERENCIAS ROLES IA
-- ============================================================================
PRINT '7. Insertando GerenciasRolesIA...';

SET IDENTITY_INSERT [dbo].[GerenciasRolesIA] ON;

INSERT INTO [dbo].[GerenciasRolesIA] ([idGerenciaRolIA], [idRol], [idGerencia], [fechaAsignacion], [activo]) VALUES 
    -- Gerencia General tiene acceso a Administrador IA
    (1, 1, 1, DATEADD(day, -100, GETDATE()), 1),
    
    -- Tecnología tiene acceso avanzado a IA
    (2, 1, 2, DATEADD(day, -95, GETDATE()), 1),
    (3, 2, 2, DATEADD(day, -95, GETDATE()), 1),
    (4, 3, 2, DATEADD(day, -95, GETDATE()), 1),
    
    -- RRHH tiene acceso a análisis con IA
    (5, 3, 3, DATEADD(day, -90, GETDATE()), 1),
    (6, 5, 3, DATEADD(day, -90, GETDATE()), 1),
    
    -- Finanzas tiene acceso a análisis avanzado
    (7, 2, 4, DATEADD(day, -85, GETDATE()), 1),
    (8, 3, 4, DATEADD(day, -85, GETDATE()), 1),
    
    -- Operaciones tiene acceso básico
    (9, 5, 5, DATEADD(day, -80, GETDATE()), 1),
    
    -- Marketing tiene acceso premium
    (10, 4, 6, DATEADD(day, -75, GETDATE()), 1),
    (11, 5, 6, DATEADD(day, -75, GETDATE()), 1),
    
    -- Ventas tiene acceso a análisis
    (12, 3, 7, DATEADD(day, -70, GETDATE()), 1),
    (13, 5, 7, DATEADD(day, -70, GETDATE()), 1),
    
    -- Logística tiene acceso básico
    (14, 5, 8, DATEADD(day, -65, GETDATE()), 1),
    
    -- Calidad tiene acceso a consulta
    (15, 6, 9, DATEADD(day, -60, GETDATE()), 1),
    
    -- Atención al Cliente tiene acceso básico
    (16, 5, 10, DATEADD(day, -55, GETDATE()), 1);

SET IDENTITY_INSERT [dbo].[GerenciasRolesIA] OFF;

PRINT '   - 16 relaciones Gerencia-RolIA insertadas';
GO

-- ============================================================================
-- 8. USUARIOS ROLES IA
-- ============================================================================
PRINT '8. Insertando UsuariosRolesIA...';

SET IDENTITY_INSERT [dbo].[UsuariosRolesIA] ON;

INSERT INTO [dbo].[UsuariosRolesIA] ([idUsuarioRolIA], [idRol], [idUsuario], [fechaAsignacion], [activo]) VALUES 
    -- Administradores con acceso total
    (1, 1, 1, DATEADD(day, -90, GETDATE()), 1),
    
    -- Gerentes con análisis avanzado
    (2, 2, 2, DATEADD(day, -85, GETDATE()), 1),
    (3, 2, 3, DATEADD(day, -80, GETDATE()), 1),
    
    -- Supervisores con análisis
    (4, 3, 4, DATEADD(day, -75, GETDATE()), 1),
    (5, 3, 5, DATEADD(day, -70, GETDATE()), 1),
    
    -- Analistas con acceso premium
    (6, 4, 6, DATEADD(day, -65, GETDATE()), 1),
    (7, 3, 7, DATEADD(day, -60, GETDATE()), 1),
    
    -- Usuarios con acceso básico
    (8, 5, 8, DATEADD(day, -55, GETDATE()), 1),
    (9, 5, 9, DATEADD(day, -50, GETDATE()), 1),
    
    -- Consultas solo lectura
    (10, 6, 10, DATEADD(day, -45, GETDATE()), 1),
    
    -- Coordinadores con acceso premium
    (11, 4, 11, DATEADD(day, -40, GETDATE()), 1),
    (12, 4, 12, DATEADD(day, -35, GETDATE()), 1),
    
    -- Especialistas con análisis
    (13, 3, 13, DATEADD(day, -30, GETDATE()), 1),
    (14, 3, 14, DATEADD(day, -25, GETDATE()), 1),
    
    -- Usuarios varios con acceso básico
    (15, 5, 15, DATEADD(day, -20, GETDATE()), 1),
    (16, 5, 16, DATEADD(day, -15, GETDATE()), 1),
    (17, 5, 17, DATEADD(day, -10, GETDATE()), 1),
    (18, 5, 18, DATEADD(day, -8, GETDATE()), 1),
    (19, 5, 19, DATEADD(day, -5, GETDATE()), 1),
    (20, 6, 20, DATEADD(day, -3, GETDATE()), 1);

SET IDENTITY_INSERT [dbo].[UsuariosRolesIA] OFF;

PRINT '   - 20 relaciones Usuario-RolIA insertadas';
GO

-- ============================================================================
-- RESUMEN DE DATOS INSERTADOS
-- ============================================================================
PRINT '';
PRINT '============================================================================';
PRINT 'RESUMEN DE DATOS DE PRUEBA INSERTADOS';
PRINT '============================================================================';
PRINT '';

SELECT 'Roles' AS Tabla, COUNT(*) AS Registros FROM [dbo].[Roles]
UNION ALL
SELECT 'RolesIA', COUNT(*) FROM [dbo].[RolesIA]
UNION ALL
SELECT 'Usuarios', COUNT(*) FROM [dbo].[Usuarios]
UNION ALL
SELECT 'Gerencias', COUNT(*) FROM [dbo].[Gerencias]
UNION ALL
SELECT 'GerenciaUsuarios', COUNT(*) FROM [dbo].[GerenciaUsuarios]
UNION ALL
SELECT 'AreaAtendedora', COUNT(*) FROM [dbo].[AreaAtendedora]
UNION ALL
SELECT 'GerenciasRolesIA', COUNT(*) FROM [dbo].[GerenciasRolesIA]
UNION ALL
SELECT 'UsuariosRolesIA', COUNT(*) FROM [dbo].[UsuariosRolesIA];

PRINT '';
PRINT '============================================================================';
PRINT 'Datos de prueba insertados exitosamente';
PRINT '============================================================================';
GO

-- ============================================================================
-- CONSULTAS DE VERIFICACIÓN (OPCIONAL)
-- ============================================================================

PRINT '';
PRINT '============================================================================';
PRINT 'CONSULTAS DE VERIFICACIÓN';
PRINT '============================================================================';
PRINT '';

-- Ver usuarios con sus roles y gerencias
PRINT '-- Usuarios con Roles y Gerencias:';
SELECT TOP 5
    u.idUsuario,
    u.idEmpleado,
    u.nombre + ' ' + u.apellido AS NombreCompleto,
    r.nombre AS Rol,
    g.gerencia AS Gerencia,
    g.alias AS AliasGerencia
FROM [dbo].[Usuarios] u
INNER JOIN [dbo].[Roles] r ON u.rol = r.idRol
LEFT JOIN [dbo].[GerenciaUsuarios] gu ON u.idUsuario = gu.idUsuario
LEFT JOIN [dbo].[Gerencias] g ON gu.idGerencia = g.idGerencia
WHERE u.activo = 1
ORDER BY u.idUsuario;

PRINT '';
PRINT '-- Gerencias con Responsables:';
SELECT 
    g.idGerencia,
    g.gerencia,
    g.alias,
    CASE 
        WHEN u.idUsuario IS NOT NULL THEN u.nombre + ' ' + u.apellido
        ELSE 'Sin Responsable'
    END AS Responsable,
    g.correo
FROM [dbo].[Gerencias] g
LEFT JOIN [dbo].[Usuarios] u ON g.idResponsable = u.idUsuario
WHERE g.activo = 1
ORDER BY g.idGerencia;

PRINT '';
PRINT '-- Usuarios con Roles IA:';
SELECT TOP 5
    u.idUsuario,
    u.nombre + ' ' + u.apellido AS Usuario,
    ri.nombre AS RolIA,
    uri.fechaAsignacion
FROM [dbo].[Usuarios] u
INNER JOIN [dbo].[UsuariosRolesIA] uri ON u.idUsuario = uri.idUsuario
INNER JOIN [dbo].[RolesIA] ri ON uri.idRol = ri.idRol
WHERE u.activo = 1 AND uri.activo = 1
ORDER BY u.idUsuario;

PRINT '';
PRINT '============================================================================';
PRINT 'Script de datos de prueba finalizado';
PRINT '============================================================================';
GO