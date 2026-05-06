from flask import Blueprint, jsonify

health_blueprint = Blueprint('health', __name__)


@health_blueprint.route('/health', methods=['GET'])
def health() -> tuple[dict[str, str], int]:
    return jsonify({
        'status': 'ok',
        'services': ['groq', 'prompt-sanitizer', 'rate-limiter'],
    }), 200
