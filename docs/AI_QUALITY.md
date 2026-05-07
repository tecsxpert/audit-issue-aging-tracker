# AI Quality Review Process

## Objective
Day 10 validates whether Tool-125 AI outputs are accurate, clear, structured, actionable, and security-relevant across the three AI endpoints.

Target quality threshold:

```text
Average score >= 4.0 / 5.0
```

Verified result:

```text
Overall average: 4.93 / 5.0
Cases evaluated: 30
Target met: yes
```

## Evaluation Architecture
| Component | Purpose |
|---|---|
| `quality/scoring_utils.py` | Scores responses across five categories |
| `quality/evaluation_engine.py` | Loads cases, invokes responders, validates schema, exports results |
| `quality/ai_quality_review.py` | CLI runner for offline or endpoint-backed evaluation |
| `quality/data/sample_inputs.json` | Thirty realistic enterprise audit findings |
| `quality/data/endpoint_test_cases.json` | Ten mapped cases per AI endpoint |
| `quality/results/quality_dashboard_data.json` | Machine-readable dashboard output |
| `docs/ai_quality_report.md` | Generated markdown quality report |

## Scoring Methodology
Each response is scored from 1 to 5 for:

| Category | What It Measures |
|---|---|
| Accuracy | Response remains grounded in the issue and repeats relevant issue concepts |
| Clarity | Clear language, adequate length, and readable sentence structure |
| Structure | Endpoint-specific formatting and required sections |
| Actionability | Concrete remediation, validation, ownership, or monitoring steps |
| Security Relevance | Audit, risk, compliance, control, security, and verification relevance |

The category average becomes the case score. Endpoint and overall averages are computed from case averages.

## Prompt Tuning Strategy
Prompt version `v2.0-quality-reviewed` improves:

- fixed endpoint-specific output structures
- grounded-only instructions to reduce hallucination
- explicit security/compliance audience
- remediation and verification requirements
- evidence retention for report outputs

## Running Evaluation
Offline deterministic evaluation:

```bash
python quality/ai_quality_review.py
```

Evaluation against a running service:

```bash
python quality/ai_quality_review.py --base-url http://127.0.0.1:8000 --token <JWT>
```

## Quality Gate
The release quality gate passes when:

- overall average is at least 4.0
- each endpoint has 10 evaluated cases
- schema error count is 0
- fallback rate is acceptable for the environment
- weak categories are reviewed and prompt updates are documented
