from __future__ import annotations

import os

import redis

from validation.common import ValidationConfig, log, main_exit, request_json, tcp_check


def check_container_health() -> None:
    config = ValidationConfig()
    status, body, latency = request_json('GET', '/health', config=config)
    if status != 200 or body.get('status') != 'ok':
        raise AssertionError(f'Application health failed: {status} {body}')
    log('app_health_ok', latency_ms=latency, services=body.get('services'))

    redis_url = os.getenv('REDIS_URL', config.redis_url)
    client = redis.from_url(redis_url, socket_connect_timeout=5, socket_timeout=5, decode_responses=True)
    if client.ping() is not True:
        raise AssertionError('Redis ping did not return PONG.')
    log('redis_health_ok', redis_url=redis_url)

    postgres_host = os.getenv('POSTGRES_HOST', 'postgres')
    postgres_port = int(os.getenv('POSTGRES_PORT', '5432'))
    if not tcp_check(postgres_host, postgres_port):
        raise AssertionError(f'PostgreSQL TCP check failed for {postgres_host}:{postgres_port}.')
    log('postgres_tcp_ok', host=postgres_host, port=postgres_port)


if __name__ == '__main__':
    main_exit(check_container_health)
