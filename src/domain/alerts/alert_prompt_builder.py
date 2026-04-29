"""
Alert Prompt Builder — Construye el prompt enriquecido para análisis de alertas.

El builder recibe un AlertContext (evento + tickets + template + matriz + contactos)
y produce un par (system_prompt, user_prompt) listo para generate_messages().

Estructura del prompt:
  1. Datos del evento activo (Equipo, IP, Sensor, Áreas responsables)
  2. Tickets históricos (TOP 15, [Salto] → \\n)
  3. Template + GerenciaDesarrollo + Matriz de escalamiento
  4. Instrucción al LLM con estructura Markdown esperada

Adaptación vs GS-prod:
  - Usa entidades Pydantic (AlertContext) en lugar de dicts crudos
  - Retorna (system, user) separados para usar con generate_messages()
"""

from src.domain.alerts.alert_entity import AlertContext

DISCLAIMER = (
    "\n\n---\n"
    "⚠️ Las sugerencias anteriores son orientativas. "
    "La decisión de ejecutar cualquier acción es responsabilidad exclusiva del operador. "
    "Valide siempre el impacto antes de actuar."
)

_SYSTEM = (
    "Eres un asistente experto en operaciones de TI y monitoreo de infraestructura. "
    "Analizas alertas activas de PRTG y generas diagnósticos estructurados en Markdown "
    "para Telegram. Usa los datos exactos del contexto — no inventes información. "
    "El resultado debe ser visual y profesional: usa emojis como íconos de sección, "
    "viñetas (•) para listas anidadas, y bloques de código (```) exclusivamente para "
    "comandos de terminal. No uses asteriscos (*) para negrita."
)


