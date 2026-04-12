"""Re-export de compatibilidad hacia src.domain.interaction.interaction_repository."""
from src.domain.interaction.interaction_repository import InteractionRepository as ObservabilityRepository

__all__ = ["ObservabilityRepository"]
