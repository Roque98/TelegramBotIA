-- ============================================================================
-- Script: Pre-Migración SEC-01 — Verificación antes de crear BotPermisos
-- Base de Datos: abcmasplus
-- Descripción: Verifica que la BD está en estado correcto antes de migrar
-- ============================================================================

USE abcmasplus;
GO

PRINT '============================================================================';
PRINT 'PRE-MIGRACIÓN SEC-01: Verificaciones';
PRINT '============================================================================';

-- 1. Usuarios activos sin gerencia asignada
--    (válido — solo tendrán permisos via autenticado, sin gerencia)
PRINT '';
PRINT '1. Usuarios activos sin gerencia asignada:';
SELECT
    u.idUsuario,
    u.Nombre,
    r.nombre AS rol
FROM abcmasplus..Usuarios u
INNER JOIN abcmasplus..Roles r ON u.idRol = r.idRol
WHERE u.activo = 1
  AND NOT EXISTS (
      SELECT 1 FROM abcmasplus..GerenciasUsuarios gu
      WHERE gu.idUsuario = u.idUsuario AND gu.activo = 1
  )
ORDER BY u.Nombre;

-- 2. Roles en uso que deben estar cubiertos por datos iniciales
--    Los datos iniciales cubren: 1,2,3,4,5,6,7,8
--    Si aparece algún idRol fuera de ese rango, hay que agregarlo al script 11
PRINT '';
PRINT '2. Roles en uso por usuarios activos (deben estar en datos iniciales):';
SELECT DISTINCT
    r.idRol,
    r.nombre,
    COUNT(u.idUsuario) AS totalUsuarios
FROM abcmasplus..Usuarios u
INNER JOIN abcmasplus..Roles r ON u.idRol = r.idRol
WHERE u.activo = 1
GROUP BY r.idRol, r.nombre
ORDER BY r.idRol;

-- 3. Verificar que las tablas legacy existen (para el DROP posterior en Fase 6)
PRINT '';
PRINT '3. Tablas legacy a eliminar en Fase 6:';
SELECT
    v.nombre AS tabla,
    CASE WHEN t.name IS NOT NULL THEN 'EXISTS' ELSE 'NOT FOUND' END AS estado
FROM (VALUES
    ('RolesOperaciones'),
    ('OperacionesIA'),
    ('PerfilOperacion'),
    ('RolesIA'),
    ('GerenciasRolesIA')
) AS v(nombre)
LEFT JOIN sys.objects t ON t.name = v.nombre AND t.type = 'U';

PRINT '';
PRINT 'Pre-migración completada. Revisar resultados antes de continuar.';
GO
