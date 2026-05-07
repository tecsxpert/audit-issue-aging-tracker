# Deployment Guide

## 1. Prepare Environment

Create `.env` from `.env.example` and set production values:

```sh
cp .env.example .env
python -m validation.env_validator
```

## 2. Build and Start

```sh
docker compose up --build -d
```

## 3. Verify

```sh
python -m validation.verify_all_services
```

If running the shell workflow:

```sh
sh validation/verify_all_services.sh
```

## 4. Run Full Gate

```sh
python -m validation.automated_validation
pytest
```

## 5. Observe

```sh
docker compose ps
docker compose logs --tail 120 ai-service
```

## 6. Stop

```sh
docker compose down
```

Use `docker compose down -v` only for disposable local environments because it deletes Redis and PostgreSQL volumes.
