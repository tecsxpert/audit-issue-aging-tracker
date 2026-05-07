# Demo Flow

## Primary Flow

1. Confirm service status with `GET /health`.
2. Present a realistic audit issue from `demo_inputs.json`.
3. Call `POST /describe` to explain the issue.
4. Call `POST /recommend` to generate remediation guidance.
5. Call `POST /generate-report` to produce a structured report.
6. Explain the Flask, Groq, Redis, JWT, and Docker architecture.
7. Show one controlled failure case, such as missing JWT or prompt injection rejection.
8. Close with the business value and backup workflow.

## Recommended Timing

| Segment | Time | Purpose |
| --- | ---: | --- |
| Opening | 20 sec | Identify Tool-125 and the AI service |
| Health check | 20 sec | Prove runtime readiness |
| `/describe` | 40 sec | Show issue explanation |
| `/recommend` | 40 sec | Show prioritized remediation |
| `/generate-report` | 45 sec | Show audit-ready reporting |
| Architecture | 60 sec | Explain technical design |
| Security | 40 sec | Explain protections |
| Fallback | 25 sec | Show reliability posture |
| Close | 10 sec | Summarize value |

## Feature Transitions

From health to describe:

The service is running, so now I will use a real aged audit issue and show how the AI translates it into operational context.

From describe to recommend:

The issue is now clear. Next, I will ask the AI to produce an actionable remediation path.

From recommend to report:

The remediation plan is useful for engineers. The next endpoint reformats the same risk for audit and leadership review.

From report to security:

The AI output is only half of the service. The other half is controlling how requests reach the model.

From security to fallback:

Finally, because demos and production systems can face dependency failures, the service uses predictable fallback responses and an offline backup workflow.

## Fallback Flow

If live Groq calls fail:

1. Keep the service running.
2. Show `/health`.
3. Show the `502` structured error response.
4. Open `expected_outputs.json`.
5. Present the offline response for the same input.
6. Explain that Redis and Flask remain available while the external AI provider is degraded.

