# API Validation Summary

## Endpoint Coverage

| Endpoint | Method | Auth | Expected Success |
| --- | --- | --- | --- |
| `/health` | GET | No | HTTP 200 |
| `/describe` | POST | JWT | HTTP 200 |
| `/recommend` | POST | JWT | HTTP 200 |
| `/generate-report` | POST | JWT | HTTP 200 |

## Protected Endpoint Validation

Each protected endpoint is validated for:

- Valid JWT succeeds.
- Missing JWT returns 401 or 403.
- Malformed JWT returns 401 or 403.
- Empty issue returns HTTP 400.
- Prompt injection returns HTTP 400.
- SQL injection returns HTTP 400.
- PII payload returns HTTP 400.

## Example Request

```sh
curl -X POST http://127.0.0.1:8000/describe \
  -H "Authorization: Bearer <jwt>" \
  -H "Content-Type: application/json" \
  -d "{\"issue\":\"Audit issue AI-125 has been open for 96 days.\"}"
```
