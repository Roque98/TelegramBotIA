"""
Módulo de conocimiento empresarial.

Proporciona acceso a la base de conocimiento institucional
y funcionalidades de búsqueda.
"""

from .knowledge_categories import KnowledgeCategory
from .company_knowledge import KnowledgeEntry, get_knowledge_base, get_entries_by_category
from .knowledge_manager import KnowledgeManager

__all__ = [
    'KnowledgeCategory',
    'KnowledgeEntry',
    'KnowledgeManager',
    'get_knowledge_base',
    'get_entries_by_category'
]
