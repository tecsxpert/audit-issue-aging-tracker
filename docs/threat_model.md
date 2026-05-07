# Threat Model

## Scope

This model covers Flask API endpoints, JWT authentication, Groq AI calls, Redis, PostgreSQL connectivity, Docker runtime, validation scripts, and environment configuration.

## Threat Register

| Threat | Severity | Impact | Mitigation | Residual Risk |
| --- | --- | --- | --- | --- |
| Missing or stolen JWT | High | Unauthorized AI endpoint access | Bearer token validation with signature, audience, issuer, and expiration | Token theft remains possible if client storage is compromised |
| Malformed JWT attacks | Medium | Auth bypass attempts or parser errors | PyJWT validation and structured 401 responses | Library vulnerabilities require dependency monitoring |
| Prompt injection | High | Model behavior manipulation | Sanitization middleware blocks known injection patterns | Novel indirect prompt attacks may require tuning |
| SQL injection content | High | Attempted database manipulation | SQL-like payload detection and rejection | False negatives possible for new payload shapes |
| XSS payloads | Medium | Script injection in downstream consumers | Script tags rejected and HTML stripped | Consumers must still escape rendered AI output |
| PII leakage | High | Sensitive data sent to AI provider or logs | PII detector rejects payloads and log filters redact secrets | Advanced PII formats may require expanded patterns |
| API abuse and brute force | Medium | Resource exhaustion and cost increase | Redis-backed rate limiting | Distributed attacks require edge-layer rate limits |
| Groq outage or API change | Medium | AI endpoint degradation | Retries and structured 502 errors | Third-party availability remains external |
| Container breakout | High | Host compromise | Non-root container and isolated network | Runtime/kernel vulnerabilities remain platform risk |
| Redis exposure | Medium | Cache or rate-limit tampering | Compose network isolation | Production must add auth/TLS/private network policy |
| Secret leakage | High | Credential compromise | `.env` excluded, docs require secret manager | Operator mishandling remains possible |

## AI-Specific Threats

- Direct prompt injection through user issue text.
- Requests containing secrets or personal identifiers.
- Hallucinated recommendations that appear authoritative.
- Unstable model output shape.
- Excessive prompt retries increasing cost.

## Assumptions

- TLS is enforced by the deployment ingress.
- `.env` is not committed.
- Groq API keys are rotated if exposed.
- Redis and PostgreSQL are not publicly reachable in production.