class AlertPromptBuilder:
    """Construye prompts de análisis de alerta a partir de un AlertContext."""

    def build(self, context: AlertContext) -> tuple[str, str]:
        """
        Construye el par (system_prompt, user_prompt) para el LLM.

        Args:
            context: AlertContext con el evento y todos los datos enriquecidos

        Returns:
            (system_prompt, user_prompt)
        """
        user_prompt = "\n\n".join([
            self._seccion_evento(context),
            self._seccion_tickets(context),
            self._seccion_template(context),
            self._instruccion(context),
        ])
        return _SYSTEM, user_prompt

    # ─────────────────────────────────────────────────────────────────────────
    # Secciones del prompt
    # ─────────────────────────────────────────────────────────────────────────

    def _seccion_evento(self, ctx: AlertContext) -> str:
        e = ctx.evento
        lines = ["## ALERTA ACTIVA"]
        lines.append(f"- Equipo: {e.equipo}")
        lines.append(f"- IP: {e.ip}")
        lines.append(f"- Sensor: {e.sensor}")
        lines.append(f"- Status: {e.status}")
        lines.append(f"- Detalle: {e.mensaje}")
        lines.append(f"- Prioridad: {e.prioridad}")
        lines.append(f"- Área atendedora: {e.area_atendedora}")
        lines.append(f"- Responsable atendedor: {e.responsable_atendedor}")
        lines.append(f"- Área administradora: {e.area_administradora}")
        lines.append(f"- Responsable administrador: {e.responsable_administrador}")

        if ctx.contacto_atendedora:
            c = ctx.contacto_atendedora
            lines.append(f"  - Contacto atendedora: {c.correos} | Ext: {c.extensiones}")
        if ctx.contacto_administradora:
            c = ctx.contacto_administradora
            lines.append(f"  - Contacto administradora: {c.correos} | Ext: {c.extensiones}")

        return "\n".join(lines)

    def _seccion_tickets(self, ctx: AlertContext) -> str:
        if not ctx.tickets:
            return (
                "## TICKETS HISTÓRICOS\n"
                "No se encontraron tickets previos para este nodo ni nodos hermanos."
            )

        lines = ["## TICKETS HISTÓRICOS (últimos similares)"]
        for t in ctx.tickets:
            lines.append(f"\n**Ticket:** {t.ticket or 'N/A'}")
            lines.append(f"**Alerta:** {t.alerta}")
            lines.append(f"**Detalle:** {t.detalle}")
            lines.append(f"**Acción correctiva:**\n{t.accion_formateada}")
            lines.append("---")
        return "\n".join(lines)

    def _seccion_template(self, ctx: AlertContext) -> str:
        lines = ["## TEMPLATE Y ESCALAMIENTO"]

        if ctx.template:
            t = ctx.template
            lines.append(f"- Aplicación: {t.aplicacion} (#{t.id_template}) [{t.etiqueta}]")
            if t.gerencia_desarrollo:
                lines.append(f"- Gerencia de desarrollo: {t.gerencia_desarrollo}")
        else:
            lines.append("- Sin template asociado")

        if ctx.matriz:
            lines.append("\n**Matriz de escalamiento:**")
            for nivel in ctx.matriz:
                lines.append(
                    f"  Nivel {nivel.nivel}: {nivel.nombre} ({nivel.puesto}) | "
                    f"Ext: {nivel.extension} | Cel: {nivel.celular} | "
                    f"Email: {nivel.correo} | ⏱ {nivel.tiempo_escalacion} min"
                )
        else:
            lines.append("- Sin matriz de escalamiento")

        return "\n".join(lines)

    def _instruccion(self, ctx: AlertContext) -> str:
        e = ctx.evento
        t = ctx.template

        # ── Cabecera con template ──────────────────────────────────────────
        if t and t.id_template:
            header_line = f"📌 {t.aplicacion} #{t.id_template} | {t.etiqueta}"
        else:
            header_line = ""

        # ── Sección de áreas responsables ─────────────────────────────────
        area_lines = []
        # Atendedora
        area_lines.append(f"Atendedora: {e.area_atendedora}")
        area_lines.append(f"👤 {e.responsable_atendedor}")
        if ctx.contacto_atendedora:
            ca = ctx.contacto_atendedora
            if ca.correos:
                area_lines.append(f"📧 {ca.correos}")
            if ca.extensiones:
                area_lines.append(f"☎️ Ext: {ca.extensiones}")
        # Administradora
        area_lines.append(f"Administradora: {e.area_administradora}")
        area_lines.append(f"👤 {e.responsable_administrador}")
        if ctx.contacto_administradora:
            cm = ctx.contacto_administradora
            if cm.correos:
                area_lines.append(f"📧 {cm.correos}")
            if cm.extensiones:
                area_lines.append(f"☎️ Ext: {cm.extensiones}")

        # ── Matriz de escalamiento ─────────────────────────────────────────
        if ctx.matriz:
            matriz_lines = []
            for nivel in ctx.matriz:
                matriz_lines.append(
                    f"Nivel {nivel.nivel} — {nivel.nombre}\n"
                    f"{nivel.puesto} | Ext: {nivel.extension} | "
                    f"Cel: {nivel.celular} | ⏱ {nivel.tiempo_escalacion} min"
                )
            matriz_str = "\n\n".join(matriz_lines)
        else:
            matriz_str = "Sin matriz de escalamiento registrada."

        # ── Construcción del prompt ────────────────────────────────────────
        estructura = []
        if header_line:
            estructura.append(header_line)
        estructura.append(f"🔴 ALERTA: {e.equipo} ({e.ip})")
        estructura.append(f"📡 Sensor: {e.sensor} — [descripción breve del problema según el mensaje de alerta]")
        estructura.append("")
        estructura.append("👥 Área responsable en operaciones")
        estructura.extend(area_lines)
        estructura.append("")
        estructura.append("📞 Matriz de escalamiento")
        estructura.append(matriz_str)
        estructura.append("")
        estructura.append(
            "🛠 Acciones recomendadas\n"
            "1. [acción concreta basada en tickets históricos; incluye comandos de terminal si aplica]\n"
            "2. [acción]\n"
            "...\n"
            "(máximo 5 acciones)"
        )
        estructura.append("")
        estructura.append(
            "🔍 Posible causa raíz\n"
            "[1-2 oraciones basadas en el historial de tickets o procedimiento estándar]"
        )
        estructura.append("")
        estructura.append(
            "📋 Contexto histórico\n"
            "[Una oración sobre los tickets usados como base o el procedimiento estándar aplicado]"
        )

        formato = "\n".join(estructura)

        return (
            f"## INSTRUCCIÓN\n"
            f"Genera el análisis usando EXACTAMENTE esta estructura. "
            f"No uses asteriscos (*) para negrita. "
            f"Usa bloques de código (```) para comandos de terminal. "
            f"No agregues secciones adicionales. "
            f"No repitas datos ya incluidos en la estructura.\n\n"
            f"{formato}\n\n"
            f"Consulta del operador: \"{ctx.query_usuario}\""
        )
