from __future__ import annotations

from typing import Any

from flask import Blueprint, current_app, jsonify, request

from routes.ai_routes import utc_timestamp
from scalability.queue import TaskQueueError, create_task_queue
from scalability.tasks import PROMPT_BUILDERS

task_blueprint = Blueprint('tasks', __name__)


@task_blueprint.route('/tasks/ai', methods=['POST'])
def submit_ai_task() -> tuple[Any, int]:
    try:
        payload = request.get_json(silent=False)
        endpoint = str(payload.get('endpoint', '')).strip()
        issue = str(payload.get('issue', '')).strip()
        if endpoint not in PROMPT_BUILDERS:
            return jsonify(_error_payload('Unsupported endpoint for background AI task.')), 400
        if not issue:
            return jsonify(_error_payload('The "issue" field is required and must be a non-empty string.')), 400
        queue = _queue()
        task = queue.enqueue(
            endpoint=endpoint,
            issue=issue,
            metadata={'submitted_by': request.environ.get('jwt_payload', {}).get('sub', 'unknown')},
        )
        current_app.logger.info('background_ai_task_queued', extra={'task_id': task['task_id'], 'endpoint': endpoint})
        return jsonify({
            'success': True,
            'status': 'queued',
            'task_id': task['task_id'],
            'endpoint': endpoint,
            'status_url': f'/tasks/{task["task_id"]}',
            'generated_at': utc_timestamp(),
        }), 202
    except TaskQueueError as error:
        current_app.logger.error('Task queue unavailable', exc_info=error)
        return jsonify(_error_payload(str(error))), 503
    except Exception as error:
        current_app.logger.exception('Background task submission failed', exc_info=error)
        return jsonify(_error_payload('Background task submission failed.')), 503


@task_blueprint.route('/tasks/<task_id>', methods=['GET'])
def get_task(task_id: str) -> tuple[Any, int]:
    try:
        task = _queue().get(task_id)
    except TaskQueueError as error:
        return jsonify(_error_payload(str(error))), 503
    if task is None:
        return jsonify(_error_payload('Task not found.')), 404
    return jsonify({
        'success': True,
        'status': task.get('status'),
        'task': _safe_task_view(task),
        'generated_at': utc_timestamp(),
    }), 200


@task_blueprint.route('/tasks/health', methods=['GET'])
def task_health() -> tuple[Any, int]:
    try:
        queue = _queue()
        worker_id = request.args.get('worker_id', 'default')
        return jsonify({
            'success': True,
            'status': 'ok',
            'queue': queue.stats(),
            'worker': queue.worker_status(worker_id),
            'generated_at': utc_timestamp(),
        }), 200
    except TaskQueueError as error:
        return jsonify(_error_payload(str(error))), 503


def _queue():
    return create_task_queue(
        current_app.config.get('REDIS_URL'),
        queue_name=current_app.config.get('AI_TASK_QUEUE_NAME', 'tool125:task-queue:ai'),
        result_ttl_seconds=current_app.config.get('AI_TASK_RESULT_TTL_SECONDS', 3600),
        max_attempts=current_app.config.get('AI_TASK_MAX_ATTEMPTS', 3),
        heartbeat_ttl_seconds=current_app.config.get('AI_WORKER_HEARTBEAT_TTL_SECONDS', 30),
    )


def _safe_task_view(task: dict[str, Any]) -> dict[str, Any]:
    safe = {key: value for key, value in task.items() if key not in {'issue', 'metadata'}}
    if 'result' in safe and isinstance(safe['result'], dict):
        safe['result'] = {key: value for key, value in safe['result'].items() if key != 'issue'}
    return safe


def _error_payload(message: str) -> dict[str, Any]:
    return {
        'success': False,
        'status': 'error',
        'message': message,
        'generated_at': utc_timestamp(),
    }
