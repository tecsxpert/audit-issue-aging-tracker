from __future__ import annotations

import time

from validation.api_flow_test import run_api_flow
from validation.auth_helper import generate_test_jwt
from validation.common import ValidationConfig, log, main_exit, wait_for_http_health
from validation.endpoint_validation import validate_endpoints


def run_e2e_suite() -> None:
    config = ValidationConfig()
    started = time.perf_counter()
    log('e2e_suite_start', base_url=config.base_url)
    generate_test_jwt(subject='day11-e2e-preflight')
    wait_for_http_health(config)
    validate_endpoints()
    run_api_flow()
    elapsed_ms = round((time.perf_counter() - started) * 1000, 2)
    log('e2e_suite_passed', elapsed_ms=elapsed_ms)


if __name__ == '__main__':
    main_exit(run_e2e_suite)
