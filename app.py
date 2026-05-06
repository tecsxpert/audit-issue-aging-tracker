<<<<<<< HEAD
from __future__ import annotations
import logging
import os
from flask import Flask
from dotenv import load_dotenv
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from pythonjsonlogger import jsonlogger
from config import Config
from routes.ai_routes import ai_blueprint
from routes.health_routes import health_blueprint
from middleware.sanitization import attach_sanitization_middleware
from middleware.security import attach_security_middleware


def create_app() -> Flask:
    load_dotenv()
    config = Config()
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object(config)
    app.config['MAX_CONTENT_LENGTH'] = config.MAX_CONTENT_LENGTH
    app.config['JSON_SORT_KEYS'] = config.JSON_SORT_KEYS
    _configure_logging(app)
    Limiter(
        key_func=get_remote_address,
        default_limits=[config.RATE_LIMIT],
        storage_uri=config.RATE_LIMIT_STORAGE_URI or None,
        app=app,
    )
    attach_security_middleware(app, config)
    attach_sanitization_middleware(app)
    app.register_blueprint(ai_blueprint)
    app.register_blueprint(health_blueprint)
    return app


def _configure_logging(app: Flask) -> None:
    handler = logging.StreamHandler()
    formatter = jsonlogger.JsonFormatter(
        '%(asctime)s %(levelname)s %(name)s %(message)s %(request_id)s'
    )
    handler.setFormatter(formatter)
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.handlers = [handler]
    app.logger.handlers = [handler]
    app.logger.setLevel(logging.INFO)
    app.logger.info('Application logging configured', extra={'request_id': os.getenv('REQUEST_ID', 'local')})


app = create_app()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 8000)))
=======
from flask import Flask, request, jsonify
from services.groq_client import GroqClient
from datetime import datetime

app = Flask(__name__)
client = GroqClient()


@app.route("/describe", methods=["POST"])
def describe():

    data = request.get_json()

    # ✅ Input validation
    if not data or "issue" not in data:
        return jsonify({"error": "Invalid input: 'issue' field required"}), 400

    issue = data["issue"]

    if not isinstance(issue, str) or len(issue.strip()) < 5:
        return jsonify({"error": "Issue must be a valid string (min 5 chars)"}), 400

    try:
        # ✅ Call GroqClient
        ai_response = client.generate_response(issue)

        # ✅ Structured JSON response
        return jsonify({
            "description": ai_response,
            "generated_at": datetime.utcnow().isoformat()
        })

    except Exception as e:
        return jsonify({
            "error": "Internal server error",
            "details": str(e)
        }), 500


@app.route("/recommend", methods=["POST"])
def recommend():

    data = request.get_json()

    if not data or "issue" not in data:
        return jsonify({"error": "Invalid input"}), 400

    issue = data["issue"]

    if not isinstance(issue, str) or len(issue.strip()) < 5:
        return jsonify({"error": "Issue must be valid"}), 400

    try:
        recommendations = client.generate_recommendations(issue)

        return jsonify({
            "recommendations": recommendations,
            "generated_at": datetime.utcnow().isoformat()
        })

    except Exception as e:
        return jsonify({
            "error": "Internal server error",
            "details": str(e)
        }), 500


if __name__ == "__main__":
    app.run(port=5000, debug=True)
>>>>>>> f3393327b2fa049bff12dc583fc68ce4df4bd227
