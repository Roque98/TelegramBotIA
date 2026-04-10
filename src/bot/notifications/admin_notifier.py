"""
AdminNotifier — Notificaciones de errores críticos al administrador via Telegram.

Resuelve los destinatarios dinámicamente desde la BD (usuarios con rol Administrador
verificados y activos), sin depender de admin_chat_ids hardcodeados en settings.

Rate limiting: máximo 1 notificación por tipo de error cada 5 minutos para evitar spam.

Uso típico (desde log_error en logging_middleware):
    await notify_admin(
        bot=context.bot,
        db_manager=context.bot_data.get("db_manager"),
        level="ERROR",
        error=context.error,
        user_info="12345 (@juan)",
    )
"""

import logging
import time
import traceback
from datetime import datetime
from typing import Any, Optional

logger = logging.getLogger(__name__)

# Rate limiting: {clave_de_error: timestamp_ultimo_envio}
_rate_cache: dict[str, float] = {}
_RATE_LIMIT_SECONDS = 300  # 5 minutos


async def notify_admin(
    bot: Any,
    db_manager: Any = None,
    level: str = "ERROR",
    error: Optional[BaseException] = None,
    message: str = "",
    user_info: str = "desconocido",
) -> None:
    """
    Envía una notificación de error al admin via Telegram.

    Obtiene los chat IDs de admins desde la BD. Si no hay admins con Telegram
    verificado, loggea un warning y retorna sin fallar.

    Args:
        bot: Objeto Bot de python-telegram-bot
        db_manager: Gestor de BD para consultar los admins
        level: Nivel de severidad ("ERROR", "CRITICAL", "WARNING")
        error: Excepción capturada (opcional)
        message: Mensaje descriptivo adicional
        user_info: Info del usuario afectado para el mensaje
    """
    # Construir clave para rate limiting
    error_type = type(error).__name__ if error else "generic"
    rate_key = f"{level}:{error_type}"
    now = time.time()

    if rate_key in _rate_cache and now - _rate_cache[rate_key] < _RATE_LIMIT_SECONDS:
        logger.debug(f"AdminNotifier: rate limit activo para '{rate_key}', omitiendo")
        return
    _rate_cache[rate_key] = now

    # Obtener chat IDs de admins desde BD
    chat_ids = await _get_admin_chat_ids(db_manager)
    if not chat_ids:
        logger.warning("AdminNotifier: no hay admins con Telegram verificado, notificación omitida")
        return

    text = _build_message(level=level, error=error, message=message, user_info=user_info)

    sent = 0
    for chat_id in chat_ids:
        try:
            await bot.send_message(chat_id=chat_id, text=text, parse_mode="MarkdownV2")
            sent += 1
        except Exception as e:
            logger.error(f"AdminNotifier: error enviando a chat_id={chat_id}: {e}")

    if sent:
        logger.info(f"AdminNotifier: notificación [{level}] enviada a {sent} admin(s)")


# ---------------------------------------------------------------------------
# Helpers internos
# ---------------------------------------------------------------------------

async def _get_admin_chat_ids(db_manager: Any) -> list[int]:
    """Consulta los chat IDs de admins desde BD."""
    if not db_manager:
        return []
    try:
        from src.domain.auth.user_query_repository import UserQueryRepository
        repo = UserQueryRepository(db_manager)
        return await repo.get_admin_chat_ids()
    except Exception as e:
        logger.error(f"AdminNotifier: error consultando admin chat IDs: {e}")
        return []


def _esc(text: str) -> str:
    """Escapa texto para MarkdownV2 de Telegram."""
    import re
    return re.sub(r'([_\*\[\]\(\)~`>#+\-=|{}.!])', r'\\\1', text)


def _build_message(
    level: str,
    error: Optional[BaseException],
    message: str,
    user_info: str,
) -> str:
    """Construye el texto del mensaje de notificación en formato MarkdownV2."""
    emoji = {"CRITICAL": "🚨", "ERROR": "❌", "WARNING": "⚠️"}.get(level, "⚠️")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    lines = [
        f"{emoji} *\\[{_esc(level)}\\] Iris Bot*",
        f"_{_esc(timestamp)}_",
        f"*Usuario:* `{_esc(user_info)}`",
    ]

    if message:
        lines.append(f"*Detalle:* {_esc(message)}")

    if error:
        error_type = type(error).__name__
        error_msg = str(error)[:200]
        # Dentro de `inline code` solo se escapan ` y \
        safe_error = f"{error_type}: {error_msg}".replace('\\', '\\\\').replace('`', '\\`')
        lines.append(f"*Error:* `{safe_error}`")

        tb_lines = traceback.format_tb(error.__traceback__)
        if tb_lines:
            # Solo la última línea del traceback; dentro de ``` solo se escapan ` y \
            last_frame = tb_lines[-1].strip()[:300]
            safe_frame = last_frame.replace('\\', '\\\\').replace('`', '\\`')
            lines.append(f"*Traceback:*\n```\n{safe_frame}\n```")

    return "\n".join(lines)


def reset_rate_cache() -> None:
    """Limpia el cache de rate limiting. Útil en tests."""
    _rate_cache.clear()
