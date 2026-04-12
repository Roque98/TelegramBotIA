"""
AdminNotifier — Notificaciones de errores críticos al administrador via Telegram.

Envía mensajes a todos los admins con Telegram verificado y activo.
Los destinatarios se resuelven dinámicamente via el callable `get_admin_ids`
inyectado al crear el notifier — ver factory.py.

Rate limiting: máximo 1 notificación por tipo de error cada 5 minutos para evitar spam.
"""

import logging
import time
import traceback
from datetime import datetime
from typing import Any, Awaitable, Callable, Optional

logger = logging.getLogger(__name__)

# Rate limiting: {clave_de_error: timestamp_ultimo_envio}
_rate_cache: dict[str, float] = {}
_RATE_LIMIT_SECONDS = 300  # 5 minutos


async def notify_admin(
    bot: Any,
    get_admin_ids: Callable[[], Awaitable[list[int]]],
    level: str = "ERROR",
    error: Optional[BaseException] = None,
    message: str = "",
    user_info: str = "desconocido",
) -> None:
    """
    Envía una notificación de error al admin via Telegram.

    Args:
        bot: Objeto Bot de python-telegram-bot
        get_admin_ids: Callable async sin argumentos que retorna lista de chat IDs
        level: Nivel de severidad ("ERROR", "CRITICAL", "WARNING")
        error: Excepción capturada (opcional)
        message: Mensaje descriptivo adicional
        user_info: Info del usuario afectado para el mensaje
    """
    error_type = type(error).__name__ if error else "generic"
    rate_key = f"{level}:{error_type}"
    now = time.time()

    if rate_key in _rate_cache and now - _rate_cache[rate_key] < _RATE_LIMIT_SECONDS:
        logger.debug(f"AdminNotifier: rate limit activo para '{rate_key}', omitiendo")
        return
    _rate_cache[rate_key] = now

    try:
        chat_ids = await get_admin_ids()
    except Exception as e:
        logger.error(f"AdminNotifier: error obteniendo admin chat IDs: {e}")
        return

    if not chat_ids:
        logger.warning("AdminNotifier: no hay admins con Telegram verificado, notificación omitida")
        return

    text = _build_message(level=level, error=error, message=message, user_info=user_info)

    sent = 0
    for chat_id in chat_ids:
        try:
            await bot.send_message(chat_id=chat_id, text=text, parse_mode="Markdown")
            sent += 1
        except Exception as e:
            logger.error(f"AdminNotifier: error enviando a chat_id={chat_id}: {e}")

    if sent:
        logger.info(f"AdminNotifier: notificación [{level}] enviada a {sent} admin(s)")


def _build_message(
    level: str,
    error: Optional[BaseException],
    message: str,
    user_info: str,
) -> str:
    """Construye el texto del mensaje de notificación."""
    emoji = {"CRITICAL": "🚨", "ERROR": "❌", "WARNING": "⚠️"}.get(level, "⚠️")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    lines = [
        f"{emoji} *\\[{level}\\] Iris Bot*",
        f"_{timestamp}_",
        f"*Usuario:* `{user_info}`",
    ]

    if message:
        lines.append(f"*Detalle:* {message}")

    if error:
        error_type = type(error).__name__
        error_msg = str(error)[:200]
        lines.append(f"*Error:* `{error_type}: {error_msg}`")

        tb_lines = traceback.format_tb(error.__traceback__)
        if tb_lines:
            last_frame = tb_lines[-1].strip().replace("`", "'")[:300]
            lines.append(f"*Traceback:*\n```\n{last_frame}\n```")

    return "\n".join(lines)


def reset_rate_cache() -> None:
    """Limpia el cache de rate limiting. Útil en tests."""
    _rate_cache.clear()
