# AI Quick Reference

## What This AI Service Does

The Tool-125 AI service converts an audit issue description into three reviewer-ready outputs:

- `/describe`: explains the issue, risk, aging concern, and likely root cause.
- `/recommend`: proposes remediation actions, owners, priority, and follow-up steps.
- `/generate-report`: creates a concise report section for audit documentation.

## Request Shape

```json
{
  "issue": "User access reviews for the finance system are overdue by 90 days."
}
```

Protected AI endpoints require:

```http
Authorization: Bearer <jwt>
Content-Type: application/json
```

## Response Shape

```json
{
  "success": true,
  "status": "success",
  "endpoint": "/describe",
  "issue": "User access reviews are overdue...",
  "score": 8,
  "response": "AI-generated audit guidance...",
  "generated_at": "2026-05-07T00:00:00+00:00"
}
```

## AI Controls

| Control | Purpose |
| --- | --- |
| Prompt templates | Keep responses focused on audit issue aging |
| Prompt optimization | Re-prompts if generated response quality score is low |
| Redis cache | Avoids repeated Groq calls for identical prompts |
| Fallback errors | Returns structured 4xx/5xx responses without crashing |
| Security middleware | Blocks unsafe, sensitive, or unauthenticated requests |

## Reviewer Commands

```sh
docker compose up --build -d
curl http://127.0.0.1:8000/health
python -m validation.reviewer_validation
python -m pytest
```
