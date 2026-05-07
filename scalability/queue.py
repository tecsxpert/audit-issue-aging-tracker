from __future__ import annotations

import json
import time
import uuid
from dataclasses import dataclass
from typing import Any

import redis

from cache.redis_client import create_redis_client
from monitoring.metrics import metrics_registry


TERMINAL_STATES = {'completed', 'failed'}


class TaskQueueError(RuntimeError):
    pass


@dataclass(frozen=True)
class TaskQueueConfig:
    queue_name: str = 'tool125:task-queue:ai'
    result_ttl_seconds: int = 3600
    max_attempts: int = 3
    heartbeat_ttl_seconds: int = 30


class RedisTaskQueue:
    def __init__(
        self,
        redis_client: redis.Redis,
        config: TaskQueueConfig | None = None,
    ) -> None:
        self.redis = redis_client
        self.config = config or TaskQueueConfig()

    def enqueue(self, endpoint: str, issue: str, metadata: dict[str, Any] | None = None) -> dict[str, Any]:
        task_id = str(uuid.uuid4())
        task = {
            'task_id': task_id,
            'endpoint': endpoint,
            'issue': issue,
            'metadata': metadata or {},
            'status': 'queued',
            'attempts': 0,
            'max_attempts': self.config.max_attempts,
            'created_at': _now(),
            'updated_at': _now(),
        }
        self.redis.setex(_task_key(task_id), self.config.result_ttl_seconds, json.dumps(task, sort_keys=True))
        self.redis.rpush(self.config.queue_name, task_id)
        metrics_registry.record_task_event(self.config.queue_name, 'queued')
        return task

    def dequeue(self, timeout_seconds: int = 5) -> dict[str, Any] | None:
        item = self.redis.blpop(self.config.queue_name, timeout=timeout_seconds)
        if not item:
            return None
        task_id = item[1] if isinstance(item, tuple) else item
        task = self.get(str(task_id))
        if task is None:
            metrics_registry.record_task_event(self.config.queue_name, 'missing')
            return None
        task['status'] = 'running'
        task['attempts'] = int(task.get('attempts', 0)) + 1
        task['updated_at'] = _now()
        self._save(task)
        metrics_registry.record_task_event(self.config.queue_name, 'started')
        return task

    def get(self, task_id: str) -> dict[str, Any] | None:
        raw = self.redis.get(_task_key(task_id))
        if raw is None:
            return None
        try:
            task = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise TaskQueueError(f'Task payload is not valid JSON: {task_id}') from exc
        return task if isinstance(task, dict) else None

    def complete(self, task_id: str, result: dict[str, Any]) -> dict[str, Any]:
        task = self.get(task_id)
        if task is None:
            raise TaskQueueError(f'Task not found: {task_id}')
        task.update({
            'status': 'completed',
            'result': result,
            'updated_at': _now(),
            'completed_at': _now(),
        })
        self._save(task)
        metrics_registry.record_task_event(self.config.queue_name, 'completed')
        return task

    def fail(self, task_id: str, error: str, retryable: bool = True) -> dict[str, Any]:
        task = self.get(task_id)
        if task is None:
            raise TaskQueueError(f'Task not found: {task_id}')
        attempts = int(task.get('attempts', 0))
        if retryable and attempts < int(task.get('max_attempts', self.config.max_attempts)):
            task.update({'status': 'queued', 'last_error': error, 'updated_at': _now()})
            self._save(task)
            self.redis.rpush(self.config.queue_name, task_id)
            metrics_registry.record_task_event(self.config.queue_name, 'retried')
            return task
        task.update({'status': 'failed', 'error': error, 'updated_at': _now(), 'failed_at': _now()})
        self._save(task)
        metrics_registry.record_task_event(self.config.queue_name, 'failed')
        return task

    def stats(self) -> dict[str, Any]:
        return {
            'queue_name': self.config.queue_name,
            'queued_count': int(self.redis.llen(self.config.queue_name)),
            'result_ttl_seconds': self.config.result_ttl_seconds,
            'max_attempts': self.config.max_attempts,
        }

    def heartbeat(self, worker_id: str) -> None:
        key = _worker_key(worker_id)
        self.redis.setex(key, self.config.heartbeat_ttl_seconds, json.dumps({'worker_id': worker_id, 'heartbeat_at': _now()}))

    def worker_status(self, worker_id: str = 'default') -> dict[str, Any]:
        raw = self.redis.get(_worker_key(worker_id))
        return {
            'worker_id': worker_id,
            'status': 'ok' if raw else 'unknown',
            'heartbeat': json.loads(raw) if raw else None,
        }

    def _save(self, task: dict[str, Any]) -> None:
        self.redis.setex(
            _task_key(str(task['task_id'])),
            self.config.result_ttl_seconds,
            json.dumps(task, sort_keys=True),
        )


def create_task_queue(
    redis_url: str | None,
    queue_name: str = 'tool125:task-queue:ai',
    result_ttl_seconds: int = 3600,
    max_attempts: int = 3,
    heartbeat_ttl_seconds: int = 30,
) -> RedisTaskQueue:
    client = create_redis_client(redis_url)
    if client is None:
        raise TaskQueueError('Redis is required for background task queue support.')
    return RedisTaskQueue(
        client,
        TaskQueueConfig(
            queue_name=queue_name,
            result_ttl_seconds=result_ttl_seconds,
            max_attempts=max_attempts,
            heartbeat_ttl_seconds=heartbeat_ttl_seconds,
        ),
    )


def _task_key(task_id: str) -> str:
    return f'tool125:task:{task_id}'


def _worker_key(worker_id: str) -> str:
    return f'tool125:worker:{worker_id}:heartbeat'


def _now() -> str:
    return time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
