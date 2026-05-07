# Docker Compose Test

## Services

- `ai-service`: Flask/Gunicorn API container.
- `redis`: Redis 7 with append-only persistence.
- `postgres`: PostgreSQL 16 for capstone data persistence integration.

## Test Flow

```sh
python -m validation.compose_validation
```

The script performs:

1. Compose configuration rendering.
2. Image build and detached startup.
3. HTTP readiness wait.
4. Service status inspection.
5. AI service restart verification.
6. Redis persistence check across restart.
7. Final health confirmation.

## Manual Verification

```sh
docker compose ps
docker compose logs --tail 120 ai-service
curl http://127.0.0.1:8000/health
```

## Pass Criteria

- All containers are `running` or `healthy`.
- `GET /health` returns HTTP 200.
- Redis keeps `day11:persistence=ok` after a Redis restart.
- API remains available after `docker compose restart ai-service`.
