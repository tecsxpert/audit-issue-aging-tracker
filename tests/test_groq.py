from __future__ import annotations
import json
import os
import pytest
import requests
from services.groq_client import GroqClient, GroqClientError


def test_groq_client_raises_without_key() -> None:
    with pytest.raises(ValueError):
        GroqClient(api_key='', base_url='https://api.groq.com/v1', model='llama-3.3-70b-versatile')


def test_groq_client_retry_and_parse(monkeypatch) -> None:
    class DummyResponse:
        def __init__(self, status_code: int, body: dict[str, object]):
            self.status_code = status_code
            self._body = body
            self.text = json.dumps(body)

        def json(self) -> dict[str, object]:
            return self._body

    calls = {'count': 0}

    def fake_post(url, json, timeout):
        calls['count'] += 1
        if calls['count'] == 1:
            raise requests.ConnectionError('timeout')
        return DummyResponse(200, {'output': 'Test output'})

    client = GroqClient(api_key='stub-key', base_url='https://api.groq.com/v1', model='llama-3.3-70b-versatile')
    monkeypatch.setattr(client.session, 'post', fake_post)
    assert client.generate('Hello') == 'Test output'
    assert calls['count'] == 2


@pytest.mark.skipif(
    os.getenv('RUN_GROQ_INTEGRATION', 'false').lower() != 'true' or os.getenv('GROQ_API_KEY', '') in ('', 'test-key'),
    reason='Groq integration tests are disabled. Set RUN_GROQ_INTEGRATION=true with a valid key to run.',
)
def test_groq_api_sample_call() -> None:
    client = GroqClient(
        api_key=os.getenv('GROQ_API_KEY', ''),
        base_url=os.getenv('GROQ_API_BASE_URL', 'https://api.groq.com/v1'),
        model=os.getenv('GROQ_MODEL', 'llama-3.3-70b-versatile'),
    )
    response = client.generate('Summarize the following sample audit finding: data exposure due to missing filters.')
    assert isinstance(response, str)
    assert len(response) > 10
