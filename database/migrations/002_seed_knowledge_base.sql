-- ============================================================================
-- Migración 002: Seed data de Knowledge Base
-- Fecha: 2025-11-29
-- Descripción: Carga las entradas iniciales de conocimiento desde el código
-- Base de datos: abcmasplus
-- ============================================================================

USE [abcmasplus];
GO

-- ============================================================================
-- 1. Insertar Categorías
-- ============================================================================

PRINT 'Insertando categorías...';

-- Limpiar datos existentes (opcional - comentar si quieres mantener datos)
-- DELETE FROM knowledge_entries;
-- DELETE FROM knowledge_categories;

SET IDENTITY_INSERT knowledge_categories ON;


INSERT INTO knowledge_categories (id, name, display_name, description, icon, active)
VALUES (1, 'PROCESOS', N'Procesos', N'Procesos y procedimientos internos', N'📋', 1);

INSERT INTO knowledge_categories (id, name, display_name, description, icon, active)
VALUES (2, 'POLITICAS', N'Politicas', N'Políticas de la empresa', N'📜', 1);

INSERT INTO knowledge_categories (id, name, display_name, description, icon, active)
VALUES (3, 'FAQS', N'Faqs', N'Preguntas frecuentes', N'❓', 1);

INSERT INTO knowledge_categories (id, name, display_name, description, icon, active)
VALUES (4, 'CONTACTOS', N'Contactos', N'Información de contacto de departamentos', N'📞', 1);

INSERT INTO knowledge_categories (id, name, display_name, description, icon, active)
VALUES (5, 'SISTEMAS', N'Sistemas', N'Información sobre sistemas y herramientas', N'💻', 1);

INSERT INTO knowledge_categories (id, name, display_name, description, icon, active)
VALUES (6, 'RECURSOS_HUMANOS', N'Recursos Humanos', N'Temas de RRHH: vacaciones, permisos, beneficios', N'👥', 1);

INSERT INTO knowledge_categories (id, name, display_name, description, icon, active)
VALUES (7, 'BASE_DATOS', N'Base Datos', N'Información sobre tablas y estructura de la base de datos', N'🗄️', 1);

SET IDENTITY_INSERT knowledge_categories OFF;

PRINT '  Categorías insertadas: 7';

-- ============================================================================
-- 2. Insertar Entradas de Conocimiento
-- ============================================================================

PRINT 'Insertando entradas de conocimiento...';


-- Entrada 1: ¿Cómo solicito vacaciones?...
INSERT INTO knowledge_entries (category_id, question, answer, keywords, related_commands, priority, active, created_by)
VALUES (
    1,
    N'¿Cómo solicito vacaciones?',
    N'🏖️ **Para solicitar vacaciones:**

1️⃣ Ingresar al portal de empleados con tu usuario y contraseña
2️⃣ Ir a la sección ''Solicitudes > Vacaciones''
3️⃣ Llenar el formulario indicando las fechas deseadas
4️⃣ La solicitud debe hacerse con al menos **15 días de anticipación** ⏰
5️⃣ Esperar aprobación de tu supervisor directo ✅
6️⃣ Recibirás notificación por email cuando sea aprobada 📧',
    N'["vacaciones", "solicitar", "pedir", "días libres", "descanso", "ausentarse"]',
    N'["/help"]',
    2,
    1,
    'migration_001'
);

-- Entrada 2: ¿Cómo creo un ticket de soporte?...
INSERT INTO knowledge_entries (category_id, question, answer, keywords, related_commands, priority, active, created_by)
VALUES (
    1,
    N'¿Cómo creo un ticket de soporte?',
    N'🎫 **Crear un ticket de soporte:**

Tienes 3 opciones:

📱 **Opción 1:** Usar el comando /crear_ticket en este bot
📧 **Opción 2:** Enviar email a soporte@empresa.com
☎️ **Opción 3:** Llamar a la extensión 123

⚠️ **Incluye siempre:**
• Descripción del problema
• Departamento
• Nivel de urgencia (🔵 bajo / 🟡 medio / 🔴 alto)',
    N'["ticket", "soporte", "ayuda", "problema", "incidencia", "reporte"]',
    N'["/crear_ticket"]',
    3,
    1,
    'migration_001'
);

