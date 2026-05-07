# Deployment Security Checklist

## Environment

- `.env` exists only on deployment hosts.
- `GROQ_API_KEY` is configured and valid.
- `GROQ_MODEL=llama-3.3-70b-versatile`.
- `JWT_SECRET` is at least 32 characters.
- `JWT_AUDIENCE` and `JWT_ISSUER` match token issuer configuration.
- `POSTGRES_PASSWORD` is not a default in production.

## Runtime

- Docker containers are healthy.
- AI service runs as non-root `appuser`.
- Redis and PostgreSQL are not publicly exposed in production.
- Gunicorn is used instead of Flask development server.
- Health check endpoint returns HTTP 200.

## API Security

- `/describe`, `/recommend`, and `/generate-report` reject missing tokens.
- Malformed JWTs are rejected.
- Valid JWTs succeed.
- Injection and PII payloads are rejected.
- Rate limiting is enabled.

## Evidence

Attach output from:

```sh
docker compose ps
python -m validation.security_validation
python -m validation.e2e_test_runner
```
