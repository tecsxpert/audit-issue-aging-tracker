from __future__ import annotations
import re
from typing import Any
from flask import Flask, jsonify, request
from werkzeug.exceptions import RequestEntityTooLarge
from services.pii_detector import contains_pii
from routes.ai_routes import utc_timestamp

SCRIPT_TAG_PATTERN = re.compile(r'(?is)<script.*?>.*?</script>')
HTML_TAG_PATTERN = re.compile(r'(?is)<[^>]+>')
PROMPT_INJECTION_PATTERN = re.compile(
    r'(?i)(ignore previous instructions|ignore above instructions|do not follow(?:\s+\w+){0,4}\s+instructions?|do not follow(?:\s+the)?\s+system\s+prompt|bypass|prompt injection|disregard this message)'
)
COMMAND_INJECTION_PATTERN = re.compile(
    r'(?is)(\b(?:curl|wget|nc|netcat|bash|sh|powershell|cmd\.exe|python\s+-c)\b|[`$]\(|\|\||&&|;\s*(?:rm|del|curl|wget|bash|sh|powershell)\b)'
)
DANGEROUS_KEY_PATTERN = re.compile(r'(?i)^(__proto__|constructor|prototype|\$where|\$ne|\$gt|\$regex|\$function)$')
MAX_JSON_DEPTH = 8
MAX_LIST_ITEMS = 100
MAX_STRING_LENGTH = 12_000


class SanitizationError(ValueError):
    pass


def attach_sanitization_middleware(app: Flask) -> None:
    @app.errorhandler(SanitizationError)
    def handle_sanitization(error: SanitizationError):
        return jsonify({
            'success': False,
            'status': 'error',
            'message': str(error),
            'generated_at': utc_timestamp(),
        }), 400

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
            raise RequestEntityTooLarge()
        data = request.get_json(silent=False)
        sanitized = _sanitize_payload(data)
        request._cached_json = {False: sanitized, True: sanitized}


def _sanitize_payload(payload: Any, depth: int = 0) -> Any:
    if depth > MAX_JSON_DEPTH:
        raise SanitizationError('JSON payload exceeds maximum nesting depth.')
    if isinstance(payload, dict):
        sanitized: dict[str, Any] = {}
        for key, value in payload.items():
            if not isinstance(key, str) or DANGEROUS_KEY_PATTERN.search(key):
                raise SanitizationError('Dangerous JSON key detected and rejected.')
            sanitized[key] = _sanitize_payload(value, depth + 1)
        return sanitized
    if isinstance(payload, list):
        if len(payload) > MAX_LIST_ITEMS:
            raise SanitizationError('JSON array exceeds maximum item count.')
        return [_sanitize_payload(item, depth + 1) for item in payload]
    if isinstance(payload, str):
        if len(payload) > MAX_STRING_LENGTH:
            raise SanitizationError('Input field exceeds maximum allowed length.')
        if SCRIPT_TAG_PATTERN.search(payload):
            raise SanitizationError('Script tags are not allowed in input.')
        if PROMPT_INJECTION_PATTERN.search(payload):
            raise SanitizationError('Prompt injection detected and rejected.')
        if COMMAND_INJECTION_PATTERN.search(payload):
            raise SanitizationError('Command injection payload detected and rejected.')
        if contains_pii(payload):
            raise SanitizationError('Sensitive personal information detected in input.')
        if HTML_TAG_PATTERN.search(payload):
            payload = HTML_TAG_PATTERN.sub('', payload)
        return payload.strip()
    return payload
