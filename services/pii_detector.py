from __future__ import annotations
import re
from typing import Iterable

PII_PATTERNS: dict[str, re.Pattern[str]] = {
    'email': re.compile(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'),
    'phone': re.compile(r'(?<!\d)(?:\+\d{1,3}[\s-]?)?(?:\(\d{2,4}\)|\d{2,4})[\s-]?\d{3,4}[\s-]?\d{3,4}(?!\d)'),
    'jwt': re.compile(r'eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+'),
    'api_key': re.compile(r'(?i)(?:api[_-]?key|secret|token|passwd|password)\s*[:=]\s*[A-Za-z0-9\-_.]+'),
    'credit_card': re.compile(r'(?<!\d)(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14})(?!\d)'),
    'ssn': re.compile(r'(?<!\d)(?:\d{3}-\d{2}-\d{4}|\d{9})(?!\d)'),
}


def find_pii(text: str) -> list[str]:
    matches: list[str] = []
    for label, pattern in PII_PATTERNS.items():
        if pattern.search(text):
            matches.append(label)
    return matches


def contains_pii(text: str) -> bool:
    return bool(find_pii(text))


def mask_pii(text: str) -> str:
    sanitized = text
    for pattern in PII_PATTERNS.values():
        sanitized = pattern.sub('[REDACTED]', sanitized)
    return sanitized


def sanitize_payload(value: str) -> str:
    return mask_pii(value)
