# Runtime Validation

## Runtime Checks

- Gunicorn starts with two workers and four threads.
- Application logging initializes as JSON.
- `/health` returns dependency status.
- JWT-protected endpoints reject missing tokens.
- Redis responds to ping.
- PostgreSQL accepts TCP connections.
- Groq model is configured as `llama-3.3-70b-versatile`.

## Commands

```sh
docker compose logs --tail 120 ai-service
python -m validation.startup_verification
python -m validation.container_health_check
python -m validation.security_validation
```

## Expected Result

All commands exit with status code 0 and log structured `*_passed` events.
