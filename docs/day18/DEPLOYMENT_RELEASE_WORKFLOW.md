# Day 18 Deployment and Release Workflow

## CI/CD Coverage

GitHub Actions now includes:

- `ai-service-ci.yml`: compile check, Ruff lint, pytest, pip-audit, Bandit, Day 18 static validation, Docker build, and Compose config validation.
- `ai-service-release.yml`: tag-driven release image build and publish to GitHub Container Registry.

## Environment Strategy

Environment examples are stored in `deployment/env/`:

- `.env.development.example`
- `.env.staging.example`
- `.env.production.example`

Production secrets must be injected by the deployment platform or secret manager. Do not commit real Groq API keys, JWT secrets, database passwords, or bearer tokens.

## Deployment Commands

```sh
python scripts/deploy.py --environment production --version 0.18.0
python scripts/health_verify.py --base-url http://127.0.0.1:8000
python -m validation.day18_deployment_validation
```

## Rollback

```sh
python scripts/rollback.py --environment production --image-tag previous-tag
```

Rollback writes an audit event to `deployment/audit/deployment_audit.jsonl`.

## Backup and Recovery

```sh
python scripts/backup.py
python scripts/backup.py --postgres
python scripts/backup.py --redis
```

Backups are written under `deployment/backups/`. Restore operations should be reviewed before execution and are audited through `scripts/restore.py`.

## Release Tagging

Use tags like:

```sh
git tag ai-service-v0.18.0
git push origin ai-service-v0.18.0
```

The release workflow builds and publishes the image with the version tag and `latest`.
