"""
Categorías de conocimiento empresarial.

Define las categorías para organizar el conocimiento institucional.
"""
from enum import Enum


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

    def __str__(self) -> str:
        """Representación en string."""
        return self.value

    @classmethod
    def get_all(cls):
        """Obtener todas las categorías."""
        return list(cls)

    @classmethod
    def get_display_name(cls, category: 'KnowledgeCategory') -> str:
        """Obtener nombre legible de la categoría."""
        names = {
            cls.PROCESOS: "Procesos",
            cls.POLITICAS: "Políticas",
            cls.FAQS: "Preguntas Frecuentes",
            cls.CONTACTOS: "Contactos",
            cls.SISTEMAS: "Sistemas",
            cls.RECURSOS_HUMANOS: "Recursos Humanos"
        }
        return names.get(category, category.value.title())
