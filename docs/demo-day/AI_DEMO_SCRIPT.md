# Tool-125 AI Demo Script

## Demo Goal

Show that the AI service can turn aging audit issues into clear explanations, prioritized remediation, and stakeholder-ready reports while enforcing authentication, input safety, rate limiting, caching, and graceful failure behavior.

## Speaking Flow

### 0:00-0:20 - Opening

Good morning. I am presenting the AI service for Tool-125, the Audit Issue Aging Tracker. This service helps audit, security, and compliance teams understand unresolved issues faster by generating risk descriptions, remediation recommendations, and structured reports from a single audit issue input.

### 0:20-0:40 - Service Context

The AI service is a Flask microservice running on Python 3.11. It exposes four main endpoints: `/describe`, `/recommend`, `/generate-report`, and `/health`. The protected AI endpoints require JWT authentication and JSON input. The service uses Groq with `llama-3.3-70b-versatile`, Redis for response caching and rate limiting, and Docker Compose for repeatable deployment.

Transition: I will start with a realistic aged audit issue and show how the same issue moves through the AI workflow.

### 0:40-1:20 - Demonstrate `/describe`

Endpoint: `POST /describe`

Input issue:

```json
{
  "issue": "Critical VPN appliance vulnerability remains unpatched for 47 days on the finance network segment, exposing remote access infrastructure to known exploit activity."
}
```

Speaking line:

First, `/describe` explains the audit issue in business and technical terms. It identifies the likely root cause, the operational impact, and why the issue becomes more dangerous as it ages.

Expected result:

The response should include `success: true`, endpoint `/describe`, the original issue text, a quality score, and an AI-generated explanation.

Transition: Now that the issue is clearly described, I will ask the AI for concrete remediation actions.

### 1:20-2:00 - Demonstrate `/recommend`

Endpoint: `POST /recommend`

Use the same issue.

Speaking line:

The `/recommend` endpoint turns the issue into a remediation plan. The response prioritizes immediate containment, patch validation, compensating controls, and evidence that the audit team can use to close the finding.

Expected result:

The response should recommend actions such as isolating the vulnerable VPN appliance, applying the vendor patch, validating exposure, rotating impacted credentials if needed, and documenting closure evidence.

Transition: For leadership and audit review, we also need a report format.

### 2:00-2:45 - Demonstrate `/generate-report`

Endpoint: `POST /generate-report`

Use the same issue or switch to the compliance failure example:

```json
{
  "issue": "SOX privileged access review for the ERP production database is overdue by 32 days, and 14 admin accounts have no documented business owner approval."
}
```

Speaking line:

The `/generate-report` endpoint produces a stakeholder-ready audit issue report. It is designed for review meetings, status updates, and closure documentation, with sections for summary, risk, remediation, and verification.

Expected result:

The report should contain a concise executive summary, risk assessment, remediation owner actions, due-date guidance, and verification evidence.

Transition: Before trusting the AI endpoints, I will show service health and dependency visibility.

### 2:45-3:10 - Demonstrate `/health`

Endpoint: `GET /health`

Speaking line:

The `/health` endpoint is intentionally public and lightweight. It confirms that the service is running and reports dependency status for Groq configuration, Redis, the prompt sanitizer, and the rate limiter.

Expected result:

The response should return `status: ok`, list the service components, and show Redis as `ok`, `unhealthy`, or `not_configured` depending on the runtime.

### 3:10-3:45 - AI Workflow Explanation

When a request reaches a protected endpoint, Flask first applies security middleware. The middleware checks content type, JWT, request size, PII, SQL injection patterns, and prompt injection patterns. Then the route builds a task-specific prompt using the prompt manager. The Groq client checks Redis for a cached response, calls Groq if needed, validates the response, scores the output, and retries with an optimized prompt if the quality score is low.

### 3:45-4:20 - Security Explanation

Security is built into the request path. JWT protects the AI endpoints. Prompt sanitization blocks attempts to override system instructions. PII detection prevents sensitive personal data from being sent to the model. SQL injection checks reject malicious payloads. Flask-Limiter controls abuse, Redis supports shared rate limits, and secure response headers reduce browser-side risk. Errors return structured fallback responses rather than stack traces.

### 4:20-4:45 - Fallback Explanation

If Groq is unavailable, the endpoint returns a clear `502` response with a controlled error payload. If Redis is unavailable, the service can still call Groq without cached responses. If authentication fails, the endpoint returns `401`. During a live demo, the backup workflow uses prepared offline responses that match the same API shape.

### 4:45-5:00 - Closing

This AI service makes aged audit issues easier to understand, prioritize, and communicate. It gives teams faster remediation guidance while preserving secure API behavior, deployment repeatability, and demo-safe fallback options.

