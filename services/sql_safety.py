from __future__ import annotations
import re

SQL_INJECTION_PATTERN = re.compile(
    r'(?is)(\bor\b\s+1\s*=\s*1|\band\b\s+1\s*=\s*1|union\s+select|drop\s+table|insert\s+into|update\s+\w+\s+set|delete\s+from|--|;|/\*|\*/)',
)


def contains_sql_injection(value: str) -> bool:
    return bool(SQL_INJECTION_PATTERN.search(value))


def is_high_risk_sql_payload(value: str) -> bool:
    return contains_sql_injection(value) and 'audit issue' not in value.lower()
