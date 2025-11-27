"""
Gestor de prompts con versionado y A/B testing.

Proporciona funcionalidades para:
- Gestión de versiones de prompts
- A/B testing entre diferentes versiones
- Tracking de métricas por versión
- Selección dinámica de prompts
"""
import logging
import random
from typing import Dict, Any, Optional, List
from datetime import datetime
from jinja2 import Template
from .prompt_templates import PromptTemplates

logger = logging.getLogger(__name__)


class PromptVersion:
    """Representa una versión específica de un prompt."""

    def __init__(self, template: Template, version: int, metadata: Optional[Dict[str, Any]] = None):
        """
        Inicializar una versión de prompt.

        Args:
            template: Plantilla Jinja2
            version: Número de versión
            metadata: Metadatos adicionales (ej: fecha creación, descripción, autor)
        """
        self.template = template
        self.version = version
        self.metadata = metadata or {}
        self.usage_count = 0
        self.created_at = datetime.now()

    def render(self, **kwargs) -> str:
        """
        Renderizar el prompt con las variables proporcionadas.

        Args:
            **kwargs: Variables para el template

        Returns:
            Prompt renderizado
        """
        self.usage_count += 1
        return self.template.render(**kwargs)


class ABTestConfig:
    """Configuración para A/B testing de prompts."""

    def __init__(
        self,
        enabled: bool = False,
        variants: Optional[Dict[int, float]] = None,
        strategy: str = "random"
    ):
        """
        Inicializar configuración de A/B testing.

        Args:
            enabled: Si el A/B testing está habilitado
            variants: Diccionario de {versión: peso} para distribución
                     Ej: {1: 0.5, 2: 0.5} = 50% cada versión
            strategy: Estrategia de selección ('random', 'weighted', 'round_robin')
        """
        self.enabled = enabled
        self.variants = variants or {}
        self.strategy = strategy
        self._round_robin_index = 0

    def select_version(self, available_versions: List[int]) -> int:
        """
        Seleccionar una versión basada en la estrategia configurada.

        Args:
            available_versions: Lista de versiones disponibles

        Returns:
            Versión seleccionada
        """
        if not self.enabled or not self.variants:
            # Si A/B testing no está habilitado, usar la última versión
            return max(available_versions)

        # Filtrar solo las versiones disponibles que están en variants
        active_variants = {v: w for v, w in self.variants.items() if v in available_versions}

        if not active_variants:
            return max(available_versions)

        if self.strategy == "random" or self.strategy == "weighted":
            # Selección ponderada
            versions = list(active_variants.keys())
            weights = list(active_variants.values())
            return random.choices(versions, weights=weights, k=1)[0]

        elif self.strategy == "round_robin":
            # Rotación circular
            versions = sorted(active_variants.keys())
            selected = versions[self._round_robin_index % len(versions)]
            self._round_robin_index += 1
            return selected

        else:
            logger.warning(f"Estrategia desconocida: {self.strategy}, usando random")
            return random.choice(list(active_variants.keys()))


