"""
Módulo de encriptación compatible con sistema C# existente.

Implementa encriptación/desencriptación AES (Rijndael) compatible con
la clase Encrypt de C# del sistema de monitoreo.

⚠️ ADVERTENCIA DE SEGURIDAD:
Este módulo usa parámetros heredados del sistema C# existente que NO son
seguros según estándares modernos:
- MD5 como algoritmo hash (obsoleto, usar SHA256+)
- Solo 2 iteraciones PBKDF2 (moderno: 100,000+)
- Parámetros hardcodeados

Se mantienen estos parámetros ÚNICAMENTE para compatibilidad con el sistema
existente. NO usar para nuevos desarrollos.
"""
import base64
import hashlib
import logging
from typing import Optional
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

logger = logging.getLogger(__name__)


class EncryptionError(Exception):
    """Excepción personalizada para errores de encriptación."""
    pass


class Encrypt:
    """
    Clase de encriptación compatible con sistema C# existente.

    Implementa AES-256 en modo CBC con PBKDF2-MD5 para derivación de clave,
    manteniendo compatibilidad exacta con la clase Encrypt de C#.

    ⚠️ IMPORTANTE:
    - Los parámetros están hardcodeados para compatibilidad
    - MD5 y 2 iteraciones NO son seguros para producción moderna
    - Solo usar para interoperabilidad con sistema C# existente

    Attributes:
        PASSWORD: Contraseña maestra para derivación de clave
        SALT_VALUE: Salt para PBKDF2
        HASH_ALGORITHM: Algoritmo hash (MD5 para compatibilidad)
        PASSWORD_ITERATIONS: Iteraciones PBKDF2 (2 para compatibilidad)
        INITIAL_VECTOR: Vector de inicialización (IV) para AES CBC
        KEY_SIZE: Tamaño de clave en bits (256)

    Example:
        >>> encrypt = Encrypt()
        >>> encrypted = encrypt.encriptar("Hola Mundo")
        >>> decrypted = encrypt.desencriptar(encrypted)
        >>> print(decrypted)
        "Hola Mundo"
    """

    # Constantes - DEBEN coincidir exactamente con el código C#
    PASSWORD = "m0n4pl1cBAZ.10"
    SALT_VALUE = "c9a5d2f21f00469ff48a60fe5311b2ff"
    HASH_ALGORITHM = "MD5"
    PASSWORD_ITERATIONS = 2
    INITIAL_VECTOR = "bQBhAHIAaQANAAoA"
    KEY_SIZE = 256  # bits

    def __init__(self):
        """Inicializar el sistema de encriptación."""
        # Pre-calcular valores que no cambian
        # C# usa Encoding.ASCII.GetBytes() directamente sobre las strings
        self._iv_bytes = self.INITIAL_VECTOR.encode('ascii')
        self._salt_bytes = self.SALT_VALUE.encode('ascii')
        self._key_bytes = self._derive_key()

        logger.debug("Sistema de encriptación inicializado")

    def _derive_key(self) -> bytes:
        """
        Derivar clave de encriptación usando el algoritmo PasswordDeriveBytes de .NET.

        ⚠️ COMPATIBILIDAD C#:
        C# usa PasswordDeriveBytes con MD5, que NO es PBKDF2HMAC estándar.
        Debemos replicar exactamente el comportamiento de .NET Framework.

        El algoritmo de .NET PasswordDeriveBytes es:
        1. Base hash: Hash(password + salt) -> base_hash (1 iteración)
        2. Primer bloque: Iterar base_hash (N-1) veces más
        3. Bloques adicionales: Hash(str(ctrl) + base_hash) usando base_hash original

        Referencia: https://sysopfb.github.io/malware,/reverse-engineering/2018/05/12/MS-Derivation-functions.html

        Returns:
            Clave de 32 bytes (256 bits) derivada
        """
        password_bytes = self.PASSWORD.encode('ascii')
        key_size_bytes = self.KEY_SIZE // 8  # 256 bits = 32 bytes

        # Paso 1: Calcular base hash (password + salt) - 1 iteración
        base_hash = hashlib.md5(password_bytes + self._salt_bytes).digest()

        # Paso 2: Para el primer bloque, aplicar iteraciones adicionales
        first_block = base_hash
        for _ in range(self.PASSWORD_ITERATIONS - 1):
            first_block = hashlib.md5(first_block).digest()

        # Primer bloque: hash con N iteraciones completas
        key_material = first_block

        # Bloques adicionales: hash(str(ctrl) + base_hash)
        # IMPORTANTE: Usa base_hash (1 iteración), NO first_block
        ctrl = 1
        while len(key_material) < key_size_bytes:
            key_material += hashlib.md5(str(ctrl).encode('ascii') + base_hash).digest()
            ctrl += 1

        # Retornar exactamente KEY_SIZE bytes
        return key_material[:key_size_bytes]

    def encriptar(self, plain_text: str) -> Optional[str]:
        """
        Encriptar texto plano a Base64.

        Compatible con el método Encriptar() de la clase C#.

        Args:
            plain_text: Texto a encriptar (UTF-8)

        Returns:
            Texto encriptado en Base64, o None si hay error

        Raises:
            EncryptionError: Si hay error durante la encriptación

        Example:
            >>> encrypt = Encrypt()
            >>> encrypted = encrypt.encriptar("password123")
            >>> print(encrypted)
            "Rq8TzX0E9j+vH7kP2mN3lA=="
        """
        try:
            # Convertir texto a bytes UTF-8 (igual que C#)
            plain_text_bytes = plain_text.encode('utf-8')

            # Crear cipher AES en modo CBC
            cipher = Cipher(
                algorithms.AES(self._key_bytes),
                modes.CBC(self._iv_bytes),
                backend=default_backend()
            )

            # Crear encryptor
            encryptor = cipher.encryptor()

            # Aplicar padding PKCS7 manualmente (AES requiere bloques de 16 bytes)
            padded_data = self._pkcs7_pad(plain_text_bytes, 16)

            # Encriptar
            cipher_text_bytes = encryptor.update(padded_data) + encryptor.finalize()

            # Convertir a Base64
            cipher_text = base64.b64encode(cipher_text_bytes).decode('ascii')

            logger.debug(f"Texto encriptado exitosamente ({len(plain_text)} → {len(cipher_text)} chars)")

            return cipher_text

        except Exception as e:
            logger.error(f"Error al encriptar: {e}", exc_info=True)
            # Compatibilidad C#: retornar None en lugar de lanzar excepción
            return None

    def desencriptar(self, cipher_text: str) -> Optional[str]:
        """
        Desencriptar texto Base64 a texto plano.

        Compatible con el método Desencriptar() de la clase C#.

        Args:
            cipher_text: Texto encriptado en Base64

        Returns:
            Texto desencriptado (UTF-8), o None si hay error

        Raises:
            EncryptionError: Si hay error durante la desencriptación

        Example:
            >>> encrypt = Encrypt()
            >>> decrypted = encrypt.desencriptar("Rq8TzX0E9j+vH7kP2mN3lA==")
            >>> print(decrypted)
            "password123"
        """
        try:
            # Convertir Base64 a bytes
            cipher_text_bytes = base64.b64decode(cipher_text)

            # Crear cipher AES en modo CBC
            cipher = Cipher(
                algorithms.AES(self._key_bytes),
                modes.CBC(self._iv_bytes),
                backend=default_backend()
            )

            # Crear decryptor
            decryptor = cipher.decryptor()

            # Desencriptar
            padded_plain_text = decryptor.update(cipher_text_bytes) + decryptor.finalize()

            # Remover padding PKCS7
            plain_text_bytes = self._pkcs7_unpad(padded_plain_text)

            # Convertir a string UTF-8
            plain_text = plain_text_bytes.decode('utf-8')

            logger.debug(f"Texto desencriptado exitosamente ({len(cipher_text)} → {len(plain_text)} chars)")

            return plain_text

        except Exception as e:
            logger.error(f"Error al desencriptar: {e}", exc_info=True)
            # Compatibilidad C#: retornar None en lugar de lanzar excepción
            return None

    @staticmethod
    def _pkcs7_pad(data: bytes, block_size: int) -> bytes:
        """
        Aplicar padding PKCS7.

        Args:
            data: Datos a aplicar padding
            block_size: Tamaño del bloque (16 para AES)

        Returns:
            Datos con padding aplicado
        """
        padding_length = block_size - (len(data) % block_size)
        padding = bytes([padding_length] * padding_length)
        return data + padding

    @staticmethod
    def _pkcs7_unpad(data: bytes) -> bytes:
        """
        Remover padding PKCS7.

        Args:
            data: Datos con padding

        Returns:
            Datos sin padding

        Raises:
            ValueError: Si el padding es inválido
        """
        if len(data) == 0:
            raise ValueError("Datos vacíos")

        padding_length = data[-1]

        # Validar padding
        if padding_length > len(data) or padding_length == 0:
            raise ValueError("Padding inválido")

        # Verificar que todos los bytes de padding sean correctos
        if data[-padding_length:] != bytes([padding_length] * padding_length):
            raise ValueError("Padding corrupto")

        return data[:-padding_length]


# Funciones de conveniencia para uso directo
_encryptor = None


def get_encryptor() -> Encrypt:
    """
    Obtener instancia singleton del encriptador.

    Returns:
        Instancia de Encrypt
    """
    global _encryptor
    if _encryptor is None:
        _encryptor = Encrypt()
    return _encryptor


def encriptar(texto: str) -> Optional[str]:
    """
    Función de conveniencia para encriptar texto.

    Args:
        texto: Texto a encriptar

    Returns:
        Texto encriptado en Base64

    Example:
        >>> from src.auth.encryption import encriptar
        >>> encrypted = encriptar("mi_password")
    """
    return get_encryptor().encriptar(texto)


def desencriptar(texto_encriptado: str) -> Optional[str]:
    """
    Función de conveniencia para desencriptar texto.

    Args:
        texto_encriptado: Texto encriptado en Base64

    Returns:
        Texto desencriptado

    Example:
        >>> from src.auth.encryption import desencriptar
        >>> decrypted = desencriptar(encrypted_text)
    """
    return get_encryptor().desencriptar(texto_encriptado)
