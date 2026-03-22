"""
Base de conocimiento empresarial.

Contiene información institucional estructurada sobre procesos,
políticas, FAQs y contactos de la empresa.
"""
from dataclasses import dataclass, field
from typing import List, Optional
from .knowledge_categories import KnowledgeCategory


@dataclass
class KnowledgeEntry:
    """Entrada de conocimiento empresarial."""

    category: KnowledgeCategory
    question: str
    answer: str
    keywords: List[str]
    related_commands: List[str] = field(default_factory=list)
    priority: int = 1  # 1=normal, 2=high, 3=critical

    def __repr__(self) -> str:
        return f"KnowledgeEntry(category={self.category.value}, question='{self.question[:50]}...')"


# ============================================================================
# BASE DE CONOCIMIENTO EMPRESARIAL
# ============================================================================

KNOWLEDGE_BASE: List[KnowledgeEntry] = [

    # ========================================================================
    # PROCESOS
    # ========================================================================

    KnowledgeEntry(
        category=KnowledgeCategory.PROCESOS,
        question="¿Cómo solicito vacaciones?",
        answer=(
            "🏖️ **Para solicitar vacaciones:**\n\n"
            "1️⃣ Ingresar al portal de empleados con tu usuario y contraseña\n"
            "2️⃣ Ir a la sección 'Solicitudes > Vacaciones'\n"
            "3️⃣ Llenar el formulario indicando las fechas deseadas\n"
            "4️⃣ La solicitud debe hacerse con al menos **15 días de anticipación** ⏰\n"
            "5️⃣ Esperar aprobación de tu supervisor directo ✅\n"
            "6️⃣ Recibirás notificación por email cuando sea aprobada 📧"
        ),
        keywords=["vacaciones", "solicitar", "pedir", "días libres", "descanso", "ausentarse"],
        related_commands=["/help"],
        priority=2
    ),

    KnowledgeEntry(
        category=KnowledgeCategory.PROCESOS,
        question="¿Cómo creo un ticket de soporte?",
        answer=(
            "🎫 **Crear un ticket de soporte:**\n\n"
            "Tienes 3 opciones:\n\n"
            "📱 **Opción 1:** Usar el comando /crear_ticket en este bot\n"
            "📧 **Opción 2:** Enviar email a soporte@empresa.com\n"
            "☎️ **Opción 3:** Llamar a la extensión 123\n\n"
            "⚠️ **Incluye siempre:**\n"
            "• Descripción del problema\n"
            "• Departamento\n"
            "• Nivel de urgencia (🔵 bajo / 🟡 medio / 🔴 alto)"
        ),
        keywords=["ticket", "soporte", "ayuda", "problema", "incidencia", "reporte"],
        related_commands=["/crear_ticket"],
        priority=3
    ),

    KnowledgeEntry(
        category=KnowledgeCategory.PROCESOS,
        question="¿Cómo reporto una ausencia?",
        answer=(
            "Para reportar una ausencia:\n"
            "1. Si es planificada: solicítala con al menos 48 horas de anticipación "
            "en el portal de empleados\n"
            "2. Si es imprevista (enfermedad, emergencia): notifica a tu supervisor "
            "por WhatsApp o llamada antes de las 9:00 AM\n"
            "3. Presenta justificante médico dentro de las 48 horas siguientes"
        ),
        keywords=["ausencia", "falta", "no asistir", "enfermedad", "permiso"],
        related_commands=[],
        priority=2
    ),

    # ========================================================================
    # POLÍTICAS
    # ========================================================================

    KnowledgeEntry(
        category=KnowledgeCategory.POLITICAS,
        question="¿Qué políticas tiene la empresa?",
        answer=(
            "📋 **Políticas de la Empresa:**\n\n"
            "Tenemos políticas en las siguientes áreas:\n\n"
            "⏰ **Horarios de Trabajo:**\n"
            "• Lunes a Viernes: 8:00 AM - 6:00 PM\n"
            "• 9 horas diarias, 45 horas semanales\n"
            "• Pregunta: `/ia ¿Cuál es el horario de trabajo?`\n\n"
            "🏖️ **Vacaciones:**\n"
            "• 15-25 días según antigüedad\n"
            "• Pregunta: `/ia ¿Cuántos días de vacaciones tengo?`\n\n"
            "🏠 **Trabajo Remoto:**\n"
            "• Hasta 2 días por semana (modalidad híbrida)\n"
            "• Pregunta: `/ia ¿Cuál es la política de trabajo remoto?`\n\n"
            "💡 **Tip:** Haz preguntas específicas sobre cada política para obtener información detallada"
        ),
        keywords=["políticas", "política", "reglas", "normas", "reglamento", "normativa", "directrices"],
        related_commands=["/help", "/ia"],
        priority=3
    ),

    KnowledgeEntry(
        category=KnowledgeCategory.POLITICAS,
        question="¿Cuál es el horario de trabajo?",
        answer=(
            "El horario laboral estándar es:\n"
            "• Lunes a Viernes: 8:00 AM - 6:00 PM\n"
            "• Hora de almuerzo: 12:00 PM - 2:00 PM (1 hora flexible)\n"
            "• Total: 9 horas diarias, 45 horas semanales\n\n"
            "Algunos departamentos tienen horarios especiales. "
            "Consulta con tu supervisor."
        ),
        keywords=["horario", "hora", "entrada", "salida", "jornada", "trabajo", "políticas", "política"],
        related_commands=[],
        priority=2
    ),

    KnowledgeEntry(
        category=KnowledgeCategory.POLITICAS,
        question="¿Cuántos días de vacaciones tengo al año?",
        answer=(
            "Los días de vacaciones dependen de tu antigüedad:\n"
            "• 0-1 año: 15 días\n"
            "• 1-5 años: 20 días\n"
            "• Más de 5 años: 25 días\n\n"
            "Los días se acumulan por año trabajado y deben usarse antes del 31 de diciembre. "
            "No se pueden transferir al siguiente año salvo autorización especial."
        ),
        keywords=["vacaciones", "días", "cuántos", "derecho", "corresponden", "políticas", "política"],
        related_commands=[],
        priority=2
    ),

    KnowledgeEntry(
        category=KnowledgeCategory.POLITICAS,
        question="¿Cuál es la política de trabajo remoto?",
        answer=(
            "Política de trabajo remoto (Home Office):\n"
            "• Disponible para puestos elegibles según aprobación del supervisor\n"
            "• Máximo 2 días por semana en modalidad híbrida\n"
            "• Requiere solicitud previa en el portal con 48 horas de anticipación\n"
            "• Debes estar disponible en horario laboral y con conexión estable\n"
            "• Aplican mismas reglas de productividad y entregas"
        ),
        keywords=["remoto", "home office", "casa", "teletrabajo", "virtual", "políticas", "política"],
        related_commands=[],
        priority=1
    ),

    # ========================================================================
    # FAQS
    # ========================================================================

    KnowledgeEntry(
        category=KnowledgeCategory.FAQS,
        question="¿Qué hacer si olvido mi contraseña?",
        answer=(
            "🔑 **Recuperar contraseña:**\n\n"
            "1️⃣ En la pantalla de login, haz clic en '¿Olvidaste tu contraseña?'\n"
            "2️⃣ Ingresa tu email corporativo 📧\n"
            "3️⃣ Recibirás un enlace para resetearla 🔗\n"
            "4️⃣ Si no recibes el email en 5 minutos, contacta a IT (ext. 123) ⏱️\n\n"
            "💡 **Tip:** También puedes crear un ticket usando /crear_ticket"
        ),
        keywords=["contraseña", "password", "olvidé", "resetear", "cambiar", "recuperar"],
        related_commands=["/crear_ticket"],
        priority=3
    ),

    KnowledgeEntry(
        category=KnowledgeCategory.FAQS,
        question="¿Cómo accedo al portal de empleados?",
        answer=(
            "Para acceder al portal de empleados:\n"
            "1. Ingresa a: https://portal.empresa.com\n"
            "2. Usa tu email corporativo como usuario\n"
            "3. Tu contraseña inicial es tu cédula (cámbiala en el primer ingreso)\n"
            "4. Si tienes problemas, contacta a IT"
        ),
        keywords=["portal", "acceso", "ingresar", "login", "empleados"],
        related_commands=[],
        priority=2
    ),

    KnowledgeEntry(
        category=KnowledgeCategory.FAQS,
        question="¿Dónde encuentro mi recibo de pago?",
        answer=(
            "Tu recibo de pago está disponible en:\n"
            "1. Portal de empleados > Sección 'Nómina'\n"
            "2. Se publica el último día hábil de cada mes\n"
            "3. Puedes descargar recibos de los últimos 12 meses\n"
            "4. Para recibos más antiguos, solicita en RRHH"
        ),
        keywords=["recibo", "pago", "nómina", "sueldo", "salario", "comprobante"],
        related_commands=[],
        priority=2
    ),

    # ========================================================================
    # CONTACTOS
    # ========================================================================

    KnowledgeEntry(
        category=KnowledgeCategory.CONTACTOS,
        question="¿Cómo contacto al departamento de IT?",
        answer=(
            "Contactos del departamento de IT:\n"
            "• Extensión: 123\n"
            "• Email: it@empresa.com\n"
            "• WhatsApp: +123456789\n"
            "• Horario de atención: Lunes a Viernes 8AM-6PM\n"
            "• Para urgencias fuera de horario: crear ticket marcando como 'Urgente'"
        ),
        keywords=["it", "sistemas", "soporte técnico", "tecnología", "contacto"],
        related_commands=["/crear_ticket"],
        priority=2
    ),

    KnowledgeEntry(
        category=KnowledgeCategory.CONTACTOS,
        question="¿Cómo contacto a Recursos Humanos?",
        answer=(
            "Contactos de Recursos Humanos:\n"
            "• Extensión: 456\n"
            "• Email: rrhh@empresa.com\n"
            "• Oficina: Edificio Principal, 2do piso\n"
            "• Horario de atención: Lunes a Viernes 8AM-5PM\n"
            "• Para temas urgentes, solicitar cita previa"
        ),
        keywords=["rrhh", "recursos humanos", "personal", "contacto", "talento"],
        related_commands=[],
        priority=2
    ),

    KnowledgeEntry(
        category=KnowledgeCategory.CONTACTOS,
        question="¿A quién contacto para temas de nómina?",
        answer=(
            "Contactos para temas de nómina:\n"
            "• Departamento: RRHH - Área de Nómina\n"
            "• Email: nomina@empresa.com\n"
            "• Extensión: 789\n"
            "• Horario: Lunes a Viernes 8AM-12PM y 2PM-5PM\n"
            "• Días de corte: 25 de cada mes"
        ),
        keywords=["nómina", "pago", "sueldo", "salario", "planilla"],
        related_commands=[],
        priority=2
    ),

    # ========================================================================
    # SISTEMAS
    # ========================================================================

    KnowledgeEntry(
        category=KnowledgeCategory.SISTEMAS,
        question="¿Qué comandos puedo usar en este bot?",
        answer=(
            "Comandos disponibles en el bot:\n"
            "• /help - Ver ayuda general\n"
            "• /ia <consulta> - Hacer consultas con IA\n"
            "• /stats - Ver estadísticas del sistema\n"
            "• /crear_ticket - Crear ticket de soporte\n"
            "• /register - Registrarse en el sistema\n\n"
            "Usa /help para ver la lista completa con descripciones."
        ),
        keywords=["comandos", "ayuda", "usar", "bot", "funciones", "opciones"],
        related_commands=["/help"],
        priority=3
    ),

    KnowledgeEntry(
        category=KnowledgeCategory.SISTEMAS,
        question="¿Cómo me registro en el bot?",
        answer=(
            "Para registrarte en el bot:\n"
            "1. Usa el comando /register\n"
            "2. El bot te solicitará tu código de verificación\n"
            "3. Obtén tu código desde el Portal de Consola de Monitoreo\n"
            "4. Envía el código al bot usando /verify <codigo>\n"
            "5. Una vez verificado, podrás usar todas las funciones"
        ),
        keywords=["registro", "registrar", "verificar", "activar", "cuenta"],
        related_commands=["/register", "/verify"],
        priority=3
    ),

    # ========================================================================
    # RECURSOS HUMANOS
    # ========================================================================

    KnowledgeEntry(
        category=KnowledgeCategory.RECURSOS_HUMANOS,
        question="¿Qué beneficios tengo como empleado?",
        answer=(
            "Beneficios para empleados:\n"
            "• Seguro médico privado (cobertura familiar)\n"
            "• Seguro de vida\n"
            "• Bono anual por desempeño\n"
            "• 15-25 días de vacaciones (según antigüedad)\n"
            "• Capacitaciones y desarrollo profesional\n"
            "• Descuentos en comercios afiliados\n"
            "• Bono de alimentación\n\n"
            "Consulta el manual de empleados para detalles completos."
        ),
        keywords=["beneficios", "ventajas", "seguro", "bono", "prestaciones"],
        related_commands=[],
        priority=1
    ),

    KnowledgeEntry(
        category=KnowledgeCategory.RECURSOS_HUMANOS,
        question="¿Cómo solicito una constancia de trabajo?",
        answer=(
            "Para solicitar una constancia de trabajo:\n"
            "1. Envía email a rrhh@empresa.com indicando el tipo de constancia\n"
            "2. Tipos disponibles: laboral, salarial, antigüedad\n"
            "3. Tiempo de entrega: 48 horas hábiles\n"
            "4. Retiro en oficina de RRHH con identificación\n"
            "5. Servicio gratuito para empleados activos"
        ),
        keywords=["constancia", "certificado", "carta", "trabajo", "laboral"],
        related_commands=[],
        priority=1
    ),

    KnowledgeEntry(
        category=KnowledgeCategory.RECURSOS_HUMANOS,
        question="¿Qué hacer en caso de emergencia en la oficina?",
        answer=(
            "En caso de emergencia:\n"
            "1. Mantén la calma y evalúa la situación\n"
            "2. Emergencia médica: llama a la enfermería (ext. 911) o 911\n"
            "3. Incendio: activa alarma, evacua por salidas de emergencia\n"
            "4. Sismo: protégete bajo escritorio, evacua cuando cese\n"
            "5. Punto de reunión: Estacionamiento principal\n"
            "6. Brigadas de emergencia identificadas con chaleco naranja"
        ),
        keywords=["emergencia", "urgencia", "peligro", "evacuación", "seguridad"],
        related_commands=[],
        priority=3
    ),

    # ========================================================================
    # BASE DE DATOS
    # ========================================================================

    KnowledgeEntry(
        category=KnowledgeCategory.BASE_DATOS,
        question="¿Qué información contiene la tabla Ventas?",
        answer=(
            "📊 **Tabla Ventas** ([Pruebas].[dbo].[Ventas])\n\n"
            "Contiene información sobre transacciones de ventas:\n\n"
            "🔑 **customer_id** → Identificador único del cliente\n"
            "📦 **product_name** → Nombre del producto vendido\n"
            "🔢 **quantity** → Cantidad de unidades vendidas\n"
            "💵 **unit_price** → Precio unitario del producto\n"
            "💰 **total_price** → Precio total (quantity × unit_price)\n\n"
            "✨ **Úsala para:**\n"
            "• Consultas sobre ventas\n"
            "• Productos más vendidos\n"
            "• Ingresos totales\n"
            "• Análisis de clientes\n"
            "• Reportes financieros"
        ),
        keywords=[
            "ventas", "tabla ventas", "productos", "clientes", "transacciones",
            "customer_id", "product_name", "quantity", "unit_price", "total_price",
            "base de datos", "bd", "tabla", "campos"
        ],
        related_commands=["/ia", "/query"],
        priority=2
    ),

    KnowledgeEntry(
        category=KnowledgeCategory.BASE_DATOS,
        question="¿Qué tablas están disponibles en la base de datos?",
        answer=(
            "🗄️ **Tablas Disponibles:**\n\n"
            "📊 **1. Ventas** ([Pruebas].[dbo].[Ventas])\n"
            "   • Contiene: Transacciones de ventas con info de clientes, productos, cantidades y precios\n"
            "   • Campos: customer_id, product_name, quantity, unit_price, total_price\n"
            "   • Usa para: Ventas, análisis de productos, reportes financieros\n\n"
            "💡 **¿Cómo consultar?**\n"
            "Usa el comando `/ia` seguido de tu pregunta. "
            "El sistema generará automáticamente la consulta SQL necesaria ✨"
        ),
        keywords=[
            "tablas", "base de datos", "bd", "esquema", "estructura",
            "disponibles", "qué tablas", "cuáles tablas", "acceso"
        ],
        related_commands=["/ia"],
        priority=3
    ),

    KnowledgeEntry(
        category=KnowledgeCategory.BASE_DATOS,
        question="¿Cómo puedo consultar información de la base de datos?",
        answer=(
            "🤖 **Consultar la base de datos es súper fácil:**\n\n"
            "Simplemente usa `/ia` + tu pregunta en lenguaje natural\n\n"
            "📝 **Ejemplos:**\n\n"
            "🔢 `/ia ¿Cuántas ventas hay?`\n"
            "   → Cuenta total de registros\n\n"
            "🏆 `/ia ¿Cuál es el producto más vendido?`\n"
            "   → Análisis de productos\n\n"
            "👤 `/ia Muéstrame las ventas del cliente 123`\n"
            "   → Filtrado por cliente\n\n"
            "💰 `/ia ¿Cuál es el total de ingresos?`\n"
            "   → Suma de ventas\n\n"
            "✨ **El sistema hace esto por ti:**\n"
            "1️⃣ Analiza tu pregunta\n"
            "2️⃣ Genera el SQL automáticamente\n"
            "3️⃣ Ejecuta la consulta de forma segura\n"
            "4️⃣ Te responde en lenguaje natural\n\n"
            "💡 **No necesitas saber SQL**, solo pregunta naturalmente"
        ),
        keywords=[
            "consultar", "query", "preguntar", "datos", "información",
            "cómo consulto", "cómo pregunto", "usar ia", "comando ia"
        ],
        related_commands=["/ia", "/help"],
        priority=3
    ),

]


def get_knowledge_base() -> List[KnowledgeEntry]:
    """Obtener la base de conocimiento completa."""
    return KNOWLEDGE_BASE


def get_entries_by_category(category: KnowledgeCategory) -> List[KnowledgeEntry]:
    """Obtener entradas por categoría."""
    return [entry for entry in KNOWLEDGE_BASE if entry.category == category]


def get_high_priority_entries() -> List[KnowledgeEntry]:
    """Obtener entradas de alta prioridad."""
    return [entry for entry in KNOWLEDGE_BASE if entry.priority >= 2]
