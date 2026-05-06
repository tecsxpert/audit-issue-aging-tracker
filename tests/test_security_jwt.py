from __future__ import annotations
from datetime import datetime, timedelta, timezone
import jwt
import pytest


def create_jwt(payload: dict[str, object], secret: str = 'test-secret') -> str:
    return jwt.encode(payload, secret, algorithm='HS256')


def test_missing_jwt_returns_401(client) -> None:
    response = client.post('/describe', json={'issue': 'Valid audit issue.'})
    assert response.status_code == 401
    assert 'Authorization header' in response.get_json()['message']


def test_invalid_jwt_returns_401(client) -> None:
    headers = {'Authorization': 'Bearer invalid.token.value'}
    response = client.post('/recommend', json={'issue': 'Valid audit issue.'}, headers=headers)
    assert response.status_code == 401
    assert 'Invalid JWT token' in response.get_json()['message']


def test_expired_jwt_returns_401(client) -> None:
    payload = {
        'sub': 'tester',
        'aud': 'tool-125',
        'iss': 'tool-125-auth',
        'exp': datetime.now(tz=timezone.utc) - timedelta(minutes=1),
    }
    token = create_jwt(payload)
    headers = {'Authorization': f'Bearer {token}'}
    response = client.post('/generate-report', json={'issue': 'Valid audit issue.'}, headers=headers)
    assert response.status_code == 401
    assert 'expired' in response.get_json()['message'].lower()


def test_tampered_jwt_returns_401(client) -> None:
    payload = {
        'sub': 'tester',
        'aud': 'tool-125',
        'iss': 'tool-125-auth',
        'exp': datetime.now(tz=timezone.utc) + timedelta(minutes=10),
    }
    token = create_jwt(payload)
    tampered = token[:-1] + ('A' if token[-1] != 'A' else 'B')
    headers = {'Authorization': f'Bearer {tampered}'}
    response = client.post('/describe', json={'issue': 'Valid audit issue.'}, headers=headers)
    assert response.status_code == 401
    assert 'Invalid JWT token' in response.get_json()['message']


def test_unauthorized_jwt_wrong_audience_returns_401(client) -> None:
    payload = {
        'sub': 'tester',
        'aud': 'wrong-audience',
        'iss': 'tool-125-auth',
        'exp': datetime.now(tz=timezone.utc) + timedelta(minutes=10),
    }
    token = create_jwt(payload)
    headers = {'Authorization': f'Bearer {token}'}
    response = client.post('/recommend', json={'issue': 'Valid audit issue.'}, headers=headers)
    assert response.status_code == 401
    assert 'Invalid JWT token' in response.get_json()['message']
