-- ============================================================
-- Migración 012: Fix — descripción del agente alertas para mejor routing
--
-- Problema: El intent classifier no enruta "con quien reporto",
-- "quién atiende", "a quién escalo" al agente alertas porque la
-- descripción no cubre esas frases.
--
-- Solución: Ampliar descripcion con términos de escalamiento y
-- responsables, e incrementar version para invalidar cache.
-- ============================================================

USE abcmasplus;
GO

UPDATE abcmasplus..BotIAv2_AgenteDef
SET
    descripcion = N'Especialista en monitoreo PRTG. Maneja consultas sobre: '
        + N'alertas activas, equipos caídos, sensores en Down/Warning, '
        + N'quién atiende o es responsable de un equipo, con quién reportar una alerta, '
        + N'a quién escalar un incidente, contactos de área, matriz de escalamiento, '
        + N'historial de tickets de un nodo, análisis de incidentes de red e infraestructura.',
    version = version + 1
WHERE nombre = 'alertas';

IF @@ROWCOUNT = 0
    PRINT 'ADVERTENCIA: No se encontró el agente alertas.';
ELSE
    PRINT 'OK: Descripción del agente alertas actualizada para mejor routing.';
GO

-- Verificar
SELECT nombre, descripcion, version
FROM abcmasplus..BotIAv2_AgenteDef
WHERE nombre = 'alertas';
GO
