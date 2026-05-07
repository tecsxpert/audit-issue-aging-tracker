from __future__ import annotations

from validation.ai_monitoring import monitor_ai_integrations
from validation.common import (
    AI_ENDPOINTS,
    DEFAULT_ISSUE,
    ValidationConfig,
    assert_success_shape,
    auth_headers,
    log,
    main_exit,
    request_json,
    wait_for_http_health,
)
from validation.container_health_check import check_container_health
from validation.env_validator import validate_environment
from validation.security_validation import run_security_validation


def verify_ai_stack() -> None:
    config = ValidationConfig()
    validate_environment()
    wait_for_http_health(config, deadline_seconds=120)
    check_container_health()
    run_security_validation()
    _validate_ai_connectivity(config)
    monitor_ai_integrations(iterations=1)
    log('ai_stack_verification_passed')


def _validate_ai_connectivity(config: ValidationConfig) -> None:
    headers = auth_headers(config)
    for endpoint in AI_ENDPOINTS:
        status, body, latency = request_json(
            'POST',
            endpoint,
            {'issue': DEFAULT_ISSUE},
            headers=headers,
            config=config,
        )
        assert_success_shape(endpoint, status, body)
        log('ai_connectivity_check_passed', endpoint=endpoint, latency_ms=latency, score=body.get('score'))


if __name__ == '__main__':
    main_exit(verify_ai_stack)
