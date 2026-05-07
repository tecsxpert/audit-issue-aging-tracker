# Tool-125 Security Report

## Project Overview

Tool-125 Audit Issue Aging Tracker is a Flask-based AI service that analyzes aged audit issues through JWT-protected API endpoints, Groq-hosted language models, Redis-backed rate limiting and AI caching, PostgreSQL service dependencies, and containerized deployment.

Protected endpoints:

- `POST /describe`
- `POST /recommend`
- `POST /generate-report`

Public endpoint:

- `GET /health`

## Security Architecture

The service applies layered controls before requests reach AI generation:

1. Docker isolates runtime dependencies and runs the app as a non-root user.
2. Flask middleware enforces JSON content type, body size limits, JWT authentication, PII rejection, SQL injection detection, prompt injection detection, and command injection detection.
3. Flask-Limiter applies request throttling using Redis storage.
4. Secure response headers are applied to all responses.
5. Structured JSON logging masks secrets and sensitive values before emission.
6. Groq API calls use retries, response validation, Redis caching, and structured error handling.

## Authentication Flow

Clients call protected endpoints with:

```text
Authorization: Bearer <JWT>
Content-Type: application/json
```

JWT validation checks:

- Signature using `JWT_SECRET`.
- Algorithm from `JWT_ALGORITHM`.
- Audience from `JWT_AUDIENCE`.
- Issuer from `JWT_ISSUER`.
- Expiration claim.

Validation utilities generate short-lived test tokens with `sub`, `aud`, `iss`, `iat`, and `exp` claims.

## Authorization Strategy

The current authorization model is endpoint-level access control. Any caller with a valid JWT issued for the configured audience and issuer may access the AI endpoints. Production role-based authorization can be layered onto the existing JWT payload by validating scopes or roles in `request.environ['jwt_payload']`.

## AI Security Controls

- Prompt injection phrases are rejected before prompt construction.
- PII and secrets in request payloads are blocked.
- SQL and command injection patterns are rejected.
- AI output is checked for non-empty structured response behavior.
- Prompt quality scoring triggers a controlled prompt optimization retry.
- Groq failures return structured JSON instead of stack traces.
- Redis AI caching reduces repeated third-party API exposure.

## API Protection

- JWT required on all AI endpoints.
- Missing and malformed tokens return structured 401 errors.
- Non-JSON requests are rejected.
- Large payloads are rejected with HTTP 413.
- Error responses use a consistent `success=false` JSON format.
- Rate limits are enforced through Redis-backed Flask-Limiter storage.

## Docker and Container Security

- Python 3.11 slim base image.
- Gunicorn production server.
- Non-root `appuser`.
- Container health check on `/health`.
- Redis and PostgreSQL isolated on a Compose network.
- Secrets are injected through environment variables and `.env`, not source code.

## Redis Security

Redis is used for rate limiting and AI response caching. It is isolated inside the Compose network for service communication. Production deployments should use private networking, authentication, TLS where supported, backups for persistence, and least-privilege network rules.

## Environment Variable Protection

Required sensitive values:

- `GROQ_API_KEY`
- `JWT_SECRET`
- `POSTGRES_PASSWORD`

Security expectations:

- `.env` remains uncommitted.
- Production secrets live in a secret manager.
- `JWT_SECRET` is at least 32 characters.
- API keys are rotated after exposure or team changes.

## Validation Commands

```sh
python -m validation.security_validation
python -m validation.e2e_test_runner
python -m validation.automated_validation
pytest
```

## Security Sign-Off

Status: Ready for capstone demo after validation scripts pass in the deployment environment.

Owner: AI Developer 2

Approval records are maintained in `docs/team_security_signoff.md` and `docs/release_security_approval.md`.
