from unittest.mock import MagicMock

from redis.exceptions import RedisError

from app.core.config import settings
from app.services.rate_limit_service import RateLimiter


def test_rate_limiter_disabled_allows_request(
    monkeypatch,
):
    monkeypatch.setattr(
        settings,
        "RATE_LIMIT_ENABLED",
        False,
    )

    redis_client = MagicMock()

    limiter = RateLimiter(
        redis_client=redis_client,
    )

    result = limiter.check(
        key="disabled-test",
        limit=5,
        window_seconds=60,
    )

    assert result.allowed is True
    assert result.limit == 5
    assert result.remaining == 5
    assert result.retry_after_seconds is None

    redis_client.incr.assert_not_called()
    redis_client.expire.assert_not_called()
    redis_client.ttl.assert_not_called()


def test_first_request_sets_expiry(
    monkeypatch,
):
    monkeypatch.setattr(
        settings,
        "RATE_LIMIT_ENABLED",
        True,
    )

    redis_client = MagicMock()

    redis_client.incr.return_value = 1
    redis_client.ttl.return_value = 60

    limiter = RateLimiter(
        redis_client=redis_client,
    )

    result = limiter.check(
        key="first-request",
        limit=5,
        window_seconds=60,
    )

    assert result.allowed is True
    assert result.limit == 5
    assert result.remaining == 4
    assert result.retry_after_seconds is None

    redis_client.incr.assert_called_once_with(
        "rate_limit:first-request"
    )

    redis_client.expire.assert_called_once_with(
        "rate_limit:first-request",
        60,
    )

    redis_client.ttl.assert_called_once_with(
        "rate_limit:first-request"
    )


def test_existing_counter_does_not_reset_expiry(
    monkeypatch,
):
    monkeypatch.setattr(
        settings,
        "RATE_LIMIT_ENABLED",
        True,
    )

    redis_client = MagicMock()

    redis_client.incr.return_value = 2
    redis_client.ttl.return_value = 45

    limiter = RateLimiter(
        redis_client=redis_client,
    )

    result = limiter.check(
        key="existing-counter",
        limit=5,
        window_seconds=60,
    )

    assert result.allowed is True
    assert result.remaining == 3

    redis_client.expire.assert_not_called()


def test_requests_reduce_remaining_quota(
    monkeypatch,
):
    monkeypatch.setattr(
        settings,
        "RATE_LIMIT_ENABLED",
        True,
    )

    redis_client = MagicMock()

    redis_client.incr.return_value = 4
    redis_client.ttl.return_value = 20

    limiter = RateLimiter(
        redis_client=redis_client,
    )

    result = limiter.check(
        key="remaining-test",
        limit=5,
        window_seconds=60,
    )

    assert result.allowed is True
    assert result.limit == 5
    assert result.remaining == 1
    assert result.retry_after_seconds is None


def test_request_at_limit_is_still_allowed(
    monkeypatch,
):
    monkeypatch.setattr(
        settings,
        "RATE_LIMIT_ENABLED",
        True,
    )

    redis_client = MagicMock()

    redis_client.incr.return_value = 5
    redis_client.ttl.return_value = 15

    limiter = RateLimiter(
        redis_client=redis_client,
    )

    result = limiter.check(
        key="at-limit",
        limit=5,
        window_seconds=60,
    )

    assert result.allowed is True
    assert result.remaining == 0
    assert result.retry_after_seconds is None


def test_request_over_limit_is_denied(
    monkeypatch,
):
    monkeypatch.setattr(
        settings,
        "RATE_LIMIT_ENABLED",
        True,
    )

    redis_client = MagicMock()

    redis_client.incr.return_value = 6
    redis_client.ttl.return_value = 25

    limiter = RateLimiter(
        redis_client=redis_client,
    )

    result = limiter.check(
        key="over-limit",
        limit=5,
        window_seconds=60,
    )

    assert result.allowed is False
    assert result.limit == 5
    assert result.remaining == 0
    assert result.retry_after_seconds == 25


def test_over_limit_uses_window_when_ttl_is_invalid(
    monkeypatch,
):
    monkeypatch.setattr(
        settings,
        "RATE_LIMIT_ENABLED",
        True,
    )

    redis_client = MagicMock()

    redis_client.incr.return_value = 6
    redis_client.ttl.return_value = -1

    limiter = RateLimiter(
        redis_client=redis_client,
    )

    result = limiter.check(
        key="invalid-ttl",
        limit=5,
        window_seconds=60,
    )

    assert result.allowed is False
    assert result.remaining == 0
    assert result.retry_after_seconds == 60


def test_redis_failure_fails_open(
    monkeypatch,
):
    monkeypatch.setattr(
        settings,
        "RATE_LIMIT_ENABLED",
        True,
    )

    redis_client = MagicMock()

    redis_client.incr.side_effect = RedisError(
        "redis unavailable"
    )

    limiter = RateLimiter(
        redis_client=redis_client,
    )

    result = limiter.check(
        key="redis-failure",
        limit=5,
        window_seconds=60,
    )

    assert result.allowed is True
    assert result.limit == 5
    assert result.remaining == 5
    assert result.retry_after_seconds is None
