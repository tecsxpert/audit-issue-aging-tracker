from __future__ import annotations

from validation.ai_monitoring import monitor_ai_integrations
from validation.container_health_check import check_container_health
from validation.e2e_test_runner import run_e2e_suite
from validation.env_validator import validate_environment
from validation.startup_verification import verify_startup
from validation.common import log, main_exit


def verify_all_services() -> None:
    validate_environment()
    verify_startup()
    check_container_health()
    run_e2e_suite()
    monitor_ai_integrations(iterations=2)
    log('verify_all_services_passed')


if __name__ == '__main__':
    main_exit(verify_all_services)
