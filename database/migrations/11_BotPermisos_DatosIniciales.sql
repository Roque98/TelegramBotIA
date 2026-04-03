-- ============================================================================
-- Script: SEC-01 — Datos iniciales de BotTipoEntidad, BotRecurso y BotPermisos
-- Base de Datos: abcmasplus
-- Idempotente: usa MERGE para no duplicar si se ejecuta de nuevo
-- ============================================================================

USE abcmasplus;
GO

PRINT '============================================================================';
PRINT 'SEC-01: Insertando datos iniciales';
PRINT '============================================================================';

-- ============================================================================
-- 1. BotTipoEntidad
-- ============================================================================
PRINT '';
PRINT '1. BotTipoEntidad...';

MERGE dbo.BotTipoEntidad AS target
USING (VALUES
    ('usuario',     1, 'definitivo', 'Override individual — pisa todo'),
    ('autenticado', 2, 'permisivo',  'Cualquier usuario autenticado, filtrable por rol'),
    ('gerencia',    3, 'permisivo',  'Gerencia(s) del usuario, filtrable por rol'),
    ('direccion',   4, 'permisivo',  'Dirección del usuario, filtrable por rol')
) AS source (nombre, prioridad, tipoResolucion, descripcion)
ON target.nombre = source.nombre
WHEN NOT MATCHED THEN
    INSERT (nombre, prioridad, tipoResolucion, descripcion)
    VALUES (source.nombre, source.prioridad, source.tipoResolucion, source.descripcion)
WHEN MATCHED THEN
    UPDATE SET
        prioridad      = source.prioridad,
        tipoResolucion = source.tipoResolucion,
        descripcion    = source.descripcion;

PRINT 'BotTipoEntidad: OK';
GO

-- ============================================================================
-- 2. BotRecurso
-- ============================================================================
PRINT '';
PRINT '2. BotRecurso...';

MERGE dbo.BotRecurso AS target
USING (VALUES
    ('tool:database_query',    'tool', 0, 'Consultas SQL a la BD'),
    ('tool:calculate',         'tool', 0, 'Cálculos matemáticos'),
    ('tool:knowledge_search',  'tool', 0, 'Búsqueda en base de conocimiento'),
    ('tool:save_preference',   'tool', 0, 'Guardar preferencias del usuario'),
    ('tool:save_memory',       'tool', 0, 'Guardar notas de sesión'),
    ('tool:datetime',          'tool', 0, 'Consultar fecha y hora'),
    ('tool:reload_permissions','tool', 1, 'Recargar permisos del usuario (siempre disponible)'),
    ('cmd:/ia',                'cmd',  0, 'Comando principal del agente'),
    ('cmd:/start',             'cmd',  1, 'Inicio del bot'),
    ('cmd:/help',              'cmd',  1, 'Ayuda del bot'),
    ('cmd:/costo',             'cmd',  0, 'Ver costos de sesión'),
    ('cmd:/recargar_permisos', 'cmd',  1, 'Recargar permisos del usuario')
) AS source (recurso, tipoRecurso, esPublico, descripcion)
ON target.recurso = source.recurso
WHEN NOT MATCHED THEN
    INSERT (recurso, tipoRecurso, esPublico, descripcion)
    VALUES (source.recurso, source.tipoRecurso, source.esPublico, source.descripcion)
WHEN MATCHED THEN
    UPDATE SET
        tipoRecurso = source.tipoRecurso,
        esPublico   = source.esPublico,
        descripcion = source.descripcion;

PRINT 'BotRecurso: OK';
GO

-- ============================================================================
-- 3. BotPermisos — datos iniciales por rol
-- Roles: 1=Administrador, 2=Gerente, 3=Supervisor, 4=Analista,
--        5=Usuario, 6=Consulta, 7=Coordinador, 8=Especialista
-- ============================================================================
PRINT '';
PRINT '3. BotPermisos...';

-- Helper: obtener IDs una sola vez
DECLARE @tAutenticado INT = (SELECT idTipoEntidad FROM dbo.BotTipoEntidad WHERE nombre = 'autenticado');
DECLARE @tUsuario     INT = (SELECT idTipoEntidad FROM dbo.BotTipoEntidad WHERE nombre = 'usuario');

DECLARE @rDbQuery     INT = (SELECT idRecurso FROM dbo.BotRecurso WHERE recurso = 'tool:database_query');
DECLARE @rCalculate   INT = (SELECT idRecurso FROM dbo.BotRecurso WHERE recurso = 'tool:calculate');
DECLARE @rKnowledge   INT = (SELECT idRecurso FROM dbo.BotRecurso WHERE recurso = 'tool:knowledge_search');
DECLARE @rPref        INT = (SELECT idRecurso FROM dbo.BotRecurso WHERE recurso = 'tool:save_preference');
DECLARE @rMemory      INT = (SELECT idRecurso FROM dbo.BotRecurso WHERE recurso = 'tool:save_memory');
DECLARE @rDatetime    INT = (SELECT idRecurso FROM dbo.BotRecurso WHERE recurso = 'tool:datetime');
DECLARE @rCmdIa       INT = (SELECT idRecurso FROM dbo.BotRecurso WHERE recurso = 'cmd:/ia');
DECLARE @rCmdCosto    INT = (SELECT idRecurso FROM dbo.BotRecurso WHERE recurso = 'cmd:/costo');

