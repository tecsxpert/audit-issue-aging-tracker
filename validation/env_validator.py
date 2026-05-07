from __future__ import annotations

import os
from urllib.parse import urlparse

from services.jwt_manager import validate_jwt_configuration
from validation.common import log, main_exit

REQUIRED = {
    'GROQ_API_KEY': 'Groq API authentication',
    'GROQ_MODEL': 'model selection',
    'JWT_SECRET': 'JWT validation',
    'JWT_ALGORITHM': 'JWT validation',
    'JWT_AUDIENCE': 'JWT claim validation',
    'JWT_ISSUER': 'JWT claim validation',
    'REDIS_URL': 'rate limiting and AI cache',
}


def validate_environment() -> None:
    findings: list[str] = []
    for name, purpose in REQUIRED.items():
        if not os.getenv(name):
            findings.append(f'{name} is required for {purpose}.')

    redis_url = os.getenv('REDIS_URL', '')
    if redis_url:
        parsed = urlparse(redis_url)
        if parsed.scheme not in {'redis', 'rediss'} or not parsed.hostname:
            findings.append('REDIS_URL must be a valid redis:// or rediss:// URL.')

    jwt_secret = os.getenv('JWT_SECRET', '')
    jwt_algorithm = os.getenv('JWT_ALGORITHM', 'HS256')
    findings.extend(validate_jwt_configuration(jwt_secret, jwt_algorithm, strict=False))

    if os.getenv('GROQ_MODEL') != 'llama-3.3-70b-versatile':
        log('env_warning', message='GROQ_MODEL differs from capstone target model.', model=os.getenv('GROQ_MODEL'))

    if findings:
        raise AssertionError('Environment validation failed: ' + ' '.join(findings))
    log('environment_validation_passed')


if __name__ == '__main__':
    main_exit(validate_environment)
