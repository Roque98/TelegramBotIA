"""
Tests para el middleware de autenticación con tokens.
"""
import pytest
import json
from datetime import datetime, timedelta
from src.domain.auth.token_middleware import TokenMiddleware, validar_token, generar_token
from src.domain.auth.encryption import encriptar


class TestTokenMiddleware:
    """Tests para la clase TokenMiddleware."""

    def test_generar_token_valido(self):
        """Test de generación de token válido."""
        numero_empleado = 12345

        token = TokenMiddleware.generar_token(numero_empleado)

        # Verificar que el token es un string en Base64
        assert isinstance(token, str)
        assert len(token) > 0

        # Verificar que puede desencriptarse
        valido, datos, error = TokenMiddleware.validar_token(token)

        assert valido is True
        assert datos is not None
        assert error is None
        assert datos['numero_empleado'] == numero_empleado

    def test_validar_token_valido(self):
        """Test de validación de token válido."""
        token = TokenMiddleware.generar_token(54321)

        valido, datos, error = TokenMiddleware.validar_token(token)

        assert valido is True
        assert datos is not None
        assert error is None
        assert datos['numero_empleado'] == 54321
        assert 'timestamp' in datos
        assert 'timestamp_parsed' in datos

    def test_validar_token_expirado(self):
        """Test de rechazo de token expirado (más de 3 minutos)."""
        # Crear token con timestamp de hace 5 minutos
        timestamp_viejo = (datetime.now() - timedelta(minutes=5)).isoformat()

        token_data = {
            "numero_empleado": 99999,
            "timestamp": timestamp_viejo
        }

        token_expirado = encriptar(json.dumps(token_data))

        valido, datos, error = TokenMiddleware.validar_token(token_expirado)

        assert valido is False
        assert datos is None
        assert error is not None
        assert "expirado" in error.lower()

    def test_validar_token_futuro(self):
        """Test de rechazo de token con timestamp del futuro."""
        # Crear token con timestamp del futuro
        timestamp_futuro = (datetime.now() + timedelta(minutes=5)).isoformat()

        token_data = {
            "numero_empleado": 11111,
            "timestamp": timestamp_futuro
        }

        token_futuro = encriptar(json.dumps(token_data))

        valido, datos, error = TokenMiddleware.validar_token(token_futuro)

        assert valido is False
        assert "futuro" in error.lower()

    def test_validar_token_invalido(self):
        """Test de rechazo de token que no se puede desencriptar."""
        token_invalido = "esto_no_es_un_token_valido"

        valido, datos, error = TokenMiddleware.validar_token(token_invalido)

        assert valido is False
        assert datos is None
        assert error is not None

    def test_validar_token_json_invalido(self):
        """Test de rechazo de token con JSON inválido."""
        # Encriptar texto que no es JSON
        token_no_json = encriptar("esto no es JSON")

        valido, datos, error = TokenMiddleware.validar_token(token_no_json)

        assert valido is False
        assert "json" in error.lower()

    def test_validar_token_sin_numero_empleado(self):
        """Test de rechazo de token sin número de empleado."""
        token_data = {
            "timestamp": datetime.now().isoformat()
            # Falta numero_empleado
        }

        token_incompleto = encriptar(json.dumps(token_data))

        valido, datos, error = TokenMiddleware.validar_token(token_incompleto)

        assert valido is False
        assert "numero_empleado" in error.lower()

    def test_validar_token_sin_timestamp(self):
        """Test de rechazo de token sin timestamp."""
        token_data = {
            "numero_empleado": 12345
            # Falta timestamp
        }

        token_incompleto = encriptar(json.dumps(token_data))

        valido, datos, error = TokenMiddleware.validar_token(token_incompleto)

        assert valido is False
        assert "timestamp" in error.lower()

    def test_validar_token_numero_empleado_string(self):
        """Test de aceptación de número de empleado como string."""
        token_data = {
            "numero_empleado": "12345",  # String en lugar de int
            "timestamp": datetime.now().isoformat()
        }

        token = encriptar(json.dumps(token_data))

        valido, datos, error = TokenMiddleware.validar_token(token)

        assert valido is True
        assert datos['numero_empleado'] == 12345  # Debe convertirse a int

    def test_validar_token_numero_empleado_invalido(self):
        """Test de rechazo de número de empleado inválido."""
        token_data = {
            "numero_empleado": "no_es_numero",
            "timestamp": datetime.now().isoformat()
        }

        token = encriptar(json.dumps(token_data))

        valido, datos, error = TokenMiddleware.validar_token(token)

        assert valido is False
        assert "numero_empleado" in error.lower()

    def test_extraer_numero_empleado(self):
        """Test de extracción de número de empleado."""
        numero_empleado = 77777
        token = TokenMiddleware.generar_token(numero_empleado)

        numero_extraido = TokenMiddleware.extraer_numero_empleado(token)

        assert numero_extraido == numero_empleado

    def test_extraer_numero_empleado_token_invalido(self):
        """Test de extracción con token inválido retorna None."""
        token_invalido = "token_invalido"

        numero_extraido = TokenMiddleware.extraer_numero_empleado(token_invalido)

        assert numero_extraido is None

    def test_funciones_conveniencia(self):
        """Test de funciones de conveniencia."""
        # generar_token
        token = generar_token(12345)
        assert isinstance(token, str)

        # validar_token
        valido, datos, error = validar_token(token)
        assert valido is True
        assert datos['numero_empleado'] == 12345

    def test_token_valido_dentro_ventana(self):
        """Test de que token es válido dentro de la ventana de 3 minutos."""
        # Crear token con timestamp de hace 2 minutos (dentro de la ventana)
        timestamp_reciente = (datetime.now() - timedelta(minutes=2)).isoformat()

        token_data = {
            "numero_empleado": 33333,
            "timestamp": timestamp_reciente
        }

        token = encriptar(json.dumps(token_data))

        valido, datos, error = TokenMiddleware.validar_token(token)

        assert valido is True
        assert datos['numero_empleado'] == 33333

    def test_token_formatos_timestamp(self):
        """Test de soporte para diferentes formatos de timestamp."""
        numero_empleado = 44444

        # Formato ISO 8601
        token_data_1 = {
            "numero_empleado": numero_empleado,
            "timestamp": datetime.now().isoformat()
        }
        token_1 = encriptar(json.dumps(token_data_1))
        valido_1, _, _ = TokenMiddleware.validar_token(token_1)
        assert valido_1 is True

        # Formato con milisegundos
        token_data_2 = {
            "numero_empleado": numero_empleado,
            "timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")
        }
        token_2 = encriptar(json.dumps(token_data_2))
        valido_2, _, _ = TokenMiddleware.validar_token(token_2)
        assert valido_2 is True

        # Formato sin milisegundos
        token_data_3 = {
            "numero_empleado": numero_empleado,
            "timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        }
        token_3 = encriptar(json.dumps(token_data_3))
        valido_3, _, _ = TokenMiddleware.validar_token(token_3)
        assert valido_3 is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
