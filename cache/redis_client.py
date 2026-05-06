from __future__ import annotations
import os
from typing import Optional
import redis


def create_redis_client(url: str | None = None) -> redis.Redis | None:
    redis_url = url or os.getenv('REDIS_URL', '')
    if not redis_url:
        return None
    return redis.from_url(
        redis_url,
        decode_responses=True,
        socket_connect_timeout=5,
        socket_timeout=5,
    )
