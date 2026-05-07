# Troubleshooting

## Container Does Not Start

Run:

```sh
docker compose logs ai-service
python -m validation.env_validator
```

Common causes:

- Missing `GROQ_API_KEY`.
- Weak or missing `JWT_SECRET`.
- Invalid `.env` syntax.
- Port `8000` already in use.

## Health Check Fails

Run:

```sh
curl http://127.0.0.1:8000/health
docker compose ps
```

Check that Redis and PostgreSQL are healthy before investigating the app container.

## AI Endpoints Return 401

The endpoint requires a Bearer JWT with matching `aud`, `iss`, and `exp` claims. Use the validation scripts to generate a compatible token automatically.

## AI Endpoints Return 502

Groq integration failed. Verify:

- `GROQ_API_KEY` is valid.
- `GROQ_API_BASE_URL=https://api.groq.com/openai/v1`.
- Network egress is allowed from the container.
- The selected `GROQ_MODEL` is enabled for the key.

## Redis Errors

Run:

```sh
docker compose exec redis redis-cli ping
docker compose exec redis redis-cli info persistence
```

The expected ping response is `PONG`.

## Rate Limit Errors

HTTP 429 means rate limiting is working. Increase `RATE_LIMIT` only after validating expected traffic and abuse protection requirements.
