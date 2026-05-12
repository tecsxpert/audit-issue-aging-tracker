from __future__ import annotations

import argparse
import json
import time
from typing import Any

import requests

from scripts.common import audit


def verify_health(base_url: str = 'http://127.0.0.1:8000', attempts: int = 30, delay_seconds: float = 2.0) -> dict[str, Any]:
    last_error = ''
    for attempt in range(1, attempts + 1):
        try:
            response = requests.get(f'{base_url.rstrip("/")}/health', timeout=5)
            body = response.json()
            if response.status_code == 200 and body.get('status') == 'ok':
                audit('health_verification_passed', base_url=base_url, attempt=attempt)
                return body
            last_error = f'HTTP {response.status_code}: {body}'
        except Exception as exc:
            last_error = str(exc)
        time.sleep(delay_seconds)
    audit('health_verification_failed', base_url=base_url, error=last_error)
    raise RuntimeError(f'Health verification failed: {last_error}')


def main() -> None:
    parser = argparse.ArgumentParser(description='Verify Tool-125 AI service health after deployment.')
    parser.add_argument('--base-url', default='http://127.0.0.1:8000')
    parser.add_argument('--attempts', type=int, default=30)
    args = parser.parse_args()
    print(json.dumps(verify_health(args.base_url, args.attempts), indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
