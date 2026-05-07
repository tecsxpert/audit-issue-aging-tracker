# Tool-125 Audit Issue Aging Tracker AI Service

Production-oriented Flask AI service for analyzing aged audit issues, generating remediation recommendations, and producing audit-ready reports.

## Tech Stack

- Python 3.11
- Flask 3.x
- Groq API with `llama-3.3-70b-versatile`
- Redis 7 for rate limiting and AI cache
- PostgreSQL service dependency
- Docker and Docker Compose
- pytest
- flask-limiter

## API Endpoints

| Endpoint | Method | Auth | Purpose |
| --- | --- | --- | --- |
| `/health` | GET | No | Runtime health and dependency status |
| `/describe` | POST | JWT | Explain an aged audit issue |
| `/recommend` | POST | JWT | Generate remediation recommendations |
| `/generate-report` | POST | JWT | Generate an audit-ready report |

See [API_REFERENCE.md](docs/API_REFERENCE.md) for request and response examples.

## Environment Setup

Create `.env` from `.env.example`:

```sh
cp .env.example .env
```

Required values:

- `GROQ_API_KEY`
- `GROQ_MODEL=llama-3.3-70b-versatile`
- `JWT_SECRET`
- `JWT_ALGORITHM`
- `JWT_AUDIENCE`
- `JWT_ISSUER`
- `REDIS_URL`

Validate configuration:

```sh
python -m validation.env_validator
```

## Local Docker Run

```sh
docker compose up --build -d
docker compose ps
```

Health check:

```sh
curl http://127.0.0.1:8000/health
```

## Validation

Run unit tests:

```sh
python -m pytest
```

Run security validation:

```sh
python -m validation.security_validation
```

Run authenticated E2E validation:

```sh
python -m validation.e2e_test_runner
```

Run final system gate:

```sh
python -m validation.final_system_check
```

## Security

Security controls include JWT authentication, secure headers, rate limiting, prompt injection rejection, SQL injection rejection, XSS filtering, PII detection, structured log redaction, non-root Docker runtime, and structured fallback responses.

See [SECURITY.md](SECURITY.md) and [FINAL_SECURITY_CHECKLIST.md](docs/FINAL_SECURITY_CHECKLIST.md).

## Demo

Demo documentation:

- [DEMO_DAY_GUIDE.md](docs/demo-day/DEMO_DAY_GUIDE.md)
- [AI_DEMO_SCRIPT.md](docs/demo-day/AI_DEMO_SCRIPT.md)
- [QUICK_REFERENCE.md](docs/demo-day/QUICK_REFERENCE.md)
- [DEMO_GUIDE.md](docs/DEMO_GUIDE.md)
- [DEMO_FLOW.md](docs/DEMO_FLOW.md)
- [demo_talking_points.md](docs/demo_talking_points.md)
- [demo_troubleshooting.md](docs/demo_troubleshooting.md)

## Troubleshooting

If Docker commands fail on Windows, ensure Docker Desktop is running and the shell has access to the Docker daemon.

If AI endpoints return 401, regenerate or correct the JWT.

If AI endpoints return 502, verify `GROQ_API_KEY`, `GROQ_MODEL`, Groq quota, and network egress.
