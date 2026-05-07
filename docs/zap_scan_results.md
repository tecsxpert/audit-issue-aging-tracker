# ZAP Scan Results

## Scope

Target: Tool-125 AI service local Docker deployment.

Endpoints:

- `/health`
- `/describe`
- `/recommend`
- `/generate-report`

## Scan Status

ZAP execution is documented for capstone security review. The current repository includes `zap_scan.sh` and prior ZAP report artifacts. For final production evidence, run ZAP against a non-production deployment with valid authorization headers configured for protected endpoints.

## Expected Findings

| Category | Expected Result |
| --- | --- |
| Missing auth on AI endpoints | Not present |
| Missing secure headers | Not present |
| Reflected XSS | Blocked by sanitization |
| SQL injection | Blocked by payload validation |
| Directory browsing | Not applicable |

## Evidence Placeholder

- `screenshots/zap-summary.png`
- `reports/zap-html-report.html`

## Remediation Status

No unresolved ZAP-specific critical issues are documented for Day 12.
