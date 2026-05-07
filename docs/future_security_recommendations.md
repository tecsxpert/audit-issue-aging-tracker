# Future Security Recommendations

## Authentication and Authorization

- Add role or scope checks for `describe`, `recommend`, and `generate-report`.
- Rotate JWT secrets through a secret manager.
- Add support for asymmetric JWT verification if an external identity provider is used.

## AI Safety

- Add RAG document-level access controls before retrieval.
- Add output policy checks for sensitive recommendations.
- Add model fallback configuration and provider health dashboards.

## Infrastructure

- Use managed Redis with authentication, TLS, and private networking.
- Use managed PostgreSQL with least-privilege credentials.
- Enforce HTTPS at ingress.
- Add WAF rules for known injection and abuse patterns.

## Monitoring

- Alert on repeated 401, 400, 413, 429, and 502 responses.
- Track Groq latency, failure rate, token usage, and cache hit rate.
- Send structured logs to SIEM.

## Testing

- Schedule ZAP scans in CI.
- Add dependency vulnerability scanning.
- Add container image scanning.
- Add chaos testing for Redis and Groq outages.
