from __future__ import annotations

import argparse
import json
import os
import time
import urllib.error
import urllib.request

import jwt


def build_token(secret: str) -> str:
    payload = {
        'sub': 'rate-limit-stress',
        'aud': os.getenv('JWT_AUDIENCE', 'tool-125'),
        'iss': os.getenv('JWT_ISSUER', 'tool-125-auth'),
        'exp': int(time.time()) + 600,
    }
    return jwt.encode(payload, secret, algorithm=os.getenv('JWT_ALGORITHM', 'HS256'))


def post_issue(base_url: str, token: str, index: int) -> int:
    payload = json.dumps({'issue': f'Rate limit validation request {index}: stale access review finding.'}).encode('utf-8')
    request = urllib.request.Request(
        f'{base_url.rstrip("/")}/describe',
        data=payload,
        method='POST',
        headers={
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            return response.status
    except urllib.error.HTTPError as error:
        return error.code


def main() -> int:
    parser = argparse.ArgumentParser(description='Validate rate-limit behavior against /describe.')
    parser.add_argument('--base-url', default=os.getenv('AI_SERVICE_URL', 'http://127.0.0.1:8000'))
    parser.add_argument('--jwt-secret', default=os.getenv('JWT_SECRET', 'test-secret'))
    parser.add_argument('--requests', type=int, default=35)
    parser.add_argument('--sleep', type=float, default=0.0)
    args = parser.parse_args()

    token = build_token(args.jwt_secret)
    counts: dict[int, int] = {}
    for index in range(1, args.requests + 1):
        status = post_issue(args.base_url, token, index)
        counts[status] = counts.get(status, 0) + 1
        print(f'{index:03d}: HTTP {status}')
        if args.sleep:
            time.sleep(args.sleep)

    print('Summary:', json.dumps(counts, sort_keys=True))
    return 0 if counts.get(429, 0) >= 1 else 1


if __name__ == '__main__':
    raise SystemExit(main())
