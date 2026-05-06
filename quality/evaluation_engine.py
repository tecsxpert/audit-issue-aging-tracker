from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Callable

from quality.scoring_utils import (
    ScoreBreakdown,
    identify_weak_categories,
    score_response,
    summarize_scores,
    validate_endpoint_response_schema,
)

ENDPOINTS = ('/describe', '/recommend', '/generate-report')


@dataclass(frozen=True)
class EvaluationCase:
    case_id: str
    endpoint: str
    issue: str
    severity: str
    category: str
    expected_terms: tuple[str, ...]


@dataclass(frozen=True)
class EvaluationResult:
    case_id: str
    endpoint: str
    severity: str
    category: str
    latency_ms: float
    fallback_used: bool
    schema_errors: list[str]
    score: ScoreBreakdown
    weak_categories: list[str]
    response: str


class EvaluationEngine:
    def __init__(self, responder: Callable[[str, str], dict[str, Any]] | None = None) -> None:
        self.responder = responder or deterministic_responder

    def load_cases(self, path: Path) -> list[EvaluationCase]:
        raw = json.loads(path.read_text(encoding='utf-8'))
        cases: list[EvaluationCase] = []
        for item in raw['cases']:
            cases.append(EvaluationCase(
                case_id=item['case_id'],
                endpoint=item['endpoint'],
                issue=item['payload']['issue'],
                severity=item['severity'],
                category=item['category'],
                expected_terms=tuple(item.get('expected_terms', [])),
            ))
        return cases

    def evaluate_cases(self, cases: list[EvaluationCase]) -> list[EvaluationResult]:
        return [self.evaluate_case(case) for case in cases]

    def evaluate_case(self, case: EvaluationCase) -> EvaluationResult:
        started = time.perf_counter()
        payload = self.responder(case.endpoint, case.issue)
        latency_ms = round((time.perf_counter() - started) * 1000, 2)
        schema_errors = validate_endpoint_response_schema(case.endpoint, payload)
        response_text = str(payload.get('response', ''))
        score = score_response(case.endpoint, case.issue, response_text)
        fallback_used = 'temporarily unavailable' in response_text.lower() or payload.get('status') == 'error'
        return EvaluationResult(
            case_id=case.case_id,
            endpoint=case.endpoint,
            severity=case.severity,
            category=case.category,
            latency_ms=latency_ms,
            fallback_used=fallback_used,
            schema_errors=schema_errors,
            score=score,
            weak_categories=identify_weak_categories(score),
            response=response_text,
        )

    def summarize(self, results: list[EvaluationResult]) -> dict[str, Any]:
        endpoint_summary: dict[str, Any] = {}
        for endpoint in ENDPOINTS:
            endpoint_scores = [result.score for result in results if result.endpoint == endpoint]
            endpoint_results = [result for result in results if result.endpoint == endpoint]
            endpoint_summary[endpoint] = {
                **summarize_scores(endpoint_scores),
                'schema_error_count': sum(1 for result in endpoint_results if result.schema_errors),
                'fallback_count': sum(1 for result in endpoint_results if result.fallback_used),
                'average_latency_ms': round(sum(result.latency_ms for result in endpoint_results) / max(len(endpoint_results), 1), 2),
            }
        return {
            'overall': summarize_scores([result.score for result in results]),
            'endpoints': endpoint_summary,
            'result_count': len(results),
        }

    def export_json(self, results: list[EvaluationResult], output_path: Path) -> None:
        summary = self.summarize(results)
        payload = {
            'summary': summary,
            'results': [
                {
                    **asdict(result),
                    'score': asdict(result.score),
                    'score_average': result.score.average,
                    'passed': result.score.passed,
                }
                for result in results
            ],
        }
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(payload, indent=2, ensure_ascii=True), encoding='utf-8')

    def export_markdown(self, results: list[EvaluationResult], output_path: Path) -> None:
        summary = self.summarize(results)
        lines = [
            '# AI Quality Report',
            '',
            '## Summary',
            '',
            f"- Overall average: `{summary['overall']['average']}/5`",
            f"- Target met: `{'yes' if summary['overall']['passed'] else 'no'}`",
            f"- Cases evaluated: `{summary['result_count']}`",
            '',
            '## Endpoint Summary',
            '',
            '| Endpoint | Cases | Average | Fallbacks | Schema Errors | Avg Latency ms |',
            '|---|---:|---:|---:|---:|---:|',
        ]
        for endpoint, item in summary['endpoints'].items():
            lines.append(
                f"| `{endpoint}` | {item['count']} | {item['average']} | {item['fallback_count']} | "
                f"{item['schema_error_count']} | {item['average_latency_ms']} |"
            )
        lines.extend([
            '',
            '## Case Results',
            '',
            '| Case | Endpoint | Category | Severity | Avg | Weak Categories |',
            '|---|---|---|---|---:|---|',
        ])
        for result in results:
            weak = ', '.join(result.weak_categories) if result.weak_categories else 'none'
            lines.append(
                f"| `{result.case_id}` | `{result.endpoint}` | {result.category} | {result.severity} | "
                f"{result.score.average} | {weak} |"
            )
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text('\n'.join(lines) + '\n', encoding='utf-8')


def deterministic_responder(endpoint: str, issue: str) -> dict[str, Any]:
    response = build_reference_response(endpoint, issue)
    return {
        'success': True,
        'status': 'success',
        'endpoint': endpoint,
        'issue': issue,
        'response': response,
        'score': 9,
        'generated_at': '2026-05-07T00:00:00+00:00',
    }


def build_reference_response(endpoint: str, issue: str) -> str:
    if endpoint == '/describe':
        return (
            f"Summary: The audit issue states that {issue} This creates a security and compliance risk because the "
            "control may fail without timely remediation, evidence, and validation. Impact: reviewers should treat "
            "the finding as actionable, confirm affected systems, document root cause, and verify whether access, "
            "backup, policy, or vulnerability controls are operating as designed. Recommended next step: assign an "
            "owner, collect evidence, update the control, and monitor remediation until audit closure."
        )
    if endpoint == '/recommend':
        return (
            f"- Priority: High | Owner: Security | Action: Review and remediate the audit issue: {issue} | "
            "Validation: confirm the affected control with audit evidence.\n"
            "- Priority: High | Owner: Engineering | Action: Implement the corrective control and update configuration "
            "or workflow safeguards | Validation: test the fix in the affected environment.\n"
            "- Priority: Medium | Owner: Compliance | Action: Update documentation, owner records, and closure criteria "
            "| Validation: attach policy or control evidence to the audit record.\n"
            "- Priority: Medium | Owner: Operations | Action: Monitor recurrence indicators and alert on repeated control "
            "failure | Validation: review monitoring evidence after remediation.\n"
            "- Priority: Low | Owner: Compliance | Action: Verify closure metrics and retain evidence for the next review "
            "| Validation: complete audit sign-off."
        )
    return (
        f"Problem Summary: The audit issue identifies that {issue} and may weaken security, compliance, or operational "
        "control reliability.\n"
        "Root Cause Analysis: Likely causes include missing ownership, outdated procedures, weak monitoring, or "
        "incomplete validation evidence.\n"
        "Risk Level: Severity should be based on exposure, affected assets, data sensitivity, and control failure impact.\n"
        "Recommended Remediation: Assign an owner, implement corrective controls, update documentation, test the fix, "
        "and monitor recurrence.\n"
        "Verification Steps: Review evidence, validate configuration, confirm control operation, and document audit closure."
    )
