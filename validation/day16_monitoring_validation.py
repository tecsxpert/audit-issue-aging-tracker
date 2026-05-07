from __future__ import annotations

import json
import sys
from typing import Any

from validation.common import (
    REPO_ROOT,
    ValidationConfig,
    assert_success_shape,
    log,
    request_json,
    request_with_response,
    write_json_report,
)


REQUIRED_METRICS = (
    'tool125_service_uptime_seconds',
    'tool125_http_requests_total',
    'tool125_http_errors_total',
    'tool125_http_request_latency_seconds_sum',
    'tool125_http_request_latency_seconds_count',
    'tool125_ai_response_latency_seconds_sum',
    'tool125_ai_response_latency_seconds_count',
    'tool125_ai_cache_events_total',
)


def run_day16_monitoring_validation() -> None:
    config = ValidationConfig()
    report: dict[str, Any] = {
        'base_url': config.base_url,
        'checks': [],
    }
    log('day16_monitoring_validation_start', base_url=config.base_url)

    status, body, latency, response = request_with_response('GET', '/health', config=config)
    assert_success_shape('/health', status, body)
    _assert_health_monitoring(body)
    report['checks'].append({'name': 'health_monitoring', 'status': 'pass', 'latency_ms': latency})

    status, monitoring_body, latency = request_json('GET', '/monitoring/status', config=config)
    assert_success_shape('/monitoring/status', status, monitoring_body)
    _assert_resource_shape(monitoring_body)
    report['checks'].append({'name': 'monitoring_status', 'status': 'pass', 'latency_ms': latency})

    status, metrics_body, latency, metrics_response = request_with_response('GET', '/metrics', config=config)
    if status != 200:
        raise AssertionError(f'/metrics expected HTTP 200, got {status}: {metrics_body}')
    metrics_text = metrics_response.text
    missing = [metric for metric in REQUIRED_METRICS if metric not in metrics_text]
    if missing:
        raise AssertionError(f'/metrics missing expected Prometheus metric names: {missing}')
    report['checks'].append({'name': 'prometheus_metrics', 'status': 'pass', 'latency_ms': latency})

    write_json_report(REPO_ROOT / 'validation' / 'reports' / 'day16_monitoring_validation.json', report)
    log('day16_monitoring_validation_passed')


def _assert_health_monitoring(body: dict[str, Any]) -> None:
    monitoring = body.get('monitoring')
    if not isinstance(monitoring, dict):
        raise AssertionError(f'/health missing monitoring object: {body}')
    if monitoring.get('status') != 'ok':
        raise AssertionError(f'/health monitoring status is not ok: {monitoring}')
    if monitoring.get('metrics_endpoint') != '/metrics':
        raise AssertionError(f'/health monitoring metrics endpoint is wrong: {monitoring}')


def _assert_resource_shape(body: dict[str, Any]) -> None:
    resources = body.get('resources')
    if not isinstance(resources, dict):
        raise AssertionError(f'/monitoring/status missing resources object: {body}')
    process = resources.get('process')
    if not isinstance(process, dict) or 'memory_rss_bytes' not in process or 'cpu_percent' not in process:
        raise AssertionError(f'/monitoring/status has malformed process resource data: {resources}')


if __name__ == '__main__':
    try:
        run_day16_monitoring_validation()
    except Exception as exc:
        log('day16_monitoring_validation_failed', error=str(exc))
        sys.exit(1)
