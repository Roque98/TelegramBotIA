"""
Entidades del módulo de conocimiento.

Define los modelos de datos para categorías y entradas de conocimiento.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List


class KnowledgeCategory(Enum):
    """Categorías de conocimiento empresarial."""

    PROCESOS = "procesos"
    """Procesos y procedimientos internos"""

    POLITICAS = "politicas"
    """Políticas de la empresa"""

    FAQS = "faqs"
    """Preguntas frecuentes"""

    CONTACTOS = "contactos"
    """Información de contacto de departamentos"""

    SISTEMAS = "sistemas"
    """Información sobre sistemas y herramientas"""

    RECURSOS_HUMANOS = "recursos_humanos"
    """Temas de RRHH: vacaciones, permisos, beneficios"""

    BASE_DATOS = "base_datos"
    """Información sobre tablas y estructura de la base de datos"""

    def __str__(self) -> str:
        return self.value

    @classmethod
    def get_all(cls):
        return list(cls)

    @classmethod
    def get_display_name(cls, category: 'KnowledgeCategory') -> str:
        names = {
            cls.PROCESOS: "Procesos",
            cls.POLITICAS: "Políticas",
            cls.FAQS: "Preguntas Frecuentes",
            cls.CONTACTOS: "Contactos",
            cls.SISTEMAS: "Sistemas",
            cls.RECURSOS_HUMANOS: "Recursos Humanos",
            cls.BASE_DATOS: "Base de Datos",
        }
        return names.get(category, category.value.title())


@dataclass
class KnowledgeEntry:
    """Entrada de conocimiento empresarial."""

    category: KnowledgeCategory
    question: str
    answer: str
    keywords: List[str]
    related_commands: List[str] = field(default_factory=list)
    priority: int = 1  # 1=normal, 2=high, 3=critical

    def __repr__(self) -> str:
        return f"KnowledgeEntry(category={self.category.value}, question='{self.question[:50]}...')"
