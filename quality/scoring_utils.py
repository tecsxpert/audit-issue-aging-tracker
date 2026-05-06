from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from statistics import mean
from typing import Any

SCORING_CATEGORIES = ('accuracy', 'clarity', 'structure', 'actionability', 'security_relevance')

SECURITY_TERMS = {
    'access',
    'audit',
    'backup',
    'compliance',
    'control',
    'evidence',
    'incident',
    'policy',
    'remediation',
    'review',
    'risk',
    'security',
    'validation',
    'vulnerability',
}

ACTION_TERMS = {
    'assign',
    'document',
    'enforce',
    'implement',
    'monitor',
    'remediate',
    'review',
    'rotate',
    'test',
    'update',
    'validate',
    'verify',
}

REPORT_SECTIONS = ('summary', 'root cause', 'risk', 'remediation', 'verification')


@dataclass(frozen=True)
class ScoreBreakdown:
    accuracy: int
    clarity: int
    structure: int
    actionability: int
    security_relevance: int

    @property
    def average(self) -> float:
        return round(mean(asdict(self).values()), 2)

    @property
    def passed(self) -> bool:
        return self.average >= 4.0


def score_response(endpoint: str, issue: str, response: str) -> ScoreBreakdown:
    text = _normalize(response)
    issue_text = _normalize(issue)
    return ScoreBreakdown(
        accuracy=_score_accuracy(issue_text, text),
        clarity=_score_clarity(response),
        structure=_score_structure(endpoint, response.lower()),
        actionability=_score_actionability(text),
        security_relevance=_score_security_relevance(issue_text, text),
    )


def summarize_scores(scores: list[ScoreBreakdown]) -> dict[str, Any]:
    if not scores:
        return {'average': 0.0, 'passed': False, 'count': 0}
    category_averages = {
        category: round(mean(getattr(score, category) for score in scores), 2)
        for category in SCORING_CATEGORIES
    }
    overall = round(mean(score.average for score in scores), 2)
    return {
        'average': overall,
        'passed': overall >= 4.0,
        'count': len(scores),
        'categories': category_averages,
    }


def identify_weak_categories(score: ScoreBreakdown, threshold: int = 4) -> list[str]:
    return [category for category in SCORING_CATEGORIES if getattr(score, category) < threshold]


def validate_endpoint_response_schema(endpoint: str, payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = {'success', 'status', 'endpoint', 'issue', 'response', 'score', 'generated_at'}
    missing = required - set(payload)
    if missing:
        errors.append(f'Missing fields: {", ".join(sorted(missing))}')
    if payload.get('success') is not True:
        errors.append('success must be true')
    if payload.get('status') != 'success':
        errors.append('status must be success')
    if payload.get('endpoint') != endpoint:
        errors.append('endpoint does not match requested endpoint')
    if not isinstance(payload.get('issue'), str) or not payload.get('issue', '').strip():
        errors.append('issue must be a non-empty string')
    if not isinstance(payload.get('response'), str) or not payload.get('response', '').strip():
        errors.append('response must be a non-empty string')
    if not isinstance(payload.get('score'), int):
        errors.append('score must be an integer')
    if not isinstance(payload.get('generated_at'), str) or 'T' not in payload.get('generated_at', ''):
        errors.append('generated_at must be an ISO-like timestamp')
    return errors


def _score_accuracy(issue_text: str, response_text: str) -> int:
    issue_terms = {word for word in re.findall(r'[a-z]{4,}', issue_text) if word not in {'with', 'from', 'that', 'this', 'were'}}
    overlap = len(issue_terms & set(re.findall(r'[a-z]{4,}', response_text)))
    if overlap >= 5:
        return 5
    if overlap >= 3:
        return 4
    if overlap >= 2:
        return 3
    if overlap == 1:
        return 2
    return 1


def _score_clarity(response_text: str) -> int:
    words = response_text.split()
    sentences = [item for item in re.split(r'[.!?]\s+', response_text) if item.strip()]
    if 70 <= len(words) <= 260 and len(sentences) >= 3:
        return 5
    if 45 <= len(words) <= 320 and len(sentences) >= 2:
        return 4
    if len(words) >= 25:
        return 3
    if len(words) >= 12:
        return 2
    return 1


def _score_structure(endpoint: str, response_text: str) -> int:
    bullet_count = len(re.findall(r'(^|\n)\s*(-|\d+\.)\s+', response_text))
    colon_sections = len(re.findall(r'(?m)^[A-Za-z][A-Za-z ]{2,30}:', response_text))
    if endpoint == '/recommend':
        return 5 if bullet_count >= 3 else 4 if bullet_count >= 2 else 3 if bullet_count == 1 else 2
    if endpoint == '/generate-report':
        sections = sum(1 for section in REPORT_SECTIONS if section in response_text)
        return 5 if sections >= 5 else 4 if sections >= 4 else 3 if sections >= 3 else 2
    return 5 if colon_sections >= 2 or bullet_count >= 2 else 4 if len(response_text.split()) >= 55 else 3


def _score_actionability(response_text: str) -> int:
    hits = sum(1 for term in ACTION_TERMS if term in response_text)
    if hits >= 5:
        return 5
    if hits >= 3:
        return 4
    if hits >= 2:
        return 3
    if hits == 1:
        return 2
    return 1


def _score_security_relevance(issue_text: str, response_text: str) -> int:
    combined_terms = set(re.findall(r'[a-z]{4,}', issue_text)) | set(re.findall(r'[a-z]{4,}', response_text))
    hits = len(SECURITY_TERMS & combined_terms)
    if hits >= 7:
        return 5
    if hits >= 5:
        return 4
    if hits >= 3:
        return 3
    if hits >= 1:
        return 2
    return 1


def _normalize(value: str) -> str:
    return re.sub(r'\s+', ' ', value.strip().lower())
