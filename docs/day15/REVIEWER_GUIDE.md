# Reviewer Guide

## How to Run

```sh
cd ai-service
cp .env.example .env
docker compose up --build -d
curl http://127.0.0.1:8000/health
python -m validation.reviewer_validation
```

## AI Endpoints

| Endpoint | Purpose |
| --- | --- |
| `/health` | Public health and dependency status |
| `/describe` | AI explanation for an aged audit issue |
| `/recommend` | AI remediation recommendation |
| `/generate-report` | AI report-style output |

## Security Validation

Security was validated through automated tests and middleware behavior checks:

- JWT-required behavior for protected endpoints.
- Prompt injection and command injection rejection.
- SQL injection rejection.
- PII detection and rejection.
- Rate limiting configuration.
- Secure response headers.
- Docker health checks and isolated dependency startup.

## Test Coverage Summary

The test suite includes endpoint tests for `/health`, `/describe`, `/recommend`, and `/generate-report`; Groq client tests; JWT/security middleware tests; rate limit tests; prompt evaluator tests; error handling tests; and Day 9/Day 10 quality/security utility tests.

Run:

```sh
python -m pytest
```

## Docker Verification Summary

Docker Compose starts the AI service, Redis, and PostgreSQL. Redis and PostgreSQL include health checks, and the AI service health check calls `/health` from inside the container.

## Known Limitations

- Live AI generation requires a valid Groq API key and network access.
- PostgreSQL is provisioned as a dependency but the current AI endpoints do not directly persist issue data.
- JWT generation is handled by validation helpers for local review; production should integrate with the application identity provider.
- ChromaDB and sentence-transformers are part of the broader AI stack direction, but the Day 15 endpoints primarily use prompt-based Groq generation and Redis caching.
