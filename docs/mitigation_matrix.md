# Mitigation Matrix

| Risk | Severity | Mitigation | Validation |
| --- | --- | --- | --- |
| Unauthorized AI access | High | JWT Bearer validation | `test_security_jwt.py`, `security_validation.py` |
| Prompt injection | High | Sanitization regex blocklist | `test_security.py`, fallback cases |
| SQL injection text | High | SQL safety detection | `test_pii_injection.py`, `security_validation.py` |
| Script injection | Medium | Script tag rejection and HTML stripping | `test_security.py` |
| PII leakage | High | PII detector and log redaction | `test_pii_injection.py`, secure logging filter |
| Rate abuse | Medium | Flask-Limiter with Redis | `test_rate_limit.py` |
| Oversized payloads | Medium | Flask `MAX_CONTENT_LENGTH` | `test_security.py` |
| Weak JWT config | High | Environment validation and weak secret checks | `env_validator.py` |
| Container privilege | High | Non-root app user | Dockerfile review |
| Redis outage | Medium | Health checks and validation scripts | `container_health_check.py` |
| Groq failure | Medium | Retry and structured 502 response | `test_groq_client.py` |

## Before and After

Before mitigation, unsafe requests could reach deeper layers or produce deployment-only failures. After mitigation, validation occurs early, failures are structured, and deployment scripts exercise the same controls used in production.
