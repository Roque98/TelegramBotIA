-- ============================================================================
-- Script: 002_create_user_memory_profiles.sql
-- Descripción: Crear tabla de perfiles de memoria persistente para usuarios
-- Autor: Sistema de Memoria Persistente
-- Fecha: 2025-12-29
-- ============================================================================

USE [abcmasplus];
GO

-- ============================================================================
-- Tabla: UserMemoryProfiles
-- Descripción: Almacena perfiles de memoria con resúmenes narrativos de las
--              interacciones de cada usuario para personalizar las respuestas
-- ============================================================================

CREATE TABLE [dbo].[UserMemoryProfiles] (
    -- Identificación
    [idMemoryProfile] INT IDENTITY(1,1) NOT NULL,
    [idUsuario] INT NOT NULL,

    -- Resúmenes narrativos (texto legible para inyectar en prompts)
    [resumenContextoLaboral] NVARCHAR(MAX) NULL,
    -- Ejemplo: "Juan es Analista de Datos en la Gerencia de Tecnología.
    -- Actualmente trabaja en el proyecto de Dashboard de Ventas Q4 y la
    -- migración de base de datos. Usa principalmente SQL Server, Python y Power BI."

    [resumenTemasRecientes] NVARCHAR(MAX) NULL,
    -- Ejemplo: "En los últimos días, Juan ha consultado frecuentemente sobre
    -- reportes de ventas del Q4 (5 veces), optimización de queries SQL (3 veces)
    -- y desarrollo de dashboards en Power BI (2 veces)."

    [resumenHistorialBreve] NVARCHAR(MAX) NULL,
    -- Ejemplo: "Ha resuelto problemas de performance en consultas SQL y
    -- ha trabajado en la automatización de reportes mensuales."

    -- Metadata
    [numInteracciones] INT NOT NULL DEFAULT 0,
    [ultimaActualizacion] DATETIME2 NOT NULL DEFAULT GETDATE(),
    [fechaCreacion] DATETIME2 NOT NULL DEFAULT GETDATE(),
    [version] INT NOT NULL DEFAULT 1,

    -- Constraints
    CONSTRAINT [PK_UserMemoryProfiles] PRIMARY KEY CLUSTERED ([idMemoryProfile] ASC),
    CONSTRAINT [FK_UserMemoryProfiles_Usuarios] FOREIGN KEY ([idUsuario])
        REFERENCES [dbo].[Usuarios]([idUsuario]) ON DELETE CASCADE,
    CONSTRAINT [UQ_UserMemoryProfiles_Usuario] UNIQUE ([idUsuario])
);
GO

-- ============================================================================
-- Índices
-- ============================================================================

-- Índice para búsqueda por usuario (principal)
CREATE NONCLUSTERED INDEX [IX_UserMemoryProfiles_Usuario]
    ON [dbo].[UserMemoryProfiles]([idUsuario]);
GO

-- Índice para monitoreo de actualizaciones
CREATE NONCLUSTERED INDEX [IX_UserMemoryProfiles_UltimaActualizacion]
    ON [dbo].[UserMemoryProfiles]([ultimaActualizacion] DESC);
GO

-- ============================================================================
-- Verificación
-- ============================================================================

PRINT '✅ Tabla UserMemoryProfiles creada exitosamente';

-- Mostrar estructura de la tabla
SELECT
    COLUMN_NAME AS 'Columna',
    DATA_TYPE AS 'Tipo',
    IS_NULLABLE AS 'Nullable',
    CHARACTER_MAXIMUM_LENGTH AS 'Max Length'
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_NAME = 'UserMemoryProfiles'
ORDER BY ORDINAL_POSITION;
GO
