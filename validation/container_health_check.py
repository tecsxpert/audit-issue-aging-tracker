from __future__ import annotations

import os
from urllib.parse import urlparse, urlunparse

import redis

from validation.common import ValidationConfig, log, main_exit, request_json, tcp_check


def check_container_health() -> None:
    config = ValidationConfig()
    status, body, latency = request_json('GET', '/health', config=config)
    if status != 200 or body.get('status') != 'ok':
        raise AssertionError(f'Application health failed: {status} {body}')
    log('app_health_ok', latency_ms=latency, services=body.get('services'))

    redis_url = os.getenv('REDIS_URL', config.redis_url)
    redis_url_used = _ping_redis(redis_url)
    log('redis_health_ok', redis_url=redis_url_used)

    postgres_host = os.getenv('POSTGRES_HOST', 'postgres')
    postgres_port = int(os.getenv('POSTGRES_PORT', '5432'))
    postgres_host_used = _tcp_host_with_local_fallback(postgres_host, postgres_port)
    log('postgres_tcp_ok', host=postgres_host_used, port=postgres_port)


def _ping_redis(redis_url: str) -> str:
    candidates = [redis_url]
    parsed = urlparse(redis_url)
    if parsed.hostname not in {'127.0.0.1', 'localhost'}:
        host_port = '127.0.0.1'
        if parsed.port:
            host_port = f'{host_port}:{parsed.port}'
        candidates.append(urlunparse(parsed._replace(netloc=host_port)))

    last_error: Exception | None = None
    for candidate in candidates:
        try:
            client = redis.from_url(candidate, socket_connect_timeout=5, socket_timeout=5, decode_responses=True)
            if client.ping() is True:
                return candidate
        except Exception as exc:
            last_error = exc
    raise AssertionError(f'Redis ping failed for validation URLs: {last_error}')


def _tcp_host_with_local_fallback(host: str, port: int) -> str:
    candidates = [host]
    if host not in {'127.0.0.1', 'localhost'}:
        candidates.append('127.0.0.1')
    for candidate in candidates:
        if tcp_check(candidate, port):
            return candidate
    raise AssertionError(f'TCP check failed for candidates {candidates} on port {port}.')


if __name__ == '__main__':
    main_exit(check_container_health)
