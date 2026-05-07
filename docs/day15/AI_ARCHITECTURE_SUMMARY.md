# AI Architecture Summary

## Purpose

The AI architecture provides a secure service boundary for audit issue aging analysis. It converts a short issue description into explanation, recommendation, or report output while protecting the model, API key, and downstream systems.

## Request Flow

```text
Frontend or backend
  -> Flask AI service
  -> security and sanitization middleware
  -> route validation
  -> prompt builder
  -> Redis cache check
  -> Groq API
  -> response parser and scorer
  -> JSON response
```

## Frontend to Backend to AI Service

The frontend collects issue details from the user. The application backend can attach the user authorization context and call the AI service. The AI service is responsible for model-specific logic, prompt templates, validation, caching, and final response formatting.

## Groq Response Flow

1. The Groq client builds a chat completion request.
2. The request uses the configured model and a low temperature for stable audit wording.
3. The client retries transient failures with backoff.
4. The response parser accepts standard chat completion content and validates that output is non-empty.
5. The endpoint returns a consistent JSON payload.

## Redis Caching Workflow

1. Prompt payload is serialized with stable JSON ordering.
2. SHA-256 hash creates a cache key scoped to the model.
3. Redis is checked before calling Groq.
4. Cache hits return immediately.
5. Cache misses call Groq and store the response with `AI_CACHE_TTL_SECONDS`.

## Validation Pipeline

- JSON content-type enforcement.
- JWT validation for protected routes.
- Request size and timeout controls.
- Nested JSON, list length, and string length limits.
- Prompt injection, command injection, script tag, and dangerous key rejection.
- PII and SQL injection checks.
- Required `issue` field validation.

## Fallback Mechanism

Errors are returned as structured JSON. Groq failures return `502`, invalid input returns `400`, unauthorized access returns `401`, oversized requests return `413`, and internal service failures return graceful `503` responses.
