# Tool-125 - Audit Issue Aging Tracker AI Service

Production-oriented Flask AI service for analyzing aged audit issues, generating remediation recommendations, and producing audit-ready report text for the Tool-125 capstone project.

## What It Provides

- AI explanation of aged audit issues.
- AI remediation recommendations.
- AI report generation for reviewer packets.
- JWT-protected AI endpoints.
- Prompt, SQL injection, command injection, and PII defenses.
- Redis-backed AI response caching and rate limiting.
- Docker Compose startup for AI service, Redis, and PostgreSQL.

## Tech Stack

| Area | Technology |
| --- | --- |
| API | Python 3.11, Flask 3.x |
| AI | Groq API, `llama-3.3-70b-versatile` |
| Cache and limits | Redis 7, Flask-Limiter |
| Data dependency | PostgreSQL |
| Security | JWT, sanitization middleware, secure headers, PII checks |
| Deployment | Docker, Docker Compose |
| Testing | pytest, validation scripts |

## Folder Structure

```text
ai-service/
|-- app.py
|-- config.py
|-- Dockerfile
|-- docker-compose.yml
|-- .env.example
|-- routes/
|-- services/
|-- middleware/
|-- cache/
|-- prompts/
|-- validation/
|-- tests/
|-- security/
|-- quality/
|-- docs/
|   |-- day15/
|   |-- demo-day/
|   |-- API_REFERENCE.md
|   |-- DEPLOYMENT_GUIDE.md
|   `-- TROUBLESHOOTING.md
```

## API Endpoints

| Endpoint | Method | Auth | Purpose |
| --- | --- | --- | --- |
| `/health` | GET | No | Runtime health and dependency status |
| `/metrics` | GET | No | Prometheus-compatible service metrics |
| `/monitoring/status` | GET | No | Monitoring and resource status snapshot |
| `/describe` | POST | JWT | Explain an aged audit issue |
| `/recommend` | POST | JWT | Generate remediation recommendations |
| `/generate-report` | POST | JWT | Generate an audit-ready report |

### Example Request

```sh
curl -X POST http://127.0.0.1:8000/describe \
  -H "Authorization: Bearer <jwt>" \
  -H "Content-Type: application/json" \
  -d "{\"issue\":\"User access reviews for the finance system are overdue by 90 days.\"}"
