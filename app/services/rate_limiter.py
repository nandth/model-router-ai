"""Simple in-memory rate limiting for FastAPI routes.

Notes:
- This is per-process (in-memory). If you run multiple workers/instances, each will
  enforce its own limits. For production, swap this with a shared store (Redis).
"""

from __future__ import annotations

import os
import threading
import time
from collections import deque
from dataclasses import dataclass
from typing import Deque, Dict, Optional, Tuple

from fastapi import HTTPException, Request


def _env_int(name: str, default: int) -> int:
    try:
        raw = os.getenv(name)
        if raw is None or raw == "":
            return default
        return int(raw)
    except Exception:
        return default


def _env_bool(name: str, default: bool = False) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "y", "on"}


@dataclass(frozen=True)
class RateLimitConfig:
    """Rate limit configuration for a route scope."""

    max_requests: int
    window_seconds: int


class SlidingWindowRateLimiter:
    """Thread-safe sliding window limiter."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._hits: Dict[str, Deque[float]] = {}

    def hit(self, key: str, *, max_requests: int, window_seconds: int) -> Tuple[bool, int]:
        """
        Record a hit for `key` and return (allowed, retry_after_seconds).

        retry_after_seconds is 0 when allowed.
        """
        now = time.time()
        window_start = now - window_seconds

        with self._lock:
            q = self._hits.get(key)
            if q is None:
                q = deque()
                self._hits[key] = q

            # Prune old timestamps.
            while q and q[0] <= window_start:
                q.popleft()

            if len(q) >= max_requests:
                # Oldest hit determines when the window frees up.
                retry_after = int(max(1, (q[0] + window_seconds) - now))
                return False, retry_after

            q.append(now)
            return True, 0


_DEFAULT_LIMITER = SlidingWindowRateLimiter()


def _client_ip(request: Request) -> str:
    # We intentionally do NOT trust X-Forwarded-For by default, since it is trivial
    # to spoof unless your deployment strips/sets it at the edge.
    if request.client is None or request.client.host is None:
        return "unknown"
    return request.client.host


def rate_limit_dependency(
    *,
    scope: str,
    config: RateLimitConfig,
    limiter: SlidingWindowRateLimiter = _DEFAULT_LIMITER,
):
    """
    Create a FastAPI dependency enforcing a simple per-IP rate limit.

    Env toggles:
    - RATE_LIMIT_DISABLED=true to disable all limits.
    """

    disabled = _env_bool("RATE_LIMIT_DISABLED", False)

    async def _dep(request: Request) -> None:
        if disabled:
            return

        key = f"{_client_ip(request)}:{scope}"
        allowed, retry_after = limiter.hit(
            key, max_requests=config.max_requests, window_seconds=config.window_seconds
        )
        if not allowed:
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded",
                headers={"Retry-After": str(retry_after)},
            )

    return _dep


def load_rate_limit_config(*, max_requests_env: str, default_max_requests: int) -> RateLimitConfig:
    """Load a RateLimitConfig from env with a shared window."""
    window_seconds = _env_int("RATE_LIMIT_WINDOW_SECONDS", 60)
    max_requests = _env_int(max_requests_env, default_max_requests)
    return RateLimitConfig(max_requests=max_requests, window_seconds=window_seconds)

