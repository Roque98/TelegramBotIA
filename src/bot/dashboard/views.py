"""
Vistas del dashboard — funciones de renderizado.

Cada función retorna (text: str, keyboard: InlineKeyboardMarkup).
Usa HTML parse_mode: más simple de escapar que MarkdownV2.
"""
from datetime import datetime
from telegram import InlineKeyboardButton, InlineKeyboardMarkup


# ──────────────────────────────────────────────────────────────────────────────
# Helpers internos
# ──────────────────────────────────────────────────────────────────────────────

def _h(text: str) -> str:
    """Escape HTML mínimo para contenido dinámico."""
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _sep() -> str:
    return "──────────────────"


def _truncate(text: str, limit: int = 4000) -> str:
    if len(text) <= limit:
        return text
    return text[:limit] + "\n<i>… (truncado)</i>"


def _back_row() -> list:
    return [InlineKeyboardButton("🔙 Menú", callback_data="dash:menu")]


def _refresh_back_row(refresh_callback: str) -> list:
    return [
        InlineKeyboardButton("🔄 Refrescar", callback_data=refresh_callback),
        InlineKeyboardButton("🔙 Menú", callback_data="dash:menu"),
    ]


# ──────────────────────────────────────────────────────────────────────────────
# Menú principal
# ──────────────────────────────────────────────────────────────────────────────

def render_menu() -> tuple[str, InlineKeyboardMarkup]:
    now = datetime.now().strftime("%d %b %Y · %H:%M")
    text = (
        f"📊 <b>IRIS Dashboard</b>\n"
        f"{_sep()}\n"
        f"📅 {now}\n\n"
        f"Selecciona una sección:"
    )
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📊 Overview", callback_data="dash:overview:hoy"),
            InlineKeyboardButton("🚨 Alertas", callback_data="dash:alerts"),
        ],
        [
            InlineKeyboardButton("📋 Logs", callback_data="dash:logs:1"),
            InlineKeyboardButton("🤖 Agentes", callback_data="dash:agents"),
        ],
        [
            InlineKeyboardButton("👥 Usuarios", callback_data="dash:users"),
            InlineKeyboardButton("📚 Knowledge", callback_data="dash:knowledge"),
        ],
    ])
    return text, keyboard


# ──────────────────────────────────────────────────────────────────────────────
# Overview
# ──────────────────────────────────────────────────────────────────────────────

_PERIODO_LABELS = {"hoy": "Hoy", "ayer": "Ayer", "7d": "7 días", "30d": "30 días"}


def render_overview(data: dict, periodo: str) -> tuple[str, InlineKeyboardMarkup]:
    label = _PERIODO_LABELS.get(periodo, periodo)
    pct = data["mensajes_pct_change"]
    pct_str = f" ({'↑' if pct >= 0 else '↓'}{abs(pct)}%)" if pct != 0 else ""

    agentes_text = ""
    for ag in data["agentes"][:3]:
        agentes_text += f"  • <b>{_h(ag['nombre'])}</b> · {ag['requests']} req · {ag['exito_pct']}%✓\n"
    if not agentes_text:
        agentes_text = "  Sin datos\n"

    text = (
        f"📊 <b>Overview</b> · <b>{label}</b>\n"
        f"{_sep()}\n"
        f"💬 Mensajes:        <b>{data['mensajes']}</b>{pct_str}\n"
        f"👥 Usuarios activos: <b>{data['usuarios_activos']}</b>\n"
        f"❌ Errores:         <b>{data['errores']}</b>\n"
        f"💸 Costo:           <b>${data['costo']:.4f}</b>\n\n"
        f"⏱ <b>Latencia:</b>\n"
        f"  P50: {data['p50_s']}s  ·  P90: {data['p90_s']}s\n\n"
        f"🤖 <b>Top agentes:</b>\n"
        f"{agentes_text}"
    )

    periodos = ["hoy", "ayer", "7d", "30d"]
    filtros_row = [
        InlineKeyboardButton(
            f"{'✓ ' if p == periodo else ''}{_PERIODO_LABELS[p]}",
            callback_data=f"dash:overview:{p}",
        )
        for p in periodos
    ]
    keyboard = InlineKeyboardMarkup([
        filtros_row,
        _refresh_back_row(f"dash:overview:{periodo}"),
    ])
    return _truncate(text), keyboard


# ──────────────────────────────────────────────────────────────────────────────
# Alertas
# ──────────────────────────────────────────────────────────────────────────────

_PRIORIDAD_ICON = {5: "🔴", 4: "🔴", 3: "🟠", 2: "🟡", 1: "🟢"}


