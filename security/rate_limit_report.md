# Rate Limit Verification Report

## Policy
Default policy:

```text
30 requests per minute per client IP
```

Configuration:

| Setting | Source |
|---|---|
| `RATE_LIMIT` | Environment, defaults to `30 per minute` |
| `RATE_LIMIT_STORAGE_URI` | Environment or `REDIS_URL` |
| Client key | `flask_limiter.util.get_remote_address` |

## Abuse Scenarios
| Scenario | Expected Result |
|---|---|
| 30 requests in one minute | Accepted unless endpoint validation fails |
| 31st request in same window | HTTP 429 |
| Repeated malicious payloads | Rejected with HTTP 400 and subject to limiter |
| Multi-instance deployment | Redis storage required for consistent enforcement |

## Validation
Automated unit validation:

```bash
python -m pytest tests/test_rate_limit.py
```

Runtime stress validation:

```bash
python security/stress_test.py --base-url http://127.0.0.1:8000 --requests 35
```

Expected stress-test signal:

```text
HTTP 429 appears after the configured threshold is exceeded.
```

## Limiter Headers
Flask-Limiter can emit rate-limit headers depending on application configuration and extension version. The service prioritizes deterministic HTTP status enforcement and JSON error shape. Production observability should track HTTP 429 counts by path and client IP.
