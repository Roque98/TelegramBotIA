-- Migración 005: Registrar todas las tools del catálogo en BotIAv2_Recurso
-- Cada tool debe tener una fila con tipoRecurso='tool' y activo=1/0
-- para que el factory.py sepa cuáles instanciar al arrancar.
--
-- Para desactivar una tool en un proyecto: UPDATE SET activo=0
-- Para activar una tool nueva:             UPDATE SET activo=1
-- La tabla es la única fuente de verdad de qué tools existen en este proyecto.

-- database_query
IF NOT EXISTS (SELECT 1 FROM abcmasplus..BotIAv2_Recurso WHERE recurso = 'tool:database_query')
    INSERT INTO abcmasplus..BotIAv2_Recurso (recurso, tipoRecurso, descripcion, esPublico, activo)
    VALUES ('tool:database_query', 'tool', 'Consultas SQL en lenguaje natural a bases de datos', 0, 1);

-- knowledge_search
IF NOT EXISTS (SELECT 1 FROM abcmasplus..BotIAv2_Recurso WHERE recurso = 'tool:knowledge_search')
    INSERT INTO abcmasplus..BotIAv2_Recurso (recurso, tipoRecurso, descripcion, esPublico, activo)
    VALUES ('tool:knowledge_search', 'tool', 'Búsqueda en base de conocimiento institucional', 0, 1);

-- calculate
IF NOT EXISTS (SELECT 1 FROM abcmasplus..BotIAv2_Recurso WHERE recurso = 'tool:calculate')
    INSERT INTO abcmasplus..BotIAv2_Recurso (recurso, tipoRecurso, descripcion, esPublico, activo)
    VALUES ('tool:calculate', 'tool', 'Evaluación de expresiones matemáticas', 0, 1);

-- datetime
IF NOT EXISTS (SELECT 1 FROM abcmasplus..BotIAv2_Recurso WHERE recurso = 'tool:datetime')
    INSERT INTO abcmasplus..BotIAv2_Recurso (recurso, tipoRecurso, descripcion, esPublico, activo)
    VALUES ('tool:datetime', 'tool', 'Consultas de fecha, hora y cálculos temporales', 0, 1);

-- save_preference
IF NOT EXISTS (SELECT 1 FROM abcmasplus..BotIAv2_Recurso WHERE recurso = 'tool:save_preference')
    INSERT INTO abcmasplus..BotIAv2_Recurso (recurso, tipoRecurso, descripcion, esPublico, activo)
    VALUES ('tool:save_preference', 'tool', 'Guardar preferencias del usuario en BD', 0, 1);

-- save_memory
IF NOT EXISTS (SELECT 1 FROM abcmasplus..BotIAv2_Recurso WHERE recurso = 'tool:save_memory')
    INSERT INTO abcmasplus..BotIAv2_Recurso (recurso, tipoRecurso, descripcion, esPublico, activo)
    VALUES ('tool:save_memory', 'tool', 'Persistir datos en memoria de trabajo del usuario', 0, 1);

-- reload_permissions (ya puede existir por migración anterior — solo asegurar activo=1)
IF NOT EXISTS (SELECT 1 FROM abcmasplus..BotIAv2_Recurso WHERE recurso = 'tool:reload_permissions')
    INSERT INTO abcmasplus..BotIAv2_Recurso (recurso, tipoRecurso, descripcion, esPublico, activo)
    VALUES ('tool:reload_permissions', 'tool', 'Recargar permisos del usuario desde BD', 1, 1);

-- reload_agent_config
IF NOT EXISTS (SELECT 1 FROM abcmasplus..BotIAv2_Recurso WHERE recurso = 'tool:reload_agent_config')
    INSERT INTO abcmasplus..BotIAv2_Recurso (recurso, tipoRecurso, descripcion, esPublico, activo)
    VALUES ('tool:reload_agent_config', 'tool', 'Recargar configuración de agentes desde BD (solo admin)', 0, 1);

-- read_attachment (ya puede existir por migración 004)
IF NOT EXISTS (SELECT 1 FROM abcmasplus..BotIAv2_Recurso WHERE recurso = 'tool:read_attachment')
    INSERT INTO abcmasplus..BotIAv2_Recurso (recurso, tipoRecurso, descripcion, esPublico, activo)
    VALUES ('tool:read_attachment', 'tool', 'Leer archivos adjuntos enviados por el usuario', 0, 1);

SELECT recurso, tipoRecurso, activo, esPublico
FROM abcmasplus..BotIAv2_Recurso
WHERE tipoRecurso = 'tool'
ORDER BY recurso;
