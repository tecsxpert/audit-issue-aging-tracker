# PII Audit

## Objective
Audit the service for any direct or indirect personal information exposure in prompts and payloads.

## PII patterns detected
The service detects common sensitive data patterns including:
- email addresses
- phone numbers
- JWT tokens
- API keys
- passwords and secret assignment patterns
- credit card numbers
- social security numbers

## Protection approach
- Input payloads containing PII are rejected before reaching the Groq API.
- The prompt sanitizer removes HTML content and enforces strict JSON payload validation.
- The security middleware logs suspicious payloads without storing raw sensitive values.

## Findings
- Prompt templates do not contain any hard-coded PII.
- AI endpoint inputs are inspected and rejected if they contain PII patterns.
- Generated responses are produced from sanitized prompts only.

## Residual risks
- If the upstream audit issue source already contains sensitive data, the request is refused rather than forwarded.
- Additional PII categories may be added over time as new data types are identified.

## Recommended improvements
- Add data classification rules for domain-specific identifiers.
- Use an external PII scanning service for higher fidelity detection.
- Monitor logs for repeated PII injection attempts.
