# Attack Surface Analysis

## Public Surface

- `GET /health`: unauthenticated health endpoint.
- `POST /describe`: JWT-protected AI endpoint.
- `POST /recommend`: JWT-protected AI endpoint.
- `POST /generate-report`: JWT-protected AI endpoint.

## Internal Surface

- Redis for rate limits and AI cache.
- PostgreSQL service dependency.
- Groq API egress.
- Docker Compose network.
- Environment variables.
- Application logs.

## Primary Attack Vectors

| Surface | Vector | Control |
| --- | --- | --- |
| AI endpoints | Missing token | JWT middleware |
| AI endpoints | Malformed token | JWT validation errors |
| AI endpoints | Brute force | Flask-Limiter |
| AI endpoints | Prompt injection | Sanitization regex checks |
| AI endpoints | SQL injection text | SQL safety checks |
| AI endpoints | Script tags | XSS rejection |
| AI endpoints | Oversized body | `MAX_CONTENT_LENGTH` |
| Logs | Secrets in request data | Sensitive data filter |
| Redis | Network access | Compose isolation |
| Container | Privilege escalation | Non-root app user |

## Hardening Priority

1. Enforce TLS and WAF/rate limiting at ingress.
2. Add JWT role or scope authorization.
3. Use managed Redis with auth and private networking.
4. Add SIEM alerts for repeated 401, 400, and 429 responses.
