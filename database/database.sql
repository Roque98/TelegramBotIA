IF NOT EXISTS (
    SELECT
        *
    FROM
        sys.tables
    WHERE
        name = 'BotIAv2_ApplicationLogs'
) BEGIN CREATE TABLE dbo.[BotIAv2_ApplicationLogs] (
    [id] bigint IDENTITY(1, 1) NOT NULL,
    [correlationId] varchar(50) NULL,
    [userId] nvarchar(50) NULL,
    [level] nvarchar(10) NOT NULL,
    [event] nvarchar(100) NOT NULL,
    [message] nvarchar(2000) NULL,
    [module] nvarchar(100) NULL,
    [durationMs] int NULL,
    [extra] nvarchar(2000) NULL,
    [createdAt] datetime NULL DEFAULT (getdate()),
    CONSTRAINT [PK__Applicat__3213E83F5F378D3A] PRIMARY KEY CLUSTERED ([id] ASC)
);

PRINT 'Tabla BotIAv2_ApplicationLogs creada.';

END
ELSE PRINT 'Tabla BotIAv2_ApplicationLogs ya existe, saltando.';

IF NOT EXISTS (
    SELECT
        *
    FROM
        sys.tables
    WHERE
        name = 'BotIAv2_column_documentation'
) BEGIN CREATE TABLE dbo.[BotIAv2_column_documentation] (
    [id] int IDENTITY(1, 1) NOT NULL,
    [table_doc_id] int NOT NULL,
    [column_name] varchar(100) NOT NULL,
    [display_name] nvarchar(100) NULL,
    [description] nvarchar(500) NULL,
    [data_type] varchar(50) NULL,
    [example_value] nvarchar(200) NULL,
    [icon] nvarchar(10) NULL,
    [is_key] bit NULL DEFAULT ((0)),
    [created_at] datetime2(7) NOT NULL DEFAULT (getdate()),
    [updated_at] datetime2(7) NOT NULL DEFAULT (getdate()),
    CONSTRAINT [PK__column_d__3213E83FA2C17FD5] PRIMARY KEY CLUSTERED ([id] ASC),
    CONSTRAINT [UQ_column_documentation] UNIQUE ([table_doc_id], [column_name]),
    CONSTRAINT [FK_column_documentation_table] FOREIGN KEY ([table_doc_id]) REFERENCES dbo.[BotIAv2_table_documentation] ([id]) ON DELETE CASCADE
);

PRINT 'Tabla BotIAv2_column_documentation creada.';

END
ELSE PRINT 'Tabla BotIAv2_column_documentation ya existe, saltando.';

IF NOT EXISTS (
    SELECT
        *
    FROM
        sys.tables
    WHERE
        name = 'BotIAv2_CostSesiones'
) BEGIN CREATE TABLE dbo.[BotIAv2_CostSesiones] (
    [idCosto] int IDENTITY(1, 1) NOT NULL,
    [telegramChatId] varchar(50) NOT NULL,
    [modelo] varchar(100) NOT NULL,
    [inputTokens] int NOT NULL DEFAULT ((0)),
    [outputTokens] int NOT NULL DEFAULT ((0)),
    [cacheReadTokens] int NOT NULL DEFAULT ((0)),
    [llamadasLLM] int NOT NULL DEFAULT ((1)),
    [costoUSD] decimal(12, 8) NOT NULL DEFAULT ((0)),
    [pasos] int NOT NULL DEFAULT ((0)),
    [fechaSesion] datetime NOT NULL DEFAULT (getdate()),
    CONSTRAINT [PK__CostSesi__53FA232497854BCB] PRIMARY KEY CLUSTERED ([idCosto] ASC)
);

PRINT 'Tabla BotIAv2_CostSesiones creada.';

END
ELSE PRINT 'Tabla BotIAv2_CostSesiones ya existe, saltando.';

IF NOT EXISTS (
    SELECT
        *
    FROM
        sys.tables
    WHERE
        name = 'BotIAv2_knowledge_categories'
) BEGIN CREATE TABLE dbo.[BotIAv2_knowledge_categories] (
    [id] int IDENTITY(1, 1) NOT NULL,
    [name] varchar(50) NOT NULL,
    [display_name] nvarchar(100) NOT NULL,
    [description] nvarchar(500) NULL,
    [icon] nvarchar(10) NULL,
    [active] bit NOT NULL DEFAULT ((1)),
    [created_at] datetime2(7) NOT NULL DEFAULT (getdate()),
    [updated_at] datetime2(7) NOT NULL DEFAULT (getdate()),
    CONSTRAINT [PK__knowledg__3213E83F01F84865] PRIMARY KEY CLUSTERED ([id] ASC),
    CONSTRAINT [UQ__knowledg__72E12F1B543BFDDA] UNIQUE ([name])
);

PRINT 'Tabla BotIAv2_knowledge_categories creada.';

END
ELSE PRINT 'Tabla BotIAv2_knowledge_categories ya existe, saltando.';

IF NOT EXISTS (
    SELECT
        *
    FROM
        sys.tables
    WHERE
        name = 'BotIAv2_knowledge_entries'
) BEGIN CREATE TABLE dbo.[BotIAv2_knowledge_entries] (
    [id] int IDENTITY(1, 1) NOT NULL,
    [category_id] int NOT NULL,
    [question] nvarchar(500) NOT NULL,
    [answer] nvarchar(MAX) NOT NULL,
    [keywords] nvarchar(MAX) NOT NULL,
    [related_commands] nvarchar(500) NULL,
    [priority] int NOT NULL DEFAULT ((1)),
    [active] bit NOT NULL DEFAULT ((1)),
    [created_at] datetime2(7) NOT NULL DEFAULT (getdate()),
    [updated_at] datetime2(7) NOT NULL DEFAULT (getdate()),
    [created_by] nvarchar(100) NULL DEFAULT ('system'),
    CONSTRAINT [PK__knowledg__3213E83F04008097] PRIMARY KEY CLUSTERED ([id] ASC),
    CONSTRAINT [CK_knowledge_entries_priority] CHECK (
        [priority] >=(1)
        AND [priority] <=(3)
    ),
    CONSTRAINT [FK_knowledge_entries_category] FOREIGN KEY ([category_id]) REFERENCES dbo.[BotIAv2_knowledge_categories] ([id])
);

PRINT 'Tabla BotIAv2_knowledge_entries creada.';

