from __future__ import annotations

from pathlib import Path

from quality.evaluation_engine import EvaluationEngine, build_reference_response
from quality.scoring_utils import score_response, summarize_scores, validate_endpoint_response_schema
from services.prompt_manager import PromptBuilder


def test_scoring_returns_passing_score_for_structured_recommendation() -> None:
    issue = 'Cloud storage buckets used by audit exports do not enforce server-side encryption.'
    response = build_reference_response('/recommend', issue)
    score = score_response('/recommend', issue, response)
    assert score.average >= 4.0
    assert score.passed is True


def test_endpoint_response_schema_validation_accepts_success_payload() -> None:
    payload = {
        'success': True,
        'status': 'success',
        'endpoint': '/describe',
        'issue': 'Valid audit issue.',
        'response': build_reference_response('/describe', 'Valid audit issue.'),
        'score': 9,
        'generated_at': '2026-05-07T00:00:00+00:00',
    }
    assert validate_endpoint_response_schema('/describe', payload) == []


def test_endpoint_response_schema_validation_flags_malformed_output() -> None:
    payload = {'success': True, 'status': 'success', 'endpoint': '/describe'}
    errors = validate_endpoint_response_schema('/recommend', payload)
    assert errors
    assert any('Missing fields' in error for error in errors)
    assert any('endpoint does not match' in error for error in errors)


def test_evaluation_engine_loads_thirty_cases_and_meets_target() -> None:
    engine = EvaluationEngine()
    cases = engine.load_cases(Path('quality/data/endpoint_test_cases.json'))
    results = engine.evaluate_cases(cases)
    summary = engine.summarize(results)
    assert len(cases) == 30
    assert summary['overall']['average'] >= 4.0
    assert all(item['count'] == 10 for item in summary['endpoints'].values())


def test_evaluation_engine_exports_results(tmp_path: Path) -> None:
    engine = EvaluationEngine()
    cases = engine.load_cases(Path('quality/data/endpoint_test_cases.json'))[:3]
    results = engine.evaluate_cases(cases)
    output_json = tmp_path / 'quality_dashboard_data.json'
    output_md = tmp_path / 'ai_quality_report.md'
    engine.export_json(results, output_json)
    engine.export_markdown(results, output_md)
    assert output_json.exists()
    assert output_md.exists()
    assert 'AI Quality Report' in output_md.read_text(encoding='utf-8')


def test_prompt_builder_uses_quality_reviewed_templates() -> None:
    issue = 'Audit issue workflow closure lacks verification evidence.'
    assert PromptBuilder.VERSION == 'v2.0-quality-reviewed'
    assert 'Summary:' in PromptBuilder.describe(issue)
    assert 'Priority:' in PromptBuilder.recommend(issue)
    assert 'Evidence to Retain:' in PromptBuilder.generate_report(issue)


def test_score_summary_identifies_average_and_pass_status() -> None:
    scores = [
        score_response('/describe', 'Access control audit issue.', build_reference_response('/describe', 'Access control audit issue.')),
        score_response('/generate-report', 'Backup failure audit issue.', build_reference_response('/generate-report', 'Backup failure audit issue.')),
    ]
    summary = summarize_scores(scores)
    assert summary['count'] == 2
    assert summary['average'] >= 4.0
    assert summary['passed'] is True
