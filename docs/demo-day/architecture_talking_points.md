# Architecture Talking Points

## Request Flow

1. Client sends JSON request with JWT.
2. Flask receives request.
3. Security middleware validates authentication, content type, size, PII, SQL injection, and prompt injection.
4. Route validates the `issue` field.
5. Prompt builder selects the endpoint-specific prompt.
6. Groq client checks Redis cache.
7. Groq API generates the response when cache does not contain a match.
8. Prompt optimizer scores the output and retries with an improved prompt if needed.
9. Flask returns a structured JSON response.

## Components

| Component | Role |
| --- | --- |
| Flask | API gateway and route execution |
| Groq | LLM provider for audit analysis |
| Redis | Cache and shared rate-limit storage |
| PostgreSQL | Application data dependency in the full stack |
| Flask-Limiter | Request throttling |
| JWT | Authentication for protected AI endpoints |
| Docker Compose | Repeatable local and demo deployment |

## Security Controls

- JWT validation on `/describe`, `/recommend`, and `/generate-report`.
- Public but non-sensitive `/health`.
- Prompt injection detection before model calls.
- PII rejection before external AI processing.
- SQL injection pattern rejection.
- Request size limits and timeout protection.
- Secure response headers.
- Structured error payloads with no stack traces.

