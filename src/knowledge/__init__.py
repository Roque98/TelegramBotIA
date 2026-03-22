"""
Módulo de conocimiento empresarial.

Proporciona acceso a la base de conocimiento institucional
y funcionalidades de búsqueda.
"""

from .knowledge_categories import KnowledgeCategory
from .company_knowledge import KnowledgeEntry  # get_knowledge_base, get_entries_by_category - Solo BD ahora
from .knowledge_manager import KnowledgeManager
from .knowledge_repository import KnowledgeRepository

__all__ = [
    'KnowledgeCategory',
    'KnowledgeEntry',
    'KnowledgeManager',
    'KnowledgeRepository',
    # 'get_knowledge_base',  # Comentado - Solo usar BD
    # 'get_entries_by_category'  # Comentado - Solo usar BD
]
