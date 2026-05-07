from __future__ import annotations

import logging
from typing import Any

from services.sensitive_scanner import redact_for_log

_RESERVED_ATTRS = set(logging.makeLogRecord({}).__dict__.keys())


class SensitiveDataFilter(logging.Filter):
    """Masks PII and secrets from structured log records before emission."""

    def filter(self, record: logging.LogRecord) -> bool:
        record.msg = redact_for_log(record.msg)
        if isinstance(record.args, dict):
            record.args = {key: redact_for_log(value) for key, value in record.args.items()}
        elif isinstance(record.args, tuple):
            record.args = tuple(redact_for_log(value) for value in record.args)

        for key, value in list(record.__dict__.items()):
            if key in _RESERVED_ATTRS or key in {'exc_info', 'exc_text', 'stack_info'}:
                continue
            record.__dict__[key] = redact_for_log(value)
        return True


def attach_sensitive_data_filter(handler: logging.Handler) -> None:
    if not any(isinstance(item, SensitiveDataFilter) for item in handler.filters):
        handler.addFilter(SensitiveDataFilter())


def safe_extra(**values: Any) -> dict[str, Any]:
    return {key: redact_for_log(value) for key, value in values.items()}
