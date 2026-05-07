from __future__ import annotations

import logging

from monitoring.metrics import MetricsRegistry, metrics_registry
from monitoring.resources import get_resource_snapshot
from security.secure_logging import SensitiveDataFilter


def test_metrics_endpoint_exposes_prometheus_text(client) -> None:
    response = client.get('/metrics')

    assert response.status_code == 200
    assert response.mimetype.startswith('text/plain')
    body = response.get_data(as_text=True)
    assert 'tool125_service_uptime_seconds' in body
    assert 'tool125_http_requests_total' in body
    assert 'tool125_http_request_latency_seconds_count' in body


def test_health_includes_monitoring_status(client) -> None:
    response = client.get('/health')
    body = response.get_json()

    assert response.status_code == 200
    assert 'monitoring' in body
    assert body['monitoring']['status'] == 'ok'
    assert body['monitoring']['metrics_endpoint'] == '/metrics'
    assert 'monitoring' in body['services']


def test_monitoring_status_endpoint_includes_resources(client) -> None:
    response = client.get('/monitoring/status')
    body = response.get_json()

    assert response.status_code == 200
    assert body['status'] == 'ok'
    assert body['metrics']['endpoint'] == '/metrics'
    assert 'memory_rss_bytes' in body['resources']['process']
    assert 'cpu_percent' in body['resources']['process']


def test_metrics_registry_counts_requests_and_errors() -> None:
    registry = MetricsRegistry()

    registry.record_request('GET', '/health', 200, 0.25)
    registry.record_request('POST', '/describe', 401, 0.10)
    output = registry.render_prometheus()

    assert 'tool125_http_requests_total{method="GET",route="/health",status="200"} 1' in output
    assert 'tool125_http_errors_total{method="POST",route="/describe",status="401"} 1' in output
    assert 'tool125_http_request_latency_seconds_sum{method="GET",route="/health"} 0.25' in output


def test_ai_latency_recorded_for_endpoint(client, auth_headers, monkeypatch) -> None:
    metrics_registry.reset()
    monkeypatch.setattr(
        'services.groq_client.GroqClient.generate',
        lambda self, prompt: (
            'Risk: overdue access review creates control exposure. '
            'Recommendation: assign owner, set priority, define timeline, and track remediation evidence.'
        ),
    )

    response = client.post('/describe', json={'issue': 'Aged access review issue remains open.'}, headers=auth_headers)
    output = client.get('/metrics').get_data(as_text=True)

    assert response.status_code == 200
    assert 'tool125_ai_response_latency_seconds_count{endpoint="/describe",model="llama-3.3-70b-versatile"} 1' in output


def test_resource_snapshot_has_process_shape() -> None:
    snapshot = get_resource_snapshot()

    assert snapshot['status'] in {'ok', 'limited'}
    assert isinstance(snapshot['process']['pid'], int)
    assert 'memory_rss_bytes' in snapshot['process']
    assert 'cpu_percent' in snapshot['process']


def test_sensitive_data_filter_masks_secret_log_fields() -> None:
    record = logging.LogRecord(
        name='test',
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg='Authorization Bearer eyJhbGciOiJIUzI1NiJ9.secret.payload password=cleartext',
        args=(),
        exc_info=None,
    )
    record.api_key = 'gsk_test_secret_key'
    record.password = 'cleartext'

    SensitiveDataFilter().filter(record)

    assert 'eyJhbGciOiJIUzI1NiJ9.secret.payload' not in record.msg
    assert record.api_key == '[REDACTED]'
    assert record.password == '[REDACTED]'
