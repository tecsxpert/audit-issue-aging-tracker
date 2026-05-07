from __future__ import annotations

import json
import os
from datetime import datetime, timedelta, timezone
from typing import Any

import jwt
from dotenv import load_dotenv

from validation.common import REPO_ROOT

load_dotenv(REPO_ROOT / '.env')


def _log(event: str, **fields: Any) -> None:
    payload = {
        'event': event,
        'generated_at': datetime.now(tz=timezone.utc).isoformat(),
        **fields,
    }
    print(json.dumps(payload, sort_keys=True), flush=True)


def generate_test_jwt(subject: str = 'day11-validator', expires_in_seconds: int = 3600) -> str:
    jwt_secret = os.getenv('JWT_SECRET', '')
    jwt_algorithm = os.getenv('JWT_ALGORITHM', 'HS256')
    jwt_audience = os.getenv('JWT_AUDIENCE', '')
    jwt_issuer = os.getenv('JWT_ISSUER', '')

    missing = [
        name
        for name, value in {
            'JWT_SECRET': jwt_secret,
            'JWT_ALGORITHM': jwt_algorithm,
            'JWT_AUDIENCE': jwt_audience,
            'JWT_ISSUER': jwt_issuer,
        }.items()
        if not value
    ]
    if missing:
        raise RuntimeError(f'Cannot generate validation JWT. Missing environment variables: {missing}')

    now = datetime.now(tz=timezone.utc)
    issued_at = now - timedelta(seconds=5)
    payload = {
        'sub': subject,
        'aud': jwt_audience,
        'iss': jwt_issuer,
        'iat': issued_at,
        'exp': issued_at + timedelta(seconds=expires_in_seconds),
    }
    token = jwt.encode(payload, jwt_secret, algorithm=jwt_algorithm)
    _log(
        'token_generation_success',
        subject=subject,
        algorithm=jwt_algorithm,
        audience=jwt_audience,
        issuer=jwt_issuer,
        expires_in_seconds=expires_in_seconds,
    )
    return token


def authenticated_headers(subject: str = 'day11-validator') -> dict[str, str]:
    token = generate_test_jwt(subject=subject)
    return {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
    }
