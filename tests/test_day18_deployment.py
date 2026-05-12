from __future__ import annotations

from pathlib import Path

from scripts.release_audit import release_audit
from validation.day18_deployment_validation import run_day18_deployment_validation


def test_day18_static_validation_passes() -> None:
    run_day18_deployment_validation(static_only=True)


def test_release_audit_dry_run_does_not_write(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr('scripts.release_audit.audit', lambda *args, **kwargs: tmp_path / 'unused.jsonl')

    payload = release_audit('0.18.0', git_sha='abc123', dry_run=True)

    assert payload['version'] == '0.18.0'
    assert payload['git_sha'] == 'abc123'
    assert payload['dry_run'] == 'true'


def test_production_env_example_uses_secret_placeholders() -> None:
    text = Path('deployment/env/.env.production.example').read_text(encoding='utf-8')

    assert 'inject_from_secret_manager' in text
    assert 'gsk_' not in text
    assert 'sk_live_' not in text
    assert 'sk_test_' not in text
