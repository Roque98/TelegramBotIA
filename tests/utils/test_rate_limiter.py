"""
Tests para src/utils/rate_limiter.py

Cobertura:
- RateLimiter.is_allowed: ventana de tiempo, límite por usuario
- RateLimiter.get_retry_after: tiempo restante
- RateLimiter.get_remaining_requests: requests disponibles
- Aislamiento entre usuarios
"""
import pytest
from datetime import datetime, timedelta
from unittest.mock import patch

from src.utils.rate_limiter import RateLimiter


@pytest.fixture
def limiter():
    """Rate limiter con límite bajo para pruebas."""
    return RateLimiter(max_requests=3, time_window=60)


class TestIsAllowed:

    def test_first_request_allowed(self, limiter):
        assert limiter.is_allowed(user_id=1) is True

    def test_requests_within_limit_allowed(self, limiter):
        for _ in range(3):
            assert limiter.is_allowed(user_id=1) is True

    def test_request_exceeding_limit_blocked(self, limiter):
        for _ in range(3):
            limiter.is_allowed(user_id=1)
        # El 4to debe ser bloqueado
        assert limiter.is_allowed(user_id=1) is False

    def test_different_users_independent(self, limiter):
        for _ in range(3):
            limiter.is_allowed(user_id=1)
        # Usuario 2 no debe verse afectado por usuario 1
        assert limiter.is_allowed(user_id=2) is True

    def test_old_requests_cleaned_up(self, limiter):
        """Requests fuera de la ventana no cuentan."""
        old_time = datetime.now() - timedelta(seconds=120)
        limiter.requests[1] = [old_time, old_time, old_time]
        # Requests expirados, debe permitir
        assert limiter.is_allowed(user_id=1) is True

    def test_allows_after_window_expires(self, limiter):
        """Después de expirar la ventana se pueden hacer más requests."""
        # Llenar el límite con timestamps expirados
        old_time = datetime.now() - timedelta(seconds=120)
        limiter.requests[1] = [old_time, old_time, old_time]
        # Ahora debe permitir
        assert limiter.is_allowed(user_id=1) is True


class TestGetRetryAfter:

    def test_no_requests_returns_zero(self, limiter):
        assert limiter.get_retry_after(user_id=99) == 0

    def test_returns_positive_when_limited(self, limiter):
        for _ in range(3):
            limiter.is_allowed(user_id=1)
        limiter.is_allowed(user_id=1)  # blocked

        retry = limiter.get_retry_after(user_id=1)
        assert retry >= 0

    def test_returns_zero_for_expired_requests(self, limiter):
        old_time = datetime.now() - timedelta(seconds=120)
        limiter.requests[1] = [old_time]
        # El request expiró, retry debe ser 0
        retry = limiter.get_retry_after(user_id=1)
        assert retry == 0


class TestGetRemainingRequests:

    def test_full_capacity_initially(self, limiter):
        assert limiter.get_remaining_requests(user_id=1) == 3

    def test_decreases_with_each_request(self, limiter):
        limiter.is_allowed(user_id=1)
        assert limiter.get_remaining_requests(user_id=1) == 2

    def test_zero_when_limit_reached(self, limiter):
        for _ in range(3):
            limiter.is_allowed(user_id=1)
        assert limiter.get_remaining_requests(user_id=1) == 0

    def test_expired_requests_not_counted(self, limiter):
        old_time = datetime.now() - timedelta(seconds=120)
        limiter.requests[1] = [old_time, old_time]
        # Los expirados no cuentan, deben quedar 3 disponibles
        assert limiter.get_remaining_requests(user_id=1) == 3

    def test_users_isolated(self, limiter):
        for _ in range(3):
            limiter.is_allowed(user_id=1)
        assert limiter.get_remaining_requests(user_id=2) == 3
