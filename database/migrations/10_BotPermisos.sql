-- ============================================================================
-- Script: SEC-01 — Nuevo esquema de permisos
-- Base de Datos: abcmasplus
-- Descripción: Crea BotTipoEntidad, BotRecurso, BotPermisos, BotPermisosAudit
-- Idempotente: seguro de ejecutar múltiples veces
-- ============================================================================

USE abcmasplus;
GO

PRINT '============================================================================';
PRINT 'SEC-01: Creando nuevo esquema de permisos';
PRINT '============================================================================';

-- ============================================================================
-- 1. BotTipoEntidad — catálogo de tipos de entidad
-- ============================================================================
IF NOT EXISTS (SELECT 1 FROM sys.objects WHERE object_id = OBJECT_ID(N'dbo.BotTipoEntidad') AND type = 'U')
BEGIN
    CREATE TABLE dbo.BotTipoEntidad (
        idTipoEntidad   INT IDENTITY(1,1) NOT NULL,
        nombre          VARCHAR(50)       NOT NULL,
        prioridad       TINYINT           NOT NULL,
        tipoResolucion  VARCHAR(20)       NOT NULL,  -- 'definitivo' | 'permisivo'
        descripcion     VARCHAR(255)      NULL,
        activo          BIT               NOT NULL DEFAULT 1,
        fechaCreacion   DATETIME          NOT NULL DEFAULT GETDATE(),

        CONSTRAINT PK_BotTipoEntidad        PRIMARY KEY (idTipoEntidad),
        CONSTRAINT UQ_BotTipoEntidad_Nombre    UNIQUE (nombre),
        CONSTRAINT UQ_BotTipoEntidad_Prioridad UNIQUE (prioridad),
        CONSTRAINT CK_BotTipoEntidad_Resolucion
            CHECK (tipoResolucion IN ('definitivo', 'permisivo'))
    );
    PRINT 'Tabla BotTipoEntidad creada.';
END
ELSE
    PRINT 'Tabla BotTipoEntidad ya existe.';
GO

-- ============================================================================
-- 2. BotRecurso — catálogo de recursos controlables
-- ============================================================================
IF NOT EXISTS (SELECT 1 FROM sys.objects WHERE object_id = OBJECT_ID(N'dbo.BotRecurso') AND type = 'U')
BEGIN
    CREATE TABLE dbo.BotRecurso (
        idRecurso    INT IDENTITY(1,1) NOT NULL,
        recurso      VARCHAR(100)      NOT NULL,  -- 'tool:database_query', 'cmd:/ia'
        tipoRecurso  VARCHAR(20)       NOT NULL,  -- 'tool' | 'cmd'
        esPublico    BIT               NOT NULL DEFAULT 0,
        descripcion  VARCHAR(255)      NULL,
        activo       BIT               NOT NULL DEFAULT 1,
        fechaCreacion DATETIME         NOT NULL DEFAULT GETDATE(),

        CONSTRAINT PK_BotRecurso         PRIMARY KEY (idRecurso),
        CONSTRAINT UQ_BotRecurso_Recurso UNIQUE (recurso),
        CONSTRAINT CK_BotRecurso_Tipo
            CHECK (tipoRecurso IN ('tool', 'cmd'))
    );
    PRINT 'Tabla BotRecurso creada.';
END
ELSE
    PRINT 'Tabla BotRecurso ya existe.';
GO

