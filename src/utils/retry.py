"""
Decoradores de retry con backoff exponencial usando tenacity.

Proporciona decoradores reutilizables para proteger llamadas a LLM y BD
contra errores transitorios (rate limits, timeouts, conexiones perdidas).
"""

import logging

from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log,
)

logger = logging.getLogger(__name__)


def llm_retry(
    max_attempts: int = 3,
    min_wait: int = 2,
    max_wait: int = 30,
):
    """
    Retry decorator para llamadas a LLM (OpenAI, Anthropic).

    Reintenta en errores transitorios de API: rate limits, timeouts,
    errores de conexion. NO reintenta en errores de validacion o auth.

    Args:
        max_attempts: Numero maximo de intentos
        min_wait: Segundos minimos de espera entre intentos
        max_wait: Segundos maximos de espera entre intentos
    """
    # Importar excepciones de OpenAI de forma segura
    retry_exceptions = [ConnectionError, TimeoutError]

    try:
        import openai
        retry_exceptions.extend([
            openai.APIConnectionError,
            openai.APITimeoutError,
            openai.RateLimitError,
            openai.InternalServerError,
        ])
    except ImportError:
        pass

    try:
        import anthropic
        retry_exceptions.extend([
            anthropic.APIConnectionError,
            anthropic.APITimeoutError,
            anthropic.RateLimitError,
            anthropic.InternalServerError,
        ])
    except ImportError:
        pass

    return retry(
        stop=stop_after_attempt(max_attempts),
        wait=wait_exponential(multiplier=1, min=min_wait, max=max_wait),
        retry=retry_if_exception_type(tuple(retry_exceptions)),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        reraise=True,
    )


def db_retry(
    max_attempts: int = 3,
    min_wait: int = 1,
    max_wait: int = 15,
):
    """
    Retry decorator para operaciones de base de datos.

    Reintenta en errores transitorios: conexion perdida, timeouts,
    pool agotado. NO reintenta en errores de SQL o validacion.

    Args:
        max_attempts: Numero maximo de intentos
        min_wait: Segundos minimos de espera entre intentos
        max_wait: Segundos maximos de espera entre intentos
    """
    from sqlalchemy.exc import OperationalError, TimeoutError as SQLTimeoutError

    return retry(
        stop=stop_after_attempt(max_attempts),
        wait=wait_exponential(multiplier=1, min=min_wait, max=max_wait),
        retry=retry_if_exception_type((
            OperationalError,
            SQLTimeoutError,
            ConnectionError,
            TimeoutError,
        )),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        reraise=True,
    )
