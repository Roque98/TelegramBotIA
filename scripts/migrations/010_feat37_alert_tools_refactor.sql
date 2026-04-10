-- ============================================================
-- Migración 010: FEAT-37 — Refactor alert tools (4 tools estructuradas)
--
-- Prerequisitos:
--   - Migración 008 ejecutada (agente 'alertas' existe)
--   - Migración 009 ejecutada (system prompt v1 corregido)
--
-- Qué hace:
--   1. Registra las 4 tools nuevas en BotIAv2_Recurso
--   2. Asigna permisos por rol para cada tool nueva
--   3. Actualiza scope del agente alertas:
--      - Agrega las 4 tools nuevas a BotIAv2_AgenteTools
--      - Desactiva alert_analysis del scope del agente
--   4. Actualiza system prompt del agente alertas (datos estructurados)
--   5. Desactiva tool:alert_analysis en BotIAv2_Recurso
--
-- Idempotente — se puede ejecutar más de una vez sin problema.
-- ============================================================

USE abcmasplus;
GO

-- ── 1. Registrar las 4 tools nuevas en BotIAv2_Recurso ──────────────────────
IF NOT EXISTS (SELECT 1 FROM abcmasplus..BotIAv2_Recurso WHERE recurso = 'tool:get_active_alerts')
    INSERT INTO abcmasplus..BotIAv2_Recurso (recurso, tipoRecurso, descripcion, esPublico, activo)
    VALUES ('tool:get_active_alerts', 'tool',
            'Lista alertas activas de PRTG con filtros opcionales por IP, equipo o solo equipos caídos', 0, 1);

IF NOT EXISTS (SELECT 1 FROM abcmasplus..BotIAv2_Recurso WHERE recurso = 'tool:get_historical_tickets')
    INSERT INTO abcmasplus..BotIAv2_Recurso (recurso, tipoRecurso, descripcion, esPublico, activo)
    VALUES ('tool:get_historical_tickets', 'tool',
            'Retorna tickets históricos de un nodo/IP de monitoreo PRTG', 0, 1);

IF NOT EXISTS (SELECT 1 FROM abcmasplus..BotIAv2_Recurso WHERE recurso = 'tool:get_escalation_matrix')
    INSERT INTO abcmasplus..BotIAv2_Recurso (recurso, tipoRecurso, descripcion, esPublico, activo)
    VALUES ('tool:get_escalation_matrix', 'tool',
            'Retorna la matriz de escalamiento (niveles, contactos) para un equipo por IP', 0, 1);

IF NOT EXISTS (SELECT 1 FROM abcmasplus..BotIAv2_Recurso WHERE recurso = 'tool:get_alert_detail')
    INSERT INTO abcmasplus..BotIAv2_Recurso (recurso, tipoRecurso, descripcion, esPublico, activo)
    VALUES ('tool:get_alert_detail', 'tool',
            'Retorna contexto completo de una alerta: tickets históricos, template, escalamiento y contactos', 0, 1);
GO

-- ── 2. Permisos por rol para las 4 tools nuevas ─────────────────────────────
-- INNER JOIN con abcmasplus..Roles garantiza que solo se insertan roles que existen.
DECLARE @idTipoEntidad INT = (SELECT idTipoEntidad FROM abcmasplus..BotIAv2_TipoEntidad WHERE nombre = 'autenticado');

-- get_active_alerts
DECLARE @idR1 INT = (SELECT idRecurso FROM abcmasplus..BotIAv2_Recurso WHERE recurso = 'tool:get_active_alerts');
INSERT INTO abcmasplus..BotIAv2_Permisos (idTipoEntidad, idEntidad, idRecurso, idRolRequerido, permitido, activo)
SELECT @idTipoEntidad, 0, @idR1, r.idRol, 1, 1
FROM (VALUES (1),(2),(3),(4),(7),(8)) AS roles(idRol)
INNER JOIN abcmasplus..Roles r ON r.idRol = roles.idRol
WHERE NOT EXISTS (
    SELECT 1 FROM abcmasplus..BotIAv2_Permisos
    WHERE idRecurso = @idR1 AND idRolRequerido = r.idRol AND activo = 1
);

