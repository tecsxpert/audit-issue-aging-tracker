# Benchmark Results

## Benchmark Mode
The recorded benchmark uses the offline deterministic responder. This validates the quality framework, scoring pipeline, schema checks, exports, and dashboard generation without requiring live Groq access.

## Results
| Metric | Value |
|---|---:|
| Cases evaluated | 30 |
| Overall quality average | 4.93 |
| Target average | 4.0 |
| Fallback rate | 0% |
| Schema error count | 0 |
| Endpoint count | 3 |

## Endpoint Breakdown
| Endpoint | Cases | Average | Fallbacks | Schema Errors |
|---|---:|---:|---:|---:|
| `/describe` | 10 | 4.8 | 0 | 0 |
| `/recommend` | 10 | 5.0 | 0 | 0 |
| `/generate-report` | 10 | 5.0 | 0 | 0 |

## Command
```bash
python quality/ai_quality_review.py
```

## Output Artifacts
- `quality/results/quality_dashboard_data.json`
- `docs/ai_quality_report.md`
