# E2E Testing Guide

## Purpose

The E2E suite validates the complete API path from HTTP request through JWT enforcement, sanitization, prompt construction, Groq integration, response validation, and JSON error handling.

## Start the Stack

```sh
docker compose up --build -d
```

## Run E2E

```sh
python -m validation.e2e_test_runner
```

## Individual Scripts

```sh
python -m validation.endpoint_validation
python -m validation.api_flow_test
python -m validation.ai_monitoring
```

## Endpoints Covered

- `GET /health`
- `POST /describe`
- `POST /recommend`
- `POST /generate-report`

## Assertions

- Expected HTTP status codes.
- Required JSON fields.
- AI response is non-empty and endpoint-specific.
- Error responses use the shared `success=false` structure.
- Missing JWT returns HTTP 401.
- Invalid request body returns HTTP 400.
