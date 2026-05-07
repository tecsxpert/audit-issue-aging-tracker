# AI Testing Guide

## Test Modes
The quality framework supports two modes.

Offline mode uses deterministic reference responses and requires no network access:

```bash
python quality/ai_quality_review.py
```

Endpoint mode calls a running Flask service:

```bash
python quality/ai_quality_review.py --base-url http://127.0.0.1:8000 --token <JWT>
```

## Datasets
| File | Purpose |
|---|---|
| `quality/data/sample_inputs.json` | Source library of 30 enterprise audit issues |
| `quality/data/endpoint_test_cases.json` | Endpoint-mapped cases with expected terms |

## Reports
| File | Purpose |
|---|---|
| `docs/ai_quality_report.md` | Generated case and endpoint summary |
| `docs/endpoint_accuracy_report.md` | Endpoint-level accuracy conclusion |
| `docs/benchmark_results.md` | Benchmark summary |
| `docs/latency_report.md` | Latency and fallback analysis |
| `quality/results/quality_dashboard_data.json` | Machine-readable dashboard data |

## Unit Tests
Run quality framework tests:

```bash
python -m pytest tests/test_day10_quality_framework.py
```

Run the full suite:

```bash
python -m pytest
```

## Interpreting Scores
| Score | Meaning |
|---:|---|
| 5 | Excellent response with strong grounding and structure |
| 4 | Production-acceptable response with minor improvement opportunity |
| 3 | Usable but needs prompt tuning or validation |
| 2 | Weak response requiring review |
| 1 | Failing response |

## Release Rule
Do not approve AI response quality if the overall average is below 4.0 or any endpoint has repeated schema errors.
