from __future__ import annotations

from validation.common import docker_compose_command, log, main_exit, run_command, wait_for_http_health
from validation.compose_validation import validate_compose
from validation.env_validator import validate_environment
from validation.verify_ai_stack import verify_ai_stack


def run_final_system_check() -> None:
    validate_environment()
    compose = docker_compose_command()
    run_command([*compose, 'up', '--build', '-d'], timeout=300)
    wait_for_http_health(deadline_seconds=120)
    verify_ai_stack()
    validate_compose()
    log('final_system_check_passed')


if __name__ == '__main__':
    main_exit(run_final_system_check)
