# Demo Security Notes

## Opening Line

Security was designed as part of the AI request flow, not added afterward. Every protected AI request is authenticated, validated, sanitized, rate-limited, and logged safely before it can reach Groq.

## Non-Technical Explanation

We treat the AI model like a powerful assistant that should only receive clean, approved work. The service checks who is asking, checks whether the request is safe, removes risky input patterns, blocks sensitive personal data, and only then sends a focused prompt to Groq.

## Reviewer-Friendly Examples

| Security Feature | Simple Explanation |
| --- | --- |
| JWT | Confirms the caller is allowed to use the AI endpoints. |
| Prompt injection blocking | Stops requests that try to trick the AI into ignoring instructions. |
| SQL injection blocking | Rejects database attack patterns even if they appear inside text. |
| PII detection | Prevents personal data from being sent to the model. |
| Rate limiting | Prevents one user or script from overloading the service. |
| Secure headers | Adds browser and API safety defaults to every response. |
| Docker isolation | Runs dependencies in separate, repeatable containers. |

## 60-Second Security Walkthrough

When a user submits an aged audit issue, the AI service first checks that the request is JSON and that the endpoint requires authentication. It validates the JWT, checks the request size, scans for prompt injection and command injection, rejects SQL injection patterns, and blocks sensitive personal data. If the request passes those checks, Flask builds a controlled audit prompt and calls Groq. The response is returned as structured JSON with secure headers and can be cached in Redis for repeat calls.
