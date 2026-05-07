# Final Review Checklist

## Environment

- [ ] `.env` exists and was created from `.env.example`.
- [ ] `GROQ_API_KEY` is configured.
- [ ] `GROQ_MODEL` is `llama-3.3-70b-versatile`.
- [ ] `JWT_SECRET` is set and is at least 32 characters.
- [ ] Redis and PostgreSQL settings match Docker Compose.

## Docker

- [ ] `docker compose up --build -d` completes.
- [ ] `docker compose ps` shows AI service, Redis, and PostgreSQL running.
- [ ] AI service health check is healthy.
- [ ] Redis health check is healthy.
- [ ] PostgreSQL health check is healthy.

## Endpoints

- [ ] `GET /health` returns `success: true` and `status: ok`.
- [ ] `POST /describe` rejects missing JWT.
- [ ] `POST /recommend` rejects missing JWT.
- [ ] `POST /generate-report` rejects missing JWT.
- [ ] Authenticated AI endpoint call returns structured JSON when Groq is configured.

## Security

- [ ] Prompt injection payload is rejected.
- [ ] SQL injection payload is rejected.
- [ ] PII payload is rejected.
- [ ] Script tag payload is rejected or sanitized.
- [ ] Secure headers are present on responses.
- [ ] Rate limiting is configured.

## Tests and Handoff

- [ ] `python -m pytest` passes.
- [ ] `python -m validation.reviewer_validation` passes or reports only documented environment limitations.
- [ ] README links to Day 15 docs.
- [ ] Reviewer guide, deployment guide, security notes, and AI summary card are complete.
