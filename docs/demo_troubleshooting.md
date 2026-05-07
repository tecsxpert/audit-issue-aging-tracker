# Demo Troubleshooting

## Docker Does Not Start

```sh
docker compose ps
docker compose logs --tail 120 ai-service
```

Confirm Docker Desktop is running and the shell has Docker daemon access.

## Health Fails

Check Redis and PostgreSQL health:

```sh
docker compose ps
python -m validation.container_health_check
```

## AI Endpoint Returns 401

The JWT is missing, expired, malformed, or signed with a different secret. Run:

```sh
python -m validation.endpoint_validation
```

## AI Endpoint Returns 502

Groq failed. Check:

- `GROQ_API_KEY`
- `GROQ_MODEL`
- network egress
- Groq quota

## Rate Limit During Demo

Wait for the limit window to reset or temporarily increase `RATE_LIMIT` in `.env` for a controlled local demo.
