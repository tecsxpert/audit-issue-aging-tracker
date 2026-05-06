from __future__ import annotations
from typing import Any
from flask import Blueprint, current_app, jsonify, request
from services.groq_client import GroqClient, GroqClientError
from services.prompt_manager import PromptBuilder, PromptOptimizer

ai_blueprint = Blueprint('ai', __name__)


def _get_groq_client() -> GroqClient:
    return GroqClient(
        api_key=current_app.config['GROQ_API_KEY'],
        base_url=current_app.config['GROQ_API_BASE_URL'],
        model=current_app.config['GROQ_MODEL'],
        logger=current_app.logger,
    )


def _validate_body(payload: dict[str, Any]) -> str:
    issue = payload.get('issue')
    if not isinstance(issue, str) or not issue.strip():
        raise ValueError('The "issue" field is required and must be a non-empty string.')
    return issue.strip()


@ai_blueprint.route('/describe', methods=['POST'])
def describe() -> tuple[dict[str, Any], int]:
    payload = request.get_json(silent=False)
    try:
        issue = _validate_body(payload)
        prompt = PromptBuilder.describe(issue)
        client = _get_groq_client()
        response_text = client.generate(prompt)
        evaluator = PromptOptimizer()
        score = evaluator.score(response_text)
        if score < 7:
            prompt = evaluator.optimize(prompt, issue)
            response_text = client.generate(prompt)
            score = evaluator.score(response_text)
        return jsonify({
            'status': 'success',
            'endpoint': '/describe',
            'issue': issue,
            'score': score,
            'response': response_text,
        }), 200
    except GroqClientError as error:
        current_app.logger.error('Describe endpoint failed', exc_info=error)
        return jsonify({'status': 'error', 'message': str(error)}), 502
    except ValueError as error:
        return jsonify({'status': 'error', 'message': str(error)}), 400


@ai_blueprint.route('/recommend', methods=['POST'])
def recommend() -> tuple[dict[str, Any], int]:
    payload = request.get_json(silent=False)
    try:
        issue = _validate_body(payload)
        prompt = PromptBuilder.recommend(issue)
        client = _get_groq_client()
        response_text = client.generate(prompt)
        evaluator = PromptOptimizer()
        score = evaluator.score(response_text)
        if score < 7:
            prompt = evaluator.optimize(prompt, issue, context='recommendation')
            response_text = client.generate(prompt)
            score = evaluator.score(response_text)
        return jsonify({
            'status': 'success',
            'endpoint': '/recommend',
            'issue': issue,
            'score': score,
            'response': response_text,
        }), 200
    except GroqClientError as error:
        current_app.logger.error('Recommend endpoint failed', exc_info=error)
        return jsonify({'status': 'error', 'message': str(error)}), 502
    except ValueError as error:
        return jsonify({'status': 'error', 'message': str(error)}), 400


@ai_blueprint.route('/generate-report', methods=['POST'])
def generate_report() -> tuple[dict[str, Any], int]:
    payload = request.get_json(silent=False)
    try:
        issue = _validate_body(payload)
        prompt = PromptBuilder.generate_report(issue)
        client = _get_groq_client()
        response_text = client.generate(prompt)
        evaluator = PromptOptimizer()
        score = evaluator.score(response_text)
        if score < 7:
            prompt = evaluator.optimize(prompt, issue, context='report')
            response_text = client.generate(prompt)
            score = evaluator.score(response_text)
        return jsonify({
            'status': 'success',
            'endpoint': '/generate-report',
            'issue': issue,
            'score': score,
            'response': response_text,
        }), 200
    except GroqClientError as error:
        current_app.logger.error('Generate-report endpoint failed', exc_info=error)
        return jsonify({'status': 'error', 'message': str(error)}), 502
    except ValueError as error:
        return jsonify({'status': 'error', 'message': str(error)}), 400