-- ============================================================================
-- 3. BotPermisos — tabla principal de permisos
-- ============================================================================
IF NOT EXISTS (SELECT 1 FROM sys.objects WHERE object_id = OBJECT_ID(N'dbo.BotPermisos') AND type = 'U')
BEGIN
    CREATE TABLE dbo.BotPermisos (
        idPermiso           INT IDENTITY(1,1) NOT NULL,
        idTipoEntidad       INT               NOT NULL,
        idEntidad           INT               NOT NULL,  -- 0 para autenticado
        idRecurso           INT               NOT NULL,
        idRolRequerido      INT               NULL,      -- NULL = cualquier rol
        permitido           BIT               NOT NULL DEFAULT 1,
        fechaExpiracion     DATETIME          NULL,      -- NULL = permanente
        activo              BIT               NOT NULL DEFAULT 1,
        descripcion         VARCHAR(255)      NULL,
        fechaCreacion       DATETIME          NOT NULL DEFAULT GETDATE(),
        usuarioCreacion     VARCHAR(100)      NULL,
        fechaModificacion   DATETIME          NULL,
        usuarioModificacion VARCHAR(100)      NULL,

        CONSTRAINT PK_BotPermisos PRIMARY KEY (idPermiso),
        CONSTRAINT FK_BotPermisos_TipoEntidad
            FOREIGN KEY (idTipoEntidad) REFERENCES dbo.BotTipoEntidad(idTipoEntidad),
        CONSTRAINT FK_BotPermisos_Recurso
            FOREIGN KEY (idRecurso) REFERENCES dbo.BotRecurso(idRecurso),
        CONSTRAINT FK_BotPermisos_Rol
            FOREIGN KEY (idRolRequerido) REFERENCES dbo.Roles(idRol)
    );

    -- Índice único para filas CON rol requerido (evita duplicados cuando idRolRequerido IS NOT NULL)
    CREATE UNIQUE NONCLUSTERED INDEX UX_BotPermisos_ConRol
        ON dbo.BotPermisos (idTipoEntidad, idEntidad, idRecurso, idRolRequerido)
        WHERE idRolRequerido IS NOT NULL;

    -- Índice único para filas SIN rol requerido (evita duplicados cuando idRolRequerido IS NULL)
    CREATE UNIQUE NONCLUSTERED INDEX UX_BotPermisos_SinRol
        ON dbo.BotPermisos (idTipoEntidad, idEntidad, idRecurso)
        WHERE idRolRequerido IS NULL;

    -- Índice de búsqueda para el lookup en cada request
    CREATE NONCLUSTERED INDEX IX_BotPermisos_Lookup
        ON dbo.BotPermisos (idTipoEntidad, idEntidad, idRecurso)
        INCLUDE (idRolRequerido, permitido, activo, fechaExpiracion);

    PRINT 'Tabla BotPermisos creada con índices.';
END
ELSE
    PRINT 'Tabla BotPermisos ya existe.';
GO

-- ============================================================================
-- 4. BotPermisosAudit — audit trail de cambios
-- ============================================================================
IF NOT EXISTS (SELECT 1 FROM sys.objects WHERE object_id = OBJECT_ID(N'dbo.BotPermisosAudit') AND type = 'U')
BEGIN
    CREATE TABLE dbo.BotPermisosAudit (
        idAudit       BIGINT IDENTITY(1,1) NOT NULL,
        idPermiso     INT                  NOT NULL,
        accion        VARCHAR(20)          NOT NULL,  -- 'INSERT' | 'UPDATE' | 'DELETE'
        valorAnterior NVARCHAR(MAX)        NULL,      -- JSON estado anterior
        valorNuevo    NVARCHAR(MAX)        NULL,      -- JSON estado nuevo
        usuario       VARCHAR(100)         NOT NULL,
        fechaAccion   DATETIME             NOT NULL DEFAULT GETDATE(),
        ip            VARCHAR(50)          NULL,

        CONSTRAINT PK_BotPermisosAudit PRIMARY KEY (idAudit),
        CONSTRAINT CK_BotPermisosAudit_Accion
            CHECK (accion IN ('INSERT', 'UPDATE', 'DELETE'))
    );

    CREATE NONCLUSTERED INDEX IX_BotPermisosAudit_Permiso
        ON dbo.BotPermisosAudit (idPermiso, fechaAccion DESC);

    PRINT 'Tabla BotPermisosAudit creada.';
END
ELSE
    PRINT 'Tabla BotPermisosAudit ya existe.';
GO

PRINT '';
PRINT 'SEC-01 Fase 1a completada: tablas creadas.';
PRINT 'Siguiente paso: ejecutar 11_BotPermisos_DatosIniciales.sql';
GO
