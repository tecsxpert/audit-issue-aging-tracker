# Security Talking Points

## 30-Second Security Summary

The AI service is protected before a request ever reaches the model. It requires a valid JWT for AI endpoints, rejects unsafe prompts and injection patterns, blocks sensitive personal data, rate-limits requests through Redis, and returns secure HTTP headers. The goal is to keep the AI feature useful while preventing abuse, data leakage, and unsafe input from reaching Groq.

## JWT Protection

JWT is used so only authorized callers can access `/describe`, `/recommend`, and `/generate-report`. The service validates the token signature, expiration, audience, issuer, and allowed signing algorithm before processing the request.

## Prompt Injection Prevention

The service scans incoming text for phrases like attempts to ignore instructions, bypass controls, or override the system prompt. Suspicious input is rejected with a clear error instead of being sent to the AI model.

## SQL Injection Blocking

Even though the AI endpoint accepts JSON text, the service still scans the request body for SQL injection patterns. This prevents dangerous payloads from flowing through shared logs, downstream services, or future database-backed workflows.

## PII Masking and Rejection

The middleware detects sensitive personal information and rejects it before model processing. Logging utilities also mask sensitive values so secrets and personal data are not exposed in logs.

## Rate Limiting

Flask-Limiter uses Redis to enforce request limits. This protects service availability, controls Groq usage cost, and reduces abuse during demos or production traffic spikes.

## Secure Headers

Responses include security headers such as content security policy, frame blocking, no-sniff, no-store cache control, referrer policy, and HSTS. These headers reduce browser-side attack risk.

## Docker Security

The service is containerized with Docker Compose, isolated on a project network, and built for repeatable startup. Redis and PostgreSQL run as separate services so dependencies are clear and operationally testable.
