# Request Flow

## `/health`

```text
Caller -> Flask /health -> Redis ping -> dependency status JSON
```

The health endpoint is public and exists for Docker, reviewer, and deployment verification.

## Protected AI Endpoints

```text
Caller
  -> Authorization header and JSON body
  -> Flask sanitization middleware
  -> Flask security middleware
  -> AI route handler
  -> PromptBuilder
  -> GroqClient
  -> Redis cache
  -> Groq chat completion
  -> PromptOptimizer score check
  -> JSON response
```

## Success Criteria

- Request includes `Content-Type: application/json`.
- Request includes `Authorization: Bearer <jwt>`.
- Body contains a non-empty `issue` string.
- Payload passes sanitization and security checks.
- Groq returns non-empty output or Redis has a cached output.

## Failure Examples

| Condition | Status | Example Message |
| --- | --- | --- |
| Missing JWT | 401 | Authorization header must contain a Bearer token. |
| Malformed JSON | 400 | Malformed JSON request body. |
| Prompt injection | 400 | Prompt injection detected and rejected. |
| SQL injection | 400 | SQL injection payload detected and rejected. |
| PII detected | 400 | Sensitive personal information detected in input. |
| Groq outage or bad key | 502 | Groq API failed after retries. |