-- Construir datos como tabla temporal
CREATE TABLE #PermisosIniciales (
    idTipoEntidad  INT,
    idEntidad      INT,
    idRecurso      INT,
    idRolRequerido INT NULL,
    descripcion    VARCHAR(255)
);

-- Administrador (1): acceso a todo
INSERT INTO #PermisosIniciales VALUES (@tAutenticado, 0, @rDbQuery,   1, 'Administrador - database_query');
INSERT INTO #PermisosIniciales VALUES (@tAutenticado, 0, @rCalculate, 1, 'Administrador - calculate');
INSERT INTO #PermisosIniciales VALUES (@tAutenticado, 0, @rKnowledge, 1, 'Administrador - knowledge_search');
INSERT INTO #PermisosIniciales VALUES (@tAutenticado, 0, @rCmdCosto,  1, 'Administrador - cmd:/costo');

-- Gerente (2): acceso a todo salvo /costo
INSERT INTO #PermisosIniciales VALUES (@tAutenticado, 0, @rDbQuery,   2, 'Gerente - database_query');
INSERT INTO #PermisosIniciales VALUES (@tAutenticado, 0, @rCalculate, 2, 'Gerente - calculate');
INSERT INTO #PermisosIniciales VALUES (@tAutenticado, 0, @rKnowledge, 2, 'Gerente - knowledge_search');

-- Supervisor (3)
INSERT INTO #PermisosIniciales VALUES (@tAutenticado, 0, @rDbQuery,   3, 'Supervisor - database_query');
INSERT INTO #PermisosIniciales VALUES (@tAutenticado, 0, @rCalculate, 3, 'Supervisor - calculate');
INSERT INTO #PermisosIniciales VALUES (@tAutenticado, 0, @rKnowledge, 3, 'Supervisor - knowledge_search');

-- Analista (4)
INSERT INTO #PermisosIniciales VALUES (@tAutenticado, 0, @rDbQuery,   4, 'Analista - database_query');
INSERT INTO #PermisosIniciales VALUES (@tAutenticado, 0, @rCalculate, 4, 'Analista - calculate');
INSERT INTO #PermisosIniciales VALUES (@tAutenticado, 0, @rKnowledge, 4, 'Analista - knowledge_search');

-- Usuario (5)
INSERT INTO #PermisosIniciales VALUES (@tAutenticado, 0, @rCalculate, 5, 'Usuario - calculate');
INSERT INTO #PermisosIniciales VALUES (@tAutenticado, 0, @rKnowledge, 5, 'Usuario - knowledge_search');

-- Consulta (6)
INSERT INTO #PermisosIniciales VALUES (@tAutenticado, 0, @rKnowledge, 6, 'Consulta - knowledge_search');

-- Coordinador (7)
INSERT INTO #PermisosIniciales VALUES (@tAutenticado, 0, @rDbQuery,   7, 'Coordinador - database_query');
INSERT INTO #PermisosIniciales VALUES (@tAutenticado, 0, @rCalculate, 7, 'Coordinador - calculate');
INSERT INTO #PermisosIniciales VALUES (@tAutenticado, 0, @rKnowledge, 7, 'Coordinador - knowledge_search');

-- Especialista (8)
INSERT INTO #PermisosIniciales VALUES (@tAutenticado, 0, @rDbQuery,   8, 'Especialista - database_query');
INSERT INTO #PermisosIniciales VALUES (@tAutenticado, 0, @rCalculate, 8, 'Especialista - calculate');
INSERT INTO #PermisosIniciales VALUES (@tAutenticado, 0, @rKnowledge, 8, 'Especialista - knowledge_search');

-- Todos los roles autenticados: herramientas personales y cmd:/ia
INSERT INTO #PermisosIniciales VALUES (@tAutenticado, 0, @rPref,    NULL, 'Todos - save_preference');
INSERT INTO #PermisosIniciales VALUES (@tAutenticado, 0, @rMemory,  NULL, 'Todos - save_memory');
INSERT INTO #PermisosIniciales VALUES (@tAutenticado, 0, @rDatetime,NULL, 'Todos - datetime');
INSERT INTO #PermisosIniciales VALUES (@tAutenticado, 0, @rCmdIa,   NULL, 'Todos - cmd:/ia');

-- MERGE para que sea idempotente
MERGE dbo.BotPermisos AS target
USING #PermisosIniciales AS source
ON (
    target.idTipoEntidad = source.idTipoEntidad
    AND target.idEntidad = source.idEntidad
    AND target.idRecurso = source.idRecurso
    AND (
        (target.idRolRequerido IS NULL AND source.idRolRequerido IS NULL)
        OR target.idRolRequerido = source.idRolRequerido
    )
)
WHEN NOT MATCHED THEN
    INSERT (idTipoEntidad, idEntidad, idRecurso, idRolRequerido, permitido, descripcion, usuarioCreacion)
    VALUES (source.idTipoEntidad, source.idEntidad, source.idRecurso,
            source.idRolRequerido, 1, source.descripcion, 'SEC-01-migration');

DROP TABLE #PermisosIniciales;

PRINT 'BotPermisos: OK';
GO

PRINT '';
PRINT 'SEC-01 Fase 1b completada: datos iniciales insertados.';
PRINT 'Siguiente paso: ejecutar 12_BotPermisos_Audit.sql';
GO
