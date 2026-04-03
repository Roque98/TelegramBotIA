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
import asyncio
import random
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

    # Mensajes específicos por herramienta para set_tool_active()
    _TOOL_MESSAGES: dict[str, str] = {
        "database_query": "🗄️ Consultando base de datos...",
        "knowledge_search": "📚 Buscando en el conocimiento...",
        "calculate": "🔢 Calculando...",
        "datetime": "📅 Consultando fecha y hora...",
        "get_preferences": "👤 Revisando preferencias...",
        "save_preferences": "💾 Guardando preferencias...",
        "save_memory": "🧠 Guardando en memoria...",
        "reload_permissions": "🔐 Recargando permisos...",
        "read_attachment": "📎 Leyendo archivo adjunto...",
    }

    # Mensajes de progreso con personalidad de Amber
    PROCESSING_MESSAGES = [
        "🔄 Analizando tu consulta...",
        "💭 Pensando en la mejor respuesta...",
        "🔍 Revisando la información disponible...",
        "⚙️ Procesando los datos...",
        "📊 Consultando las fuentes...",
        "🧠 Razonando sobre tu pregunta...",
        "💡 Organizando las ideas...",
        "🔎 Verificando los detalles...",
        "📝 Trabajando en la respuesta...",
        "⏳ Esto puede tomar un momento...",
        "🤔 Procesando tu solicitud...",
        "🔬 Evaluando la información...",
        "📌 Considerando los detalles...",
        "🧩 Juntando las piezas...",
        "💬 Formulando una respuesta...",
        "🔁 Procesando, un momento...",
    ]

    def __init__(
        self,
        update: Update,
        initial_message: str = "🔄 Procesando tu solicitud...",
        show_elapsed_time: bool = True,
        auto_update_interval: float = 6.0,
        background_threshold: float = 15.0,
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
        self.background_threshold = background_threshold

        self._status_message: Optional[Message] = None
        self._start_time: float = 0
        self._is_started: bool = False
        self._message_index: int = 0
        self._auto_update_task: Optional[asyncio.Task] = None
        self._background_task: Optional[asyncio.Task] = None
        self._used_messages: set = set()

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

        # Iniciar tarea de actualización automática en background
        self._auto_update_task = asyncio.create_task(self._auto_update_loop())
        # Iniciar tarea de aviso de background (si el proceso supera el umbral)
        self._background_task = asyncio.create_task(self._background_warning())

    async def _auto_update_loop(self) -> None:
        """Loop de actualización automática en background."""
        available = list(self.PROCESSING_MESSAGES)
        random.shuffle(available)
        for msg in available:
            await asyncio.sleep(self.auto_update_interval)
            if not self._status_message or not self._is_started:
                break
            elapsed = time.time() - self._start_time
            text = msg
            if elapsed > 5:
                text += f"\n_({elapsed:.0f}s)_"
            try:
                await self._status_message.edit_text(text)
                logger.debug(f"Auto-update: {msg}")
            except TelegramError as e:
                if "message is not modified" not in str(e).lower():
                    logger.debug(f"Auto-update falló: {e}")

    async def set_phase(self, text: str) -> None:
        """
        Actualizar el mensaje de estado con texto específico.

        Llamado por el event_callback del agente para mostrar
        la fase real en lugar de mensajes aleatorios.

        Args:
            text: Texto a mostrar (ej. "🗄️ Consultando base de datos...")
        """
        if not self._is_started or not self._status_message:
            return

        # Cancelar loop aleatorio ya que tenemos fases reales
        if self._auto_update_task and not self._auto_update_task.done():
            self._auto_update_task.cancel()
            try:
                await self._auto_update_task
            except asyncio.CancelledError:
                pass
            self._auto_update_task = None

        elapsed = time.time() - self._start_time
        if elapsed > 5:
            text += f"\n_({elapsed:.0f}s)_"

        try:
            await self._status_message.edit_text(text)
        except TelegramError as e:
            if "message is not modified" not in str(e).lower():
                logger.debug(f"set_phase falló: {e}")

    async def _background_warning(self) -> None:
        """
        Tarea en background que avisa al usuario si el procesamiento supera el umbral.

        Envía un mensaje NUEVO (no edita el de estado) para no interferir
        con set_phase(). Esto da al usuario feedback de que el bot sigue trabajando.
        """
        await asyncio.sleep(self.background_threshold)
        if not self._is_started:
            return
        try:
            await self.update.message.reply_text(
                "⏳ _Sigo trabajando, esto está tomando más de lo esperado..._\n"
                "_Un momento más, por favor._",
                parse_mode="Markdown",
            )
            logger.debug(f"Background warning enviado después de {self.background_threshold:.0f}s")
        except Exception as e:
            logger.debug(f"Background warning falló (ignorado): {e}")

    async def set_tool_active(self, tool_name: str) -> None:
        """
        Muestra el mensaje de progreso específico para una herramienta.

        Atajo que busca el mensaje predefinido por nombre de tool y llama set_phase().
        Útil cuando se llama una tool directamente sin pasar por agent_events.

        Args:
            tool_name: Nombre de la herramienta (ej. "database_query")
        """
        text = self._TOOL_MESSAGES.get(tool_name, f"🔧 Ejecutando {tool_name}...")
        await self.set_phase(text)

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

        # Cancelar loop de auto-update y tarea de background
        for task in (self._auto_update_task, self._background_task):
            if task and not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
        self._background_task = None

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
                try:
                    await self.update.message.reply_text(
                        final_text,
                        parse_mode='Markdown'
                    )
                except TelegramError as parse_error:
                    if "can't parse entities" in str(parse_error).lower():
                        # Reintento sin Markdown
                        await self.update.message.reply_text(final_text)
                    else:
                        raise
                await self._delete_status_message()
            else:
                # Editar mensaje existente con la respuesta final
                await self._status_message.edit_text(
                    full_message,
                    parse_mode='Markdown'
                )

            logger.debug(f"Operación completada en {total_duration:.2f}s")
        except TelegramError as e:
            # Si falla el parseo de Markdown, intentar sin parse_mode
            if "can't parse entities" in str(e).lower():
                logger.debug(f"Error parseando Markdown, reintentando sin formato: {e}")
                try:
                    # Intentar editar sin Markdown
                    await self._status_message.edit_text(final_text + footer)
                    logger.debug(f"Mensaje enviado sin Markdown en {total_duration:.2f}s")
                except TelegramError as e2:
                    logger.error(f"Error al editar sin Markdown: {e2}")
                    # Último intento: enviar mensaje nuevo sin Markdown
                    try:
                        await self.update.message.reply_text(final_text)
                        await self._delete_status_message()
                    except TelegramError as e3:
                        logger.error(f"Error al enviar mensaje final sin Markdown: {e3}")
            else:
                # Otro tipo de error, intentar enviar como mensaje nuevo
                logger.error(f"Error al completar mensaje de estado: {e}")
                try:
                    await self.update.message.reply_text(final_text)
                    await self._delete_status_message()
                except TelegramError as e2:
                    logger.error(f"Error al enviar mensaje final alternativo: {e2}")

    async def error(self, error_message: str = "Oh no, tuve un problema procesando eso") -> None:
        """
        Marcar operación como fallida y mostrar mensaje de error (con personalidad de Amber).

        Args:
            error_message: Mensaje de error a mostrar
        """
        if not self._is_started:
            logger.warning("StatusMessage no ha sido iniciado")
            return

        if not self._status_message:
            logger.error("No hay mensaje de estado para marcar como error")
            return

        # Cancelar loop de auto-update y tarea de background
        for task in (self._auto_update_task, self._background_task):
            if task and not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
        self._background_task = None

        total_duration = time.time() - self._start_time

        formatted_error = (
            f"❌ **Error**\n\n"
            f"{error_message}\n\n"
            f"_Intenta de nuevo o usa /help si necesitas ayuda_ ✨"
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
