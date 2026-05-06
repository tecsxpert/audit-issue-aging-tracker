from flask import Blueprint, jsonify
from routes.ai_routes import utc_timestamp

health_blueprint = Blueprint('health', __name__)


@health_blueprint.route('/health', methods=['GET'])
def health() -> tuple[dict[str, object], int]:
    return jsonify({
        'success': True,
        'status': 'ok',
        'services': ['groq', 'prompt-sanitizer', 'rate-limiter'],
        'generated_at': utc_timestamp(),
    }), 200
