"""
Tests para el módulo de encriptación.

Verifica compatibilidad con la implementación C# y funcionalidad correcta.
"""
import pytest
from src.auth.encryption import Encrypt, encriptar, desencriptar


class TestEncrypt:
    """Tests para la clase Encrypt."""

    def test_encriptar_desencriptar_simple(self):
        """Test básico de encriptación y desencriptación."""
        encrypt = Encrypt()

        texto_original = "Hola Mundo"
        texto_encriptado = encrypt.encriptar(texto_original)
        texto_desencriptado = encrypt.desencriptar(texto_encriptado)

        assert texto_desencriptado == texto_original

    def test_encriptar_desencriptar_password(self):
        """Test con password común."""
        encrypt = Encrypt()

        password = "MiPassword123!@#"
        encrypted = encrypt.encriptar(password)
        decrypted = encrypt.desencriptar(encrypted)

        assert decrypted == password

    def test_encriptar_desencriptar_texto_largo(self):
        """Test con texto largo (múltiples bloques AES)."""
        encrypt = Encrypt()

        texto_largo = "Este es un texto mucho más largo que requiere múltiples bloques de AES para ser encriptado correctamente. " * 5
        encrypted = encrypt.encriptar(texto_largo)
        decrypted = encrypt.desencriptar(encrypted)

        assert decrypted == texto_largo

    def test_encriptar_texto_vacio(self):
        """Test con string vacío."""
        encrypt = Encrypt()

        texto = ""
        encrypted = encrypt.encriptar(texto)
        decrypted = encrypt.desencriptar(encrypted)

        assert decrypted == texto

    def test_encriptar_caracteres_especiales(self):
        """Test con caracteres especiales y UTF-8."""
        encrypt = Encrypt()

        texto = "Ñoño 你好 🚀 @#$%^&*()"
        encrypted = encrypt.encriptar(texto)
        decrypted = encrypt.desencriptar(encrypted)

        assert decrypted == texto

    def test_resultado_encriptado_es_base64(self):
        """Verificar que el resultado encriptado es Base64 válido."""
        import base64
        import re

        encrypt = Encrypt()
        encrypted = encrypt.encriptar("test")

        # Patrón Base64 válido
        base64_pattern = re.compile(r'^[A-Za-z0-9+/]*={0,2}$')
        assert base64_pattern.match(encrypted) is not None

        # Debe poder decodificarse
        try:
            base64.b64decode(encrypted)
        except Exception:
            pytest.fail("El texto encriptado no es Base64 válido")

    def test_mismo_texto_produce_mismo_cifrado(self):
        """
        Verificar que el mismo texto siempre produce el mismo cifrado.

        Esto es porque usamos IV fijo (por compatibilidad C#).
        En producción moderna, se usaría IV random.
        """
        encrypt = Encrypt()

        texto = "test123"
        encrypted1 = encrypt.encriptar(texto)
        encrypted2 = encrypt.encriptar(texto)

        assert encrypted1 == encrypted2

    def test_diferentes_textos_producen_diferentes_cifrados(self):
        """Verificar que textos diferentes producen cifrados diferentes."""
        encrypt = Encrypt()

        encrypted1 = encrypt.encriptar("texto1")
        encrypted2 = encrypt.encriptar("texto2")

        assert encrypted1 != encrypted2

    def test_desencriptar_texto_invalido_retorna_none(self):
        """Verificar que texto inválido retorna None."""
        encrypt = Encrypt()

        # Base64 inválido
        result = encrypt.desencriptar("esto no es base64 válido!")
        assert result is None

    def test_desencriptar_base64_invalido_retorna_none(self):
        """Verificar que Base64 válido pero contenido inválido retorna None."""
        encrypt = Encrypt()

        # Base64 válido pero no es resultado de nuestra encriptación
        result = encrypt.desencriptar("SGVsbG8gV29ybGQ=")  # "Hello World" en base64
        assert result is None

    def test_funciones_conveniencia(self):
        """Test de funciones de conveniencia encriptar() y desencriptar()."""
        texto = "Test de funciones globales"

        encrypted = encriptar(texto)
        decrypted = desencriptar(encrypted)

        assert decrypted == texto

    def test_singleton_encryptor(self):
        """Verificar que get_encryptor() retorna singleton."""
        from src.auth.encryption import get_encryptor

        enc1 = get_encryptor()
        enc2 = get_encryptor()

        assert enc1 is enc2


