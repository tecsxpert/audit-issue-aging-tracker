from __future__ import annotations
import os
import json
from datetime import datetime, timedelta, timezone
from typing import Any, Generator
from unittest.mock import MagicMock, patch
import jwt
import pytest
from flask import Flask

os.environ.setdefault('GROQ_API_KEY', 'test-key')
os.environ.setdefault('GROQ_API_BASE_URL', 'https://api.groq.com/v1')
os.environ.setdefault('RATE_LIMIT', '10000 per minute')
os.environ.setdefault('RATE_LIMIT_STORAGE_URI', 'memory://')
os.environ.setdefault('AI_CACHE_ENABLED', 'false')
os.environ.setdefault('JWT_AUTH_ENABLED', 'true')
os.environ.setdefault('JWT_SECRET', 'test-secret')
os.environ.setdefault('JWT_ALGORITHM', 'HS256')
os.environ.setdefault('JWT_AUDIENCE', 'tool-125')
os.environ.setdefault('JWT_ISSUER', 'tool-125-auth')
os.environ.setdefault('ALLOWED_ORIGINS', 'http://localhost,http://127.0.0.1')

from app import create_app


@pytest.fixture(scope='session')
def app() -> Flask:
    app = create_app()
    app.config['TESTING'] = True
    return app


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def valid_jwt_token() -> str:
    payload = {
        'sub': 'test-user',
        'aud': 'tool-125',
        'iss': 'tool-125-auth',
        'exp': datetime.now(tz=timezone.utc) + timedelta(hours=1),
    }
    return jwt.encode(payload, 'test-secret', algorithm='HS256')


@pytest.fixture()
def expired_jwt_token() -> str:
    payload = {
        'sub': 'test-user',
        'aud': 'tool-125',
        'iss': 'tool-125-auth',
        'exp': datetime.now(tz=timezone.utc) - timedelta(minutes=1),
    }
    return jwt.encode(payload, 'test-secret', algorithm='HS256')


@pytest.fixture()
def invalid_jwt_token() -> str:
    return 'invalid.token.value'


@pytest.fixture()
def auth_headers(valid_jwt_token: str) -> dict[str, str]:
    return {'Authorization': f'Bearer {valid_jwt_token}', 'Content-Type': 'application/json'}


@pytest.fixture()
def mock_groq_client() -> MagicMock:
    mock = MagicMock()
    mock.generate.return_value = 'This is a mocked AI response for audit analysis.'
    return mock


@pytest.fixture()
def mock_groq_failure() -> MagicMock:
    mock = MagicMock()
    from services.groq_client import GroqClientError
    mock.generate.side_effect = GroqClientError('Simulated Groq API failure.')
    return mock


@pytest.fixture()
def mock_groq_malformed() -> MagicMock:
    mock = MagicMock()
    mock.generate.return_value = None
    return mock


@pytest.fixture()
def sample_audit_issue() -> str:
    return 'Weak access controls allow unauthorized users to view admin audit records.'


@pytest.fixture()
def oversized_payload() -> dict[str, str]:
    large_string = 'x' * (16 * 1024 + 1)
    return {'issue': large_string}


@pytest.fixture()
def valid_describe_request(sample_audit_issue: str) -> dict[str, str]:
    return {'issue': sample_audit_issue}


@pytest.fixture()
def valid_recommend_request(sample_audit_issue: str) -> dict[str, str]:
    return {'issue': sample_audit_issue}


@pytest.fixture()
def valid_generate_report_request(sample_audit_issue: str) -> dict[str, str]:
    return {'issue': sample_audit_issue}


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture(autouse=True)
def block_live_groq_network(monkeypatch: pytest.MonkeyPatch) -> None:
    """Fail fast if a test accidentally reaches the real Groq API."""
    import requests

    def _blocked_post(*args: Any, **kwargs: Any) -> None:
        raise AssertionError('Live network access is disabled in unit tests.')

    monkeypatch.setattr(requests.sessions.Session, 'post', _blocked_post)