-- Entrada 3: ¿Cómo reporto una ausencia?...
INSERT INTO knowledge_entries (category_id, question, answer, keywords, related_commands, priority, active, created_by)
VALUES (
    1,
    N'¿Cómo reporto una ausencia?',
    N'Para reportar una ausencia:
1. Si es planificada: solicítala con al menos 48 horas de anticipación en el portal de empleados
2. Si es imprevista (enfermedad, emergencia): notifica a tu supervisor por WhatsApp o llamada antes de las 9:00 AM
3. Presenta justificante médico dentro de las 48 horas siguientes',
    N'["ausencia", "falta", "no asistir", "enfermedad", "permiso"]',
    N'[]',
    2,
    1,
    'migration_001'
);

-- Entrada 4: ¿Qué políticas tiene la empresa?...
INSERT INTO knowledge_entries (category_id, question, answer, keywords, related_commands, priority, active, created_by)
VALUES (
    2,
    N'¿Qué políticas tiene la empresa?',
    N'📋 **Políticas de la Empresa:**

Tenemos políticas en las siguientes áreas:

⏰ **Horarios de Trabajo:**
• Lunes a Viernes: 8:00 AM - 6:00 PM
• 9 horas diarias, 45 horas semanales
• Pregunta: `/ia ¿Cuál es el horario de trabajo?`

🏖️ **Vacaciones:**
• 15-25 días según antigüedad
• Pregunta: `/ia ¿Cuántos días de vacaciones tengo?`

🏠 **Trabajo Remoto:**
• Hasta 2 días por semana (modalidad híbrida)
• Pregunta: `/ia ¿Cuál es la política de trabajo remoto?`

💡 **Tip:** Haz preguntas específicas sobre cada política para obtener información detallada',
    N'["políticas", "política", "reglas", "normas", "reglamento", "normativa", "directrices"]',
    N'["/help", "/ia"]',
    3,
    1,
    'migration_001'
);

-- Entrada 5: ¿Cuál es el horario de trabajo?...
INSERT INTO knowledge_entries (category_id, question, answer, keywords, related_commands, priority, active, created_by)
VALUES (
    2,
    N'¿Cuál es el horario de trabajo?',
    N'El horario laboral estándar es:
• Lunes a Viernes: 8:00 AM - 6:00 PM
• Hora de almuerzo: 12:00 PM - 2:00 PM (1 hora flexible)
• Total: 9 horas diarias, 45 horas semanales

Algunos departamentos tienen horarios especiales. Consulta con tu supervisor.',
    N'["horario", "hora", "entrada", "salida", "jornada", "trabajo", "políticas", "política"]',
    N'[]',
    2,
    1,
    'migration_001'
);

-- Entrada 6: ¿Cuántos días de vacaciones tengo al año?...
INSERT INTO knowledge_entries (category_id, question, answer, keywords, related_commands, priority, active, created_by)
VALUES (
    2,
    N'¿Cuántos días de vacaciones tengo al año?',
    N'Los días de vacaciones dependen de tu antigüedad:
• 0-1 año: 15 días
• 1-5 años: 20 días
• Más de 5 años: 25 días

Los días se acumulan por año trabajado y deben usarse antes del 31 de diciembre. No se pueden transferir al siguiente año salvo autorización especial.',
    N'["vacaciones", "días", "cuántos", "derecho", "corresponden", "políticas", "política"]',
    N'[]',
    2,
    1,
    'migration_001'
);

-- Entrada 7: ¿Cuál es la política de trabajo remoto?...
INSERT INTO knowledge_entries (category_id, question, answer, keywords, related_commands, priority, active, created_by)
VALUES (
    2,
    N'¿Cuál es la política de trabajo remoto?',
    N'Política de trabajo remoto (Home Office):
• Disponible para puestos elegibles según aprobación del supervisor
• Máximo 2 días por semana en modalidad híbrida
• Requiere solicitud previa en el portal con 48 horas de anticipación
• Debes estar disponible en horario laboral y con conexión estable
• Aplican mismas reglas de productividad y entregas',
    N'["remoto", "home office", "casa", "teletrabajo", "virtual", "políticas", "política"]',
    N'[]',
    1,
    1,
    'migration_001'
);

