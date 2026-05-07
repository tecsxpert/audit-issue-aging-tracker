# Demo Troubleshooting Guide

## Groq API Failure

Symptoms:

- AI endpoints return `502`.
- Response message begins with `Groq API failed`.

Recovery:

1. Confirm `GROQ_API_KEY` is present in `.env`.
2. Confirm `GROQ_MODEL=llama-3.3-70b-versatile`.
3. Check network access and provider quota.
4. Retry with a shorter demo input.
5. Switch to `expected_outputs.json` for the same input if the provider remains unavailable.

Demo explanation:

The AI provider is external, so the service returns a controlled error and the backup workflow preserves the demo.

## Docker Failure

Symptoms:

- `docker compose up --build -d` fails.
- Docker daemon is not running or inaccessible.

Recovery:

1. Start Docker Desktop.
2. Wait until Docker reports that the engine is running.
3. Run `docker compose config` to validate Compose syntax.
4. Run `docker compose up --build -d`.
5. Run `docker compose ps`.
6. Open `offline_demo_assets.md` if Docker cannot be restored.

## Redis Unavailable

Symptoms:

- `/health` shows Redis as `unhealthy`.
- Logs show Redis cache read or write warnings.

Recovery:

1. Run `docker compose restart redis`.
2. Confirm `docker compose ps`.
3. Confirm `redis-cli ping` inside the Redis container if available.
4. Continue the demo if Groq responses still work.

Demo explanation:

Redis improves cache speed and shared rate limiting. The service can still generate live AI responses when Redis cache operations fail.

## Invalid JWT

Symptoms:

- Protected endpoints return `401`.
- Message references missing, expired, malformed, or invalid token.

Recovery:

1. Regenerate a demo JWT using the configured `JWT_SECRET`, `JWT_AUDIENCE`, and `JWT_ISSUER`.
2. Confirm the request uses `Authorization: Bearer <token>`.
3. Confirm `Content-Type: application/json`.

## Endpoint Timeout

Symptoms:

- Endpoint returns `504`.
- Demo request takes longer than configured timeout.

Recovery:

1. Retry once with the same input.
2. Use a shorter audit issue input.
3. Confirm `REQUEST_TIMEOUT_SECONDS` is not set too low.
4. Switch to offline expected outputs if provider latency continues.

## Container Restart

Symptoms:

- AI service container exits or becomes unhealthy.

Recovery:

1. Run `docker compose logs ai-service --tail 80`.
2. Confirm required environment variables.
3. Run `docker compose restart ai-service`.
4. Recheck `GET /health`.

## Fallback Mode Activation

Use fallback mode when:

- Groq is unavailable.
- Docker cannot start before presentation time.
- Network access is blocked.
- Token generation cannot be repaired quickly.

Fallback steps:

1. Show `demo_inputs.json`.
2. Show matching examples in `expected_outputs.json`.
3. Walk through `demo_sequence.md`.
4. Explain the structured API response format and security behavior.
5. Close with `backup_demo_plan.md`.

