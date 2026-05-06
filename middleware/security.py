from __future__ import annotations
import logging
import re
import signal
import time
from typing import Any
from flask import Flask, current_app, jsonify, request
from werkzeug.exceptions import RequestEntityTooLarge
from services.jwt_manager import JwtValidationError, validate_jwt
from services.pii_detector import contains_pii
from services.sql_safety import contains_sql_injection

SECURE_HEADERS: dict[str, str] = {
    'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
    'X-Content-Type-Options': 'nosniff',
    'X-Frame-Options': 'DENY',
    'Referrer-Policy': 'no-referrer',
    'Permissions-Policy': 'interest-cohort=()',
    'Content-Security-Policy': "default-src 'none'; frame-ancestors 'none'; base-uri 'none'; form-action 'none';",
    'Cache-Control': 'no-store, no-cache, must-revalidate, max-age=0',
}
PROTECTED_PATHS = {'/describe', '/recommend', '/generate-report'}


class SecurityError(ValueError):
    pass


class RequestTimeoutError(RuntimeError):
    pass


def attach_security_middleware(app: Flask, config: Any) -> None:
    @app.errorhandler(SecurityError)
    def handle_security(error: SecurityError):
        current_app.logger.warning('Security validation failed', extra={'error': str(error)})
        return jsonify({'status': 'error', 'message': str(error)}), 400

    @app.errorhandler(JwtValidationError)
    def handle_jwt(error: JwtValidationError):
        current_app.logger.warning('JWT validation failed', extra={'error': str(error)})
        return jsonify({'status': 'error', 'message': str(error)}), 401

    @app.errorhandler(RequestEntityTooLarge)
    def handle_request_too_large(error: RequestEntityTooLarge):
        return jsonify({'status': 'error', 'message': 'Request body too large.'}), 413

    @app.errorhandler(RequestTimeoutError)
    def handle_timeout(error: RequestTimeoutError):
        current_app.logger.error('Request timeout triggered', exc_info=error)
        return jsonify({'status': 'error', 'message': 'Request processing timed out.'}), 504

    def _set_timeout(seconds: int) -> None:
        if hasattr(signal, 'SIGALRM'):
            signal.signal(signal.SIGALRM, lambda signum, frame: (_ for _ in ()).throw(RequestTimeoutError('Request timed out.')))
            signal.alarm(seconds)

    def _clear_timeout() -> None:
        if hasattr(signal, 'SIGALRM'):
            signal.alarm(0)

    @app.before_request
    def enforce_security() -> None:
        if request.content_length is not None and request.content_length > app.config['MAX_CONTENT_LENGTH']:
            raise RequestEntityTooLarge()

        if request.method in {'POST', 'PUT', 'PATCH'} and request.path in PROTECTED_PATHS:
            content_type = request.headers.get('Content-Type', '')
            if not content_type.startswith('application/json'):
                raise SecurityError('Content-Type must be application/json for AI endpoints.')

            if config.JWT_AUTH_ENABLED:
                auth_header = request.headers.get('Authorization', '')
                if not auth_header.startswith('Bearer '):
                    raise JwtValidationError('Authorization header must contain a Bearer token.')
                token = auth_header.split(' ', 1)[1].strip()
                payload = validate_jwt(
                    token=token,
                    secret=config.JWT_SECRET,
                    algorithms=[config.JWT_ALGORITHM],
                    audience=config.JWT_AUDIENCE or None,
                    issuer=config.JWT_ISSUER or None,
                )
                request.environ['jwt_payload'] = payload

            request.environ['request_start_time'] = time.monotonic()
            _set_timeout(config.REQUEST_TIMEOUT_SECONDS)
            body_text = request.get_data(as_text=True, parse_form_data=False)
            if contains_pii(body_text):
                raise SecurityError('Sensitive personal information detected in request payload.')
            if contains_sql_injection(body_text):
                current_app.logger.warning(
                    'Potential SQL injection payload detected in request body',
                    extra={
                        'path': request.path,
                        'client_ip': request.remote_addr,
                        'payload_snippet': body_text[:160],
                    },
                )

    @app.after_request
    def add_security_headers(response: Any) -> Any:
        origin = request.headers.get('Origin', '')
        allowed_origins = [origin.strip() for origin in config.ALLOWED_ORIGINS.split(',') if origin.strip()]
        if origin and origin in allowed_origins:
            response.headers['Access-Control-Allow-Origin'] = origin
            response.headers['Vary'] = 'Origin'
            response.headers['Access-Control-Allow-Methods'] = 'GET,POST,OPTIONS'
            response.headers['Access-Control-Allow-Headers'] = 'Authorization,Content-Type'

        for header_name, header_value in SECURE_HEADERS.items():
            response.headers.setdefault(header_name, header_value)

        elapsed = None
        if request.environ.get('request_start_time') is not None:
            elapsed = time.monotonic() - request.environ['request_start_time']
            if elapsed > config.REQUEST_TIMEOUT_SECONDS:
                current_app.logger.warning(
                    'Request exceeded configured timeout threshold',
                    extra={'path': request.path, 'duration': elapsed},
                )
        _clear_timeout()
        return response