-- Entrada 8: ¿Qué hacer si olvido mi contraseña?...
INSERT INTO knowledge_entries (category_id, question, answer, keywords, related_commands, priority, active, created_by)
VALUES (
    3,
    N'¿Qué hacer si olvido mi contraseña?',
    N'🔑 **Recuperar contraseña:**

1️⃣ En la pantalla de login, haz clic en ''¿Olvidaste tu contraseña?''
2️⃣ Ingresa tu email corporativo 📧
3️⃣ Recibirás un enlace para resetearla 🔗
4️⃣ Si no recibes el email en 5 minutos, contacta a IT (ext. 123) ⏱️

💡 **Tip:** También puedes crear un ticket usando /crear_ticket',
    N'["contraseña", "password", "olvidé", "resetear", "cambiar", "recuperar"]',
    N'["/crear_ticket"]',
    3,
    1,
    'migration_001'
);

-- Entrada 9: ¿Cómo accedo al portal de empleados?...
INSERT INTO knowledge_entries (category_id, question, answer, keywords, related_commands, priority, active, created_by)
VALUES (
    3,
    N'¿Cómo accedo al portal de empleados?',
    N'Para acceder al portal de empleados:
1. Ingresa a: https://portal.empresa.com
2. Usa tu email corporativo como usuario
3. Tu contraseña inicial es tu cédula (cámbiala en el primer ingreso)
4. Si tienes problemas, contacta a IT',
    N'["portal", "acceso", "ingresar", "login", "empleados"]',
    N'[]',
    2,
    1,
    'migration_001'
);

-- Entrada 10: ¿Dónde encuentro mi recibo de pago?...
INSERT INTO knowledge_entries (category_id, question, answer, keywords, related_commands, priority, active, created_by)
VALUES (
    3,
    N'¿Dónde encuentro mi recibo de pago?',
    N'Tu recibo de pago está disponible en:
1. Portal de empleados > Sección ''Nómina''
2. Se publica el último día hábil de cada mes
3. Puedes descargar recibos de los últimos 12 meses
4. Para recibos más antiguos, solicita en RRHH',
    N'["recibo", "pago", "nómina", "sueldo", "salario", "comprobante"]',
    N'[]',
    2,
    1,
    'migration_001'
);

