from __future__ import annotations
import json
import logging
import time
from typing import Any
import requests
from requests import Response


class GroqClientError(Exception):
    pass


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

    def generate(self, prompt: str, max_tokens: int = 1024) -> str:
        if not prompt:
            raise ValueError('Prompt cannot be empty.')
        payload = {
            'model': self.model,
            'input': prompt,
            'max_output_tokens': max_tokens,
        }
        return self._call_groq(payload)

    def _call_groq(self, payload: dict[str, Any]) -> str:
        retries = 3
        backoff = 1.0
        last_error: Exception | None = None
        for attempt in range(1, retries + 1):
            try:
                self.logger.info('Sending request to Groq API', extra={'attempt': attempt})
                response = self.session.post(f'{self.base_url}/predict', json=payload, timeout=10)
                self._assert_response(response)
                return self._parse_response(response)
            except (requests.RequestException, GroqClientError, json.JSONDecodeError) as exc:
                last_error = exc
                self.logger.warning(
                    'Groq request failed, retrying',
                    extra={
                        'attempt': attempt,
                        'error': str(exc),
                        'status_code': getattr(exc, 'response', None).status_code if isinstance(exc, requests.HTTPError) else None,
                    },
                )
                time.sleep(backoff)
                backoff *= 2
        raise GroqClientError(f'Groq API failed after {retries} attempts: {last_error}')

    def _assert_response(self, response: Response) -> None:
        if response.status_code >= 400:
            raise GroqClientError(
                f'Groq API returned HTTP {response.status_code}: {response.text}'
            )

    def _parse_response(self, response: Response) -> str:
        raw_json = response.json()
        self.logger.info('Groq response received', extra={'response_keys': list(raw_json.keys())})
        output = raw_json.get('output')
        if output is None and 'outputs' in raw_json:
            outputs = raw_json['outputs']
            if isinstance(outputs, list) and outputs:
                output = outputs[0]
        if output is None:
            raise GroqClientError('Groq API response did not contain a valid output.')
        if isinstance(output, (dict, list)):
            return json.dumps(output, ensure_ascii=False)
        if isinstance(output, str):
            return self._safe_parse_json_string(output)
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