def render_alerts(data: dict) -> tuple[str, InlineKeyboardMarkup]:
    if "error" in data and not data["alertas"]:
        text = (
            f"🚨 <b>Alertas Activas</b>\n"
            f"{_sep()}\n"
            f"⚠️ No se pudo conectar a la BD de monitoreo.\n"
            f"<i>{_h(data['error'])}</i>"
        )
        keyboard = InlineKeyboardMarkup([_refresh_back_row("dash:alerts")])
        return text, keyboard

    criticos = data["criticos"]
    warnings = data["warnings"]
    alertas = data["alertas"]

    if not alertas:
        text = (
            f"🚨 <b>Alertas Activas</b>\n"
            f"{_sep()}\n"
            f"✅ Sin alertas activas en este momento."
        )
    else:
        lines = [
            f"🚨 <b>Alertas Activas</b>",
            f"{_sep()}",
            f"🔴 Críticas: <b>{criticos}</b>   ⚠️ Warnings: <b>{warnings}</b>",
            "",
        ]
        for i, a in enumerate(alertas[:10], 1):
            icon = _PRIORIDAD_ICON.get(a["prioridad"], "⚪")
            lines.append(
                f"{icon} <b>{_h(a['equipo'])}</b> · {_h(a['ip'])}\n"
                f"   {_h(a['sensor'])} · {_h(a['status'])} · P{a['prioridad']}"
            )
        if len(alertas) > 10:
            lines.append(f"\n<i>… y {len(alertas) - 10} más</i>")
        text = "\n".join(lines)

    keyboard = InlineKeyboardMarkup([_refresh_back_row("dash:alerts")])
    return _truncate(text), keyboard


# ──────────────────────────────────────────────────────────────────────────────
# Logs
# ──────────────────────────────────────────────────────────────────────────────

def render_logs(data: dict) -> tuple[str, InlineKeyboardMarkup]:
    page = data["page"]
    total_pages = data["total_pages"]
    logs = data["logs"]

    lines = [
        f"📋 <b>Logs Recientes</b>  <i>(pág. {page}/{total_pages})</i>",
        _sep(),
    ]
    for i, log in enumerate(logs, 1):
        estado = "✅" if log["exitoso"] else "❌"
        duracion = f"{log['duracion_ms']}ms"
        query_short = _h(log["query"][:45]) + ("…" if len(log["query"]) > 45 else "")
        lines.append(
            f"{estado} <b>@{_h(log['username'])}</b> · {_h(log['agente'])} · {duracion}\n"
            f"   <i>{query_short}</i>"
        )

    text = "\n".join(lines)

    nav_row = []
    if page > 1:
        nav_row.append(InlineKeyboardButton("◀", callback_data=f"dash:logs:{page - 1}"))
    nav_row.append(InlineKeyboardButton(f"· {page}/{total_pages} ·", callback_data="dash:noop"))
    if page < total_pages:
        nav_row.append(InlineKeyboardButton("▶", callback_data=f"dash:logs:{page + 1}"))

    keyboard = InlineKeyboardMarkup([
        nav_row,
        _back_row(),
    ])
    return _truncate(text), keyboard


# ──────────────────────────────────────────────────────────────────────────────
# Agentes
# ──────────────────────────────────────────────────────────────────────────────

def render_agents(agents: list) -> tuple[str, InlineKeyboardMarkup]:
    lines = [f"🤖 <b>Agentes Activos</b> ({len(agents)})", _sep()]
    for ag in agents:
        modelo = ag["modelo_override"] or "default"
        generalista = " · generalista" if ag["es_generalista"] else ""
        lines.append(
            f"<b>{_h(ag['nombre'])}</b>{generalista}\n"
            f"  Modelo: {_h(modelo)} · T: {ag['temperatura']} · v{ag['version']}\n"
            f"  Tools: {ag['tools_count']} · Hoy: {ag['requests_hoy']} req"
        )
        if ag["descripcion"]:
            lines.append(f"  <i>{_h(ag['descripcion'])}</i>")

    text = "\n".join(lines)
    keyboard = InlineKeyboardMarkup([_refresh_back_row("dash:agents")])
    return _truncate(text), keyboard


# ──────────────────────────────────────────────────────────────────────────────
# Usuarios
# ──────────────────────────────────────────────────────────────────────────────

_ESTADO_ICON = {"ACTIVO": "✅", "INACTIVO": "⏸", "BLOQUEADO": "🚫"}


def render_users(users: list) -> tuple[str, InlineKeyboardMarkup]:
    lines = [f"👥 <b>Usuarios Registrados</b> ({len(users)})", _sep()]
    for u in users:
        icon = _ESTADO_ICON.get(u["estado"], "❓")
        verificado = "✓" if u["verificado"] else "✗ sin verificar"
        ultima = u["ultima_actividad"][:10] if u["ultima_actividad"] else "—"
        lines.append(
            f"{icon} <b>{_h(u['nombre'])}</b> · {_h(u['rol'])}\n"
            f"  {verificado} · última act.: {ultima}"
        )

    text = "\n".join(lines)
    keyboard = InlineKeyboardMarkup([_refresh_back_row("dash:users")])
    return _truncate(text), keyboard


# ──────────────────────────────────────────────────────────────────────────────
# Knowledge
# ──────────────────────────────────────────────────────────────────────────────

def render_knowledge(data: dict) -> tuple[str, InlineKeyboardMarkup]:
    lines = [
        f"📚 <b>Base de Conocimiento</b>",
        _sep(),
        f"📦 Categorías:    <b>{data['total_categorias']}</b>",
        f"📄 Entradas:      <b>{data['total_entradas']}</b>",
        f"🔍 Búsquedas hoy: <b>{data['busquedas_hoy']}</b>",
        "",
        "<b>Categorías:</b>",
    ]
    for cat in data["categorias"]:
        icon = cat["icono"] or "📁"
        lines.append(f"  {icon} {_h(cat['nombre'])} · {cat['entradas']} entradas")

    text = "\n".join(lines)
    keyboard = InlineKeyboardMarkup([_refresh_back_row("dash:knowledge")])
    return _truncate(text), keyboard
