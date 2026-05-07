# Deployment Cheatsheet

## Start

```sh
docker compose up --build -d
```

## Stop

```sh
docker compose down
```

## Logs

```sh
docker compose logs -f ai-service
docker compose logs redis
docker compose logs postgres
```

## Health

```sh
curl http://127.0.0.1:8000/health
```

## Redis Ping

```sh
docker compose exec redis redis-cli ping
```

## Tests

```sh
python -m pytest
python -m validation.reviewer_validation
python -m validation.security_validation
```

## Required Environment

```env
GROQ_API_KEY=<required>
GROQ_MODEL=llama-3.3-70b-versatile
JWT_AUTH_ENABLED=true
JWT_SECRET=<required strong secret>
JWT_ALGORITHM=HS256
JWT_AUDIENCE=tool-125
JWT_ISSUER=tool-125-auth
REDIS_URL=redis://redis:6379/0
RATE_LIMIT_STORAGE_URI=redis://redis:6379/1
```
