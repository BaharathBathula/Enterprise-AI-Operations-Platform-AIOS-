import logging
from dataclasses import dataclass

import redis
from redis import Redis
from redis.exceptions import RedisError

from app.core.config import settings

logger = logging.getLogger("app.rate_limit")


@dataclass
class RateLimitResult:
    allowed: bool
    limit: int
    remaining: int
    retry_after_seconds: int | None


class RateLimiter:
    def __init__(
        self,
        redis_client: Redis | None = None,
    ):
        self.redis = (
            redis_client
            if redis_client is not None
            else redis.from_url(
                settings.REDIS_URL,
                decode_responses=True,
            )
        )

    def check(
        self,
        *,
        key: str,
        limit: int | None = None,
        window_seconds: int | None = None,
    ) -> RateLimitResult:
        resolved_limit = (
            limit
            if limit is not None
            else settings.RATE_LIMIT_REQUESTS
        )

        resolved_window = (
            window_seconds
            if window_seconds is not None
            else settings.RATE_LIMIT_WINDOW_SECONDS
        )

        if not settings.RATE_LIMIT_ENABLED:
            return RateLimitResult(
                allowed=True,
                limit=resolved_limit,
                remaining=resolved_limit,
                retry_after_seconds=None,
            )

        redis_key = f"rate_limit:{key}"

        try:
            current = self.redis.incr(
                redis_key
            )

            if current == 1:
                self.redis.expire(
                    redis_key,
                    resolved_window,
                )

            ttl = self.redis.ttl(
                redis_key
            )

        except RedisError:
            logger.exception(
                "Rate limiter Redis failure"
            )

            return RateLimitResult(
                allowed=True,
                limit=resolved_limit,
                remaining=resolved_limit,
                retry_after_seconds=None,
            )

        remaining = max(
            resolved_limit - current,
            0,
        )

        if current > resolved_limit:
            retry_after = (
                ttl
                if ttl is not None and ttl > 0
                else resolved_window
            )

            return RateLimitResult(
                allowed=False,
                limit=resolved_limit,
                remaining=0,
                retry_after_seconds=retry_after,
            )

        return RateLimitResult(
            allowed=True,
            limit=resolved_limit,
            remaining=remaining,
            retry_after_seconds=None,
        )


rate_limiter = RateLimiter()
