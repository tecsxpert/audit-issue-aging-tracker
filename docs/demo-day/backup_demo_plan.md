# Backup Demo Plan

## Backup Objective

Deliver the same story even if Groq, Docker, Redis, or local networking fails during the live presentation.

## Backup Materials

- `demo_inputs.json` for exact input examples.
- `expected_outputs.json` for offline AI responses.
- `fallback_demo_cases.json` for controlled error examples.
- `demo_sequence.md` for endpoint order.
- `offline_demo_assets.md` for screenshot placeholders and presentation assets.

## Offline Presentation Flow

1. Introduce the service and endpoint purpose.
2. Show the exact input from `demo_inputs.json`.
3. Show the matching expected response from `expected_outputs.json`.
4. Explain how JWT and sanitization protect the endpoint.
5. Show the fallback response shape from `fallback_demo_cases.json`.
6. Summarize the architecture using `architecture_talking_points.md`.

## Backup API Responses

Use these status codes:

| Scenario | Status |
| --- | ---: |
| Successful AI response | 200 |
| Invalid request body | 400 |
| Missing or invalid JWT | 401 |
| Request too large | 413 |
| Groq provider failure | 502 |
| Request timeout | 504 |

## Presenter Line

The live dependency is unavailable, so I am switching to the prepared offline response set. These examples use the same request bodies, response schema, and failure behavior as the running service.

