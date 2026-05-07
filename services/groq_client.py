from __future__ import annotations

import json
import logging
import hashlib
import os
import time
from typing import Any

import requests
from requests import Response

from cache.redis_client import create_redis_client
from monitoring.metrics import metrics_registry


class GroqClientError(Exception):
    """Raised when the Groq API cannot produce a usable response."""


class GroqClient:
    def __init__(
        self,
        api_key: str,
        base_url: str,
        model: str,
        logger: logging.Logger | None = None,
    ) -> None:
        if not api_key:
            raise ValueError('GROQ_API_KEY must be configured in environment variables.')
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.model = model
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
        })
        self.logger = logger or logging.getLogger(__name__)
        self.cache_ttl_seconds = int(os.getenv('AI_CACHE_TTL_SECONDS', '900'))
        self.cache_enabled = os.getenv('AI_CACHE_ENABLED', 'true').lower() in {'1', 'true', 'yes'}
        self.cache = create_redis_client() if self.cache_enabled else None

    def generate(self, prompt: str, max_tokens: int = 1024) -> str:
        if not isinstance(prompt, str) or not prompt.strip():
            raise ValueError('Prompt cannot be empty.')
        payload = {
            'model': self.model,
            'messages': [
                {
                    'role': 'system',
                    'content': (
                        'You are an audit issue aging analyst. Return clear, concise, '
                        'actionable risk and remediation guidance.'
                    ),
                },
                {'role': 'user', 'content': prompt},
            ],
            'temperature': 0.2,
            'max_tokens': max_tokens,
        }
        cache_key = self._cache_key(payload)
        cached = self._cache_get(cache_key)
        if cached:
            metrics_registry.record_ai_cache_event(self.model, 'hit')
            self.logger.info('Groq response served from Redis cache', extra={'cache_key': cache_key})
            return cached

        metrics_registry.record_ai_cache_event(self.model, 'miss' if self.cache_enabled else 'disabled')
        response_text = self._call_groq(payload)
        self._cache_set(cache_key, response_text)
        return response_text

    def _call_groq(self, payload: dict[str, Any]) -> str:
        retries = 3
        backoff = 1.0
        last_error: Exception | None = None

        for attempt in range(1, retries + 1):
            try:
                self.logger.info('Sending request to Groq API', extra={'attempt': attempt})
                response = self.session.post(f'{self.base_url}/chat/completions', json=payload, timeout=10)
                self._assert_response(response)
                return self._parse_response(response)
            except (requests.RequestException, ConnectionError, GroqClientError, ValueError) as exc:
                last_error = exc
                self.logger.warning(
                    'Groq request failed',
                    extra={'attempt': attempt, 'error': str(exc)},
                )
                if attempt < retries:
                    time.sleep(backoff)
                    backoff *= 2

        raise GroqClientError(f'Groq API failed after {retries} attempts: {last_error}')

    def _cache_key(self, payload: dict[str, Any]) -> str:
        raw = json.dumps(payload, sort_keys=True, separators=(',', ':'))
        digest = hashlib.sha256(raw.encode('utf-8')).hexdigest()
        return f'tool125:ai-cache:{self.model}:{digest}'

    def _cache_get(self, key: str) -> str | None:
        if self.cache is None:
            return None
        try:
            cached = self.cache.get(key)
        except Exception as exc:  # pragma: no cover - depends on runtime Redis availability
            self.logger.warning('Redis AI cache read failed', extra={'error': str(exc)})
            return None
        return cached if isinstance(cached, str) and cached.strip() else None

    def _cache_set(self, key: str, value: str) -> None:
        if self.cache is None or not value:
            return
        try:
            self.cache.setex(key, self.cache_ttl_seconds, value)
        except Exception as exc:  # pragma: no cover - depends on runtime Redis availability
            self.logger.warning('Redis AI cache write failed', extra={'error': str(exc)})

    def _assert_response(self, response: Response) -> None:
        if response.status_code >= 400:
            raise GroqClientError(
                f'Groq API returned HTTP {response.status_code}: {response.text}'
            )

    def _parse_response(self, response: Response) -> str:
        raw_json = response.json()
        self.logger.info('Groq response received', extra={'response_keys': list(raw_json.keys())})

        output = raw_json.get('output')
        if output is None and 'choices' in raw_json:
            choices = raw_json['choices']
            if isinstance(choices, list) and choices:
                first_choice = choices[0]
                if isinstance(first_choice, dict):
                    message = first_choice.get('message')
                    if isinstance(message, dict):
                        output = message.get('content')
                    output = output or first_choice.get('text')
        if output is None and 'outputs' in raw_json:
            outputs = raw_json['outputs']
            if isinstance(outputs, list) and outputs:
                output = outputs[0]
        if output is None:
            raise GroqClientError('Groq API response did not contain a valid output.')
        if isinstance(output, (dict, list)):
            return json.dumps(output, ensure_ascii=False)
        if isinstance(output, str):
            parsed = self._safe_parse_json_string(output)
            if not parsed.strip():
                raise GroqClientError('Groq API returned an empty output.')
            return parsed
        raise GroqClientError('Groq API returned an unsupported output type.')

    def _safe_parse_json_string(self, output: str) -> str:
        trimmed = output.strip()
        if trimmed.startswith('{') or trimmed.startswith('['):
            try:
                parsed = json.loads(trimmed)
                return json.dumps(parsed, ensure_ascii=False)
            except json.JSONDecodeError:
                return output
        return output
