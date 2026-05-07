# Security Revalidation

## Controls Revalidated

- JWT protection for all AI endpoints.
- Rate limiting through `flask-limiter`.
- Redis-backed limiter storage in Compose.
- Prompt injection blocking.
- SQL injection blocking.
- PII rejection and secure logging filters.
- Secure response headers.
- Maximum request body size.
- Non-root container runtime.

## Commands

```sh
pytest tests/test_security.py tests/test_security_jwt.py tests/test_rate_limit.py
python -m validation.endpoint_validation
python security/stress_test_runner.py
```

## Required Evidence

- Missing or invalid JWT returns HTTP 401.
- Malformed or hostile payloads return HTTP 400.
- Excessive request volume returns HTTP 429 instead of service failure.
- Logs do not expose JWTs, API keys, or PII.
- Dockerfile contains `USER appuser`.
