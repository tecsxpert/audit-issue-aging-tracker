# Tool-125 AI Service Security

## Executive Summary
The AI service has completed Week 2 security sign-off for the protected AI endpoints:

| Endpoint | JWT Required | Rate Limited | Injection Protected | PII Protected |
|---|---:|---:|---:|---:|
| `POST /describe` | Yes | Yes | Yes | Yes |
| `POST /recommend` | Yes | Yes | Yes | Yes |
| `POST /generate-report` | Yes | Yes | Yes | Yes |
| `GET /health` | No | Yes | Not applicable | Not applicable |

The service enforces JWT authentication, strict JSON validation, prompt-injection rejection, SQL/command/script payload blocking, PII detection, structured JSON errors, secure response headers, request size limits, timeout handling, and IP-based rate limiting.

## Threat Model
Primary threats addressed:

| Threat | Risk | Mitigation |
|---|---|---|
| Unauthorized AI endpoint access | Unauthorized audit analysis generation | Bearer JWT validation on protected routes |
| Token tampering or expiry bypass | Account/session abuse | PyJWT signature, issuer, audience, expiry, and algorithm checks |
| Prompt injection | Model instruction override or unsafe output | Dangerous instruction pattern rejection before prompt generation |
| SQL/command/script injection | Payload smuggling, unsafe logs, downstream risk | SQL, command, and script detection with HTTP 400 rejection |
| PII leakage into prompts/logs | Sensitive data exposure | PII request rejection and log masking filter |
| Abuse and brute force | Cost or availability impact | Flask-Limiter 30 requests/minute policy, Redis-ready storage |
| Oversized request payloads | Memory pressure | `MAX_CONTENT_LENGTH` and field length checks |
| Docker privilege escalation | Container breakout blast radius | Non-root runtime user and bytecode suppression |

## Security Architecture
Request flow:

```text
Client
  -> Flask-Limiter
  -> Sanitization middleware
  -> Security middleware
  -> Route validation
  -> Prompt builder
  -> Groq client
  -> Structured JSON response
```

Protected routes require:

```http
Authorization: Bearer <jwt>
Content-Type: application/json
```

Success and error responses include:

```json
{
  "success": false,
  "status": "error",
  "message": "Prompt injection detected and rejected.",
  "generated_at": "2026-05-06T19:49:32.121000+00:00"
}
```

## JWT Protection
JWT validation is implemented in `services/jwt_manager.py`.

Validated controls:

| Control | Status |
|---|---|
| Missing token returns HTTP 401 | Passed |
| Invalid token returns HTTP 401 | Passed |
| Expired token returns HTTP 401 | Passed |
| Tampered token returns HTTP 401 | Passed |
| Wrong audience returns HTTP 401 | Passed |
| Unsupported algorithm rejected | Passed |
| Weak secret detection utility available | Passed |

Production deployment must set `JWT_SECRET` from a secret manager or protected environment variable. The placeholder value in `.env.example` must never be used in production.

## Rate Limiting
Default policy:

```text
30 requests per minute
```

The limiter uses IP-based throttling and supports Redis storage through `RATE_LIMIT_STORAGE_URI` or `REDIS_URL`.

Validated controls:

| Scenario | Expected |
|---|---|
| Normal traffic under threshold | HTTP 200 or service fallback |
| Repeated traffic over threshold | HTTP 429 |
| Repeated attack payloads | Rejected before AI execution and throttled by limiter |
| Multi-instance deployment | Configure Redis-backed limiter storage |

## Injection Defense
The service rejects:

- prompt injection phrases such as “ignore previous instructions”
- script tags and script variants
- SQL injection payloads such as `UNION SELECT`, `OR 1=1`, and destructive statements
- command injection payloads such as `curl`, `wget`, shell chains, and command substitution
- malicious JSON keys such as `__proto__`, `$where`, and `$regex`
- deeply nested or oversized JSON payloads

Regular harmless HTML tags are stripped before the route sees the payload.

## PII Protection
PII detection is implemented in `services/pii_detector.py` and recursive scanning/masking in `services/sensitive_scanner.py`.

Detected categories:

| Category | Action |
|---|---|
| Email address | Reject request or mask in logs |
| Phone number | Reject request or mask in logs |
| JWT token | Reject request or mask in logs |
| API key/secret/password field | Reject request or mask in logs |
| Credit card | Reject request or mask in logs |
| SSN-like value | Reject request or mask in logs |

Log output is filtered by `security.secure_logging.SensitiveDataFilter` so structured extras such as `payload_snippet` are masked before emission.

## Vulnerabilities Fixed
| Finding | Resolution |
|---|---|
| Unresolved merge conflict in core service files | Resolved to factory-based Flask app and production Groq client |
| Endpoint responses lacked consistent `success` and timestamp fields | Standardized success/error payloads |
| SQL injection payloads were logged but not blocked | Now rejected with HTTP 400 |
| Script/prompt injection coverage needed stronger variants | Added stronger patterns and tests |
| Command injection payloads were not explicitly rejected | Added command-injection detection |
| Logs could include sensitive snippets | Added masking scanner and logging filter |
| Docker container ran as root | Added non-root `appuser` runtime |

## Residual Risks
| Risk | Recommendation |
|---|---|
| Model hallucination | Keep human review for audit conclusions |
| Distributed rate-limit consistency | Use Redis in production |
| Secret rotation | Integrate with deployment secret manager |
| Dependency vulnerabilities | Run `pip-audit` or equivalent in CI |
| Production observability | Add alerting for repeated 401/400/429 bursts |

## Validation Commands
Run the unit/security suite:

```bash
python -m pytest
```

Run final endpoint validation against a running service:

```bash
python security/final_security_check.py --base-url http://127.0.0.1:8000
```

Run rate-limit stress validation:

```bash
python security/stress_test.py --base-url http://127.0.0.1:8000 --requests 35
```

## Sign-Off
Week 2 security sign-off status: **Approved for capstone demo and controlled staging use**, assuming production secrets are externally managed and Redis-backed rate limiting is enabled for multi-instance deployments.
