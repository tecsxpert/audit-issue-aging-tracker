# Emergency Demo Steps

## Five-Minute Recovery

1. Run `python -m pytest` if local Python is available.
2. Run `python -m validation.env_validator`.
3. Run `docker compose config`.
4. Start Docker Desktop if Compose cannot reach the daemon.
5. Run `docker compose up --build -d`.
6. Check `http://127.0.0.1:8000/health`.

## If Live API Is Not Available

1. Open `demo_sequence.md`.
2. Open `demo_inputs.json`.
3. Open `expected_outputs.json`.
4. Present the API call order verbally.
5. Show the expected JSON response shape.
6. Explain fallback behavior using `fallback_demo_cases.json`.

## Minimum Viable Demo

Use these three points:

- The service accepts an aged audit issue and returns AI analysis.
- Protected endpoints use JWT and input safety checks.
- The architecture supports Docker deployment, Redis caching, and controlled fallback responses.

