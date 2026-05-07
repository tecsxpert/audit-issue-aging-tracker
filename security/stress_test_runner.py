from __future__ import annotations

import concurrent.futures
import statistics
import time

from validation.common import DEFAULT_ISSUE, ValidationConfig, auth_headers, log, main_exit, request_json


def _single_request(index: int, config: ValidationConfig) -> dict[str, object]:
    status, body, latency = request_json(
        'POST',
        '/describe',
        {'issue': f'{DEFAULT_ISSUE} Stress iteration {index}.'},
        headers=auth_headers(config),
        config=config,
    )
    return {
        'index': index,
        'status_code': status,
        'success': body.get('success') is True,
        'latency_ms': latency,
    }


def run_stress_test(total_requests: int = 30, concurrency: int = 5) -> None:
    config = ValidationConfig()
    started = time.perf_counter()
    with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency) as executor:
        futures = [executor.submit(_single_request, index, config) for index in range(total_requests)]
        results = [future.result() for future in concurrent.futures.as_completed(futures)]

    latencies = [float(result['latency_ms']) for result in results]
    accepted_statuses = {200, 429}
    unexpected = [result for result in results if result['status_code'] not in accepted_statuses]
    summary = {
        'total_requests': total_requests,
        'concurrency': concurrency,
        'elapsed_seconds': round(time.perf_counter() - started, 2),
        'success_count': sum(1 for result in results if result['status_code'] == 200),
        'rate_limited_count': sum(1 for result in results if result['status_code'] == 429),
        'average_latency_ms': round(statistics.mean(latencies), 2) if latencies else 0,
        'max_latency_ms': round(max(latencies), 2) if latencies else 0,
    }
    log('stress_test_summary', **summary)
    if unexpected:
        raise AssertionError(f'Unexpected stress responses: {unexpected}')


if __name__ == '__main__':
    main_exit(run_stress_test)
