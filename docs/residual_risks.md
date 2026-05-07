# Residual Risks

## Third-Party API Dependency

Groq availability, quota, model lifecycle, and network egress are external dependencies.

Mitigation: Retry logic, structured 502 errors, monitoring, and model configuration validation.

Residual risk: Service quality depends on provider availability and account limits.

## AI Hallucination

Generated recommendations may be plausible but incomplete or incorrect.

Mitigation: Prompt templates, quality scoring, and response validation.

Residual risk: Human review remains required for audit decisions.

## Free-Tier API Limits

Development or free-tier Groq usage can hit rate or quota limits.

Mitigation: Redis caching and monitoring.

Residual risk: Live demos may degrade if quota is exhausted.

## Container Runtime Assumptions

Security depends on Docker host patching and runtime isolation.

Mitigation: Non-root container, health checks, minimal base image.

Residual risk: Host compromise or Docker daemon exposure remains out of app scope.

## Prompt Unpredictability

Novel prompt injection variants may bypass regex checks.

Mitigation: Defense-in-depth filtering and fallback handling.

Residual risk: Ongoing prompt attack tuning is required.
