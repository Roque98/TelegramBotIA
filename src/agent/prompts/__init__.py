"""
Sistema de prompts modular y versionado.

Este paquete proporciona:
- Plantillas de prompts reutilizables con Jinja2
- Versionado de prompts para experimentación
- Sistema de A/B testing
- Gestión centralizada de prompts
"""
from .prompt_manager import PromptManager, get_default_manager
from .prompt_templates import PromptTemplates

__all__ = ['PromptManager', 'PromptTemplates', 'get_default_manager']
