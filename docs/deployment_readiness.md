# Deployment Readiness

## Automated Gate

```sh
python -m validation.automated_validation
```

This gate validates:

- Environment configuration.
- Compose startup.
- Health readiness.
- All AI endpoints.
- Redis connectivity.
- AI monitoring samples.
- Restart behavior.
- Recent service logs.

## Readiness Decision

The service is deployment-ready when:

- The automated gate exits with code `0`.
- `pytest` exits with code `0`.
- No secret values appear in logs.
- All generated validation reports are attached to the Day 11 submission.

## Generated Evidence

- `validation/reports/ai_monitoring_report.json`
- Docker Compose logs from `ai-service`
- Test output from `pytest`
- E2E output from `validation.e2e_test_runner`
