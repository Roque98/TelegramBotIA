"""
Punto de entrada principal del bot de Telegram con agente de base de datos.
"""
import asyncio
import logging
import nest_asyncio
from src.config.settings import settings
from src.config.logging_config import configure_logging
from src.bot.telegram_bot import TelegramBot

# Permitir event loops anidados
nest_asyncio.apply()


def setup_logging():
    """Configurar el sistema de logging estructurado."""
    configure_logging(log_level=settings.log_level)



async def main():
    """Función principal para ejecutar el bot."""
    setup_logging()
    logger = logging.getLogger(__name__)

    logger.info("Iniciando bot de Telegram...")

    # Inicializar y ejecutar el bot
    bot = TelegramBot()
    await bot.run()


if __name__ == "__main__":
    asyncio.run(main())
