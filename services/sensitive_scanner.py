from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

from services.pii_detector import find_pii, mask_pii

SENSITIVE_KEYWORDS = {
    'authorization',
    'api_key',
    'apikey',
    'groq_api_key',
    'jwt_secret',
    'password',
    'passwd',
    'secret',
    'token',
}


@dataclass(frozen=True)
class SensitiveFinding:
    category: str
    location: str


def scan_text(value: str, location: str = 'text') -> list[SensitiveFinding]:
    return [SensitiveFinding(category=label, location=location) for label in find_pii(value)]


def scan_payload(value: Any, location: str = '$') -> list[SensitiveFinding]:
    findings: list[SensitiveFinding] = []
    if isinstance(value, dict):
        for key, item in value.items():
            key_text = str(key)
            key_path = f'{location}.{key_text}'
            if _is_sensitive_key(key_text):
                findings.append(SensitiveFinding(category='sensitive_key', location=key_path))
            findings.extend(scan_payload(item, key_path))
        return findings
    if isinstance(value, list):
        for index, item in enumerate(value):
            findings.extend(scan_payload(item, f'{location}[{index}]'))
        return findings
    if isinstance(value, str):
        findings.extend(scan_text(value, location))
    return findings


def mask_sensitive_text(value: str) -> str:
    return mask_pii(value)


def mask_sensitive_payload(value: Any) -> Any:
    if isinstance(value, dict):
        masked: dict[str, Any] = {}
        for key, item in value.items():
            if _is_sensitive_key(str(key)):
                masked[key] = '[REDACTED]'
            else:
                masked[key] = mask_sensitive_payload(item)
        return masked
    if isinstance(value, list):
        return [mask_sensitive_payload(item) for item in value]
    if isinstance(value, str):
        return mask_sensitive_text(value)
    return value


def redact_for_log(value: Any) -> Any:
    if isinstance(value, str):
        return mask_sensitive_text(value)
    if isinstance(value, (dict, list)):
        return mask_sensitive_payload(value)
    return value


def assert_no_sensitive_data(value: Any) -> None:
    findings = scan_payload(value)
    if findings:
        rendered = ', '.join(f'{finding.category}@{finding.location}' for finding in findings)
        raise ValueError(f'Sensitive data detected: {rendered}')


def to_safe_json(value: Any) -> str:
    return json.dumps(mask_sensitive_payload(value), ensure_ascii=True, sort_keys=True)


def _is_sensitive_key(key: str) -> bool:
    normalized = key.lower().replace('-', '_')
    return normalized in SENSITIVE_KEYWORDS or any(term in normalized for term in ('password', 'secret', 'token', 'api_key'))
