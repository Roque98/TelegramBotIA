"""
Bot de Telegram principal.

Refactorizado para actuar como orquestador de routing únicamente.
Toda la lógica de handlers está delegada a módulos especializados.
"""
import logging
from telegram import Update
from telegram.ext import Application
from src.config.settings import settings
from src.agent.llm_agent import LLMAgent
from src.database.connection import DatabaseManager
from .handlers import (
    register_command_handlers,
    register_query_handlers,
    register_registration_handlers,
    register_tools_handlers
)
from .middleware import setup_logging_middleware, setup_auth_middleware

logger = logging.getLogger(__name__)


class TelegramBot:
    """
    Bot de Telegram con capacidades de agente de base de datos.

    Actúa como orquestador de routing, delegando toda la lógica
    a handlers especializados.
    """

    def __init__(self):
        """Inicializar el bot."""
        logger.info("Inicializando TelegramBot...")

        # Inicializar agente LLM
        self.agent = LLMAgent()

        # Inicializar gestor de base de datos
        self.db_manager = DatabaseManager()

        # Inicializar sistema de Tools
        logger.info("Inicializando sistema de Tools...")
        from src.tools import initialize_builtin_tools
        initialize_builtin_tools()
        logger.info("Sistema de Tools inicializado correctamente")

        # Inicializar aplicación de Telegram
        self.application = (
            Application.builder()
            .token(settings.telegram_bot_token)
            .build()
        )

        # Inyectar dependencias en bot_data para acceso global
        self.application.bot_data['db_manager'] = self.db_manager
        self.application.bot_data['agent'] = self.agent

        # Configurar middleware
        self._setup_middleware()

        # Configurar handlers
        self._setup_handlers()

        logger.info(
            f"TelegramBot inicializado exitosamente con "
            f"LLM provider: {self.agent.llm_provider.get_provider_name()}"
        )

    def _setup_middleware(self):
        """Configurar middleware de la aplicación."""
        logger.info("Configurando middleware...")

        # Middleware de logging
        setup_logging_middleware(self.application)

        # Middleware de autenticación
        setup_auth_middleware(self.application, self.db_manager)

        # TODO: Agregar más middleware cuando se implementen:
        # - setup_rate_limiting_middleware()
        # - setup_metrics_middleware()

        logger.info("Middleware configurado exitosamente")

    def _setup_handlers(self):
        """Configurar handlers de la aplicación."""
        logger.info("Registrando handlers...")

        # Registrar registration handlers (/register, /verify, /resend)
        # IMPORTANTE: Estos van primero porque no requieren autenticación
        register_registration_handlers(self.application, self.db_manager)

        # Registrar command handlers (/start, /help, /stats, etc.)
        register_command_handlers(self.application)

        # Registrar tools handlers (/ia, /query) - Sistema de Tools
        # IMPORTANTE: Va antes de query_handlers para que los comandos tengan prioridad
        register_tools_handlers(self.application)

        # Registrar query handlers (mensajes de texto sin comando)
        register_query_handlers(self.application, self.agent)

        # TODO: Registrar handlers adicionales cuando se implementen:
        # - register_admin_handlers() (requiere permisos específicos)
        # - register_callback_handlers() (para inline keyboards)

        logger.info("Handlers registrados exitosamente")

    async def run(self):
        """Ejecutar el bot."""
        logger.info("🤖 Bot iniciado y esperando mensajes...")
        logger.info(f"✅ Configuración: {settings.environment}")
        logger.info(f"✅ Base de datos: {settings.db_type}")
        logger.info(f"✅ LLM: {self.agent.llm_provider.get_provider_name()} "
                   f"({self.agent.llm_provider.get_model_name()})")

        await self.application.run_polling(
            allowed_updates=Update.ALL_TYPES,
            drop_pending_updates=True  # Ignorar mensajes pendientes al iniciar
        )

    async def stop(self):
        """Detener el bot de manera ordenada."""
        logger.info("Deteniendo bot...")
        await self.application.stop()

        # Cerrar conexiones de base de datos
        self.db_manager.close()

        logger.info("Bot detenido exitosamente")
