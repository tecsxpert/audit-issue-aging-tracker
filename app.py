from __future__ import annotations

import logging
import os
from typing import Any

from dotenv import load_dotenv
from flask import Flask, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from pythonjsonlogger import jsonlogger
from werkzeug.exceptions import BadRequest, HTTPException

from config import Config
from middleware.sanitization import attach_sanitization_middleware
from middleware.security import attach_security_middleware
from monitoring.middleware import attach_monitoring_middleware
from routes.ai_routes import ai_blueprint
from routes.health_routes import health_blueprint
from routes.monitoring_routes import monitoring_blueprint
from routes.task_routes import task_blueprint
from security.secure_logging import attach_sensitive_data_filter, safe_extra


def create_app() -> Flask:
    load_dotenv()
    config = Config()
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object(config)
    app.config['MAX_CONTENT_LENGTH'] = config.MAX_CONTENT_LENGTH
    app.config['JSON_SORT_KEYS'] = config.JSON_SORT_KEYS

    _configure_logging(app)
    _register_error_handlers(app)
    attach_monitoring_middleware(app)

    Limiter(
        key_func=get_remote_address,
        default_limits=[config.RATE_LIMIT],
        storage_uri=config.RATE_LIMIT_STORAGE_URI or None,
        app=app,
    )
    attach_sanitization_middleware(app)
    attach_security_middleware(app, config)
    app.register_blueprint(ai_blueprint)
    app.register_blueprint(health_blueprint)
    app.register_blueprint(monitoring_blueprint)
    app.register_blueprint(task_blueprint)
    return app


def _configure_logging(app: Flask) -> None:
    handler = logging.StreamHandler()
    formatter = jsonlogger.JsonFormatter(
        '%(asctime)s %(levelname)s %(name)s %(message)s %(request_id)s'
    )
    handler.setFormatter(formatter)
    attach_sensitive_data_filter(handler)

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.handlers = [handler]

    app.logger.handlers = [handler]
    app.logger.setLevel(logging.INFO)
    app.logger.propagate = False
    app.logger.info(
        'Application logging configured',
        extra=safe_extra(request_id=os.getenv('REQUEST_ID', 'local')),
    )


def _register_error_handlers(app: Flask) -> None:
    @app.errorhandler(BadRequest)
    def handle_bad_request(error: BadRequest):
        app.logger.warning('Malformed JSON or bad request rejected', extra={'error': str(error)})
        return jsonify(_error_payload('Malformed JSON request body.')), 400

    @app.errorhandler(HTTPException)
    def handle_http_error(error: HTTPException):
        return jsonify(_error_payload(error.description or error.name)), error.code or 500

    @app.errorhandler(Exception)
    def handle_unexpected_error(error: Exception):
        app.logger.exception('Unhandled application exception', exc_info=error)
        return jsonify(_error_payload('Internal service error.')), 503


def _error_payload(message: str) -> dict[str, Any]:
    from routes.ai_routes import utc_timestamp

    return {
        'success': False,
        'status': 'error',
        'message': message,
        'generated_at': utc_timestamp(),
    }


app = create_app()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 8000)))
