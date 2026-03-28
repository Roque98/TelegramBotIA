"""
Gateway Package.

Normalización de mensajes de diferentes canales de entrada:
- MessageGateway: Convierte mensajes de Telegram, API REST, WebSocket
  a ConversationEvent para procesamiento uniforme.
"""

from .message_gateway import MessageGateway

__all__ = ["MessageGateway"]
