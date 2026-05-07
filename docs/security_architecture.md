# Security Architecture

## Overview

Tool-125 uses defense in depth across API ingress, authentication, input validation, AI prompt handling, dependency access, logging, and container runtime controls.

## Request Path

1. Client sends HTTPS request through the deployment boundary.
2. Flask receives the request through Gunicorn.
3. Sanitization middleware validates JSON structure and blocks prompt injection, command injection, script tags, dangerous JSON keys, oversized fields, deep nesting, and PII.
4. Security middleware validates JWT, body size, content type, PII, SQL injection indicators, and secure response headers.
5. AI routes construct prompts and call Groq through `GroqClient`.
6. Redis stores rate-limit state and optional AI cache entries.
7. Structured logs are emitted with sensitive fields redacted.

## Security Layers

| Layer | Control |
| --- | --- |
| Authentication | JWT Bearer tokens |
| Input validation | JSON schema expectations, size checks, injection checks |
| AI safety | Prompt injection blocking, response validation, fallback errors |
| Abuse control | Flask-Limiter with Redis storage |
| Secrets | Environment variables and `.env` exclusion |
| Logging | JSON logs with PII and secret redaction |
| Container | Non-root user, health checks, private network |

## Production Notes

Use a reverse proxy or platform ingress with TLS termination, managed Redis/PostgreSQL, centralized logging, and secret-manager injection.
