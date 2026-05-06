# Security Scan Guide

## Purpose
This guide explains how to prepare and run OWASP ZAP scans for the `Tool-125 — Audit Issue Aging Tracker` AI service.

## Prerequisites
- Docker installed
- Service running locally at `http://localhost:8000`
- Environment variables configured from `.env.example`

## Run the service
```bash
cd ai-service
python -m flask run --host=0.0.0.0 --port=8000
```

## Run the OWASP ZAP scan
```bash
cd ai-service
bash zap_scan.sh http://host.docker.internal:8000
```

## Scan types
- `zap-baseline.py`: passive scan, site crawling, and quick vulnerability checks
- `zap-full-scan.py`: active scan including injection and authentication tests

## Authentication testing
The application requires JWT authorization for `/describe`, `/recommend`, and `/generate-report`.

### Postman example
1. Create a `Bearer` token signed with `JWT_SECRET`.
2. Add request header:
   - `Authorization: Bearer <token>`
   - `Content-Type: application/json`
3. Example body:
```json
{
  "issue": "Audit issue involving missing authorization checks."
}
```

## Injection testing
The scan should verify:
- prompt injection rejection
- HTML/script sanitization
- SQL injection patterns are detected and logged
- strict JSON content and size limits

## Report export
Generated reports are stored in `zap-reports/`:
- `zap_baseline_report.html`
- `zap_baseline_report.json`
- `zap_full_scan_report.html`
- `zap_full_scan_report.json`

## Expected outputs
- No critical vulnerabilities
- Medium issues should be documented and reviewed
- Authentication enforcement confirmed for all AI endpoints

## Notes
When running on Windows, use `host.docker.internal` to allow the container to reach the local Flask endpoint.
