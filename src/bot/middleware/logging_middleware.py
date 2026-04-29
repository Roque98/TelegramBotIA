"""
Middleware de logging para el bot.

Intercepta y loggea todas las actualizaciones del bot para tracking y debugging.
"""
import logging
import time
from telegram import Update
from telegram.error import Conflict as TelegramConflict
from telegram.error import NetworkError as TelegramNetworkError
from telegram.ext import Application, BaseHandler
from typing import Callable

logger = logging.getLogger(__name__)


class LoggingMiddleware:
    """Middleware para loggear actualizaciones del bot."""

    def __init__(self, log_level: str = "INFO"):
        """
        Inicializar el middleware.

        Args:
            log_level: Nivel de logging (DEBUG, INFO, WARNING, ERROR)
        """
        self.log_level = getattr(logging, log_level.upper())
        logger.setLevel(self.log_level)
        logger.info("Middleware de logging inicializado")

    async def log_update(self, update: Update, context) -> None:
        """
        Loggear información sobre una actualización.

        Args:
            update: Objeto de actualización de Telegram
            context: Contexto de la aplicación
        """
        if not update:
            return

        # Extraer información del usuario
        user = update.effective_user
        chat = update.effective_chat

        # Construir mensaje de log
        log_parts = []

        if user:
            log_parts.append(f"User: {user.id} (@{user.username or 'sin_username'})")

        if chat:
            log_parts.append(f"Chat: {chat.id} ({chat.type})")

        # Tipo de actualización
        if update.message:
            if update.message.text:
                text = update.message.text[:50]  # Limitar longitud
                log_parts.append(f"Message: '{text}'")
            elif update.message.photo:
                log_parts.append("Message: [PHOTO]")
            elif update.message.document:
                log_parts.append("Message: [DOCUMENT]")
            else:
                log_parts.append("Message: [OTHER]")

        elif update.callback_query:
            callback_data = update.callback_query.data
            log_parts.append(f"Callback: '{callback_data}'")

        elif update.inline_query:
            query = update.inline_query.query[:50]
            log_parts.append(f"InlineQuery: '{query}'")

        # Loggear
        log_message = " | ".join(log_parts)
        logger.debug(f"📥 {log_message}")

    async def log_error(self, update: Update, context) -> None:
        """
        Loggear errores que ocurren durante el procesamiento.

        Args:
            update: Objeto de actualización de Telegram
            context: Contexto de la aplicación
        """
        error = context.error

        if isinstance(error, TelegramNetworkError):
            logger.warning("NetworkError transitorio (ignorado): %s", error)
            return

        if isinstance(error, TelegramConflict):
            logger.warning("Conflict de polling (reinicio del bot, ignorado): %s", error)
            return

        # Información del usuario
        user_info = "Unknown"
        if update and update.effective_user:
            user = update.effective_user
            user_info = f"{user.id} (@{user.username or 'sin_username'})"

        # Loggear error
        logger.error(
            f"❌ Error para usuario {user_info}: {error}",
            exc_info=error
        )

        # Notificar al admin via Telegram (fire-and-forget, no bloquea el error handler)
        try:
            admin_notify = context.bot_data.get("admin_notify") if context.bot_data else None
            if admin_notify:
                admin_notify(context.bot, level="ERROR", error=error, user_info=user_info)
        except Exception as notify_err:
            logger.debug(f"AdminNotifier no disponible: {notify_err}")


class PerformanceMiddleware:
    """Middleware para medir performance de handlers."""

    def __init__(self):
        """Inicializar el middleware."""
        logger.info("Middleware de performance inicializado")

    async def measure_performance(
        self,
        update: Update,
        context,
        handler_callback: Callable
    ) -> None:
        """
        Medir el tiempo de ejecución de un handler.

        Args:
            update: Objeto de actualización de Telegram
            context: Contexto de la aplicación
            handler_callback: Callback del handler a ejecutar
        """
        start_time = time.time()

        # Ejecutar el handler
        await handler_callback(update, context)

        # Calcular tiempo transcurrido
        elapsed_time = time.time() - start_time

        # Loggear si tarda más de 1 segundo
        if elapsed_time > 1.0:
            logger.warning(
                f"⚠️ Handler lento: {handler_callback.__name__} "
                f"tardó {elapsed_time:.2f}s"
            )
        else:
            logger.debug(f"⏱️ Handler: {handler_callback.__name__} - {elapsed_time:.2f}s")


def setup_logging_middleware(application: Application) -> None:
    """
    Configurar middleware de logging en la aplicación.

    Args:
        application: Aplicación de Telegram
    """
    # Crear instancia del middleware
    logging_middleware = LoggingMiddleware()

    # Registrar error handler
    application.add_error_handler(logging_middleware.log_error)

    logger.info("Middleware de logging configurado exitosamente")

