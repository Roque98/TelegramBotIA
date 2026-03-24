"""
Middleware de autenticación con tokens encriptados.

Valida tokens que contienen JSON con número de empleado y timestamp.
El token es válido si:
1. Se puede desencriptar correctamente
2. La fecha no tiene más de 3 minutos de antigüedad
"""
import json
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Tuple

from src.utils.encryption_util import desencriptar

logger = logging.getLogger(__name__)


class TokenValidationError(Exception):
    """Excepción para errores de validación de token."""
    pass


class TokenMiddleware:
    """
    Middleware para validar tokens encriptados.

    El token debe contener un JSON encriptado con:
    {
        "numero_empleado": 12345,
        "timestamp": "2025-12-23T10:30:00"
    }
    """

    # Tiempo máximo de validez del token (en minutos)
    MAX_TOKEN_AGE_MINUTES = 3

    @classmethod
    def validar_token(cls, token_encriptado: str) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
        """
        Validar token encriptado.

        Args:
            token_encriptado: Token en formato Base64 encriptado

        Returns:
            Tupla de (es_valido, datos, mensaje_error)
            - es_valido: True si el token es válido
            - datos: Diccionario con numero_empleado y timestamp si es válido, None si no
            - mensaje_error: Mensaje de error si no es válido, None si es válido

        Example:
            >>> valido, datos, error = TokenMiddleware.validar_token(token)
            >>> if valido:
            ...     print(f"Empleado: {datos['numero_empleado']}")
            ... else:
            ...     print(f"Error: {error}")
        """
        try:
            # 1. Desencriptar el token
            token_json = desencriptar(token_encriptado)

            if token_json is None:
                return False, None, "Token inválido: no se pudo desencriptar"

            # 2. Parsear JSON
            try:
                datos = json.loads(token_json)
            except json.JSONDecodeError as e:
                logger.warning(f"Token con JSON inválido: {e}")
                return False, None, f"Token inválido: JSON malformado ({e})"

            # 3. Validar estructura
            if "numero_empleado" not in datos:
                return False, None, "Token inválido: falta 'numero_empleado'"

            if "timestamp" not in datos:
                return False, None, "Token inválido: falta 'timestamp'"

            # 4. Validar tipo de numero_empleado
            if not isinstance(datos["numero_empleado"], (int, str)):
                return False, None, "Token inválido: 'numero_empleado' debe ser int o string"

            # Convertir a int si es string numérico
            try:
                numero_empleado = int(datos["numero_empleado"])
                datos["numero_empleado"] = numero_empleado
            except (ValueError, TypeError):
                return False, None, f"Token inválido: 'numero_empleado' no es un número válido"

            # 5. Validar timestamp
            try:
                # Soportar múltiples formatos
                timestamp_str = datos["timestamp"]

                # Intentar ISO 8601
                try:
                    timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                except ValueError:
                    # Intentar formato con milisegundos
                    try:
                        timestamp = datetime.strptime(timestamp_str, "%Y-%m-%dT%H:%M:%S.%f")
                    except ValueError:
                        # Intentar formato sin milisegundos
                        timestamp = datetime.strptime(timestamp_str, "%Y-%m-%dT%H:%M:%S")

                datos["timestamp_parsed"] = timestamp

            except (ValueError, TypeError) as e:
                logger.warning(f"Timestamp inválido: {e}")
                return False, None, f"Token inválido: timestamp mal formado ({e})"

            # 6. Validar antigüedad del token (máximo 3 minutos)
            ahora = datetime.now()
            edad_token = ahora - timestamp

            if edad_token.total_seconds() < 0:
                # Token del futuro
                return False, None, "Token inválido: timestamp es del futuro"

            max_edad = timedelta(minutes=cls.MAX_TOKEN_AGE_MINUTES)

            if edad_token > max_edad:
                minutos_transcurridos = int(edad_token.total_seconds() / 60)
                return False, None, f"Token expirado: han pasado {minutos_transcurridos} minutos (máximo {cls.MAX_TOKEN_AGE_MINUTES})"

            # 7. Token válido
            logger.info(f"Token válido para empleado {numero_empleado}")
            return True, datos, None

        except Exception as e:
            logger.error(f"Error inesperado validando token: {e}", exc_info=True)
            return False, None, f"Error interno validando token: {str(e)}"

    @classmethod
    def generar_token(cls, numero_empleado: int) -> str:
        """
        Generar token encriptado para un empleado.

        Útil para testing o para generar tokens desde Python.

        Args:
            numero_empleado: Número de empleado

        Returns:
            Token encriptado en Base64

        Example:
            >>> token = TokenMiddleware.generar_token(12345)
            >>> print(token)
            "xyz123abc..."
        """
        from src.utils.encryption_util import encriptar

        # Generar timestamp actual en formato ISO 8601
        timestamp = datetime.now().isoformat()

        # Crear JSON
        datos = {
            "numero_empleado": numero_empleado,
            "timestamp": timestamp
        }

        # Convertir a JSON string
        token_json = json.dumps(datos)

        # Encriptar
        token_encriptado = encriptar(token_json)

        logger.info(f"Token generado para empleado {numero_empleado}")

        return token_encriptado

    @classmethod
    def extraer_numero_empleado(cls, token_encriptado: str) -> Optional[int]:
        """
        Extraer número de empleado de un token válido.

        Args:
            token_encriptado: Token encriptado

        Returns:
            Número de empleado si el token es válido, None si no

        Example:
            >>> numero = TokenMiddleware.extraer_numero_empleado(token)
            >>> if numero:
            ...     print(f"Empleado: {numero}")
        """
        valido, datos, _ = cls.validar_token(token_encriptado)

        if valido and datos:
            return datos["numero_empleado"]

        return None


# Funciones de conveniencia
def validar_token(token_encriptado: str) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
    """
    Función de conveniencia para validar token.

    Args:
        token_encriptado: Token en Base64

    Returns:
        Tupla de (es_valido, datos, mensaje_error)
    """
    return TokenMiddleware.validar_token(token_encriptado)


def generar_token(numero_empleado: int) -> str:
    """
    Función de conveniencia para generar token.

    Args:
        numero_empleado: Número de empleado

    Returns:
        Token encriptado
    """
    return TokenMiddleware.generar_token(numero_empleado)