```

### Example Response

```json
{
  "success": true,
  "status": "success",
  "endpoint": "/describe",
  "issue": "User access reviews for the finance system are overdue by 90 days.",
  "score": 8,
  "response": "AI-generated audit guidance...",
  "generated_at": "2026-05-07T00:00:00+00:00"
}
```

See [docs/API_REFERENCE.md](docs/API_REFERENCE.md) for fuller examples.

## Environment Setup

Create `.env` from the example file:

```sh
cp .env.example .env
```

Required values:

```env
GROQ_API_KEY=<your-groq-key>
GROQ_MODEL=llama-3.3-70b-versatile
JWT_SECRET=<32-plus-character-secret>
JWT_ALGORITHM=HS256
JWT_AUDIENCE=tool-125
JWT_ISSUER=tool-125-auth
REDIS_URL=redis://localhost:6379/0
```

Validate configuration:

```sh
python -m validation.env_validator
```

## Docker Quick Start

```sh
docker compose up --build -d
docker compose ps
curl http://127.0.0.1:8000/health
```

Expected health response:

```json
{
  "success": true,
  "status": "ok"
}
```

## Validation

Run the Day 15 reviewer gate:

```sh
python -m validation.reviewer_validation
```

Run the full test suite:

```sh
python -m pytest
```

Run focused validation:

```sh
python -m validation.day16_monitoring_validation
python -m validation.security_validation
python -m validation.endpoint_validation
python -m validation.final_system_check
```

The reviewer validation report is written to:

```text
validation/reports/day15_reviewer_validation.json
```

## Security Summary

Security controls include:

- JWT authentication for `/describe`, `/recommend`, and `/generate-report`.
- Prompt injection, command injection, script tag, dangerous JSON key, and oversized input rejection.
- SQL injection pattern rejection.
- PII detection before model calls.
- Redis-backed rate limiting.
- Secure headers including CSP, HSTS, frame blocking, no-sniff, and no-store cache policy.
- Structured fallback responses for validation, auth, Groq, and internal failures.

See [SECURITY.md](SECURITY.md), [docs/day15/SECURITY_TALKING_POINTS.md](docs/day15/SECURITY_TALKING_POINTS.md), and [docs/FINAL_SECURITY_CHECKLIST.md](docs/FINAL_SECURITY_CHECKLIST.md).

## Monitoring and Observability

Day 16 monitoring adds:

- Structured request start and completion logs with request IDs.
- Sensitive field redaction for authorization headers, JWTs, API keys, passwords, secrets, tokens, and PII patterns.
- Prometheus-compatible `/metrics` output.
- HTTP request count, error count, and latency counters.
- AI response timing and AI cache hit, miss, and disabled counters.
- `/monitoring/status` resource snapshot for process CPU and memory plus container cgroup data when available.
- `/health` monitoring status and metrics endpoint reference.

Validation:

```sh
python -m validation.day16_monitoring_validation
```

## Day 15 Documentation

| Document | Purpose |
| --- | --- |
| [AI_SUMMARY_CARD.md](docs/day15/AI_SUMMARY_CARD.md) | Printable one-page AI summary card |
| [ai_quick_reference.md](docs/day15/ai_quick_reference.md) | Fast endpoint and AI controls reference |
| [TECH_STACK_SUMMARY.md](docs/day15/TECH_STACK_SUMMARY.md) | Technology, business value, and security value |
| [AI_ARCHITECTURE_SUMMARY.md](docs/day15/AI_ARCHITECTURE_SUMMARY.md) | AI request, Groq, Redis, validation, and fallback flow |
| [QUICK_DEPLOY_GUIDE.md](docs/day15/QUICK_DEPLOY_GUIDE.md) | Deployment quick-start guide |
| [REVIEWER_GUIDE.md](docs/day15/REVIEWER_GUIDE.md) | Reviewer handoff instructions |
| [FINAL_DOCUMENTATION_INDEX.md](docs/day15/FINAL_DOCUMENTATION_INDEX.md) | Complete Day 15 documentation index |

## Demo Day References

- [docs/demo-day/DEMO_DAY_GUIDE.md](docs/demo-day/DEMO_DAY_GUIDE.md)
- [docs/demo-day/AI_DEMO_SCRIPT.md](docs/demo-day/AI_DEMO_SCRIPT.md)
- [docs/demo-day/QUICK_REFERENCE.md](docs/demo-day/QUICK_REFERENCE.md)
- [docs/day15/demo_security_notes.md](docs/day15/demo_security_notes.md)
- [docs/day15/deployment_cheatsheet.md](docs/day15/deployment_cheatsheet.md)

## Troubleshooting

| Symptom | Fix |
| --- | --- |
| Docker startup fails | Confirm Docker Desktop is running and ports `8000`, `6379`, and `5432` are available. |
| `/health` fails | Check `docker compose ps` and `docker compose logs ai-service`. |
| Redis is unhealthy | Run `docker compose logs redis` and `docker compose exec redis redis-cli ping`. |
| AI endpoints return 401 | Confirm the JWT uses the configured `JWT_SECRET`, `JWT_AUDIENCE`, `JWT_ISSUER`, and has a valid `exp`. |
| AI endpoints return 400 | Review prompt injection, SQL injection, PII, content type, and required `issue` validation. |
| AI endpoints return 502 | Verify `GROQ_API_KEY`, `GROQ_MODEL`, Groq quota, and network access. |
| Rate limit errors | Wait for the limit window or adjust `RATE_LIMIT` in local development. |

## Reviewer Workflow

1. Read [docs/day15/AI_SUMMARY_CARD.md](docs/day15/AI_SUMMARY_CARD.md).
2. Configure `.env`.
3. Start with `docker compose up --build -d`.
4. Verify `/health`.
5. Run `python -m validation.reviewer_validation`.
6. Run `python -m pytest`.
7. Use [docs/day15/REVIEWER_GUIDE.md](docs/day15/REVIEWER_GUIDE.md) for final handoff notes.
