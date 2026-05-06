from __future__ import annotations
import re
from typing import Any
from flask import Flask, jsonify, request
from services.pii_detector import contains_pii

SCRIPT_TAG_PATTERN = re.compile(r'(?is)<script.*?>.*?</script>')
HTML_TAG_PATTERN = re.compile(r'(?is)<[^>]+>')
PROMPT_INJECTION_PATTERN = re.compile(
    r'(?i)(ignore previous instructions|ignore above instructions|do not follow instructions|bypass|prompt injection|disregard this message)'
)


class SanitizationError(ValueError):
    pass


def attach_sanitization_middleware(app: Flask) -> None:
    @app.errorhandler(SanitizationError)
    def handle_sanitization(error: SanitizationError):
        return jsonify({'status': 'error', 'message': str(error)}), 400

    @app.before_request
    def sanitize_request() -> None:
        if request.path not in ['/describe', '/recommend', '/generate-report']:
            return
        if not request.is_json:
            raise SanitizationError('JSON payload required for AI endpoints.')
        content_type = request.headers.get('Content-Type', '')
        if not content_type.startswith('application/json'):
            raise SanitizationError('Content-Type must be application/json.')
        if request.content_length is not None and request.content_length > app.config['MAX_CONTENT_LENGTH']:
            raise SanitizationError('Payload exceeds maximum allowed size.')
        data = request.get_json(silent=False)
        sanitized = _sanitize_payload(data)
        request._cached_json = {False: sanitized, True: sanitized}


def _sanitize_payload(payload: Any) -> Any:
    if isinstance(payload, dict):
        return {key: _sanitize_payload(value) for key, value in payload.items()}
    if isinstance(payload, list):
        return [_sanitize_payload(item) for item in payload]
    if isinstance(payload, str):
        if SCRIPT_TAG_PATTERN.search(payload):
            raise SanitizationError('Script tags are not allowed in input.')
        if PROMPT_INJECTION_PATTERN.search(payload):
            raise SanitizationError('Prompt injection detected and rejected.')
        if contains_pii(payload):
            raise SanitizationError('Sensitive personal information detected in input.')
        if HTML_TAG_PATTERN.search(payload):
            payload = HTML_TAG_PATTERN.sub('', payload)
        return payload.strip()
    return payload
