# AI Quality Report

## Summary

- Overall average: `4.93/5`
- Target met: `yes`
- Cases evaluated: `30`

## Endpoint Summary

| Endpoint | Cases | Average | Fallbacks | Schema Errors | Avg Latency ms |
|---|---:|---:|---:|---:|---:|
| `/describe` | 10 | 4.8 | 0 | 0 | 0.0 |
| `/recommend` | 10 | 5 | 0 | 0 | 0.0 |
| `/generate-report` | 10 | 5 | 0 | 0 | 0.0 |

## Case Results

| Case | Endpoint | Category | Severity | Avg | Weak Categories |
|---|---|---|---|---:|---|
| `DES-001` | `/describe` | access control | critical | 4.8 | none |
| `DES-002` | `/describe` | compliance violation | high | 4.8 | none |
| `DES-003` | `/describe` | outdated software | high | 4.8 | none |
| `DES-004` | `/describe` | missing documentation | medium | 4.8 | none |
| `DES-005` | `/describe` | security incident | critical | 4.8 | none |
| `DES-006` | `/describe` | data leakage risk | high | 4.8 | none |
| `DES-007` | `/describe` | backup failure | high | 4.8 | none |
| `DES-008` | `/describe` | infrastructure vulnerability | medium | 4.8 | none |
| `DES-009` | `/describe` | policy violation | medium | 4.8 | none |
| `DES-010` | `/describe` | configuration weakness | medium | 4.8 | none |
| `REC-001` | `/recommend` | access control | high | 5 | none |
| `REC-002` | `/recommend` | compliance violation | medium | 5 | none |
| `REC-003` | `/recommend` | outdated software | critical | 5 | none |
| `REC-004` | `/recommend` | missing documentation | low | 5 | none |
| `REC-005` | `/recommend` | security incident | high | 5 | none |
| `REC-006` | `/recommend` | data leakage risk | critical | 5 | none |
| `REC-007` | `/recommend` | backup failure | medium | 5 | none |
| `REC-008` | `/recommend` | infrastructure vulnerability | high | 5 | none |
| `REC-009` | `/recommend` | policy violation | medium | 5 | none |
| `REC-010` | `/recommend` | configuration weakness | high | 5 | none |
| `REP-001` | `/generate-report` | access control | critical | 5 | none |
| `REP-002` | `/generate-report` | compliance violation | high | 5 | none |
| `REP-003` | `/generate-report` | outdated software | medium | 5 | none |
| `REP-004` | `/generate-report` | missing documentation | medium | 5 | none |
| `REP-005` | `/generate-report` | security incident | critical | 5 | none |
| `REP-006` | `/generate-report` | data leakage risk | high | 5 | none |
| `REP-007` | `/generate-report` | backup failure | high | 5 | none |
| `REP-008` | `/generate-report` | infrastructure vulnerability | medium | 5 | none |
| `REP-009` | `/generate-report` | policy violation | low | 5 | none |
| `REP-010` | `/generate-report` | configuration weakness | medium | 5 | none |
