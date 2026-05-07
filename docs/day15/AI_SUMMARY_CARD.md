# Tool-125 AI Summary Card

**Project:** Tool-125 - Audit Issue Aging Tracker  
**AI Service:** Flask-based audit issue analysis service  
**Model:** Groq `llama-3.3-70b-versatile`  
**Owner:** AI Developer 2  
**Demo Status:** Ready for reviewer walkthrough

## AI Purpose

Tool-125 helps audit teams understand aged audit issues, identify practical remediation actions, and generate concise audit-ready reports. The AI layer turns issue descriptions into structured risk, aging, root-cause, and action guidance.

## Endpoint Summary

| Endpoint | Method | Purpose | Protection |
| --- | --- | --- | --- |
| `/health` | GET | Confirms service, Redis, rate limiter, and Groq configuration status | Public |
| `/describe` | POST | Explains an aged audit issue in plain audit language | JWT, validation, rate limit |
| `/recommend` | POST | Generates remediation recommendations and next actions | JWT, validation, rate limit |
| `/generate-report` | POST | Produces a report-style AI summary for review packets | JWT, validation, rate limit |

## Architecture Snapshot

- **Flask 3.x:** Lightweight API surface with blueprints for AI and health routes.
- **Groq API:** Sends optimized prompts to `llama-3.3-70b-versatile` with retry and response parsing.
- **Redis 7:** Supports AI response caching and rate-limit storage.
- **PostgreSQL:** Included as the application data dependency for the broader tracker platform.
- **Docker Compose:** Runs AI service, Redis, and PostgreSQL as repeatable local services.

## Security Protections

- JWT bearer-token protection on AI endpoints.
- Prompt injection, command injection, script tag, and dangerous JSON key rejection.
- SQL injection pattern blocking before AI processing.
- PII detection and rejection for sensitive payloads.
- Flask-Limiter rate limiting backed by Redis.
- Secure HTTP headers including CSP, HSTS, frame blocking, and no-store cache policy.
- Non-root Docker runtime and isolated Compose network.

## GitHub Repository References

- Main implementation: `ai-service/app.py`
- AI routes: `ai-service/routes/ai_routes.py`
- Groq client: `ai-service/services/groq_client.py`
- Security middleware: `ai-service/middleware/security.py`
- Sanitization middleware: `ai-service/middleware/sanitization.py`
- Redis client: `ai-service/cache/redis_client.py`
- Tests: `ai-service/tests/`
- Day 15 docs: `ai-service/docs/day15/`

## Demo Verification

```sh
docker compose up --build -d
python -m validation.reviewer_validation
```

Expected result: `/health` returns `status: ok`, protected endpoints reject unauthenticated requests, Redis responds to ping, and Docker services report healthy.
