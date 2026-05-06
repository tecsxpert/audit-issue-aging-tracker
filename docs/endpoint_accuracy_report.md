# Endpoint Accuracy Report

## Summary
| Endpoint | Cases | Average Score | Target Met |
|---|---:|---:|---|
| `/describe` | 10 | 4.8 | Yes |
| `/recommend` | 10 | 5.0 | Yes |
| `/generate-report` | 10 | 5.0 | Yes |
| Overall | 30 | 4.93 | Yes |

## Findings
`/describe` performs strongly on accuracy, clarity, actionability, and security relevance. Structure is intentionally concise and section-based.

`/recommend` meets the target after prompt tuning. The optimized prompt requires five bullets with priority, owner, action, and validation fields.

`/generate-report` is the strongest endpoint because the optimized prompt requires a complete stakeholder report with root cause, risk level, remediation, verification, and retained evidence.

## Accuracy Controls
The evaluator checks that responses:

- reference concepts from the original issue
- avoid unsupported facts
- include audit/security vocabulary
- provide concrete next steps
- match endpoint-specific output structure

## Conclusion
All three endpoints meet the Day 10 target average of at least 4.0/5.