-- Entrada 11: ¿Cómo contacto al departamento de IT?...
INSERT INTO knowledge_entries (category_id, question, answer, keywords, related_commands, priority, active, created_by)
VALUES (
    4,
    N'¿Cómo contacto al departamento de IT?',
    N'Contactos del departamento de IT:
• Extensión: 123
• Email: it@empresa.com
• WhatsApp: +123456789
• Horario de atención: Lunes a Viernes 8AM-6PM
• Para urgencias fuera de horario: crear ticket marcando como ''Urgente''',
    N'["it", "sistemas", "soporte técnico", "tecnología", "contacto"]',
    N'["/crear_ticket"]',
    2,
    1,
    'migration_001'
);

-- Entrada 12: ¿Cómo contacto a Recursos Humanos?...
INSERT INTO knowledge_entries (category_id, question, answer, keywords, related_commands, priority, active, created_by)
VALUES (
    4,
    N'¿Cómo contacto a Recursos Humanos?',
    N'Contactos de Recursos Humanos:
• Extensión: 456
• Email: rrhh@empresa.com
• Oficina: Edificio Principal, 2do piso
• Horario de atención: Lunes a Viernes 8AM-5PM
• Para temas urgentes, solicitar cita previa',
    N'["rrhh", "recursos humanos", "personal", "contacto", "talento"]',
    N'[]',
    2,
    1,
    'migration_001'
);

-- Entrada 13: ¿A quién contacto para temas de nómina?...
INSERT INTO knowledge_entries (category_id, question, answer, keywords, related_commands, priority, active, created_by)
VALUES (
    4,
    N'¿A quién contacto para temas de nómina?',
    N'Contactos para temas de nómina:
• Departamento: RRHH - Área de Nómina
• Email: nomina@empresa.com
• Extensión: 789
• Horario: Lunes a Viernes 8AM-12PM y 2PM-5PM
• Días de corte: 25 de cada mes',
    N'["nómina", "pago", "sueldo", "salario", "planilla"]',
    N'[]',
    2,
    1,
    'migration_001'
);

-- Entrada 14: ¿Qué comandos puedo usar en este bot?...
INSERT INTO knowledge_entries (category_id, question, answer, keywords, related_commands, priority, active, created_by)
VALUES (
    5,
    N'¿Qué comandos puedo usar en este bot?',
    N'Comandos disponibles en el bot:
• /help - Ver ayuda general
• /ia <consulta> - Hacer consultas con IA
• /stats - Ver estadísticas del sistema
• /crear_ticket - Crear ticket de soporte
• /register - Registrarse en el sistema

Usa /help para ver la lista completa con descripciones.',
    N'["comandos", "ayuda", "usar", "bot", "funciones", "opciones"]',
    N'["/help"]',
    3,
    1,
    'migration_001'
);

-- Entrada 15: ¿Cómo me registro en el bot?...
INSERT INTO knowledge_entries (category_id, question, answer, keywords, related_commands, priority, active, created_by)
VALUES (
    5,
    N'¿Cómo me registro en el bot?',
    N'Para registrarte en el bot:
1. Usa el comando /register
2. El bot te solicitará tu código de verificación
3. Obtén tu código desde el Portal de Consola de Monitoreo
4. Envía el código al bot usando /verify <codigo>
5. Una vez verificado, podrás usar todas las funciones',
    N'["registro", "registrar", "verificar", "activar", "cuenta"]',
    N'["/register", "/verify"]',
    3,
    1,
    'migration_001'
);

-- Entrada 16: ¿Qué beneficios tengo como empleado?...
INSERT INTO knowledge_entries (category_id, question, answer, keywords, related_commands, priority, active, created_by)
VALUES (
    6,
    N'¿Qué beneficios tengo como empleado?',
    N'Beneficios para empleados:
• Seguro médico privado (cobertura familiar)
• Seguro de vida
• Bono anual por desempeño
• 15-25 días de vacaciones (según antigüedad)
• Capacitaciones y desarrollo profesional
• Descuentos en comercios afiliados
• Bono de alimentación

Consulta el manual de empleados para detalles completos.',
    N'["beneficios", "ventajas", "seguro", "bono", "prestaciones"]',
    N'[]',
    1,
    1,
    'migration_001'
);

-- Entrada 17: ¿Cómo solicito una constancia de trabajo?...
INSERT INTO knowledge_entries (category_id, question, answer, keywords, related_commands, priority, active, created_by)
VALUES (
    6,
    N'¿Cómo solicito una constancia de trabajo?',
    N'Para solicitar una constancia de trabajo:
1. Envía email a rrhh@empresa.com indicando el tipo de constancia
2. Tipos disponibles: laboral, salarial, antigüedad
3. Tiempo de entrega: 48 horas hábiles
4. Retiro en oficina de RRHH con identificación
5. Servicio gratuito para empleados activos',
    N'["constancia", "certificado", "carta", "trabajo", "laboral"]',
    N'[]',
    1,
    1,
    'migration_001'
);

-- Entrada 18: ¿Qué hacer en caso de emergencia en la oficina?...
INSERT INTO knowledge_entries (category_id, question, answer, keywords, related_commands, priority, active, created_by)
VALUES (
    6,
    N'¿Qué hacer en caso de emergencia en la oficina?',
    N'En caso de emergencia:
1. Mantén la calma y evalúa la situación
2. Emergencia médica: llama a la enfermería (ext. 911) o 911
3. Incendio: activa alarma, evacua por salidas de emergencia
4. Sismo: protégete bajo escritorio, evacua cuando cese
5. Punto de reunión: Estacionamiento principal
6. Brigadas de emergencia identificadas con chaleco naranja',
    N'["emergencia", "urgencia", "peligro", "evacuación", "seguridad"]',
    N'[]',
    3,
    1,
    'migration_001'
);

-- Entrada 19: ¿Qué información contiene la tabla Ventas?...
INSERT INTO knowledge_entries (category_id, question, answer, keywords, related_commands, priority, active, created_by)
VALUES (
    7,
    N'¿Qué información contiene la tabla Ventas?',
    N'📊 **Tabla Ventas** ([Pruebas].[dbo].[Ventas])

Contiene información sobre transacciones de ventas:

🔑 **customer_id** → Identificador único del cliente
📦 **product_name** → Nombre del producto vendido
🔢 **quantity** → Cantidad de unidades vendidas
💵 **unit_price** → Precio unitario del producto
💰 **total_price** → Precio total (quantity × unit_price)

✨ **Úsala para:**
• Consultas sobre ventas
• Productos más vendidos
• Ingresos totales
• Análisis de clientes
• Reportes financieros',
    N'["ventas", "tabla ventas", "productos", "clientes", "transacciones", "customer_id", "product_name", "quantity", "unit_price", "total_price", "base de datos", "bd", "tabla", "campos"]',
    N'["/ia", "/query"]',
    2,
    1,
    'migration_001'
);

-- Entrada 20: ¿Qué tablas están disponibles en la base de datos?...
INSERT INTO knowledge_entries (category_id, question, answer, keywords, related_commands, priority, active, created_by)
VALUES (
    7,
    N'¿Qué tablas están disponibles en la base de datos?',
    N'🗄️ **Tablas Disponibles:**

📊 **1. Ventas** ([Pruebas].[dbo].[Ventas])
   • Contiene: Transacciones de ventas con info de clientes, productos, cantidades y precios
   • Campos: customer_id, product_name, quantity, unit_price, total_price
   • Usa para: Ventas, análisis de productos, reportes financieros

💡 **¿Cómo consultar?**
Usa el comando `/ia` seguido de tu pregunta. El sistema generará automáticamente la consulta SQL necesaria ✨',
    N'["tablas", "base de datos", "bd", "esquema", "estructura", "disponibles", "qué tablas", "cuáles tablas", "acceso"]',
    N'["/ia"]',
    3,
    1,
    'migration_001'
);

-- Entrada 21: ¿Cómo puedo consultar información de la base de da...
INSERT INTO knowledge_entries (category_id, question, answer, keywords, related_commands, priority, active, created_by)
VALUES (
    7,
    N'¿Cómo puedo consultar información de la base de datos?',
    N'🤖 **Consultar la base de datos es súper fácil:**

Simplemente usa `/ia` + tu pregunta en lenguaje natural

📝 **Ejemplos:**

🔢 `/ia ¿Cuántas ventas hay?`
   → Cuenta total de registros

🏆 `/ia ¿Cuál es el producto más vendido?`
   → Análisis de productos

👤 `/ia Muéstrame las ventas del cliente 123`
   → Filtrado por cliente

💰 `/ia ¿Cuál es el total de ingresos?`
   → Suma de ventas

✨ **El sistema hace esto por ti:**
1️⃣ Analiza tu pregunta
2️⃣ Genera el SQL automáticamente
3️⃣ Ejecuta la consulta de forma segura
4️⃣ Te responde en lenguaje natural

💡 **No necesitas saber SQL**, solo pregunta naturalmente',
    N'["consultar", "query", "preguntar", "datos", "información", "cómo consulto", "cómo pregunto", "usar ia", "comando ia"]',
    N'["/ia", "/help"]',
    3,
    1,
    'migration_001'
);

PRINT '  Entradas insertadas: 21';

-- ============================================================================
-- 3. Verificación
-- ============================================================================

PRINT '';
PRINT 'Verificando datos insertados...';

SELECT
    c.display_name as Categoria,
    COUNT(e.id) as Total_Entradas,
    SUM(CASE WHEN e.priority = 3 THEN 1 ELSE 0 END) as Prioridad_Alta,
    SUM(CASE WHEN e.priority = 2 THEN 1 ELSE 0 END) as Prioridad_Media,
    SUM(CASE WHEN e.priority = 1 THEN 1 ELSE 0 END) as Prioridad_Normal
FROM knowledge_categories c
LEFT JOIN knowledge_entries e ON c.id = e.category_id
GROUP BY c.display_name
ORDER BY c.display_name;

PRINT '';
PRINT '============================================================================';
PRINT 'Migración 002 completada exitosamente';
PRINT '============================================================================';
PRINT 'Total de categorías: 7';
PRINT 'Total de entradas: 21';
PRINT '';
PRINT 'Siguiente paso: Actualizar KnowledgeManager para leer desde BD';
PRINT '============================================================================';
GO
