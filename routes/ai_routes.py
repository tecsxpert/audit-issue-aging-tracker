from __future__ import annotations
from datetime import datetime, timezone
import time
from typing import Any
from flask import Blueprint, current_app, jsonify, request
from monitoring.metrics import metrics_registry
from werkzeug.exceptions import BadRequest
from services.groq_client import GroqClient, GroqClientError
from services.prompt_manager import PromptBuilder, PromptOptimizer

ai_blueprint = Blueprint('ai', __name__)


def _get_groq_client() -> GroqClient:
    return GroqClient(
        api_key=current_app.config['GROQ_API_KEY'],
        base_url=current_app.config['GROQ_API_BASE_URL'],
        model=current_app.config['GROQ_MODEL'],
        logger=current_app.logger,
        max_retries=current_app.config.get('GROQ_MAX_RETRIES'),
        backoff_seconds=current_app.config.get('GROQ_BACKOFF_SECONDS'),
        timeout_seconds=current_app.config.get('GROQ_TIMEOUT_SECONDS'),
    )


def _validate_body(payload: dict[str, Any]) -> str:
    if not isinstance(payload, dict):
        raise ValueError('Request body must be a JSON object.')
    issue = payload.get('issue')
    if not isinstance(issue, str) or not issue.strip():
        raise ValueError('The "issue" field is required and must be a non-empty string.')
    return issue.strip()


def utc_timestamp() -> str:
    return datetime.now(tz=timezone.utc).isoformat()


def _success_payload(endpoint: str, issue: str, response_text: str, score: int) -> dict[str, Any]:
    return {
        'success': True,
        'status': 'success',
        'endpoint': endpoint,
        'issue': issue,
        'score': score,
        'response': response_text,
        'generated_at': utc_timestamp(),
    }


def _error_payload(message: str) -> dict[str, Any]:
    return {
        'success': False,
        'status': 'error',
        'message': message,
        'generated_at': utc_timestamp(),
    }


def _generate_endpoint_response(endpoint: str, prompt: str, issue: str) -> tuple[Any, int]:
    client = _get_groq_client()
    response_text = _timed_ai_generate(client, prompt, endpoint)
    if not isinstance(response_text, str) or not response_text.strip():
        raise GroqClientError('Groq API returned a malformed AI response.')

    evaluator = PromptOptimizer()
    score = evaluator.score(response_text)
    if score < 7:
        prompt = evaluator.optimize(prompt, issue, context=endpoint.strip('/'))
        response_text = _timed_ai_generate(client, prompt, endpoint)
        if not isinstance(response_text, str) or not response_text.strip():
            raise GroqClientError('Groq API returned a malformed AI response.')
        score = evaluator.score(response_text)

    return jsonify(_success_payload(endpoint, issue, response_text, score)), 200


def _timed_ai_generate(client: GroqClient, prompt: str, endpoint: str) -> str:
    started_at = time.perf_counter()
    try:
        return client.generate(prompt)
    finally:
        metrics_registry.record_ai_timing(
            endpoint,
            current_app.config.get('GROQ_MODEL', 'unknown'),
            time.perf_counter() - started_at,
        )


def _safe_json_payload() -> dict[str, Any]:
    try:
        return request.get_json(silent=False)
    except BadRequest as error:
        raise ValueError('Malformed JSON request body.') from error


@ai_blueprint.route('/describe', methods=['POST'])
def describe() -> tuple[Any, int]:
    try:
        payload = _safe_json_payload()
        issue = _validate_body(payload)
        current_app.logger.info('describe_request_validated', extra={'endpoint': '/describe'})
        prompt = PromptBuilder.describe(issue)
        return _generate_endpoint_response('/describe', prompt, issue)
    except GroqClientError as error:
        current_app.logger.error('Describe endpoint failed', exc_info=error)
        return jsonify(_error_payload(f'Groq API failed: {error}')), 502
    except ValueError as error:
        return jsonify(_error_payload(str(error))), 400
    except Exception as error:
        current_app.logger.exception('Describe endpoint internal exception', exc_info=error)
        return jsonify(_error_payload('AI endpoint failed gracefully.')), 503


@ai_blueprint.route('/recommend', methods=['POST'])
def recommend() -> tuple[Any, int]:
    try:
        payload = _safe_json_payload()
        issue = _validate_body(payload)
        current_app.logger.info('recommend_request_validated', extra={'endpoint': '/recommend'})
        prompt = PromptBuilder.recommend(issue)
        return _generate_endpoint_response('/recommend', prompt, issue)
    except GroqClientError as error:
        current_app.logger.error('Recommend endpoint failed', exc_info=error)
        return jsonify(_error_payload(f'Groq API failed: {error}')), 502
    except ValueError as error:
        return jsonify(_error_payload(str(error))), 400
    except Exception as error:
        current_app.logger.exception('Recommend endpoint internal exception', exc_info=error)
        return jsonify(_error_payload('AI endpoint failed gracefully.')), 503


@ai_blueprint.route('/generate-report', methods=['POST'])
def generate_report() -> tuple[Any, int]:
    try:
        payload = _safe_json_payload()
        issue = _validate_body(payload)
        current_app.logger.info('generate_report_request_validated', extra={'endpoint': '/generate-report'})
        prompt = PromptBuilder.generate_report(issue)
        return _generate_endpoint_response('/generate-report', prompt, issue)
    except GroqClientError as error:
        current_app.logger.error('Generate-report endpoint failed', exc_info=error)
        return jsonify(_error_payload(f'Groq API failed: {error}')), 502
    except ValueError as error:
        return jsonify(_error_payload(str(error))), 400
    except Exception as error:
        current_app.logger.exception('Generate-report endpoint internal exception', exc_info=error)
        return jsonify(_error_payload('AI endpoint failed gracefully.')), 503
