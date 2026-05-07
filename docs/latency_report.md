# Latency Report

## Measurement Scope
Latency is captured per evaluation case in milliseconds by `quality/evaluation_engine.py`.

The current recorded report uses offline deterministic evaluation, so latency reflects local scoring and export overhead rather than Groq API latency.

## Recorded Results
| Endpoint | Average Latency ms | Fallback Count |
|---|---:|---:|
| `/describe` | 0.0 | 0 |
| `/recommend` | 0.0 | 0 |
| `/generate-report` | 0.0 | 0 |

## Live Endpoint Mode
To measure Flask and Groq-backed latency:

```bash
python quality/ai_quality_review.py --base-url http://127.0.0.1:8000 --token <JWT>
```

## Operational Targets
| Metric | Recommended Target |
|---|---:|
| p50 endpoint latency | <= 3 seconds |
| p95 endpoint latency | <= 12 seconds |
| fallback rate | <= 5% |
| schema error rate | 0% |

## Notes
Network latency and Groq response time are intentionally excluded from the offline CI path to keep tests deterministic.
