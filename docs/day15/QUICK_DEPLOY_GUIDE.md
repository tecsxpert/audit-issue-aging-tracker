# Quick Deploy Guide

## Prerequisites

- Docker Desktop or Docker Engine
- Python 3.11 for local validation scripts
- `.env` created from `.env.example`
- Valid `GROQ_API_KEY`
- Strong `JWT_SECRET` with at least 32 characters

## 1. Configure Environment

```sh
cp .env.example .env
```

Set these values:

```env
GROQ_API_KEY=<your-groq-key>
JWT_SECRET=<32-plus-character-secret>
GROQ_MODEL=llama-3.3-70b-versatile
```

## 2. Start Services

```sh
docker compose up --build -d
```

## 3. Confirm Containers

```sh
docker compose ps
```

Expected services:

- `tool-125-ai-service`
- Redis service on `localhost:6379`
- `tool-125-postgres`

## 4. Verify Health

```sh
curl http://127.0.0.1:8000/health
```

Expected result:

```json
{
  "success": true,
  "status": "ok"
}
```

## 5. Run Reviewer Validation

```sh
python -m validation.reviewer_validation
```

## 6. Troubleshooting

| Symptom | Check |
| --- | --- |
| `/health` fails | Confirm Docker is running and port `8000` is free. |
| Redis unhealthy | Run `docker compose logs redis` and confirm `redis-cli ping` returns `PONG`. |
| AI endpoint returns 401 | Generate a valid JWT with matching secret, issuer, audience, and expiration. |
| AI endpoint returns 502 | Confirm `GROQ_API_KEY`, model name, network access, and Groq quota. |
| Rate limit errors | Wait for the limit window or adjust `RATE_LIMIT` for local testing. |
