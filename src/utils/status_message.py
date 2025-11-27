"""
Gestor de mensajes de estado progresivo para feedback visual del usuario.

Proporciona mensajes de estado genéricos que se actualizan mientras se procesa
la solicitud del usuario, dando feedback visual de que el bot está trabajando.

Ejemplo de uso:
    >>> async with StatusMessage(update) as status:
    ...     # El mensaje inicial aparece automáticamente
    ...     result = await agent.process_query(query)
    ...     await status.complete(result)
"""
import time
from typing import Optional
from telegram import Update, Message
from telegram.error import TelegramError
import logging

logger = logging.getLogger(__name__)


class StatusMessage:
    """
    Gestor de mensajes de estado progresivo.

    Muestra un mensaje que se actualiza conforme avanza el procesamiento,
    dando feedback visual al usuario.

    Uso como context manager (recomendado):
        >>> async with StatusMessage(update) as status:
        ...     result = await do_work()
        ...     await status.complete(result)

    Uso manual:
        >>> status = StatusMessage(update)
        >>> await status.start()
        >>> # ... hacer trabajo ...
        >>> await status.complete("¡Listo!")
    """

    # Mensajes de estado genéricos
    PROCESSING_MESSAGES = [
        "🔄 Procesando tu solicitud...",
        "💭 Analizando...",
        "⚙️ Trabajando en ello...",
        "✨ Casi listo..."
    ]

    def __init__(
        self,
        update: Update,
        initial_message: str = "🔄 Procesando tu solicitud...",
        show_elapsed_time: bool = True,
        auto_update_interval: float = 3.0
    ):
        """
        Inicializar gestor de mensajes de estado.

        Args:
            update: Objeto Update de Telegram
            initial_message: Mensaje inicial a mostrar
            show_elapsed_time: Si mostrar tiempo transcurrido en el mensaje final
            auto_update_interval: Intervalo para actualización automática (segundos)
        """
        self.update = update
        self.initial_message = initial_message
        self.show_elapsed_time = show_elapsed_time
        self.auto_update_interval = auto_update_interval

        self._status_message: Optional[Message] = None
        self._start_time: float = 0
        self._is_started: bool = False
        self._message_index: int = 0

    async def __aenter__(self):
        """Iniciar context manager."""
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Salir del context manager."""
        # Si hubo una excepción, marcar como error
        if exc_type is not None:
            await self.error("Ocurrió un error al procesar tu solicitud")
        return False  # No suprimir la excepción

    async def start(self) -> None:
        """Iniciar mensaje de estado."""
        if self._is_started:
            logger.warning("StatusMessage ya fue iniciado")
            return

        self._start_time = time.time()
        self._is_started = True
        self._message_index = 0

        # Enviar acción de "escribiendo" primero
        try:
            await self.update.message.chat.send_action("typing")
        except TelegramError as e:
            logger.warning(f"No se pudo enviar acción de typing: {e}")

        # Enviar mensaje inicial
        try:
            self._status_message = await self.update.message.reply_text(
                self.initial_message
            )
            logger.debug(f"Mensaje de estado iniciado: {self._status_message.message_id}")
        except TelegramError as e:
            logger.error(f"Error al enviar mensaje de estado inicial: {e}")

    async def update_progress(self) -> None:
        """
        Actualizar mensaje al siguiente estado genérico.

        Útil para operaciones largas donde quieres mostrar progreso visual.
        """
        if not self._is_started or not self._status_message:
            return

        self._message_index += 1
        if self._message_index >= len(self.PROCESSING_MESSAGES):
            self._message_index = len(self.PROCESSING_MESSAGES) - 1

        new_message = self.PROCESSING_MESSAGES[self._message_index]
        elapsed = time.time() - self._start_time

        if elapsed > 5:  # Mostrar tiempo solo si es > 5 segundos
            new_message += f"\n_({elapsed:.0f}s)_"

        try:
            await self._status_message.edit_text(new_message)
            logger.debug(f"Mensaje actualizado: {new_message}")
        except TelegramError as e:
            if "message is not modified" not in str(e).lower():
                logger.warning(f"No se pudo actualizar mensaje: {e}")

    async def complete(self, final_text: str) -> None:
        """
        Completar operación y reemplazar mensaje con el resultado final.

        Args:
            final_text: Texto final a mostrar (la respuesta al usuario)
        """
        if not self._is_started:
            logger.warning("StatusMessage no ha sido iniciado")
            return

        if not self._status_message:
            logger.error("No hay mensaje de estado para completar")
            return

        # Calcular duración total
        total_duration = time.time() - self._start_time

        # Agregar duración si es solicitado y la operación tomó tiempo significativo
        if self.show_elapsed_time and total_duration >= 1.0:
            footer = f"\n\n_⏱️ {total_duration:.1f}s_"
        else:
            footer = ""

        # Editar mensaje con respuesta final
        try:
            # Telegram tiene límite de 4096 caracteres
            MAX_LENGTH = 4000
            full_message = final_text + footer

            if len(full_message) > MAX_LENGTH:
                # Si es muy largo, enviar mensaje nuevo y eliminar el de estado
                await self.update.message.reply_text(
                    final_text,
                    parse_mode='Markdown'
                )
                await self._delete_status_message()
            else:
                # Editar mensaje existente con la respuesta final
                await self._status_message.edit_text(
                    full_message,
                    parse_mode='Markdown'
                )

            logger.debug(f"Operación completada en {total_duration:.2f}s")
        except TelegramError as e:
            logger.error(f"Error al completar mensaje de estado: {e}")
            # Intentar enviar como mensaje nuevo
            try:
                await self.update.message.reply_text(
                    final_text,
                    parse_mode='Markdown'
                )
                await self._delete_status_message()
            except TelegramError as e2:
                logger.error(f"Error al enviar mensaje final alternativo: {e2}")

    async def error(self, error_message: str = "Lo siento, ocurrió un error al procesar tu solicitud") -> None:
        """
        Marcar operación como fallida y mostrar mensaje de error.

        Args:
            error_message: Mensaje de error a mostrar
        """
        if not self._is_started:
            logger.warning("StatusMessage no ha sido iniciado")
            return

        if not self._status_message:
            logger.error("No hay mensaje de estado para marcar como error")
            return

        total_duration = time.time() - self._start_time

        formatted_error = (
            f"❌ **Error**\n\n"
            f"{error_message}\n\n"
            f"_Por favor, intenta de nuevo o usa /help para más información_"
        )

        try:
            await self._status_message.edit_text(
                formatted_error,
                parse_mode='Markdown'
            )
            logger.debug(f"Mensaje marcado como error después de {total_duration:.2f}s")
        except TelegramError as e:
            logger.error(f"Error al marcar mensaje como fallido: {e}")

    async def _delete_status_message(self) -> None:
        """Eliminar mensaje de estado (uso interno)."""
        if self._status_message:
            try:
                await self._status_message.delete()
                logger.debug("Mensaje de estado eliminado")
            except TelegramError as e:
                logger.warning(f"No se pudo eliminar mensaje de estado: {e}")

    def get_elapsed_time(self) -> float:
        """
        Obtener tiempo transcurrido desde el inicio.

        Returns:
            Segundos transcurridos
        """
        if not self._is_started:
            return 0.0
        return time.time() - self._start_time
