-- ============================================================
-- Migration 20: DROP Stored Procedures de permisos legacy
-- ============================================================
-- Ejecutar SOLO después de:
--   - Verificar que no haya consumidores externos (reportes, otros sistemas)
--   - Confirmar que los nuevos BotPermisos cubren todos los casos
--   - Ejecutar y validar en staging primero
-- ============================================================
-- Idempotente: se puede re-ejecutar sin error
-- ============================================================

USE abcmasplus;
GO

-- ---- sp_VerificarPermisoOperacion ----
IF OBJECT_ID('abcmasplus..sp_VerificarPermisoOperacion', 'P') IS NOT NULL
BEGIN
    DROP PROCEDURE abcmasplus..sp_VerificarPermisoOperacion;
    PRINT 'Dropped: sp_VerificarPermisoOperacion';
END
ELSE
    PRINT 'Skip (not found): sp_VerificarPermisoOperacion';
GO

-- ---- sp_ObtenerOperacionesUsuario ----
IF OBJECT_ID('abcmasplus..sp_ObtenerOperacionesUsuario', 'P') IS NOT NULL
BEGIN
    DROP PROCEDURE abcmasplus..sp_ObtenerOperacionesUsuario;
    PRINT 'Dropped: sp_ObtenerOperacionesUsuario';
END
ELSE
    PRINT 'Skip (not found): sp_ObtenerOperacionesUsuario';
GO

-- ---- Verificación post-drop ----
SELECT
    name,
    type_desc,
    create_date,
    modify_date
FROM sys.procedures
WHERE name IN (
    'sp_VerificarPermisoOperacion',
    'sp_ObtenerOperacionesUsuario'
);
-- Debe retornar 0 filas
GO