-- get_historical_tickets
DECLARE @idR2 INT = (SELECT idRecurso FROM abcmasplus..BotIAv2_Recurso WHERE recurso = 'tool:get_historical_tickets');
INSERT INTO abcmasplus..BotIAv2_Permisos (idTipoEntidad, idEntidad, idRecurso, idRolRequerido, permitido, activo)
SELECT @idTipoEntidad, 0, @idR2, r.idRol, 1, 1
FROM (VALUES (1),(2),(3),(4),(7),(8)) AS roles(idRol)
INNER JOIN abcmasplus..Roles r ON r.idRol = roles.idRol
WHERE NOT EXISTS (
    SELECT 1 FROM abcmasplus..BotIAv2_Permisos
    WHERE idRecurso = @idR2 AND idRolRequerido = r.idRol AND activo = 1
);

-- get_escalation_matrix
DECLARE @idR3 INT = (SELECT idRecurso FROM abcmasplus..BotIAv2_Recurso WHERE recurso = 'tool:get_escalation_matrix');
INSERT INTO abcmasplus..BotIAv2_Permisos (idTipoEntidad, idEntidad, idRecurso, idRolRequerido, permitido, activo)
SELECT @idTipoEntidad, 0, @idR3, r.idRol, 1, 1
FROM (VALUES (1),(2),(3),(4),(7),(8)) AS roles(idRol)
INNER JOIN abcmasplus..Roles r ON r.idRol = roles.idRol
WHERE NOT EXISTS (
    SELECT 1 FROM abcmasplus..BotIAv2_Permisos
    WHERE idRecurso = @idR3 AND idRolRequerido = r.idRol AND activo = 1
);

-- get_alert_detail
DECLARE @idR4 INT = (SELECT idRecurso FROM abcmasplus..BotIAv2_Recurso WHERE recurso = 'tool:get_alert_detail');
INSERT INTO abcmasplus..BotIAv2_Permisos (idTipoEntidad, idEntidad, idRecurso, idRolRequerido, permitido, activo)
SELECT @idTipoEntidad, 0, @idR4, r.idRol, 1, 1
FROM (VALUES (1),(2),(3),(4),(7),(8)) AS roles(idRol)
INNER JOIN abcmasplus..Roles r ON r.idRol = roles.idRol
WHERE NOT EXISTS (
    SELECT 1 FROM abcmasplus..BotIAv2_Permisos
    WHERE idRecurso = @idR4 AND idRolRequerido = r.idRol AND activo = 1
);
GO

-- ── 3. Actualizar scope del agente alertas ───────────────────────────────────
DECLARE @idAgente INT = (SELECT idAgente FROM abcmasplus..BotIAv2_AgenteDef WHERE nombre = 'alertas');

-- Agregar las 4 tools nuevas al scope (si no existen)
IF @idAgente IS NOT NULL BEGIN
    IF NOT EXISTS (SELECT 1 FROM abcmasplus..BotIAv2_AgenteTools WHERE idAgente = @idAgente AND nombreTool = 'get_active_alerts')
        INSERT INTO abcmasplus..BotIAv2_AgenteTools (idAgente, nombreTool, activo) VALUES (@idAgente, 'get_active_alerts', 1);

    IF NOT EXISTS (SELECT 1 FROM abcmasplus..BotIAv2_AgenteTools WHERE idAgente = @idAgente AND nombreTool = 'get_historical_tickets')
        INSERT INTO abcmasplus..BotIAv2_AgenteTools (idAgente, nombreTool, activo) VALUES (@idAgente, 'get_historical_tickets', 1);

    IF NOT EXISTS (SELECT 1 FROM abcmasplus..BotIAv2_AgenteTools WHERE idAgente = @idAgente AND nombreTool = 'get_escalation_matrix')
        INSERT INTO abcmasplus..BotIAv2_AgenteTools (idAgente, nombreTool, activo) VALUES (@idAgente, 'get_escalation_matrix', 1);

    IF NOT EXISTS (SELECT 1 FROM abcmasplus..BotIAv2_AgenteTools WHERE idAgente = @idAgente AND nombreTool = 'get_alert_detail')
        INSERT INTO abcmasplus..BotIAv2_AgenteTools (idAgente, nombreTool, activo) VALUES (@idAgente, 'get_alert_detail', 1);

    -- Desactivar alert_analysis del scope del agente
    UPDATE abcmasplus..BotIAv2_AgenteTools
    SET activo = 0
    WHERE idAgente = @idAgente AND nombreTool = 'alert_analysis';
