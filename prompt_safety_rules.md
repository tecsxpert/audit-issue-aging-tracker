# Prompt Safety Rules

## Principles
- Never include passwords, API keys, tokens, JWTs, or personally identifiable information in prompt templates.
- Do not echo user-provided secrets back in AI responses.
- Keep prompts focused on audit issue analysis, recommendations, and report generation.

## Service rules
- All incoming payloads must be valid JSON with `Content-Type: application/json`.
- HTML and script tags are stripped before prompt construction.
- Common prompt injection phrases are rejected immediately.
- Sensitive data patterns are detected and blocked before requests are processed.

## Safe prompt design
- Use explicit instructions about the task and expected format.
- Avoid open-ended language that could cause the model to invent credentials.
- Do not embed test tokens, user identifiers, or environment secrets.

## Example safe prompt
```
You are an enterprise-grade audit issue analyst. Describe the root cause, business impact, and continuing risk of the issue below.
Issue:
<sanitized issue text>
```

## Unsafe prompt content to avoid
- `password=12345`
- `Authorization: Bearer <token>`
- `admin@example.com`
- `apikey=...`
- `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`

## Enforcement
The middleware rejects payloads containing PII, XSS, and prompt injection attempts before the model is called.
