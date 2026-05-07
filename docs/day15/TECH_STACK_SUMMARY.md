# Tech Stack Summary

| Technology | Why It Was Used | Business Value | Security Value |
| --- | --- | --- | --- |
| Flask 3.x | Provides a small, clear API layer for AI endpoints. | Fast to develop, easy to review, and simple to deploy for a capstone AI service. | Centralizes request validation, error handling, and secure response headers. |
| Groq API | Provides hosted LLM inference using `llama-3.3-70b-versatile`. | Gives audit users high-quality explanations and recommendations without operating model infrastructure. | Keeps model access server-side and avoids exposing API keys to clients. |
| Redis 7 | Stores AI cache entries and rate-limit counters. | Improves response time and reduces repeated AI calls. | Enables abuse control through shared rate-limit state. |
| JWT | Protects AI endpoints with signed bearer tokens. | Allows only authorized application users or reviewers to use AI features. | Validates expiration, issuer, audience, and supported algorithms. |
| Docker | Packages the service and dependencies consistently. | Makes Demo Day startup repeatable on reviewer machines. | Runs the service with a controlled image and isolated Compose network. |
| PostgreSQL | Represents the durable data dependency for the audit tracker platform. | Supports audit issue persistence in the full system architecture. | Keeps structured audit records in a purpose-built database service. |
| Flask-Limiter | Applies request rate limits at the API boundary. | Protects demo reliability and avoids accidental overuse. | Reduces brute-force, spam, and cost-amplification risks. |
| Prompt Sanitization | Rejects prompt injection, command injection, script tags, dangerous keys, and oversized inputs. | Keeps AI outputs relevant and predictable for audit workflows. | Prevents malicious payloads from reaching prompt construction and model calls. |

## Production Readiness Notes

- Configuration is environment-driven through `.env` and Docker Compose.
- Health checks verify runtime readiness for the service and Redis dependency.
- Tests cover endpoint behavior, JWT validation, middleware, rate limiting, Groq client behavior, and security utilities.
- Documentation includes deployment, reviewer handoff, security talking points, and validation checklists.
