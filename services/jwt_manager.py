from __future__ import annotations
from typing import Any, Iterable
import jwt
from jwt import ExpiredSignatureError, InvalidTokenError


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
    try:
        payload = jwt.decode(
            token,
            secret,
            algorithms=list(algorithms),
            audience=audience if audience else None,
            issuer=issuer if issuer else None,
        )
    except ExpiredSignatureError as exc:
        raise JwtValidationError('JWT token has expired.') from exc
    except InvalidTokenError as exc:
        raise JwtValidationError(f'Invalid JWT token: {exc}') from exc
    if not isinstance(payload, dict):
        raise JwtValidationError('JWT payload must be a valid JSON object.')
    return payload
