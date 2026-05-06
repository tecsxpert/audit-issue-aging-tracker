# Secure Deployment Checklist

## Required Before Production
| Item | Status |
|---|---:|
| `GROQ_API_KEY` stored in secret manager | Required |
| `JWT_SECRET` is at least 32 random characters | Required |
| `JWT_AUTH_ENABLED=true` | Required |
| `RATE_LIMIT=30 per minute` or stricter | Required |
| Redis configured for distributed rate limiting | Required for multiple instances |
| PostgreSQL credentials stored outside source control | Required |
| TLS terminated at gateway or load balancer | Required |
| Container runs as non-root user | Complete |
| Security headers enabled | Complete |
| Healthcheck enabled | Complete |
| Logs shipped to secure sink | Required |
| Dependency scan completed | Required |
| Container image scan completed | Required |
| Final security check script passes | Required |

## Validation Commands
```bash
python -m pytest
python security/final_security_check.py --base-url https://your-ai-service.example.com
python security/stress_test.py --base-url https://your-ai-service.example.com --requests 35
```

## Runtime Monitoring
Alert on:

- repeated HTTP 401 from the same IP
- repeated HTTP 400 injection rejections
- HTTP 429 spikes
- Groq upstream failures
- unexpected HTTP 503 responses
