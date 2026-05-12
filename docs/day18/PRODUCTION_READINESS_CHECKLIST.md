# Production Readiness Checklist

- [ ] CI workflow passes on pull request.
- [ ] Docker build check passes.
- [ ] `docker compose -f docker-compose.yml -f docker-compose.prod.yml config` passes.
- [ ] `python -m pytest` passes.
- [ ] `python -m validation.day18_deployment_validation --static-only` passes.
- [ ] Runtime `/health` returns `status: ok`.
- [ ] Runtime `/metrics` exposes Prometheus metrics.
- [ ] Runtime `/tasks/health` reports queue status.
- [ ] Groq API key is injected through secrets, not committed.
- [ ] JWT secret is at least 32 characters and injected through secrets.
- [ ] PostgreSQL password is injected through secrets.
- [ ] Redis and PostgreSQL backups have been tested.
- [ ] Rollback image tag is known before deployment.
- [ ] Deployment audit log is retained.
