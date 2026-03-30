"""
Tests para src/utils/input_validator.py

Cobertura:
- InputValidator.validate_query: longitud, vacío, patrones peligrosos, caracteres especiales
- InputValidator.sanitize_query: null bytes, espacios
"""
import pytest

from src.utils.input_validator import InputValidator


class TestValidateQuery:

    def test_valid_query(self):
        ok, err = InputValidator.validate_query("¿Cuántas ventas hubo hoy?")
        assert ok is True
        assert err == ""

    def test_empty_string(self):
        ok, err = InputValidator.validate_query("")
        assert ok is False
        assert "vacía" in err

    def test_whitespace_only(self):
        ok, err = InputValidator.validate_query("   ")
        assert ok is False

    def test_too_short(self):
        ok, err = InputValidator.validate_query("ab")
        assert ok is False
        assert "corta" in err

    def test_exactly_min_length(self):
        query = "a" * InputValidator.MIN_QUERY_LENGTH
        ok, _ = InputValidator.validate_query(query)
        assert ok is True

    def test_too_long(self):
        query = "a" * (InputValidator.MAX_QUERY_LENGTH + 1)
        ok, err = InputValidator.validate_query(query)
        assert ok is False
        assert "larga" in err

    def test_exactly_max_length(self):
        query = "a" * InputValidator.MAX_QUERY_LENGTH
        ok, _ = InputValidator.validate_query(query)
        assert ok is True

    def test_xss_script_tag(self):
        ok, err = InputValidator.validate_query("<script>alert(1)</script>")
        assert ok is False
        assert "no permitido" in err

    def test_xss_javascript_protocol(self):
        ok, err = InputValidator.validate_query("javascript:alert(1)")
        assert ok is False

    def test_xss_data_uri(self):
        ok, err = InputValidator.validate_query("data:text/html,<h1>XSS</h1>")
        assert ok is False

    def test_null_byte(self):
        ok, err = InputValidator.validate_query("query\x00injection")
        assert ok is False

    def test_too_many_special_chars(self):
        # Más del 30% de caracteres especiales
        query = "abc" + "!@#$%^&*()" * 10
        ok, err = InputValidator.validate_query(query)
        assert ok is False
        assert "caracteres especiales" in err

    def test_acceptable_special_chars(self):
        # Signos de puntuación normales no deben fallar
        ok, _ = InputValidator.validate_query("¿Cuánto es el 50% de 200?")
        assert ok is True

    def test_case_insensitive_xss(self):
        ok, _ = InputValidator.validate_query("<SCRIPT>alert(1)</SCRIPT>")
        assert ok is False


class TestSanitizeQuery:

    def test_removes_null_bytes(self):
        result = InputValidator.sanitize_query("hello\x00world")
        assert "\x00" not in result
        assert "helloworld" in result

    def test_normalizes_multiple_spaces(self):
        result = InputValidator.sanitize_query("hola   mundo   test")
        assert result == "hola mundo test"

    def test_strips_whitespace(self):
        result = InputValidator.sanitize_query("  hola mundo  ")
        assert result == "hola mundo"

    def test_empty_string_stays_empty(self):
        result = InputValidator.sanitize_query("")
        assert result == ""

    def test_normal_text_unchanged(self):
        text = "Consulta normal de ventas"
        assert InputValidator.sanitize_query(text) == text
