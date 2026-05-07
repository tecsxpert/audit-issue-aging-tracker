# Speaking Notes

## Opening

This is the AI service for Tool-125, the Audit Issue Aging Tracker. It helps audit and security teams understand aged issues, decide what should happen next, and generate clean report language for review.

## `/describe`

This endpoint explains the issue. It focuses on root cause, business impact, and why the aging period increases risk.

## `/recommend`

This endpoint turns the issue into action. It gives remediation steps, validation checks, and a risk reduction summary.

## `/generate-report`

This endpoint prepares stakeholder-ready language. It is useful for audit updates, closure evidence, and leadership communication.

## `/health`

This endpoint confirms the service is running and reports dependency status. It does not require JWT because it does not expose sensitive data.

## Technical Architecture

Flask handles the API. Security middleware validates JWT, content type, request size, prompt injection patterns, SQL injection patterns, and PII. Groq generates the AI response. Redis supports caching and rate limiting. Docker Compose makes the service repeatable.

## Security

The protected AI endpoints require JWT. Unsafe prompt patterns and sensitive data are blocked before the request reaches the model. Failures return structured JSON responses instead of stack traces.

## Non-Technical Value

The service saves time, improves consistency, and helps teams communicate risk clearly. It does not replace the audit team. It gives them a faster and more reliable starting point.

## Closing

Tool-125 turns unresolved audit issues into clear analysis, prioritized action, and report-ready language while keeping the AI workflow protected and deployment-ready.

