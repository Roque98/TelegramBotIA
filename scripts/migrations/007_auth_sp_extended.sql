-- ============================================================
-- Migración 007: SPs extendidos de auth (memoria, preferencias, costos, observabilidad)
-- Complementa migración 006 cubriendo los repositorios restantes que
-- referencian Usuarios, Roles, GerenciasUsuarios o BotIAv2_UsuariosTelegram.
-- BD destino: abcmasplus
-- ============================================================

-- ============================================================
-- 1. BotIAv2_sp_GetPerfilMemoria
--    Reemplaza: memory_repository.get_profile
--    Retorna perfil completo con datos de memoria (UserMemoryProfiles)
-- ============================================================
CREATE OR ALTER PROCEDURE abcmasplus..BotIAv2_sp_GetPerfilMemoria
    @telegramChatId BIGINT
AS
BEGIN
    SET NOCOUNT ON;
    SELECT
        u.idUsuario                     AS Id_Usuario,
        u.Nombre                        AS Nombre,
        u.idRol                         AS role_id,
        r.nombre                        AS role_name,
        STUFF((
            SELECT ',' + CAST(gu.idGerencia AS VARCHAR)
            FROM abcmasplus..GerenciasUsuarios gu
            WHERE gu.idUsuario = u.idUsuario
            FOR XML PATH('')
        ), 1, 1, '')                    AS gerencia_ids_csv,
        ump.resumenContextoLaboral      AS resumen_contexto_laboral,
        ump.resumenTemasRecientes       AS resumen_temas_recientes,
        ump.resumenHistorialBreve       AS resumen_historial_breve,
        ump.numInteracciones            AS num_interacciones,
        ump.ultimaActualizacion         AS ultima_actualizacion,
        ump.preferencias                AS preferencias
    FROM abcmasplus..BotIAv2_UsuariosTelegram ut
    INNER JOIN abcmasplus..Usuarios              u   ON ut.idUsuario  = u.idUsuario
    LEFT  JOIN abcmasplus..Roles                 r   ON u.idRol       = r.idRol
    LEFT  JOIN abcmasplus..BotIAv2_UserMemoryProfiles ump ON u.idUsuario = ump.idUsuario
    WHERE ut.telegramChatId = @telegramChatId
      AND ut.activo = 1;
END;
GO

-- ============================================================
-- 2. BotIAv2_sp_GetMensajesRecientes
--    Reemplaza: memory_repository.get_recent_messages
-- ============================================================
CREATE OR ALTER PROCEDURE abcmasplus..BotIAv2_sp_GetMensajesRecientes
    @telegramChatId BIGINT,
    @limit          INT = 20
AS
BEGIN
    SET NOCOUNT ON;
    SELECT TOP (@limit)
        il.query            AS user_query,
        il.respuesta        AS respuesta,
        il.fechaEjecucion   AS fecha
    FROM abcmasplus..BotIAv2_InteractionLogs il
    INNER JOIN abcmasplus..BotIAv2_UsuariosTelegram ut ON il.idUsuario = ut.idUsuario
    WHERE ut.telegramChatId = @telegramChatId
      AND ut.activo = 1
      AND il.mensajeError IS NULL
    ORDER BY il.fechaEjecucion DESC;
END;
GO

-- ============================================================
-- 3. BotIAv2_sp_GetEstadisticasUsuario
--    Reemplaza: memory_repository.get_user_stats
-- ============================================================
CREATE OR ALTER PROCEDURE abcmasplus..BotIAv2_sp_GetEstadisticasUsuario
    @telegramChatId BIGINT
AS
BEGIN
    SET NOCOUNT ON;
    SELECT
        COUNT(*)                                                        AS total,
        SUM(CASE WHEN il.mensajeError IS NULL     THEN 1 ELSE 0 END)   AS exitosos,
        SUM(CASE WHEN il.mensajeError IS NOT NULL THEN 1 ELSE 0 END)   AS errores,
        AVG(CAST(il.duracionMs AS FLOAT))                              AS avg_ms,
        MAX(il.duracionMs)                                             AS max_ms,
        MIN(il.fechaEjecucion)                                         AS primera,
        MAX(il.fechaEjecucion)                                         AS ultima
    FROM abcmasplus..BotIAv2_InteractionLogs il
    INNER JOIN abcmasplus..BotIAv2_UsuariosTelegram ut ON il.idUsuario = ut.idUsuario
    WHERE ut.telegramChatId = @telegramChatId
      AND ut.activo = 1;
END;
GO

-- ============================================================
-- 4. BotIAv2_sp_GetPreferenciasUsuario
--    Reemplaza: preference_tool.py — query GET de preferencias
-- ============================================================
CREATE OR ALTER PROCEDURE abcmasplus..BotIAv2_sp_GetPreferenciasUsuario
    @telegramChatId BIGINT
AS
BEGIN
    SET NOCOUNT ON;
    SELECT ump.preferencias
    FROM abcmasplus..BotIAv2_UserMemoryProfiles ump
    INNER JOIN abcmasplus..BotIAv2_UsuariosTelegram ut ON ump.idUsuario = ut.idUsuario
    WHERE ut.telegramChatId = @telegramChatId
      AND ut.activo = 1;
END;
GO

-- ============================================================
-- 5. BotIAv2_sp_GuardarPreferenciasUsuario
--    Reemplaza: preference_tool.py — UPDATE + INSERT de preferencias (upsert)
-- ============================================================
CREATE OR ALTER PROCEDURE abcmasplus..BotIAv2_sp_GuardarPreferenciasUsuario
    @telegramChatId BIGINT,
    @preferencias   NVARCHAR(MAX)
