# Deployment Validation

## Docker Compose Validation

```sh
docker compose config
docker compose up --build -d
docker compose ps
```

Expected services:

- `tool-125-ai-service`: healthy
- `tool-125-redis`: healthy
- `tool-125-postgres`: healthy

## Runtime Validation

```sh
python -m validation.container_health_check
python -m validation.startup_verification
python -m validation.compose_validation
```

## Network Validation

- AI service reaches Redis using `redis://redis:6379`.
- AI service reaches PostgreSQL over Compose network.
- Host reaches AI service on `http://127.0.0.1:8000`.

## Evidence

Attach `docker compose ps`, health endpoint output, and validation logs to release approval.
