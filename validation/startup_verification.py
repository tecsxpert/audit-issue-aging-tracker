from __future__ import annotations

import os
from pathlib import Path

from validation.common import REPO_ROOT, ValidationConfig, log, main_exit, wait_for_http_health

REQUIRED_ENV = (
    'GROQ_API_KEY',
    'GROQ_MODEL',
    'JWT_SECRET',
    'JWT_ALGORITHM',
    'JWT_AUDIENCE',
    'JWT_ISSUER',
    'REDIS_URL',
)


def verify_startup() -> None:
    missing = [name for name in REQUIRED_ENV if not os.getenv(name)]
    if missing:
        raise AssertionError(f'Missing required startup environment variables: {missing}')

    dockerfile = REPO_ROOT / 'Dockerfile'
    compose = REPO_ROOT / 'docker-compose.yml'
    for path in (dockerfile, compose):
        if not path.exists():
            raise AssertionError(f'Required deployment file is missing: {path}')

    dockerfile_text = dockerfile.read_text(encoding='utf-8')
    for marker in ('USER appuser', 'HEALTHCHECK', 'gunicorn', 'python:3.11-slim'):
        if marker not in dockerfile_text:
            raise AssertionError(f'Dockerfile missing production marker: {marker}')

    wait_for_http_health(ValidationConfig(), deadline_seconds=90)
    log('startup_verification_passed')


if __name__ == '__main__':
    main_exit(verify_startup)