AS
BEGIN
    SET NOCOUNT ON;

    UPDATE ump
    SET    ump.preferencias       = @preferencias,
           ump.ultimaActualizacion = GETDATE()
    FROM   abcmasplus..BotIAv2_UserMemoryProfiles ump
    INNER JOIN abcmasplus..BotIAv2_UsuariosTelegram ut ON ump.idUsuario = ut.idUsuario
    WHERE  ut.telegramChatId = @telegramChatId
      AND  ut.activo = 1;

    IF @@ROWCOUNT = 0
    BEGIN
        INSERT INTO abcmasplus..BotIAv2_UserMemoryProfiles (idUsuario, preferencias, numInteracciones)
        SELECT ut.idUsuario, @preferencias, 0
        FROM   abcmasplus..BotIAv2_UsuariosTelegram ut
        WHERE  ut.telegramChatId = @telegramChatId
          AND  ut.activo = 1;
    END

    SELECT @@ROWCOUNT AS filasAfectadas;
END;
GO

-- ============================================================
-- 6. BotIAv2_sp_GetCostosDiarios
--    Reemplaza: cost_repository.get_daily_costs
-- ============================================================
CREATE OR ALTER PROCEDURE abcmasplus..BotIAv2_sp_GetCostosDiarios
    @fecha DATE
AS
BEGIN
    SET NOCOUNT ON;
    SELECT
        cs.telegramChatId                                           AS chat_id,
        COALESCE(u.Nombre, ut.telegramUsername, 'Desconocido')     AS nombre,
        COUNT(*)                                                    AS sesiones,
        SUM(cs.llamadasLLM)                                        AS llamadas,
        SUM(cs.inputTokens)                                        AS input_tokens,
        SUM(cs.outputTokens)                                       AS output_tokens,
        SUM(cs.costoUSD)                                           AS costo_usd
    FROM abcmasplus..BotIAv2_CostSesiones cs
    LEFT JOIN abcmasplus..BotIAv2_UsuariosTelegram ut ON cs.telegramChatId = ut.telegramChatId
    LEFT JOIN abcmasplus..Usuarios u ON ut.idUsuario = u.idUsuario
    WHERE cs.fechaSesion >= @fecha
    GROUP BY cs.telegramChatId, u.Nombre, ut.telegramUsername
    ORDER BY costo_usd DESC;
END;
GO

-- ============================================================
-- 7. BotIAv2_sp_GuardarInteraccion
--    Reemplaza: sql_repository.save_interaction
--    Resuelve idUsuario desde telegramChatId internamente
-- ============================================================
CREATE OR ALTER PROCEDURE abcmasplus..BotIAv2_sp_GuardarInteraccion
    @correlationId      NVARCHAR(100),
    @telegramChatId     BIGINT,
    @telegramUsername   NVARCHAR(100)  = NULL,
    @query              NVARCHAR(MAX)  = NULL,
    @respuesta          NVARCHAR(MAX)  = NULL,
    @mensajeError       NVARCHAR(MAX)  = NULL,
    @toolsUsadas        NVARCHAR(MAX)  = NULL,
    @stepsTomados       INT            = 0,
    @memoryMs           INT            = NULL,
    @reactMs            INT            = NULL,
    @saveMs             INT            = NULL,
    @duracionMs         INT            = NULL,
    @channel            NVARCHAR(50)   = 'telegram',
    @agenteNombre       NVARCHAR(100)  = NULL,
    @totalInputTokens   INT            = 0,
    @totalOutputTokens  INT            = 0,
    @llmIteraciones     INT            = 0,
    @usedFallback       BIT            = 0,
    @classifyMs         INT            = NULL,
    @agentConfidence    FLOAT          = NULL,
    @costUSD            DECIMAL(18,8)  = 0
AS
BEGIN
    SET NOCOUNT ON;

    DECLARE @idUsuario INT;
    SELECT TOP 1 @idUsuario = idUsuario
    FROM abcmasplus..BotIAv2_UsuariosTelegram
    WHERE telegramChatId = @telegramChatId AND activo = 1;

    DECLARE @exitoso BIT = CASE WHEN @mensajeError IS NULL THEN 1 ELSE 0 END;

    INSERT INTO abcmasplus..BotIAv2_InteractionLogs (
        correlationId, idUsuario, telegramChatId, telegramUsername,
        comando, query, respuesta, mensajeError,
        toolsUsadas, stepsTomados,
        memoryMs, reactMs, saveMs, duracionMs, channel, exitoso,
        agenteNombre,
        totalInputTokens, totalOutputTokens, llmIteraciones,
        usedFallback, classifyMs, agentConfidence, costUSD
    ) VALUES (
        @correlationId, @idUsuario, @telegramChatId, @telegramUsername,
        '/ia', @query, @respuesta, @mensajeError,
        @toolsUsadas, @stepsTomados,
        @memoryMs, @reactMs, @saveMs, @duracionMs, @channel, @exitoso,
        @agenteNombre,
        @totalInputTokens, @totalOutputTokens, @llmIteraciones,
        @usedFallback, @classifyMs, @agentConfidence, @costUSD
    );
END;
GO

-- ============================================================
-- Verificación
-- ============================================================
SELECT name, create_date
FROM sys.procedures
WHERE name LIKE 'BotIAv2_sp_%'
ORDER BY name;
