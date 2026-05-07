from __future__ import annotations

import statistics
from pathlib import Path

from cache.redis_client import create_redis_client
from validation.common import (
    AI_ENDPOINTS,
    DEFAULT_ISSUE,
    REPO_ROOT,
    ValidationConfig,
    auth_headers,
    log,
    main_exit,
    request_json,
    write_json_report,
)


def monitor_ai_integrations(iterations: int = 3) -> None:
    config = ValidationConfig()
    headers = auth_headers(config)
    samples: list[dict[str, object]] = []

    for iteration in range(1, iterations + 1):
        for endpoint in AI_ENDPOINTS:
            status, body, latency = request_json(
                'POST',
                endpoint,
                {'issue': f'{DEFAULT_ISSUE} Monitoring pass {iteration}.'},
                headers=headers,
                config=config,
            )
            success = status == 200 and body.get('success') is True
            samples.append({
                'endpoint': endpoint,
                'iteration': iteration,
                'status_code': status,
                'success': success,
                'latency_ms': latency,
                'score': body.get('score'),
                'response_length': len(str(body.get('response', ''))),
            })
            log('ai_monitoring_sample', endpoint=endpoint, iteration=iteration, status_code=status, latency_ms=latency)

    failures = [sample for sample in samples if not sample['success']]
    latencies = [float(sample['latency_ms']) for sample in samples]
    cache_key_count = _count_cache_keys(config.redis_url)
    report = {
        'summary': {
            'sample_count': len(samples),
            'failure_count': len(failures),
            'average_latency_ms': round(statistics.mean(latencies), 2) if latencies else 0,
            'p95_latency_ms': round(sorted(latencies)[int(len(latencies) * 0.95) - 1], 2) if latencies else 0,
            'redis_ai_cache_keys': cache_key_count,
        },
        'samples': samples,
    }
    write_json_report(REPO_ROOT / 'validation' / 'reports' / 'ai_monitoring_report.json', report)
    if failures:
        raise AssertionError(f'AI monitoring detected failed calls: {failures}')


def _count_cache_keys(redis_url: str) -> int | str:
    if not redis_url:
        return 'not_configured'
    try:
        client = create_redis_client(redis_url)
        if client is None:
            return 'not_configured'
        return len(list(client.scan_iter(match='tool125:ai-cache:*', count=100)))
    except Exception as exc:
        log('redis_cache_monitoring_unavailable', error=str(exc))
        return 'unavailable'


if __name__ == '__main__':
    main_exit(monitor_ai_integrations)
