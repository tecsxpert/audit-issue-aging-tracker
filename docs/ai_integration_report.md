# AI Integration Report

## Integration Surface

The service integrates with Groq through `services/groq_client.py` using the OpenAI-compatible chat completions endpoint:

```text
{GROQ_API_BASE_URL}/chat/completions
```

Default model:

```text
llama-3.3-70b-versatile
```

## Validated Behaviors

- Prompt construction through `PromptBuilder`.
- Groq request retries with exponential backoff.
- HTTP error mapping to `GroqClientError`.
- Response parsing for `choices[].message.content`, `output`, and `outputs`.
- Endpoint-level fallback to structured 502 responses when Groq fails.
- Quality scoring and prompt optimization retry when the first response scores below target.

## Monitoring

Run:

```sh
python -m validation.ai_monitoring
```

The script records per-endpoint latency, response length, quality score, and success state into:

```text
validation/reports/ai_monitoring_report.json
```

## Failure Simulation

Fallback and rejection cases are stored in:

```text
validation/fallback_test_cases.json
```

These cases cover missing fields, prompt injection, SQL injection, missing JWT, and empty input.

## Production Targets

- Health endpoint p95 below 500 ms.
- AI endpoint p95 below 15 seconds.
- Zero malformed successful responses.
- All failures returned as JSON with `success=false`.
