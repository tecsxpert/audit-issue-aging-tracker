from __future__ import annotations

from validation.ai_monitoring import monitor_ai_integrations
from validation.common import docker_compose_command, log, main_exit, run_command, wait_for_http_health
from validation.compose_validation import validate_compose
from validation.e2e_test_runner import run_e2e_suite
from validation.env_validator import validate_environment


def run_all_validations() -> None:
    validate_environment()
    compose = docker_compose_command()
    run_command([*compose, 'up', '--build', '-d'], timeout=300)
    wait_for_http_health(deadline_seconds=120)
    run_e2e_suite()
    monitor_ai_integrations(iterations=2)
    validate_compose()
    run_command([*compose, 'logs', '--tail', '120', 'ai-service'], timeout=60)
    log('automated_validation_passed')


if __name__ == '__main__':
    main_exit(run_all_validations)
