from __future__ import annotations
from typing import Any, Iterable
import jwt
from jwt import ExpiredSignatureError, InvalidTokenError

SUPPORTED_JWT_ALGORITHMS = {'HS256', 'HS384', 'HS512'}
MIN_SECRET_LENGTH = 32
WEAK_SECRETS = {'secret', 'test-secret', 'changeme', 'password', 'your_jwt_secret_here'}


class JwtValidationError(ValueError):
    pass


def validate_jwt(
    token: str,
    secret: str,
    algorithms: Iterable[str],
    audience: str | None = None,
    issuer: str | None = None,
) -> dict[str, Any]:
    if not token:
        raise JwtValidationError('Missing JWT token.')
    algorithm_list = list(algorithms)
    unsupported = [algorithm for algorithm in algorithm_list if algorithm not in SUPPORTED_JWT_ALGORITHMS]
    if unsupported:
        raise JwtValidationError('Unsupported JWT signing algorithm configured.')
    try:
        payload = jwt.decode(
            token,
            secret,
            algorithms=algorithm_list,
            audience=audience if audience else None,
            issuer=issuer if issuer else None,
            options={'require': ['exp']},
        )
    except ExpiredSignatureError as exc:
        raise JwtValidationError('JWT token has expired.') from exc
    except InvalidTokenError as exc:
        raise JwtValidationError(f'Invalid JWT token: {exc}') from exc
    if not isinstance(payload, dict):
        raise JwtValidationError('JWT payload must be a valid JSON object.')
    return payload


def is_weak_jwt_secret(secret: str) -> bool:
    return len(secret) < MIN_SECRET_LENGTH or secret in WEAK_SECRETS


def validate_jwt_configuration(secret: str, algorithm: str, strict: bool = False) -> list[str]:
    findings: list[str] = []
    if algorithm not in SUPPORTED_JWT_ALGORITHMS:
        findings.append('JWT algorithm must be one of HS256, HS384, or HS512.')
    if is_weak_jwt_secret(secret):
        findings.append('JWT secret is too weak for production use.')
    if strict and findings:
        raise JwtValidationError(' '.join(findings))
    return findings
