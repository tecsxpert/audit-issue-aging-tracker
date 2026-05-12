from __future__ import annotations

import argparse
import sys
import time
from typing import Any

from validation.common import REPO_ROOT, ValidationConfig, log, request_json, write_json_report


def run_uptime_probe(samples: int = 5, interval_seconds: float = 1.0) -> None:
    config = ValidationConfig()
    results: list[dict[str, Any]] = []
    log('uptime_recovery_validation_start', samples=samples, base_url=config.base_url)
    for index in range(samples):
        try:
            status, body, latency = request_json('GET', '/health', config=config)
            ok = status == 200 and body.get('status') == 'ok'
            results.append({'sample': index + 1, 'ok': ok, 'status_code': status, 'latency_ms': latency})
        except Exception as exc:
            results.append({'sample': index + 1, 'ok': False, 'error': str(exc)})
        if index < samples - 1:
            time.sleep(interval_seconds)

    failures = [item for item in results if not item.get('ok')]
    report = {
        'base_url': config.base_url,
        'samples': samples,
        'success_count': samples - len(failures),
        'failure_count': len(failures),
        'results': results,
    }
    write_json_report(REPO_ROOT / 'validation' / 'reports' / 'uptime_recovery_validation.json', report)
    if failures:
        raise AssertionError(f'Uptime probe had {len(failures)} failures.')
    log('uptime_recovery_validation_passed', samples=samples)


def main() -> None:
    parser = argparse.ArgumentParser(description='Validate API uptime and recovery readiness.')
    parser.add_argument('--samples', type=int, default=5)
    parser.add_argument('--interval-seconds', type=float, default=1.0)
    args = parser.parse_args()
    run_uptime_probe(args.samples, args.interval_seconds)


if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        log('uptime_recovery_validation_failed', error=str(exc))
        sys.exit(1)
