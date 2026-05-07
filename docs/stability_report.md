# Stability Report

## Coverage

Day 11 stability validation covers repeated requests, malformed payloads, rate limit behavior, restart behavior, Redis persistence, and graceful API failure responses.

## Stress Test

```sh
python security/stress_test_runner.py
```

Default profile:

- 30 total requests.
- 5 concurrent workers.
- Accepted HTTP statuses: `200` and `429`.

## Malformed Payload Validation

Covered by:

```sh
python -m validation.endpoint_validation
```

Validated cases:

- Empty `issue`.
- Missing JWT.
- Invalid input shape.
- Security middleware rejections.

## Restart Validation

Covered by:

```sh
python -m validation.compose_validation
```

The service must become healthy again after `docker compose restart ai-service`.
