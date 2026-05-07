# Deployment Guide

## 1. Prepare Environment

Create `.env` from `.env.example` and set deployment values:

```sh
cp .env.example .env
python -m validation.env_validator
```

Required production-sensitive values:

- `GROQ_API_KEY`
- `JWT_SECRET`
- `POSTGRES_PASSWORD`

## 2. Build and Start

```sh
docker compose up --build -d
docker compose ps
```

Expected services:

- `tool-125-ai-service`
- Redis available on `localhost:6379`
- `tool-125-postgres`

All should report healthy.

## 3. Validate Runtime

```sh
python -m validation.startup_verification
python -m validation.container_health_check
python -m validation.e2e_test_runner
python -m validation.security_validation
```

## 4. Run Final Gate

```sh
python -m validation.final_system_check
```

Shell wrapper:

```sh
sh deployment_verify.sh
```

## 5. Observe Logs

```sh
docker compose logs --tail 120 ai-service
```

The service emits JSON logs with sensitive-data filtering.

## 6. Stop

```sh
docker compose down
```

Use `docker compose down -v` only for disposable environments because it deletes Redis and PostgreSQL volumes.

## Production Hardening

- Use a managed secret store.
- Terminate TLS at ingress.
- Restrict Redis and PostgreSQL to private networks.
- Add centralized log collection and alerting.
- Configure JWT role or scope authorization for multi-role deployments.
