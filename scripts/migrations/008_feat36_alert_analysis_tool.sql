-- ============================================================
-- Migración 008: FEAT-36 — Tool de análisis de alertas PRTG
--
-- Prerequisitos:
--   - Migración 005 ejecutada (BotIAv2_Recurso existe)
--   - Migración ARQ-35 ejecutada (BotIAv2_AgenteDef y BotIAv2_AgenteTools existen)
--   - DB_CONNECTIONS=core,monitoreo configurado en .env
--   - Variables DB_MONITOREO_* configuradas en .env
--
-- Qué hace:
--   1. Registra la tool 'alert_analysis' en BotIAv2_Recurso
--   2. Asigna permisos por rol en BotIAv2_Permisos (mismos roles que otras tools)
--   3. Inserta el agente 'alertas' en BotIAv2_AgenteDef
--   4. Asigna la tool alert_analysis al scope del agente en BotIAv2_AgenteTools
--
-- Idempotente — se puede ejecutar más de una vez sin problema.
-- ============================================================

USE abcmasplus;
GO

-- ── 1. Registrar tool en BotIAv2_Recurso ────────────────────────────────────
IF NOT EXISTS (SELECT 1 FROM abcmasplus..BotIAv2_Recurso WHERE recurso = 'tool:alert_analysis')
    INSERT INTO abcmasplus..BotIAv2_Recurso (recurso, tipoRecurso, descripcion, esPublico, activo)
    VALUES (
        'tool:alert_analysis',
        'tool',
        'Análisis de alertas activas PRTG con diagnóstico, acciones recomendadas y matriz de escalamiento',
        0,   -- esPublico=0: requiere autenticación
        1    -- activo=1: habilitada
    );
ELSE
    PRINT 'tool:alert_analysis ya existe en BotIAv2_Recurso';
GO

-- ── 2. Permisos por rol en BotIAv2_Permisos ─────────────────────────────────
-- Mismos roles que las demás tools (1,2,3,4,7,8 = roles de usuarios autenticados).
-- esPublico=0 en Recurso → el sistema verifica permisos antes de ejecutar la tool.
DECLARE @idRecurso     INT = (SELECT idRecurso     FROM abcmasplus..BotIAv2_Recurso    WHERE recurso = 'tool:alert_analysis');
DECLARE @idTipoEntidad INT = (SELECT idTipoEntidad FROM abcmasplus..BotIAv2_TipoEntidad WHERE nombre  = 'autenticado');

INSERT INTO abcmasplus..BotIAv2_Permisos
    (idTipoEntidad, idEntidad, idRecurso, idRolRequerido, permitido, activo)
SELECT @idTipoEntidad, 0, @idRecurso, idRol, 1, 1
FROM (VALUES (1),(2),(3),(4),(7),(8)) AS roles(idRol)
WHERE NOT EXISTS (
    SELECT 1 FROM abcmasplus..BotIAv2_Permisos
    WHERE idRecurso = @idRecurso AND idRolRequerido = roles.idRol AND activo = 1
);
GO

-- ── 3. Insertar agente 'alertas' en BotIAv2_AgenteDef ───────────────────────
IF NOT EXISTS (SELECT 1 FROM abcmasplus..BotIAv2_AgenteDef WHERE nombre = 'alertas')
    INSERT INTO abcmasplus..BotIAv2_AgenteDef (
        nombre,
        descripcion,
        systemPrompt,
        temperatura,
        maxIteraciones,
        modeloOverride,
        esGeneralista,
        activo
    )
    VALUES (
        'alertas',
        'Especialista en monitoreo PRTG. Maneja consultas sobre alertas activas, equipos caídos, '
        'problemas de red/infraestructura, análisis de incidentes y matriz de escalamiento.',
        N'Eres Iris, asistente de operaciones TI especializado en monitoreo de infraestructura PRTG.

Tus capacidades:
{tools_description}

{usage_hints}

Reglas:
- Usa alert_analysis para CUALQUIER consulta sobre alertas, equipos, sensores o incidentes de red.
- Si el usuario filtra por IP o equipo, pasa esos parámetros a la tool.
- Si pregunta solo por equipos caídos, usa solo_down=true.
- Presenta el análisis tal como lo retorna la tool — ya viene formateado en Markdown.
- No inventes datos de equipos ni IPs. Toda la información viene de la tool.',
        0.1,   -- temperatura
        5,     -- maxIteraciones (flujo simple: 1 tool call + finish)
        NULL,  -- modeloOverride: usa openai_loop_model del sistema
        0,     -- esGeneralista=0: agente especialista
        1      -- activo=1
    );
ELSE
    PRINT 'Agente alertas ya existe en BotIAv2_AgenteDef';
GO

-- ── 4. Asignar tool alert_analysis al scope del agente ──────────────────────
DECLARE @idAgente INT = (SELECT idAgente FROM abcmasplus..BotIAv2_AgenteDef WHERE nombre = 'alertas');

IF @idAgente IS NOT NULL AND NOT EXISTS (
    SELECT 1 FROM abcmasplus..BotIAv2_AgenteTools
    WHERE idAgente = @idAgente AND nombreTool = 'alert_analysis'
)
    INSERT INTO abcmasplus..BotIAv2_AgenteTools (idAgente, nombreTool, activo)
    VALUES (@idAgente, 'alert_analysis', 1);
ELSE
    PRINT 'Scope alert_analysis → agente alertas ya existe';
GO

-- ── Verificación ─────────────────────────────────────────────────────────────
SELECT 'BotIAv2_Recurso' AS tabla, recurso, tipoRecurso, esPublico, activo, fechaCreacion
FROM abcmasplus..BotIAv2_Recurso
WHERE recurso = 'tool:alert_analysis';

SELECT 'BotIAv2_Permisos' AS tabla, bp.idRolRequerido, bp.permitido, bp.activo
FROM abcmasplus..BotIAv2_Permisos bp
JOIN abcmasplus..BotIAv2_Recurso br ON bp.idRecurso = br.idRecurso
WHERE br.recurso = 'tool:alert_analysis'
ORDER BY bp.idRolRequerido;

SELECT 'BotIAv2_AgenteDef' AS tabla, idAgente, nombre, descripcion, temperatura, maxIteraciones, esGeneralista, activo
FROM abcmasplus..BotIAv2_AgenteDef
WHERE nombre = 'alertas';

SELECT 'BotIAv2_AgenteTools' AS tabla, at.idAgente, ad.nombre AS agente, at.nombreTool, at.activo
FROM abcmasplus..BotIAv2_AgenteTools at
JOIN abcmasplus..BotIAv2_AgenteDef ad ON at.idAgente = ad.idAgente
WHERE ad.nombre = 'alertas';
GO
