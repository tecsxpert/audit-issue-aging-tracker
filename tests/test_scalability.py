from __future__ import annotations

import json
from unittest.mock import MagicMock

import pytest

from config import Config
from scalability.load_test import run_load_test
from scalability.queue import RedisTaskQueue, TaskQueueConfig
from scalability.tasks import process_ai_task
from services.groq_client import GroqClient


class FakeRedis:
    def __init__(self) -> None:
        self.values: dict[str, str] = {}
        self.lists: dict[str, list[str]] = {}

    def setex(self, key: str, ttl: int, value: str) -> None:
        self.values[key] = value

    def get(self, key: str) -> str | None:
        return self.values.get(key)

    def rpush(self, key: str, value: str) -> None:
        self.lists.setdefault(key, []).append(value)

    def blpop(self, key: str, timeout: int = 0):
        items = self.lists.setdefault(key, [])
        if not items:
            return None
        return key, items.pop(0)

    def llen(self, key: str) -> int:
        return len(self.lists.get(key, []))


def test_redis_task_queue_enqueue_dequeue_complete() -> None:
    queue = RedisTaskQueue(FakeRedis(), TaskQueueConfig(queue_name='test:q', result_ttl_seconds=60, max_attempts=2))

    created = queue.enqueue('/describe', 'Aged audit issue')
    running = queue.dequeue(timeout_seconds=1)
    completed = queue.complete(created['task_id'], {'response': 'done'})

    assert created['status'] == 'queued'
    assert running is not None
    assert running['status'] == 'running'
    assert running['attempts'] == 1
    assert completed['status'] == 'completed'
    assert queue.stats()['queued_count'] == 0


def test_redis_task_queue_retries_until_max_attempts() -> None:
    queue = RedisTaskQueue(FakeRedis(), TaskQueueConfig(queue_name='test:q', result_ttl_seconds=60, max_attempts=2))
    created = queue.enqueue('/describe', 'Aged audit issue')
    first = queue.dequeue(timeout_seconds=1)

    retried = queue.fail(first['task_id'], 'temporary failure', retryable=True)
    second = queue.dequeue(timeout_seconds=1)
    failed = queue.fail(second['task_id'], 'still failing', retryable=True)

    assert retried['status'] == 'queued'
    assert failed['status'] == 'failed'
    assert failed['error'] == 'still failing'


def test_process_ai_task_uses_prompt_and_returns_result(monkeypatch) -> None:
    monkeypatch.setattr(
        'services.groq_client.GroqClient.generate',
        lambda self, prompt: (
            'Risk: aged issue remains unresolved. Recommendation: assign owner, set priority, '
            'define timeline, collect evidence, and monitor remediation.'
        ),
    )
    config = Config()

    result = process_ai_task({'endpoint': '/recommend', 'issue': 'Access review is overdue.'}, config)

    assert result['success'] is True
    assert result['endpoint'] == '/recommend'
    assert result['score'] >= 7


def test_async_task_endpoint_requires_jwt(client) -> None:
    response = client.post(
        '/tasks/ai',
        json={'endpoint': '/describe', 'issue': 'Aged audit issue'},
        headers={'Content-Type': 'application/json'},
    )

    assert response.status_code == 401


def test_async_task_endpoint_enqueue_and_status(client, auth_headers, monkeypatch) -> None:
    queue = RedisTaskQueue(FakeRedis(), TaskQueueConfig(queue_name='test:q', result_ttl_seconds=60, max_attempts=2))
    monkeypatch.setattr('routes.task_routes.create_task_queue', lambda *args, **kwargs: queue)

    response = client.post(
        '/tasks/ai',
        json={'endpoint': '/describe', 'issue': 'Aged audit issue'},
        headers=auth_headers,
    )
    body = response.get_json()
    status_response = client.get(body['status_url'])

    assert response.status_code == 202
    assert body['status'] == 'queued'
    assert status_response.status_code == 200
    assert status_response.get_json()['task']['status'] == 'queued'


def test_groq_retry_configuration_is_respected(monkeypatch) -> None:
    mock_session = MagicMock()
    mock_session.post.side_effect = ConnectionError('Always fails')
    monkeypatch.setattr('time.sleep', lambda _: None)
    client = GroqClient(
        api_key='test-key',
        base_url='https://api.groq.com/v1',
        model='llama-3.3-70b-versatile',
        max_retries=2,
        backoff_seconds=0.01,
        timeout_seconds=3,
    )
    client.session = mock_session

    with pytest.raises(Exception):
        client.generate('Test prompt')
    assert mock_session.post.call_count == 2
    assert mock_session.post.call_args.kwargs['timeout'] == 3


def test_load_test_utility_runs_concurrent_requests(monkeypatch) -> None:
    class FakeResponse:
        status_code = 200

    monkeypatch.setattr('requests.get', lambda *args, **kwargs: FakeResponse())

    result = run_load_test('http://localhost:8000', requests_count=4, concurrency=2)

    assert result['requests'] == 4
    assert result['concurrency'] == 2
    assert result['statuses'][200] == 4
