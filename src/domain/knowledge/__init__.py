"""
Módulo de conocimiento empresarial.

Proporciona acceso a la base de conocimiento institucional
y funcionalidades de búsqueda.
"""

from .knowledge_entity import KnowledgeCategory, KnowledgeEntry
from .knowledge_repository import KnowledgeRepository
from .knowledge_service import KnowledgeService

# Alias para compatibilidad
KnowledgeManager = KnowledgeService

__all__ = [
    'KnowledgeCategory',
    'KnowledgeEntry',
    'KnowledgeRepository',
    'KnowledgeService',
    'KnowledgeManager',
]