END
GO

-- ── 4. Actualizar system prompt del agente alertas ───────────────────────────
UPDATE abcmasplus..BotIAv2_AgenteDef
SET
    systemPrompt = N'Eres Iris, asistente de operaciones TI especializado en monitoreo de infraestructura PRTG.

## Herramientas disponibles
{tools_description}

- **finish**: Entrega la respuesta final al usuario.
  Parameters: {{"thought": "...", "action": "finish", "action_input": {{}}, "final_answer": "[respuesta Markdown]"}}

## Cuándo usar cada tool

- **get_active_alerts**: "¿hay alertas?", "¿qué equipos están caídos?", "alertas activas"
- **get_alert_detail**: "dame el detalle de X", "analiza la alerta de 10.x.x.x", detalle completo de un equipo
- **get_historical_tickets**: "¿qué incidentes ha tenido este equipo?", historial de tickets de un nodo
- **get_escalation_matrix**: "¿a quién escalo esto?", "¿quién atiende X?", contactos de escalamiento

## Reglas

- Llama cada tool UNA SOLA VEZ. No repitas llamadas con los mismos parámetros.
- Para "dame el detalle de la alerta más crítica": primero get_active_alerts, luego get_alert_detail con la IP del primero.
- Formatea la respuesta en Markdown con los datos recibidos — usa negritas, listas y emojis relevantes.
- No inventes IPs, equipos, contactos ni tickets. Usa solo los datos que retornan las tools.
- Si no hay alertas o no hay datos, indícalo claramente al usuario.

## Formato de respuesta (SIEMPRE JSON)

Llamada a tool:
{{"thought": "El usuario pregunta por alertas activas.", "action": "get_active_alerts", "action_input": {{"solo_down": true}}, "final_answer": null}}

Respuesta final (después de recibir datos):
{{"thought": "Tengo los datos. Genero respuesta formateada.", "action": "finish", "action_input": {{}}, "final_answer": "[respuesta Markdown con los datos recibidos]"}}',
    maxIteraciones = 5,
    version       = version + 1
WHERE nombre = 'alertas';

IF @@ROWCOUNT = 0
    PRINT 'ADVERTENCIA: No se encontró el agente alertas.';
ELSE
    PRINT 'OK: System prompt del agente alertas actualizado a tools estructuradas.';
GO

-- ── 5. Desactivar tool:alert_analysis en BotIAv2_Recurso ────────────────────
UPDATE abcmasplus..BotIAv2_Recurso
SET activo = 0
WHERE recurso = 'tool:alert_analysis';
PRINT 'OK: tool:alert_analysis desactivada en BotIAv2_Recurso.';
GO

-- ── Verificación ─────────────────────────────────────────────────────────────
SELECT 'BotIAv2_Recurso' AS tabla, recurso, activo
FROM abcmasplus..BotIAv2_Recurso
WHERE recurso IN ('tool:get_active_alerts','tool:get_historical_tickets',
                  'tool:get_escalation_matrix','tool:get_alert_detail',
                  'tool:alert_analysis')
ORDER BY recurso;

SELECT 'BotIAv2_AgenteTools' AS tabla, ad.nombre AS agente, at.nombreTool, at.activo
FROM abcmasplus..BotIAv2_AgenteTools at
JOIN abcmasplus..BotIAv2_AgenteDef ad ON at.idAgente = ad.idAgente
WHERE ad.nombre = 'alertas'
ORDER BY at.activo DESC, at.nombreTool;

SELECT 'BotIAv2_AgenteDef' AS tabla, nombre, version, maxIteraciones,
       LEFT(systemPrompt, 100) AS prompt_inicio
FROM abcmasplus..BotIAv2_AgenteDef
WHERE nombre = 'alertas';
GO
