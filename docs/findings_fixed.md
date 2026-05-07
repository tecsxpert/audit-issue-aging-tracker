# Findings Fixed

## Finding 1: Authenticated Validation Coverage Gap

Severity: High

Before: E2E validation could call protected endpoints without consistently generating JWT headers.

After: `validation/auth_helper.py` generates short-lived JWTs with `sub`, `aud`, `iss`, `iat`, and `exp`. Endpoint, API flow, and E2E runners now send authenticated requests automatically.

Validation: `python -m validation.e2e_test_runner`

## Finding 2: Threaded Gunicorn Timeout Failure

Severity: High

Before: `signal.alarm` could be registered from a non-main Gunicorn thread, causing HTTP 503.

After: Timeout signal handling only uses `SIGALRM` when executing in the main thread. Threaded workers rely on Gunicorn request timeout and elapsed-time logging.

Validation: Authenticated Docker E2E completed successfully.

## Finding 3: Decommissioned Groq Model

Severity: Medium

Before: `.env` used `llama3-70b-8192`, which Groq rejected as decommissioned.

After: `.env` and `.env.example` align to `llama-3.3-70b-versatile`.

Validation: Protected AI endpoints returned HTTP 200.

## Finding 4: Redis Restart Readiness Race

Severity: Medium

Before: Compose validation read Redis immediately after restart and could hit connection refused.

After: Compose validation waits for Redis `PING` before reading persistence keys.

Validation: `python -m validation.compose_validation`

## Finding 5: Structured Security Documentation Missing

Severity: Medium

Before: Security evidence was split across several day-specific files.

After: Final enterprise-grade security package created under `SECURITY.md` and `docs/`.

Validation: Documentation review checklist in `team_security_signoff.md`.
