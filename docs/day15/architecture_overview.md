# Architecture Overview

## Service Boundary

Tool-125 separates the AI capability into a dedicated Flask service. The frontend or backend sends audit issue text to the AI service, and the service returns structured audit guidance.

## Main Components

| Component | Responsibility |
| --- | --- |
| Frontend | Collects audit issue context from users and displays AI guidance. |
| Backend | Coordinates authenticated application workflows and can call the AI service. |
| AI Service | Validates input, builds prompts, calls Groq, caches responses, and returns results. |
| Groq | Runs the LLM inference for audit descriptions, recommendations, and reports. |
| Redis | Stores AI response cache entries and Flask-Limiter counters. |
| PostgreSQL | Stores application audit issue data in the broader platform. |

## Request Lifecycle

1. Client submits an audit issue to a protected endpoint.
2. Flask middleware validates content type, JWT, size limits, PII, SQL injection, and prompt safety.
3. Route logic validates the `issue` field and selects the correct prompt template.
4. Groq client checks Redis for a cached response.
5. If no cache hit exists, the service sends the prompt to Groq.
6. Response is parsed, scored, optionally re-prompted, cached, and returned as JSON.

## Deployment Topology

Docker Compose starts three services:

- `ai-service` on port `8000`
- `redis` on port `6379`
- `postgres` on port `5432`

The services share the `tool125-network` bridge network and use health checks for readiness.
