# Demo Guide

## Goal

Show that Tool-125 can analyze aged audit issues through secure, containerized AI endpoints.

## Pre-Demo Setup

```sh
docker compose up --build -d
python -m validation.e2e_test_runner
python -m validation.security_validation
```

## Demo Endpoints

1. `GET /health`
2. `POST /describe`
3. `POST /recommend`
4. `POST /generate-report`

## Expected Outputs

- Health returns dependency status.
- Describe returns a plain-language issue analysis.
- Recommend returns prioritized remediation bullets.
- Generate report returns audit-ready report sections.

## Security Demo

Show:

- Missing JWT rejected.
- Malformed JWT rejected.
- Prompt injection rejected.
- SQL injection rejected.
- PII payload rejected.

## Fallback Demo

Use invalid Groq credentials in a disposable environment to show structured HTTP 502 responses without stack traces.
