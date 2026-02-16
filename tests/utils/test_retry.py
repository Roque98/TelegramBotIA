"""
Tests para el modulo de retry con tenacity.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy.exc import OperationalError, TimeoutError as SQLTimeoutError

from src.utils.retry import llm_retry, db_retry


# ============================================================
# Tests para llm_retry
# ============================================================


class TestLLMRetry:
    """Tests para el decorador llm_retry."""

    @pytest.mark.asyncio
    async def test_success_no_retry(self):
        """No reintenta si la funcion tiene exito."""
        call_count = 0

        @llm_retry(max_attempts=3, min_wait=0, max_wait=1)
        async def successful_call():
            nonlocal call_count
            call_count += 1
            return "ok"

        result = await successful_call()
        assert result == "ok"
        assert call_count == 1

    @pytest.mark.asyncio
    async def test_retry_on_connection_error(self):
        """Reintenta en ConnectionError."""
        call_count = 0

        @llm_retry(max_attempts=3, min_wait=0, max_wait=1)
        async def flaky_call():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ConnectionError("Connection reset")
            return "recovered"

        result = await flaky_call()
        assert result == "recovered"
        assert call_count == 3

    @pytest.mark.asyncio
    async def test_retry_on_timeout_error(self):
        """Reintenta en TimeoutError."""
        call_count = 0

        @llm_retry(max_attempts=3, min_wait=0, max_wait=1)
        async def timeout_call():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise TimeoutError("Request timed out")
            return "ok"

        result = await timeout_call()
        assert result == "ok"
        assert call_count == 2

    @pytest.mark.asyncio
    async def test_no_retry_on_value_error(self):
        """NO reintenta en errores no transitorios (ValueError)."""
        call_count = 0

        @llm_retry(max_attempts=3, min_wait=0, max_wait=1)
        async def bad_call():
            nonlocal call_count
            call_count += 1
            raise ValueError("Invalid input")

        with pytest.raises(ValueError, match="Invalid input"):
            await bad_call()
        assert call_count == 1

    @pytest.mark.asyncio
    async def test_max_attempts_exhausted(self):
        """Lanza excepcion original tras agotar reintentos."""
        call_count = 0

        @llm_retry(max_attempts=3, min_wait=0, max_wait=1)
        async def always_fails():
            nonlocal call_count
            call_count += 1
            raise ConnectionError("Always fails")

        with pytest.raises(ConnectionError, match="Always fails"):
            await always_fails()
        assert call_count == 3

    @pytest.mark.asyncio
    async def test_retry_on_openai_rate_limit(self):
        """Reintenta en openai.RateLimitError si openai esta disponible."""
        try:
            import openai
        except ImportError:
            pytest.skip("openai not installed")

        call_count = 0

        @llm_retry(max_attempts=3, min_wait=0, max_wait=1)
        async def rate_limited_call():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise openai.RateLimitError(
                    message="Rate limit exceeded",
                    response=MagicMock(status_code=429, headers={}),
                    body=None,
                )
            return "ok"

        result = await rate_limited_call()
        assert result == "ok"
        assert call_count == 3


# ============================================================
# Tests para db_retry
# ============================================================


class TestDBRetry:
    """Tests para el decorador db_retry."""

    def test_success_no_retry(self):
        """No reintenta si la funcion tiene exito."""
        call_count = 0

        @db_retry(max_attempts=3, min_wait=0, max_wait=1)
        def successful_query():
            nonlocal call_count
            call_count += 1
            return [{"id": 1}]

        result = successful_query()
        assert result == [{"id": 1}]
        assert call_count == 1

    def test_retry_on_operational_error(self):
        """Reintenta en OperationalError (conexion perdida)."""
        call_count = 0

        @db_retry(max_attempts=3, min_wait=0, max_wait=1)
        def flaky_query():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise OperationalError("connection lost", {}, Exception())
            return [{"id": 1}]

        result = flaky_query()
        assert result == [{"id": 1}]
        assert call_count == 3

    def test_retry_on_sql_timeout(self):
        """Reintenta en SQLTimeoutError."""
        call_count = 0

        @db_retry(max_attempts=3, min_wait=0, max_wait=1)
        def slow_query():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise SQLTimeoutError("query timed out", {}, Exception())
            return []

        result = slow_query()
        assert result == []
        assert call_count == 2

    def test_no_retry_on_value_error(self):
        """NO reintenta en ValueError (query invalida)."""
        call_count = 0

        @db_retry(max_attempts=3, min_wait=0, max_wait=1)
        def invalid_query():
            nonlocal call_count
            call_count += 1
            raise ValueError("Solo se permiten consultas SELECT")

        with pytest.raises(ValueError):
            invalid_query()
        assert call_count == 1

    def test_max_attempts_exhausted(self):
        """Lanza excepcion original tras agotar reintentos."""
        call_count = 0

        @db_retry(max_attempts=2, min_wait=0, max_wait=1)
        def always_fails():
            nonlocal call_count
            call_count += 1
            raise OperationalError("db down", {}, Exception())

        with pytest.raises(OperationalError):
            always_fails()
        assert call_count == 2

    def test_no_retry_on_runtime_error(self):
        """NO reintenta en RuntimeError (error de SQL, no transitorio)."""
        call_count = 0

        @db_retry(max_attempts=3, min_wait=0, max_wait=1)
        def sql_error():
            nonlocal call_count
            call_count += 1
            raise RuntimeError("Invalid SQL syntax")

        with pytest.raises(RuntimeError):
            sql_error()
        assert call_count == 1
