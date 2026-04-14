"""
AdminNotifier — Notificaciones de errores críticos al administrador via Telegram.

Envía mensajes a todos los admins con Telegram verificado y activo.
Los destinatarios se resuelven dinámicamente via el callable `get_admin_ids`
inyectado al crear el notifier — ver factory.py.

Rate limiting: máximo 1 notificación por tipo de error cada 5 minutos para evitar spam.
"""

import asyncio
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

    # Deduplicar para evitar envíos dobles si el SP retorna filas repetidas
    unique_ids = list(dict.fromkeys(chat_ids))
    if not unique_ids:
        logger.warning("AdminNotifier: no hay admins con Telegram verificado, notificación omitida")
        return

    text = _build_message(level=level, error=error, message=message, user_info=user_info)

    sent = 0
    for chat_id in unique_ids:
        try:
            await bot.send_message(chat_id=chat_id, text=text, parse_mode="MarkdownV2")
            sent += 1
        except Exception as e:
            logger.error(f"AdminNotifier: error enviando a chat_id={chat_id}: {e}")

    if sent:
        logger.info(f"AdminNotifier: notificación [{level}] enviada a {sent} admin(s)")


_MARKDOWNV2_SPECIAL = r"\_*[]()~`>#+-=|{}.!"


def _esc(text: str) -> str:
    """Escapa caracteres especiales de MarkdownV2."""
    for ch in _MARKDOWNV2_SPECIAL:
        text = text.replace(ch, f"\\{ch}")
    return text


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


def fire_admin_notify(
    bot: Any,
    get_admin_ids: Optional[Callable[[], Awaitable[list[int]]]],
    *,
    level: str = "ERROR",
    error: Optional[BaseException] = None,
    user_info: str = "desconocido",
    message: str = "",
) -> None:
    """Fire-and-forget: programa notify_admin como tarea async sin bloquear.

    Si get_admin_ids es None, no hace nada. Debe llamarse desde un contexto
    donde haya un event loop activo (dentro de un handler async de Telegram).
    """
    if not get_admin_ids:
        return
    asyncio.create_task(
        notify_admin(
            bot=bot,
            get_admin_ids=get_admin_ids,
            level=level,
            error=error,
            user_info=user_info,
            message=message,
        )
    )


def reset_rate_cache() -> None:
    """Limpia el cache de rate limiting. Útil en tests."""
    _rate_cache.clear()
