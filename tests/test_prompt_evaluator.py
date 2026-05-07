from __future__ import annotations
from services.prompt_manager import PromptOptimizer


def test_prompt_evaluator_scores_realistic_audit_issues() -> None:
    evaluator = PromptOptimizer()
    sample_issues = [
        'Unvalidated file upload allows arbitrary code execution through secondary processing.',
        'Expired credentials remain active in the credentials cache after user deprovisioning.',
        'Audit logs are stored without encryption, exposing sensitive activity metadata.',
        'Cross-site scripting vulnerability in the admin feedback form input.',
        'SQL query parameters are concatenated in transaction endpoints.',
        'Insufficient CSRF protection on state-changing API operations.',
        'Third-party dependency uses vulnerable cryptographic algorithm.',
        'Missing rate limiting on authentication and password reset endpoints.',
        'Inconsistent access control for nested resource object ownership checks.',
        'Sensitive PII is logged in plaintext in backend exception pages.',
    ]

    scores = [evaluator.score(issue) for issue in sample_issues]
    assert all(isinstance(score, int) for score in scores)
    assert all(1 <= score <= 10 for score in scores)


def test_optimize_prompt_improves_instruction() -> None:
    evaluator = PromptOptimizer()
    prompt = 'Describe the issue.'
    improved = evaluator.optimize(prompt, 'Data exposure', context='analysis')
    assert 'Write with clarity' in improved
    assert 'actionable' in improved
