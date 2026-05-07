# AI Architecture Summary

## Flow

1. Client submits an audit issue to a protected endpoint.
2. JWT and input security middleware validate the request.
3. PromptBuilder creates endpoint-specific instructions.
4. GroqClient checks Redis cache.
5. Groq API is called when no cache entry exists.
6. Output is parsed and quality-scored.
7. Response returns structured JSON with endpoint, issue, response, score, and timestamp.

## Endpoint Responsibilities

- `/describe`: explains issue meaning, importance, impact, and review steps.
- `/recommend`: produces prioritized remediation actions.
- `/generate-report`: produces stakeholder-ready audit report sections.

## Operational Dependencies

- Groq for AI generation.
- Redis for rate limiting and AI cache.
- PostgreSQL as deployment dependency.
- Docker Compose for local/container deployment.
