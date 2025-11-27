"""
Handlers para consultas en lenguaje natural.

Maneja mensajes de texto que no son comandos y los procesa con el agente LLM.

Requiere autenticación y validación de permisos.
"""
import logging
import time
from telegram import Update
from telegram.ext import MessageHandler, filters, ContextTypes, Application
from src.agent.llm_agent import LLMAgent
from src.auth import PermissionChecker

logger = logging.getLogger(__name__)


class QueryHandler:
    """Handler para procesar consultas en lenguaje natural."""

    def __init__(self, agent: LLMAgent):
        """
        Inicializar el handler de consultas.

        Args:
            agent: Instancia del agente LLM
        """
        self.agent = agent
        logger.info("QueryHandler inicializado")

    async def handle_text_message(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
    ):
        """
        Manejar mensajes de texto del usuario.

        Valida autenticación y permisos antes de procesar la consulta.

        Args:
            update: Objeto de actualización de Telegram
            context: Contexto de la conversación
        """
        user_message = update.message.text
        user = update.effective_user
        chat_id = user.id
        start_time = time.time()

        # Obtener usuario autenticado del context (lo pone el middleware de auth)
        telegram_user = context.user_data.get('telegram_user')

        # Si no hay usuario autenticado, verificar autenticación
        if not telegram_user:
            from src.auth import UserManager
            db_manager = context.bot_data.get('db_manager')

            if not db_manager:
                await update.message.reply_text(
                    "❌ Error de configuración del sistema."
                )
                return

            with db_manager.get_session() as session:
                user_manager = UserManager(session)
                telegram_user = user_manager.get_user_by_chat_id(chat_id)

                if not telegram_user:
                    await update.message.reply_text(
                        "⚠️ No estás registrado en el sistema.\n\n"
                        "Por favor, usa /register para registrarte."
                    )
                    return

                if not telegram_user.is_verified:
                    await update.message.reply_text(
                        "⚠️ Tu cuenta no está verificada.\n\n"
                        "Consulta tu código de verificación en el Portal de Consola de Monitoreo.\n"
                        "Luego usa: /verify <codigo>"
                    )
                    return

                if not telegram_user.is_active:
                    await update.message.reply_text(
                        "⚠️ Tu cuenta está inactiva.\n\n"
                        "Por favor, contacta al administrador."
                    )
                    return

                # Guardar en context
                context.user_data['telegram_user'] = telegram_user

        logger.info(
            f"Usuario {telegram_user.id_usuario} ({telegram_user.nombre_completo}): "
            f"{user_message[:50]}..."
        )

        # Obtener db_manager
        db_manager = context.bot_data.get('db_manager')

        # Verificar permiso para consultas (comando /ia)
        with db_manager.get_session() as session:
            permission_checker = PermissionChecker(session)

            # Verificar permiso para hacer consultas con IA
            permission = permission_checker.check_permission(
                telegram_user.id_usuario,
                '/ia'
            )

            if not permission.is_allowed:
                # Registrar intento denegado
                permission_checker.log_operation(
                    user_id=telegram_user.id_usuario,
                    comando='/ia',
                    telegram_chat_id=chat_id,
                    telegram_username=user.username,
                    parametros={'query': user_message[:100]},
                    resultado='DENEGADO',
                    mensaje_error=permission.mensaje
                )

                await update.message.reply_text(
                    f"🚫 *Acceso Denegado*\n\n"
                    f"No tienes permiso para realizar consultas con IA.\n\n"
                    f"_{permission.mensaje}_",
                    parse_mode='Markdown'
                )
                return

        # Mostrar indicador de "escribiendo..."
        await update.message.chat.send_action("typing")

        try:
            # Procesar la consulta con el agente
            response = await self.agent.process_query(user_message)

            # Enviar respuesta al usuario
            await self._send_response(update, response)

            # Calcular duración
            duration_ms = int((time.time() - start_time) * 1000)

            # Registrar operación exitosa
            with db_manager.get_session() as session:
                permission_checker = PermissionChecker(session)
                permission_checker.log_operation(
                    user_id=telegram_user.id_usuario,
                    comando='/ia',
                    telegram_chat_id=chat_id,
                    telegram_username=user.username,
                    parametros={'query': user_message[:200]},
                    resultado='EXITOSO',
                    duracion_ms=duration_ms
                )

            logger.info(
                f"Respuesta enviada exitosamente a usuario {telegram_user.id_usuario} "
                f"({duration_ms}ms)"
            )

        except Exception as e:
            logger.error(
                f"Error procesando mensaje de usuario {telegram_user.id_usuario}: {e}",
                exc_info=True
            )

            # Registrar error
            duration_ms = int((time.time() - start_time) * 1000)
            with db_manager.get_session() as session:
                permission_checker = PermissionChecker(session)
                permission_checker.log_operation(
                    user_id=telegram_user.id_usuario,
                    comando='/ia',
                    telegram_chat_id=chat_id,
                    telegram_username=user.username,
                    parametros={'query': user_message[:200]},
                    resultado='ERROR',
                    mensaje_error=str(e),
                    duracion_ms=duration_ms
                )

            await self._send_error_message(update, user_friendly=True)

    async def _send_response(self, update: Update, response: str):
        """
        Enviar respuesta al usuario, manejando mensajes largos.

        Args:
            update: Objeto de actualización de Telegram
            response: Respuesta a enviar
        """
        # Telegram tiene un límite de 4096 caracteres por mensaje
        MAX_MESSAGE_LENGTH = 4000  # Dejamos margen de seguridad

        if len(response) <= MAX_MESSAGE_LENGTH:
            # Enviar en un solo mensaje
            await update.message.reply_text(
                response,
                parse_mode='Markdown'
            )
        else:
            # Dividir en múltiples mensajes
            await self._send_long_response(update, response, MAX_MESSAGE_LENGTH)

    async def _send_long_response(
        self,
        update: Update,
        response: str,
        max_length: int
    ):
        """
        Dividir y enviar respuestas largas en múltiples mensajes.

        Args:
            update: Objeto de actualización de Telegram
            response: Respuesta a enviar
            max_length: Longitud máxima por mensaje
        """
        # Dividir por saltos de línea para no cortar información a mitad
        lines = response.split('\n')
        current_message = ""

        for line in lines:
            # Si agregar esta línea excede el límite, enviar el mensaje actual
            if len(current_message) + len(line) + 1 > max_length:
                if current_message:
                    await update.message.reply_text(
                        current_message,
                        parse_mode='Markdown'
                    )
                    current_message = line + '\n'
                else:
                    # La línea sola es más larga que el límite, enviarla directamente
                    await update.message.reply_text(
                        line[:max_length],
                        parse_mode='Markdown'
                    )
            else:
                current_message += line + '\n'

        # Enviar el último fragmento
        if current_message:
            await update.message.reply_text(
                current_message,
                parse_mode='Markdown'
            )

    async def _send_error_message(self, update: Update, user_friendly: bool = True):
        """
        Enviar mensaje de error al usuario.

        Args:
            update: Objeto de actualización de Telegram
            user_friendly: Si debe mostrarse mensaje amigable o técnico
        """
        if user_friendly:
            error_message = (
                "❌ **Error al procesar tu consulta**\n\n"
                "Lo siento, ocurrió un error inesperado. "
                "Por favor, intenta de nuevo o reformula tu pregunta.\n\n"
                "Si el problema persiste, usa /help para más información."
            )
        else:
            error_message = (
                "❌ **Error Técnico**\n\n"
                "Ocurrió un error al procesar tu solicitud. "
                "Por favor, contacta al administrador."
            )

        await update.message.reply_text(
            error_message,
            parse_mode='Markdown'
        )


def register_query_handlers(application: Application, agent: LLMAgent) -> None:
    """
    Registrar handler de queries en la aplicación.

    Args:
        application: Aplicación de Telegram
        agent: Instancia del agente LLM
    """
    # Crear instancia del handler
    query_handler = QueryHandler(agent)

    # Registrar handler para mensajes de texto que NO son comandos
    application.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            query_handler.handle_text_message
        )
    )

    logger.info("Query handlers registrados exitosamente")
