from __future__ import annotations

import logging
import time
from typing import Any

from config import Config
from monitoring.metrics import metrics_registry
from services.groq_client import GroqClient, GroqClientError
from services.prompt_manager import PromptBuilder, PromptOptimizer


PROMPT_BUILDERS = {
    '/describe': PromptBuilder.describe,
    '/recommend': PromptBuilder.recommend,
    '/generate-report': PromptBuilder.generate_report,
}


def process_ai_task(task: dict[str, Any], config: Config, logger: logging.Logger | None = None) -> dict[str, Any]:
    endpoint = str(task.get('endpoint', ''))
    issue = str(task.get('issue', '')).strip()
    if endpoint not in PROMPT_BUILDERS:
        raise ValueError(f'Unsupported async AI endpoint: {endpoint}')
    if not issue:
        raise ValueError('Task issue is required.')

    log = logger or logging.getLogger(__name__)
    prompt = PROMPT_BUILDERS[endpoint](issue)
    client = GroqClient(
        api_key=config.GROQ_API_KEY,
        base_url=config.GROQ_API_BASE_URL,
        model=config.GROQ_MODEL,
        logger=log,
        max_retries=config.GROQ_MAX_RETRIES,
        backoff_seconds=config.GROQ_BACKOFF_SECONDS,
        timeout_seconds=config.GROQ_TIMEOUT_SECONDS,
    )
    response_text = _timed_generate(client, prompt, endpoint, config.GROQ_MODEL)
    if not isinstance(response_text, str) or not response_text.strip():
        raise GroqClientError('Groq API returned a malformed AI response.')

    evaluator = PromptOptimizer()
    score = evaluator.score(response_text)
    if score < 7:
        prompt = evaluator.optimize(prompt, issue, context=endpoint.strip('/'))
        response_text = _timed_generate(client, prompt, endpoint, config.GROQ_MODEL)
        score = evaluator.score(response_text)

    return {
        'success': True,
        'status': 'success',
        'endpoint': endpoint,
        'issue': issue,
        'score': score,
        'response': response_text,
    }


def _timed_generate(client: GroqClient, prompt: str, endpoint: str, model: str) -> str:
    started_at = time.perf_counter()
    try:
        return client.generate(prompt)
    finally:
        metrics_registry.record_ai_timing(endpoint, model, time.perf_counter() - started_at)
