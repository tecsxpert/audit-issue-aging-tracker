from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from quality.evaluation_engine import EvaluationEngine

DEFAULT_CASES = PROJECT_ROOT / 'quality' / 'data' / 'endpoint_test_cases.json'
DEFAULT_OUTPUT = PROJECT_ROOT / 'quality' / 'results' / 'quality_dashboard_data.json'
DEFAULT_REPORT = PROJECT_ROOT / 'docs' / 'ai_quality_report.md'


def endpoint_responder(base_url: str, token: str) -> Any:
    def _respond(endpoint: str, issue: str) -> dict[str, Any]:
        body = json.dumps({'issue': issue}).encode('utf-8')
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }
        request = urllib.request.Request(f'{base_url.rstrip("/")}{endpoint}', data=body, headers=headers, method='POST')
        try:
            with urllib.request.urlopen(request, timeout=20) as response:
                return json.loads(response.read().decode('utf-8'))
        except urllib.error.HTTPError as error:
            raw = error.read().decode('utf-8')
            return json.loads(raw) if raw else {'success': False, 'status': 'error', 'message': str(error)}
    return _respond


def main() -> int:
    parser = argparse.ArgumentParser(description='Run Tool-125 AI response quality evaluation.')
    parser.add_argument('--cases', type=Path, default=DEFAULT_CASES)
    parser.add_argument('--output-json', type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument('--output-md', type=Path, default=DEFAULT_REPORT)
    parser.add_argument('--base-url', default=os.getenv('AI_SERVICE_URL', ''))
    parser.add_argument('--token', default=os.getenv('AI_SERVICE_TOKEN', ''))
    args = parser.parse_args()

    responder = endpoint_responder(args.base_url, args.token) if args.base_url and args.token else None
    engine = EvaluationEngine(responder=responder)
    started = time.perf_counter()
    cases = engine.load_cases(args.cases)
    results = engine.evaluate_cases(cases)
    engine.export_json(results, args.output_json)
    engine.export_markdown(results, args.output_md)
    elapsed = round((time.perf_counter() - started) * 1000, 2)
    summary = engine.summarize(results)

    print(json.dumps({
        'result_count': summary['result_count'],
        'overall_average': summary['overall']['average'],
        'target_met': summary['overall']['passed'],
        'elapsed_ms': elapsed,
        'output_json': str(args.output_json),
        'output_md': str(args.output_md),
    }, indent=2))
    return 0 if summary['overall']['passed'] else 1


if __name__ == '__main__':
    sys.exit(main())
