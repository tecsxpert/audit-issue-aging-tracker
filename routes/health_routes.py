from flask import Blueprint, current_app, jsonify
from cache.redis_client import create_redis_client
from routes.ai_routes import utc_timestamp

health_blueprint = Blueprint('health', __name__)


@health_blueprint.route('/health', methods=['GET'])
def health() -> tuple[dict[str, object], int]:
    redis_status = 'not_configured'
    redis_url = current_app.config.get('REDIS_URL')
    if redis_url:
        try:
            redis_client = create_redis_client(redis_url)
            redis_status = 'ok' if redis_client and redis_client.ping() else 'unhealthy'
        except Exception:
            redis_status = 'unhealthy'

    return jsonify({
        'success': True,
        'status': 'ok',
        'services': ['groq', 'prompt-sanitizer', 'rate-limiter', 'redis-cache'],
        'dependencies': {
            'groq': 'configured' if current_app.config.get('GROQ_API_KEY') else 'missing',
            'redis': redis_status,
            'rate_limiter': 'configured',
        },
        'generated_at': utc_timestamp(),
    }), 200
