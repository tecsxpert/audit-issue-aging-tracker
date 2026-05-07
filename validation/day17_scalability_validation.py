from __future__ import annotations

import sys
from typing import Any

from scalability.load_test import run_load_test
from validation.common import (
    DEFAULT_ISSUE,
    REPO_ROOT,
    ValidationConfig,
    assert_auth_error_shape,
    auth_headers,
    log,
    request_json,
    request_with_response,
    write_json_report,
)


def run_day17_scalability_validation() -> None:
    config = ValidationConfig()
    report: dict[str, Any] = {'base_url': config.base_url, 'checks': []}
    log('day17_scalability_validation_start', base_url=config.base_url)

    status, body, latency = request_json('GET', '/health', config=config)
    if status != 200 or 'scalability' not in body:
        raise AssertionError(f'/health missing scalability status: HTTP {status} {body}')
    report['checks'].append({'name': 'health_scalability', 'status': 'pass', 'latency_ms': latency})

    status, body, latency = request_json('GET', '/tasks/health', config=config)
    if status not in {200, 503}:
        raise AssertionError(f'/tasks/health returned unexpected status: HTTP {status} {body}')
    report['checks'].append({'name': 'task_queue_health', 'status': 'pass', 'http_status': status, 'latency_ms': latency})

    status, body, latency = request_json(
        'POST',
        '/tasks/ai',
        {'endpoint': '/describe', 'issue': DEFAULT_ISSUE},
        headers={'Content-Type': 'application/json'},
        config=config,
    )
    assert_auth_error_shape('/tasks/ai', status, body)
    report['checks'].append({'name': 'async_endpoint_jwt_required', 'status': 'pass', 'latency_ms': latency})

    if config.jwt_secret:
        status, body, latency = request_json(
            'POST',
            '/tasks/ai',
            {'endpoint': '/describe', 'issue': DEFAULT_ISSUE},
            headers=auth_headers(config),
            config=config,
        )
        if status not in {202, 503}:
            raise AssertionError(f'/tasks/ai returned unexpected status: HTTP {status} {body}')
        report['checks'].append({'name': 'async_enqueue_or_queue_unavailable', 'status': 'pass', 'http_status': status, 'latency_ms': latency})

    status, _, latency, response = request_with_response('GET', '/metrics', config=config)
    if status != 200 or 'tool125_task_events_total' not in response.text:
        raise AssertionError('/metrics missing task queue metric family.')
    report['checks'].append({'name': 'task_metrics', 'status': 'pass', 'latency_ms': latency})

    load_result = run_load_test(config.base_url, requests_count=5, concurrency=2, path='/health', timeout_seconds=config.timeout_seconds)
    if load_result['statuses'].get(200, 0) < 5:
        raise AssertionError(f'Load probe did not receive five HTTP 200 responses: {load_result}')
    report['checks'].append({'name': 'concurrent_load_probe', 'status': 'pass', 'result': load_result})

    write_json_report(REPO_ROOT / 'validation' / 'reports' / 'day17_scalability_validation.json', report)
    log('day17_scalability_validation_passed')


if __name__ == '__main__':
    try:
        run_day17_scalability_validation()
    except Exception as exc:
        log('day17_scalability_validation_failed', error=str(exc))
        sys.exit(1)