END
ELSE PRINT 'Tabla BotIAv2_knowledge_entries ya existe, saltando.';

-- BotIAv2_LogOperaciones eliminada — reemplazada por BotIAv2_InteractionLogs (OBS-31)

IF OBJECT_ID('dbo.[BotIAv2_InteractionSteps]', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.[BotIAv2_InteractionSteps] (
        [idStep]        bigint          IDENTITY(1, 1) NOT NULL,
        [correlationId] nvarchar(50)    NOT NULL,
        [stepNum]       int             NOT NULL,
        [tipo]          nvarchar(20)    NOT NULL,
        [nombre]        nvarchar(100)   NULL,
        [entrada]       nvarchar(MAX)   NULL,
        [salida]        nvarchar(MAX)   NULL,
        [tokensIn]      int             NULL,
        [tokensOut]     int             NULL,
        [duracionMs]    int             NOT NULL,
        [fechaInicio]   datetime        NOT NULL    DEFAULT (getdate()),
        CONSTRAINT [PK_BotIAv2_InteractionSteps] PRIMARY KEY CLUSTERED ([idStep] ASC)
    )
    PRINT 'Tabla BotIAv2_InteractionSteps creada.'
END
ELSE PRINT 'Tabla BotIAv2_InteractionSteps ya existe, saltando.'

IF OBJECT_ID('dbo.[BotIAv2_InteractionLogs]', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.[BotIAv2_InteractionLogs] (
        [idLog]             bigint          IDENTITY(1, 1) NOT NULL,
        [correlationId]     nvarchar(50)    NULL,
        [idUsuario]         int             NOT NULL,
        [telegramChatId]    bigint          NULL,
        [telegramUsername]  nvarchar(100)   NULL,
        [comando]           nvarchar(100)   NULL,
        [query]             nvarchar(500)   NULL,
        [respuesta]         nvarchar(MAX)   NULL,
        [mensajeError]      nvarchar(MAX)   NULL,
        [toolsUsadas]       nvarchar(MAX)   NULL,
        [stepsTomados]      int             NULL,
        [memoryMs]          int             NULL,
        [reactMs]           int             NULL,
        [saveMs]            int             NULL,
        [duracionMs]        int             NULL,
        [channel]           nvarchar(50)    NULL        DEFAULT ('telegram'),
        [fechaEjecucion]    datetime        NOT NULL    DEFAULT (getdate()),
        CONSTRAINT [PK_BotIAv2_InteractionLogs] PRIMARY KEY CLUSTERED ([idLog] ASC),
        CONSTRAINT [FK_BotIAv2_InteractionLogs_Usuarios] FOREIGN KEY ([idUsuario]) REFERENCES dbo.[Usuarios] ([idUsuario])
    )
    PRINT 'Tabla BotIAv2_InteractionLogs creada.'
END
ELSE PRINT 'Tabla BotIAv2_InteractionLogs ya existe, saltando.'

IF NOT EXISTS (
    SELECT
        *
    FROM
        sys.tables
    WHERE
        name = 'BotIAv2_Permisos'
) BEGIN CREATE TABLE dbo.[BotIAv2_Permisos] (
    [idPermiso] int IDENTITY(1, 1) NOT NULL,
    [idTipoEntidad] int NOT NULL,
    [idEntidad] int NOT NULL,
    [idRecurso] int NOT NULL,
    [idRolRequerido] int NULL,
    [permitido] bit NOT NULL DEFAULT ((1)),
    [fechaExpiracion] datetime NULL,
    [activo] bit NOT NULL DEFAULT ((1)),
    [descripcion] varchar(255) NULL,
    [fechaCreacion] datetime NOT NULL DEFAULT (getdate()),
    [usuarioCreacion] varchar(100) NULL,
    [fechaModificacion] datetime NULL,
    [usuarioModificacion] varchar(100) NULL,
    CONSTRAINT [PK_BotPermisos] PRIMARY KEY CLUSTERED ([idPermiso] ASC),
    CONSTRAINT [FK_BotPermisos_Recurso] FOREIGN KEY ([idRecurso]) REFERENCES dbo.[BotIAv2_Recurso] ([idRecurso]),
    CONSTRAINT [FK_BotPermisos_Rol] FOREIGN KEY ([idRolRequerido]) REFERENCES dbo.[Roles] ([idRol]),
    CONSTRAINT [FK_BotPermisos_TipoEntidad] FOREIGN KEY ([idTipoEntidad]) REFERENCES dbo.[BotIAv2_TipoEntidad] ([idTipoEntidad])
);

PRINT 'Tabla BotIAv2_Permisos creada.';

END
ELSE PRINT 'Tabla BotIAv2_Permisos ya existe, saltando.';

IF NOT EXISTS (
    SELECT
        *
    FROM
        sys.tables
    WHERE
        name = 'BotIAv2_PermisosAudit'
) BEGIN CREATE TABLE dbo.[BotIAv2_PermisosAudit] (
    [idAudit] bigint IDENTITY(1, 1) NOT NULL,
    [idPermiso] int NOT NULL,
    [accion] varchar(20) NOT NULL,
    [valorAnterior] nvarchar(MAX) NULL,
    [valorNuevo] nvarchar(MAX) NULL,
    [usuario] varchar(100) NOT NULL,
    [fechaAccion] datetime NOT NULL DEFAULT (getdate()),
    [ip] varchar(50) NULL,
    CONSTRAINT [PK_BotPermisosAudit] PRIMARY KEY CLUSTERED ([idAudit] ASC),
    CONSTRAINT [CK_BotPermisosAudit_Accion] CHECK (
        [accion] = 'DELETE'
        OR [accion] = 'UPDATE'
        OR [accion] = 'INSERT'
    )
);

PRINT 'Tabla BotIAv2_PermisosAudit creada.';

END
ELSE PRINT 'Tabla BotIAv2_PermisosAudit ya existe, saltando.';

IF NOT EXISTS (
    SELECT
        *
    FROM
        sys.tables
    WHERE
        name = 'BotIAv2_Recurso'
) BEGIN CREATE TABLE dbo.[BotIAv2_Recurso] (
    [idRecurso] int IDENTITY(1, 1) NOT NULL,
    [recurso] varchar(100) NOT NULL,
    [tipoRecurso] varchar(20) NOT NULL,
    [esPublico] bit NOT NULL DEFAULT ((0)),
    [descripcion] varchar(255) NULL,
    [activo] bit NOT NULL DEFAULT ((1)),
    [fechaCreacion] datetime NOT NULL DEFAULT (getdate()),
    CONSTRAINT [PK_BotRecurso] PRIMARY KEY CLUSTERED ([idRecurso] ASC),
    CONSTRAINT [UQ_BotRecurso_Recurso] UNIQUE ([recurso]),
    CONSTRAINT [CK_BotRecurso_Tipo] CHECK (
        [tipoRecurso] = 'cmd'
        OR [tipoRecurso] = 'tool'
    )
);

PRINT 'Tabla BotIAv2_Recurso creada.';

END
ELSE PRINT 'Tabla BotIAv2_Recurso ya existe, saltando.';

IF NOT EXISTS (
    SELECT
        *
    FROM
        sys.tables
    WHERE
        name = 'BotIAv2_RolesCategoriesKnowledge'
) BEGIN CREATE TABLE dbo.[BotIAv2_RolesCategoriesKnowledge] (
    [idRolCategoria] int IDENTITY(1, 1) NOT NULL,
    [idRol] int NOT NULL,
    [idCategoria] int NOT NULL,
    [permitido] bit NOT NULL DEFAULT ((1)),
    [fechaAsignacion] datetime NULL DEFAULT (getdate()),
    [usuarioAsignacion] int NULL,
    [activo] bit NULL DEFAULT ((1)),
    CONSTRAINT [PK__RolesCat__54D753EEEBA66AD1] PRIMARY KEY CLUSTERED ([idRolCategoria] ASC),
    CONSTRAINT [UQ_RolCategoria] UNIQUE ([idRol], [idCategoria]),
    CONSTRAINT [FK_RolesCategoriesKnowledge_Categories] FOREIGN KEY ([idCategoria]) REFERENCES dbo.[BotIAv2_knowledge_categories] ([id]),
    CONSTRAINT [FK_RolesCategoriesKnowledge_Roles] FOREIGN KEY ([idRol]) REFERENCES dbo.[Roles] ([idRol])
);

PRINT 'Tabla BotIAv2_RolesCategoriesKnowledge creada.';

END
ELSE PRINT 'Tabla BotIAv2_RolesCategoriesKnowledge ya existe, saltando.';

IF NOT EXISTS (
    SELECT
        *
    FROM
        sys.tables
    WHERE
        name = 'BotIAv2_table_documentation'
) BEGIN CREATE TABLE dbo.[BotIAv2_table_documentation] (
    [id] int IDENTITY(1, 1) NOT NULL,
    [schema_name] varchar(100) NOT NULL DEFAULT ('dbo'),
    [table_name] varchar(100) NOT NULL,
    [display_name] nvarchar(100) NULL,
    [description] nvarchar(MAX) NULL,
    [usage_examples] nvarchar(MAX) NULL,
    [common_queries] nvarchar(MAX) NULL,
    [category] nvarchar(50) NULL,
    [active] bit NOT NULL DEFAULT ((1)),
    [created_at] datetime2(7) NOT NULL DEFAULT (getdate()),
    [updated_at] datetime2(7) NOT NULL DEFAULT (getdate()),
    CONSTRAINT [PK__table_do__3213E83FBF26C587] PRIMARY KEY CLUSTERED ([id] ASC),
    CONSTRAINT [UQ_table_documentation] UNIQUE ([schema_name], [table_name])
);

PRINT 'Tabla BotIAv2_table_documentation creada.';

END
ELSE PRINT 'Tabla BotIAv2_table_documentation ya existe, saltando.';

IF NOT EXISTS (
    SELECT
        *
    FROM
        sys.tables
    WHERE
        name = 'BotIAv2_TipoEntidad'
) BEGIN CREATE TABLE dbo.[BotIAv2_TipoEntidad] (
    [idTipoEntidad] int IDENTITY(1, 1) NOT NULL,
    [nombre] varchar(50) NOT NULL,
    [prioridad] tinyint NOT NULL,
    [tipoResolucion] varchar(20) NOT NULL,
    [descripcion] varchar(255) NULL,
    [activo] bit NOT NULL DEFAULT ((1)),
    [fechaCreacion] datetime NOT NULL DEFAULT (getdate()),
    CONSTRAINT [PK_BotTipoEntidad] PRIMARY KEY CLUSTERED ([idTipoEntidad] ASC),
    CONSTRAINT [UQ_BotTipoEntidad_Nombre] UNIQUE ([nombre]),
    CONSTRAINT [UQ_BotTipoEntidad_Prioridad] UNIQUE ([prioridad]),
    CONSTRAINT [CK_BotTipoEntidad_Resolucion] CHECK (
        [tipoResolucion] = 'permisivo'
        OR [tipoResolucion] = 'definitivo'
    )
);

PRINT 'Tabla BotIAv2_TipoEntidad creada.';

END
ELSE PRINT 'Tabla BotIAv2_TipoEntidad ya existe, saltando.';

-- BotIAv2_TransactionLogs eliminada — reemplazada por BotIAv2_InteractionLogs (OBS-31)

IF NOT EXISTS (
    SELECT
        *
    FROM
        sys.tables
    WHERE
        name = 'BotIAv2_UserMemoryProfiles'
) BEGIN CREATE TABLE dbo.[BotIAv2_UserMemoryProfiles] (
    [idMemoryProfile] int IDENTITY(1, 1) NOT NULL,
    [idUsuario] int NOT NULL,
    [resumenContextoLaboral] nvarchar(MAX) NULL,
    [resumenTemasRecientes] nvarchar(MAX) NULL,
    [resumenHistorialBreve] nvarchar(MAX) NULL,
    [numInteracciones] int NOT NULL DEFAULT ((0)),
    [ultimaActualizacion] datetime2(7) NOT NULL DEFAULT (getdate()),
    [fechaCreacion] datetime2(7) NOT NULL DEFAULT (getdate()),
    [version] int NOT NULL DEFAULT ((1)),
    [preferencias] nvarchar(MAX) NULL,
    CONSTRAINT [PK_UserMemoryProfiles] PRIMARY KEY CLUSTERED ([idMemoryProfile] ASC),
    CONSTRAINT [UQ_UserMemoryProfiles_Usuario] UNIQUE ([idUsuario])
);

PRINT 'Tabla BotIAv2_UserMemoryProfiles creada.';

END
ELSE PRINT 'Tabla BotIAv2_UserMemoryProfiles ya existe, saltando.';

IF NOT EXISTS (
    SELECT
        *
    FROM
        sys.tables
    WHERE
        name = 'BotIAv2_UsuariosTelegram'
) BEGIN CREATE TABLE dbo.[BotIAv2_UsuariosTelegram] (
    [idUsuarioTelegram] int IDENTITY(1, 1) NOT NULL,
    [idUsuario] int NOT NULL,
    [telegramChatId] bigint NOT NULL,
    [telegramUsername] nvarchar(100) NULL,
    [telegramFirstName] nvarchar(100) NULL,
    [telegramLastName] nvarchar(100) NULL,
    [alias] nvarchar(50) NULL,
    [esPrincipal] bit NOT NULL DEFAULT ((0)),
    [estado] nvarchar(20) NOT NULL DEFAULT ('ACTIVO'),
    [fechaRegistro] datetime NOT NULL DEFAULT (getdate()),
    [fechaUltimaActividad] datetime NULL,
    [fechaVerificacion] datetime NULL,
    [codigoVerificacion] nvarchar(10) NULL,
    [verificado] bit NOT NULL DEFAULT ((0)),
    [intentosVerificacion] int NOT NULL DEFAULT ((0)),
    [notificacionesActivas] bit NOT NULL DEFAULT ((1)),
    [observaciones] nvarchar(500) NULL,
    [activo] bit NOT NULL DEFAULT ((1)),
    [fechaCreacion] datetime NOT NULL DEFAULT (getdate()),
    [usuarioCreacion] int NULL,
    [fechaModificacion] datetime NULL,
    [usuarioModificacion] int NULL,
    CONSTRAINT [PK_UsuariosTelegram] PRIMARY KEY CLUSTERED ([idUsuarioTelegram] ASC),
    CONSTRAINT [UQ_UsuariosTelegram_ChatId] UNIQUE ([telegramChatId]),
    CONSTRAINT [CK_UsuariosTelegram_Estado] CHECK (
        [estado] = 'BLOQUEADO'
        OR [estado] = 'SUSPENDIDO'
        OR [estado] = 'ACTIVO'
    ),
    CONSTRAINT [FK_UsuariosTelegram_UsuarioCreacion] FOREIGN KEY ([usuarioCreacion]) REFERENCES dbo.[Usuarios] ([idUsuario]),
    CONSTRAINT [FK_UsuariosTelegram_UsuarioModificacion] FOREIGN KEY ([usuarioModificacion]) REFERENCES dbo.[Usuarios] ([idUsuario]),
    CONSTRAINT [FK_UsuariosTelegram_Usuarios] FOREIGN KEY ([idUsuario]) REFERENCES dbo.[Usuarios] ([idUsuario])
);

PRINT 'Tabla BotIAv2_UsuariosTelegram creada.';

END
ELSE PRINT 'Tabla BotIAv2_UsuariosTelegram ya existe, saltando.';

IF NOT EXISTS (
    SELECT
        *
    FROM
        sys.indexes
    WHERE
        name = 'IX_ApplicationLogs_correlationId'
        AND object_id = OBJECT_ID('dbo.[BotIAv2_ApplicationLogs]')
) CREATE NONCLUSTERED INDEX [IX_ApplicationLogs_correlationId] ON dbo.[BotIAv2_ApplicationLogs] ([correlationId] ASC);

IF NOT EXISTS (
    SELECT
        *
    FROM
        sys.indexes
    WHERE
        name = 'IX_ApplicationLogs_createdAt'
        AND object_id = OBJECT_ID('dbo.[BotIAv2_ApplicationLogs]')
) CREATE NONCLUSTERED INDEX [IX_ApplicationLogs_createdAt] ON dbo.[BotIAv2_ApplicationLogs] ([createdAt] DESC);

IF NOT EXISTS (
    SELECT
        *
    FROM
        sys.indexes
    WHERE
        name = 'IX_ApplicationLogs_level'
        AND object_id = OBJECT_ID('dbo.[BotIAv2_ApplicationLogs]')
) CREATE NONCLUSTERED INDEX [IX_ApplicationLogs_level] ON dbo.[BotIAv2_ApplicationLogs] ([level] ASC);

IF NOT EXISTS (
    SELECT
        *
    FROM
        sys.indexes
    WHERE
        name = 'idx_column_documentation_table'
        AND object_id = OBJECT_ID('dbo.[BotIAv2_column_documentation]')
) CREATE NONCLUSTERED INDEX [idx_column_documentation_table] ON dbo.[BotIAv2_column_documentation] ([table_doc_id] ASC);

IF NOT EXISTS (
    SELECT
        *
    FROM
        sys.indexes
    WHERE
        name = 'IX_CostSesiones_ChatId'
        AND object_id = OBJECT_ID('dbo.[BotIAv2_CostSesiones]')
) CREATE NONCLUSTERED INDEX [IX_CostSesiones_ChatId] ON dbo.[BotIAv2_CostSesiones] ([telegramChatId] ASC);

IF NOT EXISTS (
    SELECT
        *
    FROM
        sys.indexes
    WHERE
        name = 'IX_CostSesiones_Fecha'
        AND object_id = OBJECT_ID('dbo.[BotIAv2_CostSesiones]')
) CREATE NONCLUSTERED INDEX [IX_CostSesiones_Fecha] ON dbo.[BotIAv2_CostSesiones] ([fechaSesion] ASC);

IF NOT EXISTS (
    SELECT
        *
    FROM
        sys.indexes
    WHERE
        name = 'idx_knowledge_categories_active'
        AND object_id = OBJECT_ID('dbo.[BotIAv2_knowledge_categories]')
) CREATE NONCLUSTERED INDEX [idx_knowledge_categories_active] ON dbo.[BotIAv2_knowledge_categories] ([active] ASC);

IF NOT EXISTS (
    SELECT
        *
    FROM
        sys.indexes
    WHERE
        name = 'idx_knowledge_entries_active'
        AND object_id = OBJECT_ID('dbo.[BotIAv2_knowledge_entries]')
) CREATE NONCLUSTERED INDEX [idx_knowledge_entries_active] ON dbo.[BotIAv2_knowledge_entries] ([active] ASC);

IF NOT EXISTS (
    SELECT
        *
    FROM
        sys.indexes
    WHERE
        name = 'idx_knowledge_entries_category'
        AND object_id = OBJECT_ID('dbo.[BotIAv2_knowledge_entries]')
) CREATE NONCLUSTERED INDEX [idx_knowledge_entries_category] ON dbo.[BotIAv2_knowledge_entries] ([category_id] ASC);

IF NOT EXISTS (
    SELECT
        *
    FROM
        sys.indexes
    WHERE
        name = 'idx_knowledge_entries_priority'
        AND object_id = OBJECT_ID('dbo.[BotIAv2_knowledge_entries]')
) CREATE NONCLUSTERED INDEX [idx_knowledge_entries_priority] ON dbo.[BotIAv2_knowledge_entries] ([priority] DESC);

IF NOT EXISTS (
    SELECT
        *
    FROM
        sys.indexes
    WHERE
        name = 'idx_knowledge_entries_question'
        AND object_id = OBJECT_ID('dbo.[BotIAv2_knowledge_entries]')
) CREATE NONCLUSTERED INDEX [idx_knowledge_entries_question] ON dbo.[BotIAv2_knowledge_entries] ([question] ASC);

-- Índices BotIAv2_InteractionSteps
IF NOT EXISTS (
    SELECT * FROM sys.indexes
    WHERE name = 'IX_InteractionSteps_CorrelationId'
      AND object_id = OBJECT_ID('dbo.[BotIAv2_InteractionSteps]')
) CREATE NONCLUSTERED INDEX [IX_InteractionSteps_CorrelationId] ON dbo.[BotIAv2_InteractionSteps] ([correlationId] ASC, [stepNum] ASC);

IF NOT EXISTS (
    SELECT * FROM sys.indexes
    WHERE name = 'IX_InteractionSteps_FechaInicio'
      AND object_id = OBJECT_ID('dbo.[BotIAv2_InteractionSteps]')
) CREATE NONCLUSTERED INDEX [IX_InteractionSteps_FechaInicio] ON dbo.[BotIAv2_InteractionSteps] ([fechaInicio] DESC);

-- Índices BotIAv2_InteractionLogs
IF NOT EXISTS (
    SELECT * FROM sys.indexes
    WHERE name = 'IX_InteractionLogs_ChatId'
      AND object_id = OBJECT_ID('dbo.[BotIAv2_InteractionLogs]')
) CREATE NONCLUSTERED INDEX [IX_InteractionLogs_ChatId] ON dbo.[BotIAv2_InteractionLogs] ([telegramChatId] ASC);

IF NOT EXISTS (
    SELECT * FROM sys.indexes
    WHERE name = 'IX_InteractionLogs_CorrelationId'
      AND object_id = OBJECT_ID('dbo.[BotIAv2_InteractionLogs]')
) CREATE NONCLUSTERED INDEX [IX_InteractionLogs_CorrelationId] ON dbo.[BotIAv2_InteractionLogs] ([correlationId] ASC);

IF NOT EXISTS (
    SELECT * FROM sys.indexes
    WHERE name = 'IX_InteractionLogs_FechaEjecucion'
      AND object_id = OBJECT_ID('dbo.[BotIAv2_InteractionLogs]')
) CREATE NONCLUSTERED INDEX [IX_InteractionLogs_FechaEjecucion] ON dbo.[BotIAv2_InteractionLogs] ([fechaEjecucion] DESC);

IF NOT EXISTS (
    SELECT * FROM sys.indexes
    WHERE name = 'IX_InteractionLogs_IdUsuario'
      AND object_id = OBJECT_ID('dbo.[BotIAv2_InteractionLogs]')
) CREATE NONCLUSTERED INDEX [IX_InteractionLogs_IdUsuario] ON dbo.[BotIAv2_InteractionLogs] ([idUsuario] ASC);


IF NOT EXISTS (
    SELECT
        *
    FROM
        sys.indexes
    WHERE
        name = 'IX_BotPermisos_Lookup'
        AND object_id = OBJECT_ID('dbo.[BotIAv2_Permisos]')
) CREATE NONCLUSTERED INDEX [IX_BotPermisos_Lookup] ON dbo.[BotIAv2_Permisos] (
    [idTipoEntidad] ASC,
    [idEntidad] ASC,
    [idRecurso] ASC
) INCLUDE (
    [idRolRequerido],
    [permitido],
    [activo],
    [fechaExpiracion]
);

IF NOT EXISTS (
    SELECT
        *
    FROM
        sys.indexes
    WHERE
        name = 'UX_BotPermisos_ConRol'
        AND object_id = OBJECT_ID('dbo.[BotIAv2_Permisos]')
) CREATE UNIQUE NONCLUSTERED INDEX [UX_BotPermisos_ConRol] ON dbo.[BotIAv2_Permisos] (
    [idTipoEntidad] ASC,
    [idEntidad] ASC,
    [idRecurso] ASC,
    [idRolRequerido] ASC
)
WHERE
    ([idRolRequerido] IS NOT NULL);

IF NOT EXISTS (
    SELECT
        *
    FROM
        sys.indexes
    WHERE
        name = 'UX_BotPermisos_SinRol'
        AND object_id = OBJECT_ID('dbo.[BotIAv2_Permisos]')
) CREATE UNIQUE NONCLUSTERED INDEX [UX_BotPermisos_SinRol] ON dbo.[BotIAv2_Permisos] (
    [idTipoEntidad] ASC,
    [idEntidad] ASC,
    [idRecurso] ASC
)
WHERE
    ([idRolRequerido] IS NULL);

IF NOT EXISTS (
    SELECT
        *
    FROM
        sys.indexes
    WHERE
        name = 'IX_BotPermisosAudit_Permiso'
        AND object_id = OBJECT_ID('dbo.[BotIAv2_PermisosAudit]')
) CREATE NONCLUSTERED INDEX [IX_BotPermisosAudit_Permiso] ON dbo.[BotIAv2_PermisosAudit] ([idPermiso] ASC, [fechaAccion] DESC);

IF NOT EXISTS (
    SELECT
        *
    FROM
        sys.indexes
    WHERE
        name = 'IX_RolesCategoriesKnowledge_Categoria'
        AND object_id = OBJECT_ID('dbo.[BotIAv2_RolesCategoriesKnowledge]')
) CREATE NONCLUSTERED INDEX [IX_RolesCategoriesKnowledge_Categoria] ON dbo.[BotIAv2_RolesCategoriesKnowledge] ([idCategoria] ASC, [activo] ASC);

IF NOT EXISTS (
    SELECT
        *
    FROM
        sys.indexes
    WHERE
        name = 'IX_RolesCategoriesKnowledge_Rol'
        AND object_id = OBJECT_ID('dbo.[BotIAv2_RolesCategoriesKnowledge]')
) CREATE NONCLUSTERED INDEX [IX_RolesCategoriesKnowledge_Rol] ON dbo.[BotIAv2_RolesCategoriesKnowledge] ([idRol] ASC, [activo] ASC);

IF NOT EXISTS (
    SELECT
        *
    FROM
        sys.indexes
    WHERE
        name = 'idx_table_documentation_active'
        AND object_id = OBJECT_ID('dbo.[BotIAv2_table_documentation]')
) CREATE NONCLUSTERED INDEX [idx_table_documentation_active] ON dbo.[BotIAv2_table_documentation] ([active] ASC);

-- Índices IX_TransactionLogs_* eliminados — tabla reemplazada por BotIAv2_InteractionLogs (OBS-31)

IF NOT EXISTS (
    SELECT
        *
    FROM
        sys.indexes
    WHERE
        name = 'IX_UserMemoryProfiles_UltimaActualizacion'
        AND object_id = OBJECT_ID('dbo.[BotIAv2_UserMemoryProfiles]')
) CREATE NONCLUSTERED INDEX [IX_UserMemoryProfiles_UltimaActualizacion] ON dbo.[BotIAv2_UserMemoryProfiles] ([ultimaActualizacion] DESC);

IF NOT EXISTS (
    SELECT
        *
    FROM
        sys.indexes
    WHERE
        name = 'IX_UserMemoryProfiles_Usuario'
        AND object_id = OBJECT_ID('dbo.[BotIAv2_UserMemoryProfiles]')
) CREATE NONCLUSTERED INDEX [IX_UserMemoryProfiles_Usuario] ON dbo.[BotIAv2_UserMemoryProfiles] ([idUsuario] ASC);

IF NOT EXISTS (
    SELECT
        *
    FROM
        sys.indexes
    WHERE
        name = 'IX_UsuariosTelegram_ChatId'
        AND object_id = OBJECT_ID('dbo.[BotIAv2_UsuariosTelegram]')
) CREATE NONCLUSTERED INDEX [IX_UsuariosTelegram_ChatId] ON dbo.[BotIAv2_UsuariosTelegram] ([telegramChatId] ASC);

IF NOT EXISTS (
    SELECT
        *
    FROM
        sys.indexes
    WHERE
        name = 'IX_UsuariosTelegram_Estado'
        AND object_id = OBJECT_ID('dbo.[BotIAv2_UsuariosTelegram]')
) CREATE NONCLUSTERED INDEX [IX_UsuariosTelegram_Estado] ON dbo.[BotIAv2_UsuariosTelegram] ([estado] ASC);

IF NOT EXISTS (
    SELECT
        *
    FROM
        sys.indexes
    WHERE
        name = 'IX_UsuariosTelegram_IdUsuario'
        AND object_id = OBJECT_ID('dbo.[BotIAv2_UsuariosTelegram]')
) CREATE NONCLUSTERED INDEX [IX_UsuariosTelegram_IdUsuario] ON dbo.[BotIAv2_UsuariosTelegram] ([idUsuario] ASC);

IF NOT EXISTS (
    SELECT
        *
    FROM
        sys.indexes
    WHERE
        name = 'IX_UsuariosTelegram_Username'
        AND object_id = OBJECT_ID('dbo.[BotIAv2_UsuariosTelegram]')
) CREATE NONCLUSTERED INDEX [IX_UsuariosTelegram_Username] ON dbo.[BotIAv2_UsuariosTelegram] ([telegramUsername] ASC);

IF OBJECT_ID(
    'dbo.[BotIAv2_sp_ActualizarActividadTelegram]',
    'P'
) IS NOT NULL DROP PROCEDURE dbo.[BotIAv2_sp_ActualizarActividadTelegram];

GO
    CREATE PROCEDURE dbo.BotIAv2_sp_ActualizarActividadTelegram @telegramChatId BIGINT AS BEGIN
SET
    NOCOUNT ON;

UPDATE
    dbo.BotIAv2_UsuariosTelegram
SET
    fechaUltimaActividad = GETDATE()
WHERE
    telegramChatId = @telegramChatId
    AND activo = 1;

SELECT
    @ @ROWCOUNT AS FilasActualizadas;

END
GO
    IF OBJECT_ID('dbo.[BotIAv2_sp_GenerarScriptMigracion]', 'P') IS NOT NULL DROP PROCEDURE dbo.[BotIAv2_sp_GenerarScriptMigracion];

GO
    CREATE PROCEDURE [dbo].[BotIAv2_sp_GenerarScriptMigracion] AS BEGIN
SET
    NOCOUNT ON;

-- ============================================================      -- Tabla de resultado      -- ============================================================      DECLARE @resultado TABLE (          orden   INT             NOT NULL,          tipo    VARCHAR(10)     NOT NULL,   -- TABLE | INDEX | SP          nombre  NVARCHAR(128)   NOT NULL,          ddl     NVARCHAR(MAX)   NOT NULL      );        -- ============================================================      -- Tablas a exportar (en orden de dependencias)      -- ============================================================      DECLARE @tablas TABLE (nombre NVARCHAR(128), orden TINYINT);          INSERT INTO @tablas      SELECT name, 10 + ROW_NUMBER() OVER (ORDER BY name)      FROM sys.tables      WHERE name LIKE 'BotIAv2[_]%' AND is_ms_shipped = 0;        -- ============================================================      -- Cursor por tabla      -- ============================================================      DECLARE @tabla   NVARCHAR(128);      DECLARE @torden  TINYINT;      DECLARE @tid     INT;      DECLARE @ddl     NVARCHAR(MAX);      DECLARE @cols    NVARCHAR(MAX);      DECLARE @cons    NVARCHAR(MAX);      DECLARE @idxs    NVARCHAR(MAX);        DECLARE cur_tabla CURSOR FAST_FORWARD FOR          SELECT nombre, orden FROM @tablas ORDER BY orden;        OPEN cur_tabla;      FETCH NEXT FROM cur_tabla INTO @tabla, @torden;        WHILE @@FETCH_STATUS = 0      BEGIN          SET @tid = OBJECT_ID('dbo.[' + @tabla + ']');            IF @tid IS NOT NULL          BEGIN              -- ---- Columnas ----              SELECT @cols = STRING_AGG(                  CAST(                      '    [' + c.name + '] ' +                      -- Tipo de dato                      CASE                          WHEN t.name IN ('varchar','char','varbinary','binary')                              THEN t.name + '(' + CASE WHEN c.max_length = -1 THEN 'MAX'                                                        ELSE CAST(c.max_length AS VARCHAR) END + ')'                          WHEN t.name IN ('nvarchar','nchar')                              THEN t.name + '(' + CASE WHEN c.max_length = -1 THEN 'MAX'                                                        ELSE CAST(c.max_length / 2 AS VARCHAR) END + ')'                          WHEN t.name IN ('decimal','numeric')                              THEN t.name + '(' + CAST(c.precision AS VARCHAR) + ', ' + CAST(c.scale AS VARCHAR) + ')'                          WHEN t.name = 'float'                              THEN t.name + '(' + CAST(c.precision AS VARCHAR) + ')'                          WHEN t.name IN ('datetime2','time','datetimeoffset')                              THEN t.name + '(' + CAST(c.scale AS VARCHAR) + ')'                          ELSE t.name                      END +                      -- IDENTITY                      CASE WHEN ic.seed_value IS NOT NULL                          THEN ' IDENTITY(' + CAST(ic.seed_value AS VARCHAR) + ','                                            + CAST(ic.increment_value AS VARCHAR) + ')'                          ELSE '' END +                      -- Nulabilidad                      CASE WHEN c.is_nullable = 0 THEN ' NOT NULL' ELSE ' NULL' END +                      -- DEFAULT                      CASE WHEN dc.definition IS NOT NULL                          THEN ' DEFAULT ' + dc.definition                          ELSE '' END                  AS NVARCHAR(MAX)),                  ',' + CHAR(13) + CHAR(10))              WITHIN GROUP (ORDER BY c.column_id)              FROM sys.columns c              INNER JOIN sys.types t                  ON c.user_type_id = t.user_type_id              LEFT JOIN sys.identity_columns ic                  ON c.object_id = ic.object_id AND c.column_id = ic.column_id              LEFT JOIN sys.default_constraints dc                  ON c.object_id = dc.parent_object_id AND c.column_id = dc.parent_column_id              WHERE c.object_id = @tid;                -- ---- PK ----              DECLARE @pk NVARCHAR(MAX) = '';              SELECT @pk =                  '    CONSTRAINT [' + kc.name + '] PRIMARY KEY '                  + CASE i.type_desc WHEN 'CLUSTERED' THEN 'CLUSTERED' ELSE 'NONCLUSTERED' END                  + ' ('                  + (SELECT STRING_AGG(                          '[' + c2.name + '] ' + CASE ic2.is_descending_key WHEN 1 THEN 'DESC' ELSE 'ASC' END,                          ', ') WITHIN GROUP (ORDER BY ic2.key_ordinal)                     FROM sys.index_columns ic2                     INNER JOIN sys.columns c2                         ON ic2.object_id = c2.object_id AND ic2.column_id = c2.column_id                     WHERE ic2.object_id = @tid AND ic2.index_id = i.index_id)                  + ')'              FROM sys.key_constraints kc              INNER JOIN sys.indexes i                  ON kc.parent_object_id = i.object_id AND kc.unique_index_id = i.index_id              WHERE kc.parent_object_id = @tid AND kc.type = 'PK';                -- ---- UNIQUE constraints ----              DECLARE @uq NVARCHAR(MAX) = '';              SELECT @uq = @uq                  + '    CONSTRAINT [' + kc.name + '] UNIQUE ('                  + (SELECT STRING_AGG('[' + c2.name + ']', ', ')                     WITHIN GROUP (ORDER BY ic2.key_ordinal)                     FROM sys.index_columns ic2                     INNER JOIN sys.columns c2                         ON ic2.object_id = c2.object_id AND ic2.column_id = c2.column_id                     WHERE ic2.object_id = @tid AND ic2.index_id = i.index_id AND ic2.is_included_column = 0)                  + '),' + CHAR(13) + CHAR(10)              FROM sys.key_constraints kc              INNER JOIN sys.indexes i                  ON kc.parent_object_id = i.object_id AND kc.unique_index_id = i.index_id              WHERE kc.parent_object_id = @tid AND kc.type = 'UQ'              ORDER BY kc.name;                -- ---- CHECK constraints ----              DECLARE @ck NVARCHAR(MAX) = '';              SELECT @ck = @ck                  + '    CONSTRAINT [' + cc.name + '] CHECK ' + cc.definition + ',' + CHAR(13) + CHAR(10)              FROM sys.check_constraints cc              WHERE cc.parent_object_id = @tid              ORDER BY cc.name;                -- ---- FK constraints ----              DECLARE @fk NVARCHAR(MAX) = '';              SELECT @fk = @fk                  + '    CONSTRAINT [' + fk.name + '] FOREIGN KEY (['                  + cp.name + ']) REFERENCES dbo.['                  + tr.name + '] ([' + cr.name + '])'                  + CASE fk.delete_referential_action                      WHEN 1 THEN ' ON DELETE CASCADE'                      WHEN 2 THEN ' ON DELETE SET NULL'                      ELSE '' END                  + ',' + CHAR(13) + CHAR(10)              FROM sys.foreign_keys fk              INNER JOIN sys.tables tr                  ON fk.referenced_object_id = tr.object_id              INNER JOIN sys.foreign_key_columns fkc                  ON fk.object_id = fkc.constraint_object_id              INNER JOIN sys.columns cp                  ON fkc.parent_object_id = cp.object_id AND fkc.parent_column_id = cp.column_id              INNER JOIN sys.columns cr                  ON fkc.referenced_object_id = cr.object_id AND fkc.referenced_column_id = cr.column_id              WHERE fk.parent_object_id = @tid              ORDER BY fk.name;                -- ---- Ensamblar constraints ----              -- Construir bloque de constraints (sin trailing comma en el último)              SET @cons = '';              IF @pk  != '' SET @cons = @cons + @pk  + ',' + CHAR(13) + CHAR(10);              IF @uq  != '' SET @cons = @cons + @uq;              IF @ck  != '' SET @cons = @cons + @ck;              IF @fk  != '' SET @cons = @cons + @fk;                -- Quitar la última coma+salto del bloque de constraints              IF @cons != ''                  SET @cons = LEFT(@cons, LEN(@cons) - 3); -- quita ,\r\n final                -- ---- CREATE TABLE ----              IF @cons != ''                  SET @ddl =                      'IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = ''' + @tabla + ''')' + CHAR(13) + CHAR(10) +                      'BEGIN' + CHAR(13) + CHAR(10) +                      'CREATE TABLE dbo.[' + @tabla + '] (' + CHAR(13) + CHAR(10) +                      @cols + ',' + CHAR(13) + CHAR(10) +                      @cons + CHAR(13) + CHAR(10) +                      ');' + CHAR(13) + CHAR(10) +                      'PRINT ''Tabla ' + @tabla + ' creada.'';' + CHAR(13) + CHAR(10) +                      'END' + CHAR(13) + CHAR(10) +                      'ELSE PRINT ''Tabla ' + @tabla + ' ya existe, saltando.'';';              ELSE                  SET @ddl =                      'IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = ''' + @tabla + ''')' + CHAR(13) + CHAR(10) +                      'BEGIN' + CHAR(13) + CHAR(10) +                      'CREATE TABLE dbo.[' + @tabla + '] (' + CHAR(13) + CHAR(10) +                      @cols + CHAR(13) + CHAR(10) +                      ');' + CHAR(13) + CHAR(10) +                      'PRINT ''Tabla ' + @tabla + ' creada.'';' + CHAR(13) + CHAR(10) +                      'END' + CHAR(13) + CHAR(10) +                      'ELSE PRINT ''Tabla ' + @tabla + ' ya existe, saltando.'';';                INSERT INTO @resultado VALUES (@torden, 'TABLE', @tabla, @ddl);                -- ---- Índices non-clustered (no PK, no UQ) ----              SET @idxs = '';              SELECT @idxs = @idxs +                  'IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = ''' + i.name + ''' AND object_id = OBJECT_ID(''dbo.[' + @tabla + ']''))' + CHAR(13) + CHAR(10) +                  'CREATE ' + CASE i.is_unique WHEN 1 THEN 'UNIQUE ' ELSE '' END +                  'NONCLUSTERED INDEX [' + i.name + '] ON dbo.[' + @tabla + '] (' +                  (SELECT STRING_AGG(                      '[' + c2.name + '] ' + CASE ic2.is_descending_key WHEN 1 THEN 'DESC' ELSE 'ASC' END,                      ', ') WITHIN GROUP (ORDER BY ic2.key_ordinal)                   FROM sys.index_columns ic2                   INNER JOIN sys.columns c2                       ON ic2.object_id = c2.object_id AND ic2.column_id = c2.column_id                   WHERE ic2.object_id = @tid AND ic2.index_id = i.index_id AND ic2.is_included_column = 0)                  + ')'                  -- INCLUDE                  + CASE WHEN EXISTS (                          SELECT 1 FROM sys.index_columns                          WHERE object_id = @tid AND index_id = i.index_id AND is_included_column = 1)                      THEN ' INCLUDE (' +                          (SELECT STRING_AGG('[' + c3.name + ']', ', ')                           FROM sys.index_columns ic3                           INNER JOIN sys.columns c3                               ON ic3.object_id = c3.object_id AND ic3.column_id = c3.column_id                           WHERE ic3.object_id = @tid AND ic3.index_id = i.index_id AND ic3.is_included_column = 1)                           + ')'                      ELSE '' END                  -- WHERE filter                  + CASE WHEN i.filter_definition IS NOT NULL                      THEN ' WHERE ' + i.filter_definition                      ELSE '' END                  + ';' + CHAR(13) + CHAR(10)              FROM sys.indexes i              WHERE i.object_id = @tid                AND i.type = 2                AND i.is_primary_key = 0                AND i.is_unique_constraint = 0              ORDER BY i.name;                IF @idxs != ''                  INSERT INTO @resultado VALUES (@torden * 100, 'INDEX', @tabla, @idxs);          END            FETCH NEXT FROM cur_tabla INTO @tabla, @torden;      END        CLOSE cur_tabla;      DEALLOCATE cur_tabla;        -- ============================================================      -- SPs BotIAv2_      -- ============================================================      INSERT INTO @resultado (orden, tipo, nombre, ddl)      SELECT          9000 + ROW_NUMBER() OVER (ORDER BY p.name),          'SP',          p.name,          'IF OBJECT_ID(''dbo.[' + p.name + ']'', ''P'') IS NOT NULL'  + CHAR(13) + CHAR(10) +          '    DROP PROCEDURE dbo.[' + p.name + '];'                    + CHAR(13) + CHAR(10) +          'GO'                                                           + CHAR(13) + CHAR(10) +          OBJECT_DEFINITION(p.object_id)                                 + CHAR(13) + CHAR(10) +          'GO'      FROM sys.procedures p      WHERE p.name LIKE 'BotIAv2[_]%'      ORDER BY p.name;        -- ============================================================      -- Resultado final      -- ============================================================      SELECT          orden,          tipo,          nombre,          ddl      FROM @resultado      ORDER BY orden;  END    GO
IF OBJECT_ID('dbo.[BotIAv2_sp_search_knowledge]', 'P') IS NOT NULL DROP PROCEDURE dbo.[BotIAv2_sp_search_knowledge];

GO
    CREATE PROCEDURE dbo.BotIAv2_sp_search_knowledge @query NVARCHAR(500),
    @category VARCHAR(50) = NULL,
    @top_k INT = 3,
    @min_priority INT = 1 AS BEGIN
SET
    NOCOUNT ON;

SELECT
    TOP (@top_k) e.id,
    e.question,
    e.answer,
    e.keywords,
    e.related_commands,
    e.priority,
    c.name AS category,
    c.display_name AS category_display_name,
    c.icon AS category_icon,
    CASE
        WHEN e.priority = 3 THEN 1.5
        WHEN e.priority = 2 THEN 1.2
        ELSE 1.0
    END AS score
FROM
    dbo.BotIAv2_knowledge_entries e
    INNER JOIN dbo.BotIAv2_knowledge_categories c ON e.category_id = c.id
WHERE
    e.active = 1
    AND c.active = 1
    AND e.priority >= @min_priority
    AND (
        @category IS NULL
        OR c.name = @category
    )
    AND (
        e.question LIKE '%' + @query + '%'
        OR e.answer LIKE '%' + @query + '%'
        OR e.keywords LIKE '%' + @query + '%'
    )
ORDER BY
    e.priority DESC,
    LEN(e.question) ASC;

END
GO
