# Production Checklist

## Required Before Release

- `.env` exists and is not committed.
- `GROQ_API_KEY` is configured with a valid production key.
- `JWT_SECRET` is at least 32 characters and stored in a secret manager.
- `JWT_AUDIENCE` and `JWT_ISSUER` match the calling backend.
- `REDIS_URL` points to a persistent Redis instance.
- Rate limits match production traffic expectations.
- `docker compose config` passes.
- `python -m validation.automated_validation` passes.
- `pytest` passes.

## Runtime

- Run with Gunicorn.
- Run as non-root user.
- Enable container health checks.
- Keep Redis and PostgreSQL on private networks.
- Export structured JSON logs to the platform log sink.
- Monitor p95 AI latency and Groq failure rate.

## Rollback

- Keep the previous image tag available.
- Use `docker compose down` only after logs and reports are captured.
- Restore Redis/PostgreSQL volumes from backups when validating data-sensitive incidents.
