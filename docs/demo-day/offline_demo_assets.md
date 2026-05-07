# Offline Demo Assets

## Screenshot Placeholders

Capture these screenshots before Demo Day and store them with the presentation deck:

| Asset Name | Content To Capture |
| --- | --- |
| `01_health_success.png` | Browser or API client showing `GET /health` with `status: ok` |
| `02_describe_success.png` | `/describe` response for `AUD-001` |
| `03_recommend_success.png` | `/recommend` response for `AUD-002` |
| `04_generate_report_success.png` | `/generate-report` response for `AUD-005` |
| `05_invalid_jwt.png` | `401` structured error for missing JWT |
| `06_prompt_injection_blocked.png` | `400` structured error for prompt injection |
| `07_docker_compose_ps.png` | Docker Compose services healthy |
| `08_pytest_passed.png` | Test suite summary showing passing tests |

## Offline Response Examples

Use `expected_outputs.json` for successful AI examples and `fallback_demo_cases.json` for failure examples.

## Offline Script

If the service cannot run live, say:

This is the offline backup path. I am using the same demo inputs and the same API response shapes. The purpose is to show the product workflow, security behavior, and expected AI output even though the live runtime dependency is unavailable.

## Backup Presentation Order

1. Architecture slide.
2. Input example.
3. Expected `/describe` response.
4. Expected `/recommend` response.
5. Expected `/generate-report` response.
6. Security failure example.
7. Business value close.

