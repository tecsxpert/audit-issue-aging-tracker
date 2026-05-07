# Quick Reference

## Endpoints

| Endpoint | Method | Auth | Purpose |
| --- | --- | --- | --- |
| `/health` | GET | No | Service and dependency status |
| `/describe` | POST | JWT | Explain audit issue risk and impact |
| `/recommend` | POST | JWT | Generate prioritized remediation guidance |
| `/generate-report` | POST | JWT | Generate stakeholder-ready report |

## Protected Request Body

```json
{
  "issue": "Critical VPN appliance vulnerability remains unpatched for 47 days on the finance network segment, exposing remote access infrastructure to known exploit activity."
}
```

## Required Headers

```text
Authorization: Bearer <valid-demo-jwt>
Content-Type: application/json
```

## Common Commands

```sh
python -m pytest
python -m validation.env_validator
docker compose config
docker compose up --build -d
docker compose ps
docker compose logs ai-service --tail 80
docker compose restart ai-service
docker compose down
```

## Status Codes

| Status | Meaning |
| ---: | --- |
| 200 | Successful response |
| 400 | Invalid body, unsafe input, or wrong content type |
| 401 | Missing or invalid JWT |
| 413 | Request body too large |
| 429 | Rate limit exceeded |
| 502 | Groq provider failure |
| 503 | Internal service failure handled gracefully |
| 504 | Request timeout |

## Troubleshooting Quick Reference

| Problem | First Action |
| --- | --- |
| Groq failure | Check API key, quota, network, then use offline outputs |
| Docker failure | Start Docker Desktop and rerun Compose |
| Redis unhealthy | Restart Redis container |
| Invalid JWT | Regenerate token with matching secret, issuer, and audience |
| Timeout | Retry with shorter input and check provider latency |
| Prompt blocked | Use clean audit issue text without instruction override language |

