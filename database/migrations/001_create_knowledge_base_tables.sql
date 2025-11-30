-- ============================================================================
-- Migración 001: Crear tablas de Knowledge Base
-- Fecha: 2025-11-29
-- Descripción: Migra el knowledge base de código a base de datos
-- Base de datos: abcmasplus
-- ============================================================================

USE [abcmasplus];
GO

-- ============================================================================
-- 1. Tabla de Categorías de Conocimiento
-- ============================================================================

IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'knowledge_categories')
BEGIN
    CREATE TABLE knowledge_categories (
        id INT PRIMARY KEY IDENTITY(1,1),
        name VARCHAR(50) NOT NULL UNIQUE,
        display_name NVARCHAR(100) NOT NULL,
        description NVARCHAR(500),
        icon NVARCHAR(10),
        active BIT NOT NULL DEFAULT 1,
        created_at DATETIME2 NOT NULL DEFAULT GETDATE(),
        updated_at DATETIME2 NOT NULL DEFAULT GETDATE()
    );

    CREATE INDEX idx_knowledge_categories_active ON knowledge_categories(active);

    PRINT 'Tabla knowledge_categories creada exitosamente';
END
ELSE
BEGIN
    PRINT 'Tabla knowledge_categories ya existe';
END
GO

-- ============================================================================
-- 2. Tabla de Entradas de Conocimiento
-- ============================================================================

IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'knowledge_entries')
BEGIN
    CREATE TABLE knowledge_entries (
        id INT PRIMARY KEY IDENTITY(1,1),
        category_id INT NOT NULL,
        question NVARCHAR(500) NOT NULL,
        answer NVARCHAR(MAX) NOT NULL,
        keywords NVARCHAR(MAX) NOT NULL, -- JSON array: ["keyword1", "keyword2"]
        related_commands NVARCHAR(500), -- JSON array: ["/help", "/ia"]
        priority INT NOT NULL DEFAULT 1, -- 1=normal, 2=high, 3=critical
        active BIT NOT NULL DEFAULT 1,
        created_at DATETIME2 NOT NULL DEFAULT GETDATE(),
        updated_at DATETIME2 NOT NULL DEFAULT GETDATE(),
        created_by NVARCHAR(100) DEFAULT 'system',

        CONSTRAINT FK_knowledge_entries_category
            FOREIGN KEY (category_id) REFERENCES knowledge_categories(id),

        CONSTRAINT CK_knowledge_entries_priority
            CHECK (priority BETWEEN 1 AND 3)
    );

    -- Índices para búsqueda eficiente
    CREATE INDEX idx_knowledge_entries_category ON knowledge_entries(category_id);
    CREATE INDEX idx_knowledge_entries_priority ON knowledge_entries(priority DESC);
    CREATE INDEX idx_knowledge_entries_active ON knowledge_entries(active);
    CREATE INDEX idx_knowledge_entries_question ON knowledge_entries(question);

    PRINT 'Tabla knowledge_entries creada exitosamente';
END
ELSE
BEGIN
    PRINT 'Tabla knowledge_entries ya existe';
END
GO

-- ============================================================================
-- 3. Tabla de Documentación de Tablas de BD
-- ============================================================================

IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'table_documentation')
BEGIN
    CREATE TABLE table_documentation (
        id INT PRIMARY KEY IDENTITY(1,1),
        schema_name VARCHAR(100) NOT NULL DEFAULT 'dbo',
        table_name VARCHAR(100) NOT NULL,
        display_name NVARCHAR(100),
        description NVARCHAR(MAX),
        usage_examples NVARCHAR(MAX), -- JSON array
        common_queries NVARCHAR(MAX), -- JSON array
        category NVARCHAR(50), -- "Ventas", "Productos", "Clientes", etc.
        active BIT NOT NULL DEFAULT 1,
        created_at DATETIME2 NOT NULL DEFAULT GETDATE(),
        updated_at DATETIME2 NOT NULL DEFAULT GETDATE(),

        CONSTRAINT UQ_table_documentation UNIQUE (schema_name, table_name)
    );

    CREATE INDEX idx_table_documentation_active ON table_documentation(active);

    PRINT 'Tabla table_documentation creada exitosamente';
END
ELSE
BEGIN
    PRINT 'Tabla table_documentation ya existe';
END
GO

-- ============================================================================
-- 4. Tabla de Documentación de Columnas
-- ============================================================================

IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'column_documentation')
BEGIN
    CREATE TABLE column_documentation (
        id INT PRIMARY KEY IDENTITY(1,1),
        table_doc_id INT NOT NULL,
        column_name VARCHAR(100) NOT NULL,
        display_name NVARCHAR(100),
        description NVARCHAR(500),
        data_type VARCHAR(50),
        example_value NVARCHAR(200),
        icon NVARCHAR(10), -- Emoji para la columna
        is_key BIT DEFAULT 0,
        created_at DATETIME2 NOT NULL DEFAULT GETDATE(),
        updated_at DATETIME2 NOT NULL DEFAULT GETDATE(),

        CONSTRAINT FK_column_documentation_table
            FOREIGN KEY (table_doc_id) REFERENCES table_documentation(id) ON DELETE CASCADE,

        CONSTRAINT UQ_column_documentation UNIQUE (table_doc_id, column_name)
    );

    CREATE INDEX idx_column_documentation_table ON column_documentation(table_doc_id);

    PRINT 'Tabla column_documentation creada exitosamente';
END
ELSE
BEGIN
    PRINT 'Tabla column_documentation ya existe';
END
GO

-- ============================================================================
-- 5. Vista para consultas frecuentes
-- ============================================================================

IF OBJECT_ID('vw_knowledge_base', 'V') IS NOT NULL
    DROP VIEW vw_knowledge_base;
GO

CREATE VIEW vw_knowledge_base AS
SELECT
    e.id,
    e.question,
    e.answer,
    e.keywords,
    e.related_commands,
    e.priority,
    c.name as category,
    c.display_name as category_display_name,
    c.icon as category_icon,
    e.created_at,
    e.updated_at
FROM knowledge_entries e
INNER JOIN knowledge_categories c ON e.category_id = c.id
WHERE e.active = 1 AND c.active = 1;
GO

PRINT 'Vista vw_knowledge_base creada exitosamente';
GO

-- ============================================================================
-- 6. Procedimiento almacenado para búsqueda
-- ============================================================================

IF OBJECT_ID('sp_search_knowledge', 'P') IS NOT NULL
    DROP PROCEDURE sp_search_knowledge;
GO

CREATE PROCEDURE sp_search_knowledge
    @query NVARCHAR(500),
    @category VARCHAR(50) = NULL,
    @top_k INT = 3,
    @min_priority INT = 1
AS
BEGIN
    SET NOCOUNT ON;

    SELECT TOP (@top_k)
        e.id,
        e.question,
        e.answer,
        e.keywords,
        e.related_commands,
        e.priority,
        c.name as category,
        c.display_name as category_display_name,
        c.icon as category_icon,
        -- Score simple basado en prioridad
        CASE
            WHEN e.priority = 3 THEN 1.5
            WHEN e.priority = 2 THEN 1.2
            ELSE 1.0
        END as score
    FROM knowledge_entries e
    INNER JOIN knowledge_categories c ON e.category_id = c.id
    WHERE
        e.active = 1
        AND c.active = 1
        AND e.priority >= @min_priority
        AND (@category IS NULL OR c.name = @category)
        AND (
            e.question LIKE '%' + @query + '%'
            OR e.answer LIKE '%' + @query + '%'
            OR e.keywords LIKE '%' + @query + '%'
        )
    ORDER BY
        e.priority DESC,
        LEN(e.question) ASC; -- Preguntas más cortas primero
END
GO

PRINT 'Procedimiento sp_search_knowledge creado exitosamente';
GO

-- ============================================================================
-- Resumen de migración
-- ============================================================================

PRINT '';
PRINT '============================================================================';
PRINT 'Migración 001 completada exitosamente';
PRINT '============================================================================';
PRINT 'Base de datos: abcmasplus';
PRINT '';
PRINT 'Tablas creadas:';
PRINT '  - knowledge_categories';
PRINT '  - knowledge_entries';
PRINT '  - table_documentation';
PRINT '  - column_documentation';
PRINT '';
PRINT 'Vistas creadas:';
PRINT '  - vw_knowledge_base';
PRINT '';
PRINT 'Procedimientos creados:';
PRINT '  - sp_search_knowledge';
PRINT '';
PRINT 'Siguiente paso: Ejecutar 002_seed_knowledge_base.sql';
PRINT '============================================================================';
