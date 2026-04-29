"""
Punto de entrada principal del bot de Telegram con agente de base de datos.
"""
import asyncio
import logging
import threading
import nest_asyncio
from src.config.settings import settings
from src.config.logging_config import configure_logging
from src.bot.telegram_bot import TelegramBot

# Permitir event loops anidados
nest_asyncio.apply()


def setup_logging():
    configure_logging(log_level=settings.log_level)


def _start_flask():
    from src.api.chat_endpoint import app
    app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)


async def main():
    setup_logging()
    logger = logging.getLogger(__name__)

    logger.info("Iniciando bot de Telegram...")
    bot = TelegramBot()  # inicializa HandlerManager antes de arrancar Flask

    flask_thread = threading.Thread(target=_start_flask, daemon=True, name="flask-api")
    flask_thread.start()
    logger.info("API REST iniciada en http://0.0.0.0:5000 (dashboard: /admin)")

    await bot.run()


if __name__ == "__main__":
    asyncio.run(main())
