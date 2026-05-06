# Testing Documentation

## Overview
The Day 8 test suite is an offline, CI-friendly pytest suite for the AI service. It covers all public endpoints, Groq client behavior, JWT/security middleware, validation failures, rate limiting, malformed AI output, and response schema consistency.

Current verified result:

```text
102 passed, 1 skipped
Total coverage: 82.75% with branch coverage enabled
```

The skipped test is the optional live Groq integration test. It only runs when `RUN_GROQ_INTEGRATION=true` and a real API key is supplied.

## Test Architecture
Core files:

- `pytest.ini`: pytest discovery, markers, `pythonpath`, and default branch coverage command.
- `.coveragerc`: coverage source/omit rules and report settings.
- `tests/conftest.py`: test app factory, Flask client, JWT fixtures, mocked environment variables, high in-memory rate limit for normal tests, and an autouse live-network blocker.
- `tests/test_utils.py`: reusable JSON/schema assertions and malicious payload builders.
- Endpoint files: `test_endpoints_describe.py`, `test_endpoints_recommend.py`, `test_endpoints_generate_report.py`, and `test_endpoints_health.py`.
- Security and resilience files: `test_security.py`, `test_error_handling.py`, `test_pii_injection.py`, `test_rate_limit.py`, and `test_security_jwt.py`.
- Groq/prompt files: `test_groq.py`, `test_groq_client.py`, and `test_prompt_evaluator.py`.

## Mocking Strategy
All unit tests run without live network access.

- `tests/conftest.py` sets deterministic environment variables for Groq, JWT, limiter storage, and allowed origins.
- The autouse `block_live_groq_network` fixture patches `requests.sessions.Session.post` and fails fast if a test accidentally attempts a real API call.
- Endpoint tests patch `services.groq_client.GroqClient.generate` with deterministic success, timeout, failure, empty, or malformed outputs.
- Groq client tests replace `client.session` with `MagicMock` or a local fake response object.
- Rate limit testing uses an isolated Flask app configured with `3 per minute` so it does not throttle unrelated tests.

## Coverage Target
Minimum target: `>= 80%`

Verified coverage:

```text
TOTAL  82.75%
```

Branch coverage is enabled by default through `pytest.ini`:

```bash
python -m pytest
```

For HTML coverage:

```bash
python -m pytest --cov=. --cov-branch --cov-report=html --cov-report=term-missing
```

## Running Tests
Install dependencies:

```bash
python -m pip install -r requirements.txt
```

Run the full offline suite:

```bash
cd ai-service
python -m pytest
```

Run only security tests:

```bash
python -m pytest -m security
```

Run a single endpoint test file:

```bash
python -m pytest tests/test_endpoints_describe.py -v
```

## Expected Output
Expected successful local/CI result:

```text
collected 103 items
102 passed, 1 skipped
TOTAL 82.75%
```

No real Groq API key, Redis server, PostgreSQL server, or external network connection is required for the unit test suite.
