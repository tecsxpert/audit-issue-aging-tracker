from __future__ import annotations

from flask import Blueprint, Response, jsonify

from monitoring.metrics import metrics_registry
from monitoring.resources import get_resource_snapshot
from routes.ai_routes import utc_timestamp

monitoring_blueprint = Blueprint('monitoring', __name__)


@monitoring_blueprint.route('/metrics', methods=['GET'])
def metrics() -> Response:
    return Response(metrics_registry.render_prometheus(), mimetype='text/plain; version=0.0.4')


@monitoring_blueprint.route('/monitoring/status', methods=['GET'])
def monitoring_status() -> tuple[Response, int]:
    return jsonify({
        'success': True,
        'status': 'ok',
        'metrics': {
            'status': 'ok',
            'endpoint': '/metrics',
        },
        'resources': get_resource_snapshot(),
        'generated_at': utc_timestamp(),
    }), 200
