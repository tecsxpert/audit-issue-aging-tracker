from __future__ import annotations

import logging
import os
import signal
import sys
import time

from dotenv import load_dotenv

from config import Config
from scalability.queue import TaskQueueError, create_task_queue
from scalability.tasks import process_ai_task
from security.secure_logging import attach_sensitive_data_filter, safe_extra


shutdown_requested = False


def request_shutdown(signum, frame) -> None:  # type: ignore[no-untyped-def]
    global shutdown_requested
    shutdown_requested = True


def configure_worker_logging() -> logging.Logger:
    logger = logging.getLogger('tool125.ai_worker')
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    attach_sensitive_data_filter(handler)
    logger.handlers = [handler]
    logger.propagate = False
    return logger


def run_worker(worker_id: str | None = None) -> None:
    load_dotenv()
    signal.signal(signal.SIGTERM, request_shutdown)
    signal.signal(signal.SIGINT, request_shutdown)
    config = Config()
    logger = configure_worker_logging()
    resolved_worker_id = worker_id or os.getenv('AI_WORKER_ID', f'worker-{os.getpid()}')
    queue = create_task_queue(
        config.REDIS_URL,
        queue_name=config.AI_TASK_QUEUE_NAME,
        result_ttl_seconds=config.AI_TASK_RESULT_TTL_SECONDS,
        max_attempts=config.AI_TASK_MAX_ATTEMPTS,
        heartbeat_ttl_seconds=config.AI_WORKER_HEARTBEAT_TTL_SECONDS,
    )
    logger.info('AI worker started', extra=safe_extra(worker_id=resolved_worker_id, queue=config.AI_TASK_QUEUE_NAME))

    while not shutdown_requested:
        queue.heartbeat(resolved_worker_id)
        task = queue.dequeue(timeout_seconds=config.AI_WORKER_POLL_TIMEOUT_SECONDS)
        if task is None:
            continue
        task_id = str(task.get('task_id'))
        try:
            logger.info('AI task started', extra=safe_extra(task_id=task_id, endpoint=task.get('endpoint')))
            result = process_ai_task(task, config, logger=logger)
            queue.complete(task_id, result)
            logger.info('AI task completed', extra=safe_extra(task_id=task_id, endpoint=task.get('endpoint')))
        except Exception as exc:
            retryable = not isinstance(exc, ValueError)
            queue.fail(task_id, str(exc), retryable=retryable)
            logger.warning('AI task failed', extra=safe_extra(task_id=task_id, error=str(exc), retryable=retryable))

    queue.heartbeat(resolved_worker_id)
    logger.info('AI worker shutdown complete', extra=safe_extra(worker_id=resolved_worker_id))
    time.sleep(0.1)


if __name__ == '__main__':
    try:
        run_worker()
    except TaskQueueError as exc:
        print(f'Worker startup failed: {exc}', file=sys.stderr)
        sys.exit(1)
