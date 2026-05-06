from __future__ import annotations
import jwt
from datetime import datetime, timedelta, timezone


def create_test_token() -> str:
    payload = {
        'sub': 'rate-test',
        'aud': 'tool-125',
        'iss': 'tool-125-auth',
        'exp': datetime.now(tz=timezone.utc) + timedelta(minutes=30),
    }
    return jwt.encode(payload, 'test-secret', algorithm='HS256')


def test_rate_limit_blocks_after_configured_threshold(monkeypatch) -> None:
    monkeypatch.setenv('RATE_LIMIT', '3 per minute')
    monkeypatch.setenv('RATE_LIMIT_STORAGE_URI', 'memory://')
    from app import create_app

    isolated_app = create_app()
    isolated_app.config['TESTING'] = True
    client = isolated_app.test_client()
    monkeypatch.setattr('services.groq_client.GroqClient.generate', lambda self, prompt: 'OK')
    client.environ_base['REMOTE_ADDR'] = '10.0.0.2'
    headers = {'Authorization': f'Bearer {create_test_token()}'}
    for _ in range(3):
        response = client.post('/describe', json={'issue': 'Valid audit issue.'}, headers=headers)
        assert response.status_code == 200
    final_response = client.post('/describe', json={'issue': 'Valid audit issue.'}, headers=headers)
    assert final_response.status_code == 429
    body = final_response.get_json()
    assert body['success'] is False
    assert body['status'] == 'error'
    assert '3 per 1 minute' in body['message']
