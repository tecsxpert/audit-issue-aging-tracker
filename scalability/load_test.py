from __future__ import annotations

import argparse
import concurrent.futures
import json
import time
from statistics import mean
from typing import Any

import requests


def run_load_test(
    base_url: str,
    requests_count: int,
    concurrency: int,
    path: str = '/health',
    timeout_seconds: int = 10,
) -> dict[str, Any]:
    started_at = time.perf_counter()
    latencies: list[float] = []
    statuses: dict[int, int] = {}

    def call_once() -> tuple[int, float]:
        started = time.perf_counter()
        response = requests.get(f'{base_url.rstrip("/")}{path}', timeout=timeout_seconds)
        return response.status_code, round((time.perf_counter() - started) * 1000, 2)

    with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency) as executor:
        futures = [executor.submit(call_once) for _ in range(requests_count)]
        for future in concurrent.futures.as_completed(futures):
            status, latency = future.result()
            statuses[status] = statuses.get(status, 0) + 1
            latencies.append(latency)

    total_seconds = max(time.perf_counter() - started_at, 0.001)
    return {
        'requests': requests_count,
        'concurrency': concurrency,
        'path': path,
        'statuses': statuses,
        'avg_latency_ms': round(mean(latencies), 2) if latencies else None,
        'max_latency_ms': max(latencies) if latencies else None,
        'requests_per_second': round(requests_count / total_seconds, 2),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description='Tool-125 AI service concurrent load probe.')
    parser.add_argument('--base-url', default='http://127.0.0.1:8000')
    parser.add_argument('--requests', type=int, default=20)
    parser.add_argument('--concurrency', type=int, default=5)
    parser.add_argument('--path', default='/health')
    args = parser.parse_args()
    print(json.dumps(run_load_test(args.base_url, args.requests, args.concurrency, args.path), indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
