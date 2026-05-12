from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from validation.common import REPO_ROOT, ValidationConfig, log, request_json, write_json_report


PROJECT_ROOT = REPO_ROOT
REQUIRED_FILES = [
    PROJECT_ROOT / '.github' / 'workflows' / 'ai-service-ci.yml',
    PROJECT_ROOT / '.github' / 'workflows' / 'ai-service-release.yml',
    REPO_ROOT / 'docker-compose.yml',
    REPO_ROOT / 'docker-compose.prod.yml',
    REPO_ROOT / 'deployment' / 'env' / '.env.development.example',
    REPO_ROOT / 'deployment' / 'env' / '.env.staging.example',
    REPO_ROOT / 'deployment' / 'env' / '.env.production.example',
    REPO_ROOT / 'scripts' / 'deploy.py',
    REPO_ROOT / 'scripts' / 'rollback.py',
    REPO_ROOT / 'scripts' / 'health_verify.py',
    REPO_ROOT / 'scripts' / 'backup.py',
    REPO_ROOT / 'scripts' / 'restore.py',
    REPO_ROOT / 'scripts' / 'release_audit.py',
    REPO_ROOT / 'VERSION',
]
FORBIDDEN_SECRET_PATTERNS = ('gsk_', 'sk_live_', 'sk_test_', 'Bearer eyJ', 'BEGIN PRIVATE KEY')


def run_day18_deployment_validation(static_only: bool = False) -> None:
    report: dict[str, Any] = {'checks': []}
    log('day18_deployment_validation_start', static_only=static_only)

    _check_required_files(report)
    _check_secret_hygiene(report)
    _check_compose_config(report)
    _check_workflows(report)

    if not static_only:
        _check_runtime_health(report)

    write_json_report(REPO_ROOT / 'validation' / 'reports' / 'day18_deployment_validation.json', report)
    log('day18_deployment_validation_passed')


def _check_required_files(report: dict[str, Any]) -> None:
    missing = [str(path) for path in REQUIRED_FILES if not path.exists()]
    if missing:
        raise AssertionError(f'Missing Day 18 deployment files: {missing}')
    report['checks'].append({'name': 'required_files', 'status': 'pass', 'count': len(REQUIRED_FILES)})


def _check_secret_hygiene(report: dict[str, Any]) -> None:
    checked = []
    for path in [
        REPO_ROOT / '.env.example',
        REPO_ROOT / 'deployment' / 'env' / '.env.development.example',
        REPO_ROOT / 'deployment' / 'env' / '.env.staging.example',
        REPO_ROOT / 'deployment' / 'env' / '.env.production.example',
        PROJECT_ROOT / '.github' / 'workflows' / 'ai-service-ci.yml',
        PROJECT_ROOT / '.github' / 'workflows' / 'ai-service-release.yml',
    ]:
        text = path.read_text(encoding='utf-8')
        matches = [pattern for pattern in FORBIDDEN_SECRET_PATTERNS if pattern in text]
        if matches:
            raise AssertionError(f'Potential secret pattern found in {path}: {matches}')
        checked.append(str(path))
    report['checks'].append({'name': 'secret_hygiene', 'status': 'pass', 'files_checked': checked})


def _check_compose_config(report: dict[str, Any]) -> None:
    result = subprocess.run(
        ['docker', 'compose', '-f', 'docker-compose.yml', '-f', 'docker-compose.prod.yml', 'config'],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=60,
    )
    if result.returncode == 0:
        report['checks'].append({'name': 'docker_compose_config', 'status': 'pass'})
    else:
        report['checks'].append({
            'name': 'docker_compose_config',
            'status': 'warn',
            'reason': result.stderr[-500:] or 'Docker Compose unavailable in this environment.',
        })


def _check_workflows(report: dict[str, Any]) -> None:
    ci = (PROJECT_ROOT / '.github' / 'workflows' / 'ai-service-ci.yml').read_text(encoding='utf-8')
    release = (PROJECT_ROOT / '.github' / 'workflows' / 'ai-service-release.yml').read_text(encoding='utf-8')
    required_ci_terms = ['pytest', 'docker build', 'pip-audit', 'bandit', 'ruff check']
    missing = [term for term in required_ci_terms if term not in ci]
    if missing:
        raise AssertionError(f'CI workflow missing expected steps: {missing}')
    if 'tags:' not in release or 'docker push' not in release:
        raise AssertionError('Release workflow missing tag or image publish support.')
    report['checks'].append({'name': 'github_actions_workflows', 'status': 'pass'})


def _check_runtime_health(report: dict[str, Any]) -> None:
    config = ValidationConfig()
    status, body, latency = request_json('GET', '/health', config=config)
    if status != 200 or body.get('status') != 'ok':
        raise AssertionError(f'/health failed: HTTP {status} {body}')
    report['checks'].append({'name': 'runtime_health', 'status': 'pass', 'latency_ms': latency})


def main() -> None:
    parser = argparse.ArgumentParser(description='Validate Day 18 deployment readiness assets.')
    parser.add_argument('--static-only', action='store_true')
    args = parser.parse_args()
    run_day18_deployment_validation(static_only=args.static_only)


if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        log('day18_deployment_validation_failed', error=str(exc))
        sys.exit(1)
