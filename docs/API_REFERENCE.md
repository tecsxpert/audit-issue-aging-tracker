# API Reference

Base URL:

```text
http://127.0.0.1:8000
```

## Authentication

Protected endpoints require:

```text
Authorization: Bearer <jwt>
Content-Type: application/json
```

The JWT must include valid `aud`, `iss`, and `exp` claims.

## GET /health

Authentication: Not required

Response:

```json
{
  "success": true,
  "status": "ok",
  "services": ["groq", "prompt-sanitizer", "rate-limiter", "redis-cache"],
  "dependencies": {
    "groq": "configured",
    "redis": "ok",
    "rate_limiter": "configured"
  }
}
```

## POST /describe

Authentication: Required

Request:

```json
{
  "issue": "Audit issue AI-125 has been open for 96 days."
}
```

Success response includes:

- `success`
- `status`
- `endpoint`
- `issue`
- `score`
- `response`
- `generated_at`

## POST /recommend

Authentication: Required

Returns prioritized remediation recommendations.

## POST /generate-report

Authentication: Required

Returns audit-ready report sections.

## Error Format

```json
{
  "success": false,
  "status": "error",
  "message": "Error description.",
  "generated_at": "2026-05-07T00:00:00+00:00"
}
```
