"""
EventBus - Sistema de publicación/suscripción en memoria.

Permite comunicación desacoplada entre componentes del sistema.
Para producción, puede reemplazarse con Redis Pub/Sub.
"""

import asyncio
import logging
from collections import defaultdict
from datetime import UTC, datetime
from typing import Any, Awaitable, Callable, Optional
from uuid import uuid4

logger = logging.getLogger(__name__)

# Tipo para handlers de eventos
EventHandler = Callable[[dict[str, Any]], Awaitable[None]]


class EventBus:
    """
    Bus de eventos simple en memoria con patrón pub/sub.

    Permite suscribirse a tipos de eventos y publicar eventos
    que serán recibidos por todos los suscriptores.

    Attributes:
        _handlers: Diccionario de handlers por tipo de evento
        _event_history: Historial de eventos (para debugging)
    """

    _instance: Optional["EventBus"] = None

    def __new__(cls) -> "EventBus":
        """Singleton pattern para tener un único EventBus."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._handlers = defaultdict(list)
            cls._instance._event_history = []
            cls._instance._max_history = 100
        return cls._instance

    def subscribe(self, event_type: str, handler: EventHandler) -> None:
        """
        Suscribe un handler a un tipo de evento.

        Args:
            event_type: Tipo de evento (ej: "query.received", "response.sent")
            handler: Función async que procesa el evento
        """
        if handler not in self._handlers[event_type]:
            self._handlers[event_type].append(handler)
            logger.debug(f"Handler suscrito a '{event_type}'")

    def unsubscribe(self, event_type: str, handler: EventHandler) -> None:
        """
        Desuscribe un handler de un tipo de evento.

        Args:
            event_type: Tipo de evento
            handler: Handler a remover
        """
        if handler in self._handlers[event_type]:
            self._handlers[event_type].remove(handler)
            logger.debug(f"Handler desuscrito de '{event_type}'")

    async def publish(self, event_type: str, data: dict[str, Any]) -> None:
        """
        Publica un evento a todos los suscriptores.

        Los handlers se ejecutan en paralelo y los errores no
        detienen la ejecución de otros handlers.

        Args:
            event_type: Tipo de evento
            data: Datos del evento
        """
        # Enriquecer evento con metadata
        event = {
            "event_id": str(uuid4()),
            "event_type": event_type,
            "timestamp": datetime.now(UTC).isoformat(),
            "data": data,
        }

        # Guardar en historial
        self._add_to_history(event)

        # Obtener handlers
        handlers = self._handlers.get(event_type, [])
        if not handlers:
            logger.debug(f"No hay handlers para '{event_type}'")
            return

        # Ejecutar handlers en paralelo
        logger.debug(f"Publicando '{event_type}' a {len(handlers)} handlers")
        results = await asyncio.gather(
            *[self._safe_call(handler, event) for handler in handlers],
            return_exceptions=True,
        )

        # Log de errores
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(
                    f"Error en handler {i} para '{event_type}': {result}"
                )

    async def _safe_call(
        self, handler: EventHandler, event: dict[str, Any]
    ) -> None:
        """
        Llama a un handler de forma segura.

        Args:
            handler: Handler a llamar
            event: Evento a pasar
        """
        try:
            await handler(event)
        except Exception as e:
            logger.exception(f"Error en handler: {e}")
            raise

    def _add_to_history(self, event: dict[str, Any]) -> None:
        """
        Agrega evento al historial (para debugging).

        Args:
            event: Evento a agregar
        """
        self._event_history.append(event)
        # Mantener solo los últimos N eventos
        if len(self._event_history) > self._max_history:
            self._event_history = self._event_history[-self._max_history:]

    def get_history(self, event_type: Optional[str] = None) -> list[dict[str, Any]]:
        """
        Obtiene el historial de eventos.

        Args:
            event_type: Filtrar por tipo (opcional)

        Returns:
            Lista de eventos
        """
        if event_type:
            return [e for e in self._event_history if e["event_type"] == event_type]
        return list(self._event_history)

    def clear_history(self) -> None:
        """Limpia el historial de eventos."""
        self._event_history.clear()

    def clear_handlers(self) -> None:
        """Limpia todos los handlers (útil para tests)."""
        self._handlers.clear()

    @classmethod
    def reset(cls) -> None:
        """Resetea el singleton (útil para tests)."""
        if cls._instance:
            cls._instance._handlers.clear()
            cls._instance._event_history.clear()


# Singleton global
event_bus = EventBus()
