# Sanitization Rules

## Protected Routes
Rules apply to:

- `POST /describe`
- `POST /recommend`
- `POST /generate-report`

## Required Request Shape
```json
{
  "issue": "Non-empty audit issue text"
}
```

## Rejection Rules
| Rule | Response |
|---|---|
| Missing JSON content type | HTTP 400 |
| Malformed JSON | HTTP 400 |
| Non-object payload | HTTP 400 |
| Empty or non-string `issue` | HTTP 400 |
| Payload exceeds `MAX_CONTENT_LENGTH` | HTTP 413 |
| String field over 12,000 chars | HTTP 400 |
| JSON nesting depth over 8 | HTTP 400 |
| JSON array over 100 items | HTTP 400 |
| Script tags | HTTP 400 |
| Prompt injection phrases | HTTP 400 |
| SQL injection markers | HTTP 400 |
| Command injection markers | HTTP 400 |
| PII or credentials | HTTP 400 |

## Transform Rules
Regular HTML tags are stripped from string fields. Leading and trailing whitespace is removed.

## Safe Logging
Before a rejected payload is logged, PII and secret-like values are masked with `[REDACTED]`.
