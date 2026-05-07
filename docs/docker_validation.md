# Docker Validation

## Scope

Day 11 validates that the AI service starts cleanly as a non-root container, loads environment variables, exposes health checks, connects to Redis, can reach PostgreSQL over the Compose network, and can call Groq through the configured API base URL.

## Validation Commands

```sh
docker compose config
docker compose up --build -d
python -m validation.startup_verification
python -m validation.container_health_check
python -m validation.e2e_test_runner
```

## Expected Results

- `ai-service` reports healthy through `GET /health`.
- Redis responds to `PING`.
- PostgreSQL accepts TCP connections on the internal service name `postgres`.
- `/describe`, `/recommend`, and `/generate-report` return HTTP 200 with valid JSON when called with a valid JWT.
- Error paths return structured JSON and appropriate HTTP codes.

## Dockerfile Checks

- Python 3.11 slim base image.
- Dependencies installed from `requirements.txt`.
- Application runs with `gunicorn`.
- Container uses `appuser` instead of root.
- Docker health check calls `GET /health`.
- Port `8000` is exposed.

## Environment Variables

Required:

- `GROQ_API_KEY`
- `GROQ_API_BASE_URL`
- `GROQ_MODEL`
- `JWT_SECRET`
- `JWT_ALGORITHM`
- `JWT_AUDIENCE`
- `JWT_ISSUER`
- `REDIS_URL`

Run `python -m validation.env_validator` before deployment.
