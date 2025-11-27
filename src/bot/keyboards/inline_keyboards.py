"""
Inline keyboards para el bot.

Define teclados inline para acciones como paginación, confirmaciones, etc.
"""
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from typing import List, Optional


def get_pagination_keyboard(
    current_page: int,
    total_pages: int,
    callback_prefix: str = "page"
) -> InlineKeyboardMarkup:
    """
    Crear keyboard inline para paginación.

    Args:
        current_page: Página actual (1-indexed)
        total_pages: Total de páginas
        callback_prefix: Prefijo para los callback_data

    Returns:
        InlineKeyboardMarkup con botones de paginación
    """
    keyboard = []

    # Fila de navegación
    navigation_row = []

    # Botón "Primera página" (solo si no estamos en la primera)
    if current_page > 1:
        navigation_row.append(
            InlineKeyboardButton(
                "⏮️ Primera",
                callback_data=f"{callback_prefix}:1"
            )
        )

    # Botón "Anterior" (solo si no estamos en la primera)
    if current_page > 1:
        navigation_row.append(
            InlineKeyboardButton(
                "◀️ Anterior",
                callback_data=f"{callback_prefix}:{current_page - 1}"
            )
        )

    # Indicador de página actual
    navigation_row.append(
        InlineKeyboardButton(
            f"📄 {current_page}/{total_pages}",
            callback_data="current_page"
        )
    )

    # Botón "Siguiente" (solo si no estamos en la última)
    if current_page < total_pages:
        navigation_row.append(
            InlineKeyboardButton(
                "▶️ Siguiente",
                callback_data=f"{callback_prefix}:{current_page + 1}"
            )
        )

    # Botón "Última página" (solo si no estamos en la última)
    if current_page < total_pages:
        navigation_row.append(
            InlineKeyboardButton(
                "⏭️ Última",
                callback_data=f"{callback_prefix}:{total_pages}"
            )
        )

    keyboard.append(navigation_row)

    return InlineKeyboardMarkup(keyboard)


def get_confirmation_keyboard(
    confirm_callback: str,
    cancel_callback: str,
    confirm_text: str = "✅ Confirmar",
    cancel_text: str = "❌ Cancelar"
) -> InlineKeyboardMarkup:
    """
    Crear keyboard inline para confirmación.

    Args:
        confirm_callback: Callback data para confirmar
        cancel_callback: Callback data para cancelar
        confirm_text: Texto del botón de confirmación
        cancel_text: Texto del botón de cancelación

    Returns:
        InlineKeyboardMarkup con botones de confirmación
    """
    keyboard = [
        [
            InlineKeyboardButton(confirm_text, callback_data=confirm_callback),
            InlineKeyboardButton(cancel_text, callback_data=cancel_callback)
        ]
    ]

    return InlineKeyboardMarkup(keyboard)


def get_action_keyboard(
    actions: List[tuple[str, str]]
) -> InlineKeyboardMarkup:
    """
    Crear keyboard inline con acciones personalizadas.

    Args:
        actions: Lista de tuplas (texto, callback_data)

    Returns:
        InlineKeyboardMarkup con botones de acciones
    """
    keyboard = []

    # Crear una fila por cada acción (o dos botones por fila si hay muchos)
    if len(actions) <= 3:
        # Pocas acciones: una por fila
        for text, callback_data in actions:
            keyboard.append([
                InlineKeyboardButton(text, callback_data=callback_data)
            ])
    else:
        # Muchas acciones: dos por fila
        for i in range(0, len(actions), 2):
            row = [
                InlineKeyboardButton(actions[i][0], callback_data=actions[i][1])
            ]
            if i + 1 < len(actions):
                row.append(
                    InlineKeyboardButton(actions[i + 1][0], callback_data=actions[i + 1][1])
                )
            keyboard.append(row)

    return InlineKeyboardMarkup(keyboard)


def get_menu_keyboard() -> InlineKeyboardMarkup:
    """
    Crear keyboard inline con menú principal.

    Returns:
        InlineKeyboardMarkup con opciones del menú
    """
    keyboard = [
        [
            InlineKeyboardButton("📊 Estadísticas", callback_data="menu:stats"),
            InlineKeyboardButton("❓ Ayuda", callback_data="menu:help")
        ],
        [
            InlineKeyboardButton("📝 Ejemplos", callback_data="menu:examples"),
            InlineKeyboardButton("🔧 Config", callback_data="menu:config")
        ],
        [
            InlineKeyboardButton("ℹ️ Acerca de", callback_data="menu:about")
        ]
    ]

    return InlineKeyboardMarkup(keyboard)


def get_back_button(callback_data: str = "back") -> InlineKeyboardMarkup:
    """
    Crear keyboard con solo un botón de "Volver".

    Args:
        callback_data: Callback data para el botón

    Returns:
        InlineKeyboardMarkup con botón de volver
    """
    keyboard = [
        [InlineKeyboardButton("🔙 Volver", callback_data=callback_data)]
    ]

    return InlineKeyboardMarkup(keyboard)