class PromptManager:
    """
    Gestor centralizado de prompts con versionado y A/B testing.

    Permite gestionar múltiples versiones de prompts, realizar A/B testing,
    y trackear métricas de uso.

    Examples:
        >>> # Uso básico
        >>> manager = PromptManager()
        >>> prompt = manager.get_prompt(
        ...     'classification',
        ...     user_query="¿Cuántos usuarios hay?"
        ... )

        >>> # Uso con versión específica
        >>> prompt = manager.get_prompt(
        ...     'sql_generation',
        ...     version=2,
        ...     user_query="Lista de productos",
        ...     database_schema="..."
        ... )

        >>> # Habilitar A/B testing
        >>> manager.enable_ab_test(
        ...     'classification',
        ...     variants={1: 0.3, 2: 0.7}  # 30% v1, 70% v2
        ... )
    """

    def __init__(self):
        """Inicializar el gestor de prompts."""
        self.templates = PromptTemplates()
        self._ab_configs: Dict[str, ABTestConfig] = {}
        self._metrics: Dict[str, Dict[int, Dict[str, Any]]] = {}
        logger.info("PromptManager inicializado")

    def get_prompt(
        self,
        prompt_type: str,
        version: Optional[int] = None,
        **variables
    ) -> str:
        """
        Obtener un prompt renderizado.

        Args:
            prompt_type: Tipo de prompt (ej: 'classification', 'sql_generation', 'general_response')
            version: Versión específica a usar (None = auto-selección según A/B testing)
            **variables: Variables para renderizar el template

        Returns:
            Prompt renderizado listo para enviar al LLM

        Example:
            >>> prompt = manager.get_prompt(
            ...     'classification',
            ...     user_query="¿Cuántos productos tenemos?"
            ... )
        """
        # Normalizar nombre del prompt
        prompt_type_upper = prompt_type.upper()

        # Obtener versiones disponibles
        available = self._get_available_versions(prompt_type_upper)

        if not available:
            raise ValueError(f"No hay versiones disponibles para prompt tipo: {prompt_type}")

        # Determinar qué versión usar
        if version is None:
            version = self._select_version(prompt_type_upper, available)
        elif version not in available:
            logger.warning(
                f"Versión {version} no disponible para {prompt_type}, usando v{max(available)}"
            )
            version = max(available)

        # Obtener y renderizar template
        template = self.templates.get_template(prompt_type, version=version)
        rendered = template.render(**variables)

        # Registrar uso
        self._track_usage(prompt_type_upper, version)

        logger.debug(f"Prompt generado: {prompt_type} v{version} ({len(rendered)} chars)")
        return rendered

    def enable_ab_test(
        self,
        prompt_type: str,
        variants: Dict[int, float],
        strategy: str = "weighted"
    ) -> None:
        """
        Habilitar A/B testing para un tipo de prompt.

        Args:
            prompt_type: Tipo de prompt
            variants: Diccionario de {versión: peso}
            strategy: Estrategia ('random', 'weighted', 'round_robin')

        Example:
            >>> # 50% v1, 50% v2
            >>> manager.enable_ab_test('classification', {1: 0.5, 2: 0.5})

            >>> # 20% v1, 30% v2, 50% v3
            >>> manager.enable_ab_test('sql_generation', {1: 0.2, 2: 0.3, 3: 0.5})
        """
        prompt_type_upper = prompt_type.upper()

        # Validar que los pesos sumen ~1.0
        total_weight = sum(variants.values())
        if not (0.99 <= total_weight <= 1.01):
            logger.warning(f"Los pesos no suman 1.0 (suma={total_weight}), normalizando...")
            variants = {v: w/total_weight for v, w in variants.items()}

        self._ab_configs[prompt_type_upper] = ABTestConfig(
            enabled=True,
            variants=variants,
            strategy=strategy
        )

        logger.info(
            f"A/B testing habilitado para {prompt_type}: "
            f"versiones {list(variants.keys())} con estrategia '{strategy}'"
        )

    def disable_ab_test(self, prompt_type: str) -> None:
        """
        Deshabilitar A/B testing para un tipo de prompt.

        Args:
            prompt_type: Tipo de prompt
        """
        prompt_type_upper = prompt_type.upper()
        if prompt_type_upper in self._ab_configs:
            self._ab_configs[prompt_type_upper].enabled = False
            logger.info(f"A/B testing deshabilitado para {prompt_type}")

    def set_default_version(self, prompt_type: str, version: int) -> None:
        """
        Establecer una versión por defecto (deshabilita A/B testing).

        Args:
            prompt_type: Tipo de prompt
            version: Versión a usar por defecto
        """
        prompt_type_upper = prompt_type.upper()
        available = self._get_available_versions(prompt_type_upper)

        if version not in available:
            raise ValueError(f"Versión {version} no existe para {prompt_type}")

        # Deshabilitar A/B testing y configurar solo esta versión
        self._ab_configs[prompt_type_upper] = ABTestConfig(
            enabled=False,
            variants={version: 1.0},
            strategy="weighted"
        )

        logger.info(f"Versión por defecto establecida: {prompt_type} v{version}")

    def get_metrics(self, prompt_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Obtener métricas de uso de prompts.

        Args:
            prompt_type: Tipo específico (None = todas las métricas)

        Returns:
            Diccionario con métricas de uso

        Example:
            >>> metrics = manager.get_metrics('classification')
            >>> print(metrics)
            {
                'CLASSIFICATION': {
                    1: {'usage_count': 45, 'last_used': '2024-01-15 10:30:00'},
                    2: {'usage_count': 55, 'last_used': '2024-01-15 10:31:00'}
                }
            }
        """
        if prompt_type:
            prompt_type_upper = prompt_type.upper()
            return {prompt_type_upper: self._metrics.get(prompt_type_upper, {})}
        return self._metrics.copy()

    def get_ab_test_stats(self, prompt_type: str) -> Dict[str, Any]:
        """
        Obtener estadísticas de A/B testing para un prompt.

        Args:
            prompt_type: Tipo de prompt

        Returns:
            Estadísticas de A/B testing

        Example:
            >>> stats = manager.get_ab_test_stats('classification')
            >>> print(stats)
            {
                'enabled': True,
                'strategy': 'weighted',
                'variants': {1: 0.5, 2: 0.5},
                'usage': {1: 48, 2: 52}
            }
        """
        prompt_type_upper = prompt_type.upper()
        ab_config = self._ab_configs.get(prompt_type_upper)
        metrics = self._metrics.get(prompt_type_upper, {})

        if not ab_config:
            return {'enabled': False}

        return {
            'enabled': ab_config.enabled,
            'strategy': ab_config.strategy,
            'variants': ab_config.variants,
            'usage': {v: m.get('usage_count', 0) for v, m in metrics.items()}
        }

    def list_prompts(self) -> Dict[str, List[int]]:
        """
        Listar todos los prompts disponibles y sus versiones.

        Returns:
            Diccionario de {tipo: [versiones disponibles]}

        Example:
            >>> prompts = manager.list_prompts()
            >>> print(prompts)
            {
                'CLASSIFICATION': [1, 2],
                'SQL_GENERATION': [1, 2, 3],
                'GENERAL_RESPONSE': [1, 2]
            }
        """
        return self.templates.list_available_templates()

    def _get_available_versions(self, prompt_type: str) -> List[int]:
        """
        Obtener versiones disponibles de un tipo de prompt.

        Args:
            prompt_type: Tipo de prompt (ya normalizado a uppercase)

        Returns:
            Lista de versiones disponibles
        """
        all_templates = self.templates.list_available_templates()
        return all_templates.get(prompt_type, [])

    def _select_version(self, prompt_type: str, available_versions: List[int]) -> int:
        """
        Seleccionar versión según configuración de A/B testing.

        Args:
            prompt_type: Tipo de prompt (ya normalizado)
            available_versions: Versiones disponibles

        Returns:
            Versión seleccionada
        """
        ab_config = self._ab_configs.get(prompt_type)

        if ab_config and ab_config.enabled:
            return ab_config.select_version(available_versions)

        # Por defecto, usar la última versión
        return max(available_versions)

    def _track_usage(self, prompt_type: str, version: int) -> None:
        """
        Registrar uso de un prompt.

        Args:
            prompt_type: Tipo de prompt
            version: Versión usada
        """
        if prompt_type not in self._metrics:
            self._metrics[prompt_type] = {}

        if version not in self._metrics[prompt_type]:
            self._metrics[prompt_type][version] = {
                'usage_count': 0,
                'first_used': datetime.now(),
                'last_used': None
            }

        self._metrics[prompt_type][version]['usage_count'] += 1
        self._metrics[prompt_type][version]['last_used'] = datetime.now()


# Instancia global singleton (opcional, para facilitar uso)
_default_manager: Optional[PromptManager] = None


def get_default_manager() -> PromptManager:
    """
    Obtener la instancia global del PromptManager.

    Returns:
        Instancia singleton del PromptManager

    Example:
        >>> from src.agent.prompts import get_default_manager
        >>> manager = get_default_manager()
        >>> prompt = manager.get_prompt('classification', user_query="test")
    """
    global _default_manager
    if _default_manager is None:
        _default_manager = PromptManager()
    return _default_manager
