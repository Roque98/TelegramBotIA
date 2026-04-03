-- ============================================================
-- Migration 21: DROP Tablas legacy de permisos
-- ============================================================
-- Tablas a eliminar (confirmadas en pre-migración, script 09):
--   - RolesOperaciones   (roles + permisos de operaciones legacy)
--   - RolesIA            (sistema paralelo de roles IA, nunca integrado)
--   - GerenciasRolesIA   (gerencias asociadas a RolesIA, nunca integrado)
--
-- Tablas NO dropeadas (no existen en BD, verificado en script 09):
--   - OperacionesIA      → no existe, ignorar
--   - PerfilOperacion    → no existe, ignorar
--
-- PRECAUCIONES:
--   1. Verificar FKs activas antes de ejecutar (query incluida abajo)
--   2. Archivar data histórica si aplica
--   3. Confirmar en staging antes de prod
--   4. LogOperaciones NO depende de estas tablas (verificado)
-- ============================================================
-- Idempotente: se puede re-ejecutar sin error
-- ============================================================

USE abcmasplus;
GO

-- ---- PASO 0: Verificar FKs activas (revisar output antes de continuar) ----
SELECT
    fk.name                      AS fk_name,
    tp.name                      AS parent_table,
    tr.name                      AS referenced_table,
    cp.name                      AS parent_column,
    cr.name                      AS referenced_column
FROM sys.foreign_keys fk
INNER JOIN sys.tables tp  ON fk.parent_object_id = tp.object_id
INNER JOIN sys.tables tr  ON fk.referenced_object_id = tr.object_id
INNER JOIN sys.foreign_key_columns fkc ON fk.object_id = fkc.constraint_object_id
INNER JOIN sys.columns cp ON fkc.parent_object_id = cp.object_id AND fkc.parent_column_id = cp.column_id
INNER JOIN sys.columns cr ON fkc.referenced_object_id = cr.object_id AND fkc.referenced_column_id = cr.column_id
WHERE tr.name IN ('RolesOperaciones', 'RolesIA', 'GerenciasRolesIA')
   OR tp.name IN ('RolesOperaciones', 'RolesIA', 'GerenciasRolesIA');
-- Si retorna filas: drop las FKs primero o ajustar el orden de drops
GO

-- ---- PASO 1: GerenciasRolesIA (depende de RolesIA) ----
IF OBJECT_ID('abcmasplus..GerenciasRolesIA', 'U') IS NOT NULL
BEGIN
    DROP TABLE abcmasplus..GerenciasRolesIA;
    PRINT 'Dropped: GerenciasRolesIA';
END
ELSE
    PRINT 'Skip (not found): GerenciasRolesIA';
GO

-- ---- PASO 2: RolesIA ----
IF OBJECT_ID('abcmasplus..RolesIA', 'U') IS NOT NULL
BEGIN
    DROP TABLE abcmasplus..RolesIA;
    PRINT 'Dropped: RolesIA';
END
ELSE
    PRINT 'Skip (not found): RolesIA';
GO

-- ---- PASO 3: RolesOperaciones ----
IF OBJECT_ID('abcmasplus..RolesOperaciones', 'U') IS NOT NULL
BEGIN
    DROP TABLE abcmasplus..RolesOperaciones;
    PRINT 'Dropped: RolesOperaciones';
END
ELSE
    PRINT 'Skip (not found): RolesOperaciones';
GO

-- ---- Verificación post-drop ----
SELECT
    name,
    type_desc,
    create_date
FROM sys.tables
WHERE name IN ('RolesOperaciones', 'RolesIA', 'GerenciasRolesIA');
-- Debe retornar 0 filas

-- Confirmar que LogOperaciones sigue existiendo (no debe haber sido afectada)
SELECT name FROM sys.tables WHERE name = 'LogOperaciones';
-- Debe retornar 1 fila
GO
