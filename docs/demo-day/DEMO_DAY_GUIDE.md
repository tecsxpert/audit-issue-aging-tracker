# Demo Day Preparation Guide

## Folder Structure

```text
ai-service/
  docs/
    demo-day/
      AI_DEMO_SCRIPT.md
      demo_flow.md
      demo_sequence.md
      demo_inputs.json
      expected_outputs.json
      fallback_demo_cases.json
      technical_explanation.md
      architecture_talking_points.md
      non_technical_explanation.md
      business_value_summary.md
      DEMO_TROUBLESHOOTING.md
      emergency_demo_steps.md
      demo_validation_report.md
      live_demo_checklist.md
      backup_demo_plan.md
      offline_demo_assets.md
      DEMO_DAY_GUIDE.md
      SPEAKING_NOTES.md
      QUICK_REFERENCE.md
```

## Preparation Timeline

### Day Before

1. Confirm `.env` values are present.
2. Run `python -m pytest`.
3. Run `python -m validation.env_validator`.
4. Start Docker and run `docker compose up --build -d`.
5. Capture screenshots listed in `offline_demo_assets.md`.
6. Rehearse `AI_DEMO_SCRIPT.md`.

### One Hour Before

1. Start Docker Desktop.
2. Run `docker compose up --build -d`.
3. Run `docker compose ps`.
4. Call `/health`.
5. Test one protected AI endpoint with a valid JWT.
6. Open backup files.

### Five Minutes Before

1. Keep terminal, API client, and backup docs open.
2. Confirm internet access.
3. Keep the demo input copied.
4. Prepare to switch to offline mode if needed.

## Demo Architecture Overview

The service is a Flask API that receives audit issue text, validates the request, builds a controlled prompt, calls Groq, optionally uses Redis cache, scores the response, and returns structured JSON. Docker Compose provides the AI service, Redis, and PostgreSQL dependencies.

## Demo Workflow

1. Show `/health`.
2. Show `/describe`.
3. Show `/recommend`.
4. Show `/generate-report`.
5. Show one security rejection.
6. Explain architecture.
7. Explain business value.
8. Mention fallback plan.

## Readiness Definition

The demo is ready when the API starts, `/health` returns `200`, one authenticated AI request succeeds, one negative security test fails safely, and offline materials are open.

