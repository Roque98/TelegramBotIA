"""
Keyboard principal del bot.

Define el teclado de respuestas rápidas para el usuario.
"""
from telegram import ReplyKeyboardMarkup, KeyboardButton


def get_main_keyboard() -> ReplyKeyboardMarkup:
    """
    Obtener el keyboard principal con opciones comunes.

    Returns:
        ReplyKeyboardMarkup con botones de opciones comunes
    """
    keyboard = [
        [
            KeyboardButton("📊 Estadísticas"),
            KeyboardButton("❓ Ayuda")
        ],
        [
            KeyboardButton("📝 Ejemplos de consultas"),
            KeyboardButton("🔧 Configuración")
        ]
    ]

    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,
        one_time_keyboard=False,
        input_field_placeholder="Escribe tu consulta..."
    )


def get_examples_keyboard() -> ReplyKeyboardMarkup:
    """
    Obtener keyboard con ejemplos de consultas comunes.

    Returns:
        ReplyKeyboardMarkup con ejemplos de consultas
    """
    keyboard = [
        [
            KeyboardButton("¿Cuántos usuarios hay?")
        ],
        [
            KeyboardButton("Muéstrame los últimos 5 pedidos")
        ],
        [
            KeyboardButton("¿Cuál es el producto más vendido?")
        ],
        [
            KeyboardButton("Lista las ventas del último mes")
        ],
        [
            KeyboardButton("🔙 Volver al menú principal")
        ]
    ]

    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,
        one_time_keyboard=True,
        input_field_placeholder="Selecciona un ejemplo o escribe tu consulta..."
    )


def remove_keyboard():
    """
    Remover el keyboard actual.

    Returns:
        ReplyKeyboardRemove para ocultar el keyboard
    """
    from telegram import ReplyKeyboardRemove
    return ReplyKeyboardRemove()
