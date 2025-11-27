"""
Ejemplo de configuración de prompts para diferentes entornos.

Este archivo muestra cómo configurar el sistema de prompts según el entorno
(development, staging, production).
"""
from typing import Dict, Any
from .prompt_manager import get_default_manager


class PromptConfig:
    """Configuración de prompts por entorno."""

    @staticmethod
    def configure_for_development():
        """
        Configuración para entorno de desarrollo.

        - Usa siempre las últimas versiones de prompts
        - No hace A/B testing
        - Permite experimentación rápida
        """
        manager = get_default_manager()

        # En desarrollo, siempre usar las últimas versiones
        # (comportamiento por defecto, no necesita configuración)

        print("✓ Prompts configurados para DEVELOPMENT")
        print("  - Usando últimas versiones de todos los prompts")

    @staticmethod
    def configure_for_staging():
        """
        Configuración para entorno de staging.

        - A/B testing activo para validar nuevas versiones
        - Métricas detalladas de uso
        - Validación antes de producción
        """
        manager = get_default_manager()

        # A/B testing: 70% versión estable, 30% versión nueva
        manager.enable_ab_test(
            'classification',
            variants={1: 0.7, 2: 0.3},
            strategy='weighted'
        )

        # A/B testing con 3 versiones
        manager.enable_ab_test(
            'sql_generation',
            variants={2: 0.5, 3: 0.5},
            strategy='weighted'
        )

        # Respuestas generales: comparar v1 vs v2
        manager.enable_ab_test(
            'general_response',
            variants={1: 0.4, 2: 0.6},
            strategy='weighted'
        )

        print("✓ Prompts configurados para STAGING")
        print("  - A/B testing activo:")
        print("    • classification: 70% v1, 30% v2")
        print("    • sql_generation: 50% v2, 50% v3")
        print("    • general_response: 40% v1, 60% v2")

    @staticmethod
    def configure_for_production():
        """
        Configuración para entorno de producción.

        - Versiones estables y probadas
        - Sin A/B testing por defecto
        - Rollout gradual de nuevas versiones
        """
        manager = get_default_manager()

        # Versiones estables validadas en staging
        manager.set_default_version('classification', version=2)
        manager.set_default_version('sql_generation', version=3)
        manager.set_default_version('general_response', version=1)

        # Opcional: Rollout gradual de nueva versión
        # Descomentar cuando se esté haciendo rollout de v3 a v4 de sql_generation
        # manager.enable_ab_test(
        #     'sql_generation',
        #     variants={3: 0.95, 4: 0.05},  # 95% estable, 5% nueva
        #     strategy='weighted'
        # )

        print("✓ Prompts configurados para PRODUCTION")
        print("  - Versiones estables:")
        print("    • classification: v2")
        print("    • sql_generation: v3")
        print("    • general_response: v1")

    @staticmethod
    def configure_for_testing():
        """
        Configuración para entorno de testing/QA.

        - Versiones específicas para tests reproducibles
        - Sin A/B testing (comportamiento determinista)
        """
        manager = get_default_manager()

        # Fijar versiones específicas para tests reproducibles
        manager.set_default_version('classification', version=1)
        manager.set_default_version('sql_generation', version=2)
        manager.set_default_version('general_response', version=1)

        print("✓ Prompts configurados para TESTING")
        print("  - Versiones fijas para reproducibilidad")


def configure_prompts(environment: str) -> None:
    """
    Configurar prompts según el entorno.

    Args:
        environment: Nombre del entorno ('development', 'staging', 'production', 'testing')

    Raises:
        ValueError: Si el entorno no es válido

    Example:
        >>> from src.config.settings import settings
        >>> configure_prompts(settings.environment)
    """
    env_lower = environment.lower()

    config_map = {
        'development': PromptConfig.configure_for_development,
        'dev': PromptConfig.configure_for_development,
        'staging': PromptConfig.configure_for_staging,
        'stage': PromptConfig.configure_for_staging,
        'production': PromptConfig.configure_for_production,
        'prod': PromptConfig.configure_for_production,
        'testing': PromptConfig.configure_for_testing,
        'test': PromptConfig.configure_for_testing,
    }

    if env_lower not in config_map:
        raise ValueError(
            f"Entorno '{environment}' no válido. "
            f"Opciones: {list(set(config_map.keys()))}"
        )

    config_map[env_lower]()


def get_prompt_configuration_summary() -> Dict[str, Any]:
    """
    Obtener resumen de la configuración actual de prompts.

    Returns:
        Diccionario con información de configuración

    Example:
        >>> summary = get_prompt_configuration_summary()
        >>> print(summary['prompts']['CLASSIFICATION']['current_version'])
        2
    """
    manager = get_default_manager()

    summary = {
        'available_prompts': manager.list_prompts(),
        'ab_tests': {},
        'metrics': manager.get_metrics()
    }

    # Obtener configuración de A/B tests
    for prompt_type in summary['available_prompts'].keys():
        ab_stats = manager.get_ab_test_stats(prompt_type.lower())
        if ab_stats.get('enabled'):
            summary['ab_tests'][prompt_type] = ab_stats

    return summary


# Ejemplo de uso en main.py o __init__.py de la aplicación:
if __name__ == "__main__":
    # Simulación de configuración
    print("\n=== DEVELOPMENT ===")
    configure_prompts('development')

    print("\n=== STAGING ===")
    configure_prompts('staging')

    print("\n=== PRODUCTION ===")
    configure_prompts('production')

    print("\n=== TESTING ===")
    configure_prompts('testing')

    print("\n=== RESUMEN ===")
    summary = get_prompt_configuration_summary()
    print(f"Prompts disponibles: {list(summary['available_prompts'].keys())}")
    print(f"A/B tests activos: {len(summary['ab_tests'])}")