class TestCompatibilidadC:
    """
    Tests de compatibilidad con implementación C#.

    Estos valores fueron generados con la clase C# original.
    """

    def test_desencriptar_valor_generado_por_csharp(self):
        """
        Test con valor encriptado por la implementación C# original.

        ⚠️ IMPORTANTE: Si este test falla, significa que la implementación
        Python NO es compatible con C# y necesita ajustes.
        """
        encrypt = Encrypt()

        # Estos valores fueron generados con el código C# original
        # Formato: (texto_plano, texto_encriptado_por_csharp)
        test_cases = [
            ("usrmon", "ICqKPRWYKVg5pZLA7ZQCKA=="),
            ("MonAplic01@", "c+GoNihnM/3L7BeKobPKgA=="),
            ("sa", "GlMuTDkzdxRIcm7fkMsuvQ=="),
        ]

        for plain_text, csharp_encrypted in test_cases:
            decrypted = encrypt.desencriptar(csharp_encrypted)
            assert decrypted == plain_text, \
                f"Incompatibilidad C#: esperado '{plain_text}', obtenido '{decrypted}'"

    def test_encriptar_compatible_con_csharp(self):
        """
        Verificar que Python genera los mismos valores encriptados que C#.

        ⚠️ IMPORTANTE: Si este test falla, la encriptación Python -> C# no funciona.
        """
        encrypt = Encrypt()

        # Valores encriptados por Python deben coincidir exactamente con C#
        test_cases = [
            ("usrmon", "ICqKPRWYKVg5pZLA7ZQCKA=="),
            ("MonAplic01@", "c+GoNihnM/3L7BeKobPKgA=="),
            ("sa", "GlMuTDkzdxRIcm7fkMsuvQ=="),
        ]

        for plain_text, expected_encrypted in test_cases:
            encrypted = encrypt.encriptar(plain_text)
            assert encrypted == expected_encrypted, \
                f"Encriptación incompatible: '{plain_text}' -> '{encrypted}' (esperado '{expected_encrypted}')"

    def test_encriptar_para_csharp(self):
        """
        Generar valores encriptados que pueden ser verificados en C#.

        Ejecutar este test y copiar los valores a C# para verificar compatibilidad.
        """
        encrypt = Encrypt()

        test_values = [
            "password123",
            "admin",
            "Hola Mundo",
            "user@example.com",
        ]

        print("\n=== Valores para verificar en C# ===")
        for value in test_values:
            encrypted = encrypt.encriptar(value)
            print(f"Texto plano: '{value}'")
            print(f"Encriptado:  '{encrypted}'")
            print()


class TestSeguridad:
    """Tests relacionados con seguridad."""

    def test_constantes_correctas(self):
        """Verificar que las constantes coinciden con C#."""
        encrypt = Encrypt()

        assert encrypt.PASSWORD == "m0n4pl1cBAZ.10"
        assert encrypt.SALT_VALUE == "c9a5d2f21f00469ff48a60fe5311b2ff"
        assert encrypt.HASH_ALGORITHM == "MD5"
        assert encrypt.PASSWORD_ITERATIONS == 2
        assert encrypt.INITIAL_VECTOR == "bQBhAHIAaQANAAoA"
        assert encrypt.KEY_SIZE == 256

    def test_key_size_correcta(self):
        """Verificar que la clave derivada tiene el tamaño correcto."""
        encrypt = Encrypt()

        # 256 bits = 32 bytes
        assert len(encrypt._key_bytes) == 32

    def test_iv_size_correcta(self):
        """Verificar que el IV tiene el tamaño correcto para AES."""
        encrypt = Encrypt()

        # AES requiere IV de 16 bytes
        assert len(encrypt._iv_bytes) == 16


if __name__ == "__main__":
    # Ejecutar tests
    pytest.main([__file__, "-v"])
