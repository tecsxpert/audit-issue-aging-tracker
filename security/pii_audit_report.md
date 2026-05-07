# PII Audit Report

## Scope
Reviewed:

- prompt templates
- request sanitization middleware
- API responses
- error payloads
- Groq payload construction
- fallback responses
- logging configuration

## Findings
| Area | Result |
|---|---|
| Prompt templates | No hard-coded PII, secrets, passwords, tokens, or API keys |
| Incoming payloads | PII rejected before prompt generation |
| Logs | Sensitive data filter masks PII and secret-like values |
| API responses | Structured status data only; no stack traces |
| AI payloads | Sanitized issue text only |
| Fallback errors | Generic, structured messages |

## PII Categories Checked
- email addresses
- phone numbers
- JWT tokens
- API keys
- passwords
- generic secrets
- credit cards
- SSN-like identifiers

## Controls Implemented
| Control | File |
|---|---|
| Pattern detection | `services/pii_detector.py` |
| Recursive scanner and masker | `services/sensitive_scanner.py` |
| Request rejection | `middleware/security.py`, `middleware/sanitization.py` |
| Log masking | `security/secure_logging.py` |

## Conclusion
No personal data should be sent to prompts or emitted in logs under the validated request path. Requests containing detected PII are rejected with HTTP 400.
