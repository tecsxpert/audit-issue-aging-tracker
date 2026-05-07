from __future__ import annotations

import json
import os
import socket
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests
from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(REPO_ROOT / '.env')
DEFAULT_ISSUE = (
    'Audit issue AI-125 has been open for 96 days, remains assigned to the platform '
    'controls team, and has missed two remediation checkpoints.'
)
AI_ENDPOINTS = ('/describe', '/recommend', '/generate-report')


@dataclass(frozen=True)
class ValidationConfig:
    base_url: str = os.getenv('AI_SERVICE_BASE_URL', 'http://127.0.0.1:8000')
    groq_api_key: str = os.getenv('GROQ_API_KEY', '')
    jwt_secret: str = os.getenv('JWT_SECRET', '')
    jwt_algorithm: str = os.getenv('JWT_ALGORITHM', 'HS256')
    jwt_audience: str = os.getenv('JWT_AUDIENCE', 'tool-125')
    jwt_issuer: str = os.getenv('JWT_ISSUER', 'tool-125-auth')
    redis_url: str = os.getenv('REDIS_URL', 'redis://127.0.0.1:6379/0')
    timeout_seconds: int = int(os.getenv('VALIDATION_TIMEOUT_SECONDS', '15'))


def utc_now() -> str:
    return datetime.now(tz=timezone.utc).isoformat()


def log(event: str, **fields: Any) -> None:
    payload = {'event': event, 'generated_at': utc_now(), **fields}
    print(json.dumps(payload, sort_keys=True), flush=True)


def make_jwt(config: ValidationConfig | None = None, subject: str = 'day11-validator') -> str:
    from validation.auth_helper import generate_test_jwt

    return generate_test_jwt(subject=subject)


def auth_headers(config: ValidationConfig | None = None) -> dict[str, str]:
    from validation.auth_helper import authenticated_headers

    return authenticated_headers()


def request_json(
    method: str,
    path: str,
    payload: dict[str, Any] | None = None,
    headers: dict[str, str] | None = None,
    config: ValidationConfig | None = None,
) -> tuple[int, dict[str, Any], float]:
    cfg = config or ValidationConfig()
    url = f'{cfg.base_url.rstrip("/")}{path}'
    started = time.perf_counter()
    response = requests.request(
        method,
        url,
        json=payload,
        headers=headers,
        timeout=cfg.timeout_seconds,
    )
    _log_authenticated_request(method, path, headers)
    latency_ms = round((time.perf_counter() - started) * 1000, 2)
    try:
        body = response.json()
    except ValueError:
        body = {'raw': response.text}
    return response.status_code, body, latency_ms


def request_with_response(
    method: str,
    path: str,
    payload: dict[str, Any] | None = None,
    headers: dict[str, str] | None = None,
    config: ValidationConfig | None = None,
) -> tuple[int, dict[str, Any], float, requests.Response]:
    cfg = config or ValidationConfig()
    url = f'{cfg.base_url.rstrip("/")}{path}'
    started = time.perf_counter()
    response = requests.request(
        method,
        url,
        json=payload,
        headers=headers,
        timeout=cfg.timeout_seconds,
    )
    _log_authenticated_request(method, path, headers)
    latency_ms = round((time.perf_counter() - started) * 1000, 2)
    try:
        body = response.json()
    except ValueError:
        body = {'raw': response.text}
    return response.status_code, body, latency_ms, response


def assert_success_shape(path: str, status_code: int, body: dict[str, Any]) -> None:
    if status_code != 200:
        raise AssertionError(f'{path} expected HTTP 200, got {status_code}: {body}')
    required = {'success', 'status', 'generated_at'}
    if path in AI_ENDPOINTS:
        required.update({'endpoint', 'issue', 'response', 'score'})
    missing = required - set(body)
    if missing:
        raise AssertionError(f'{path} missing JSON fields: {sorted(missing)}')
    if body.get('success') is not True or body.get('status') not in {'ok', 'success'}:
        raise AssertionError(f'{path} returned an unsuccessful payload: {body}')


def assert_error_shape(path: str, status_code: int, body: dict[str, Any], expected: int) -> None:
    if status_code != expected:
        raise AssertionError(f'{path} expected HTTP {expected}, got {status_code}: {body}')
    for field in ('success', 'status', 'message', 'generated_at'):
        if field not in body:
            raise AssertionError(f'{path} error payload missing {field}: {body}')
    if body['success'] is not False or body['status'] != 'error':
        raise AssertionError(f'{path} returned malformed error payload: {body}')


def assert_auth_error_shape(path: str, status_code: int, body: dict[str, Any]) -> None:
    if status_code not in {401, 403}:
        raise AssertionError(f'{path} expected HTTP 401/403, got {status_code}: {body}')
    for field in ('success', 'status', 'message', 'generated_at'):
        if field not in body:
            raise AssertionError(f'{path} auth error payload missing {field}: {body}')
    if body['success'] is not False or body['status'] != 'error':
        raise AssertionError(f'{path} returned malformed auth error payload: {body}')


def assert_secure_headers(path: str, response: requests.Response) -> None:
    required = {
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'DENY',
        'Cache-Control': 'no-store, no-cache, must-revalidate, max-age=0',
    }
    for header, expected in required.items():
        actual = response.headers.get(header)
        if actual != expected:
            raise AssertionError(
                f'{path} missing secure header {header}: expected {expected!r}, got {actual!r}'
            )


def _log_authenticated_request(
    method: str,
    path: str,
    headers: dict[str, str] | None,
) -> None:
    if path in AI_ENDPOINTS and headers and str(headers.get('Authorization', '')).startswith('Bearer '):
        log('authenticated_request_sent', method=method, endpoint=path)


def wait_for_http_health(config: ValidationConfig | None = None, deadline_seconds: int = 90) -> None:
    cfg = config or ValidationConfig()
    deadline = time.monotonic() + deadline_seconds
    last_error: Exception | None = None
    while time.monotonic() < deadline:
        try:
            status, body, latency = request_json('GET', '/health', config=cfg)
            if status == 200 and body.get('status') == 'ok':
                log('health_ready', status_code=status, latency_ms=latency)
                return
        except Exception as exc:  # pragma: no cover - runtime guard
            last_error = exc
        time.sleep(2)
    raise RuntimeError(f'Health endpoint did not become ready: {last_error}')


def docker_compose_command() -> list[str]:
    if subprocess.run(['docker', 'compose', 'version'], capture_output=True, text=True).returncode == 0:
        return ['docker', 'compose']
    if subprocess.run(['docker-compose', 'version'], capture_output=True, text=True).returncode == 0:
        return ['docker-compose']
    raise RuntimeError('Docker Compose is not available on PATH.')


def run_command(command: list[str], timeout: int = 120) -> subprocess.CompletedProcess[str]:
    log('command_start', command=' '.join(command))
    result = subprocess.run(command, cwd=REPO_ROOT, capture_output=True, text=True, timeout=timeout)
    log('command_finish', command=' '.join(command), returncode=result.returncode)
    if result.returncode != 0:
        raise RuntimeError(
            f'Command failed: {" ".join(command)}\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}'
        )
    return result


def tcp_check(host: str, port: int, timeout: float = 5.0) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def write_json_report(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True), encoding='utf-8')
    log('report_written', path=str(path))


def main_exit(callback) -> None:
    try:
        callback()
    except Exception as exc:
        log('validation_failed', error=str(exc))
        sys.exit(1)
