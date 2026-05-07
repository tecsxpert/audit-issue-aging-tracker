from __future__ import annotations

import time

from validation.common import docker_compose_command, log, main_exit, run_command, wait_for_http_health


def validate_compose() -> None:
    compose = docker_compose_command()
    run_command([*compose, 'config'], timeout=60)
    run_command([*compose, 'up', '--build', '-d'], timeout=300)
    wait_for_http_health(deadline_seconds=120)
    run_command([*compose, 'ps'], timeout=60)
    run_command([*compose, 'restart', 'ai-service'], timeout=120)
    wait_for_http_health(deadline_seconds=120)
    run_command([*compose, 'exec', '-T', 'redis', 'redis-cli', 'set', 'day11:persistence', 'ok'], timeout=60)
    run_command([*compose, 'restart', 'redis'], timeout=120)
    wait_for_redis(compose)
    redis_value = run_command(
        [*compose, 'exec', '-T', 'redis', 'redis-cli', 'get', 'day11:persistence'],
        timeout=60,
    ).stdout.strip()
    if redis_value != 'ok':
        raise AssertionError(f'Redis persistence check failed, expected ok and got {redis_value!r}.')
    log('compose_validation_passed')


def wait_for_redis(compose: list[str], deadline_seconds: int = 60) -> None:
    deadline = time.monotonic() + deadline_seconds
    while time.monotonic() < deadline:
        result = run_command_allow_failure([*compose, 'exec', '-T', 'redis', 'redis-cli', 'ping'], timeout=30)
        if result.returncode == 0 and 'PONG' in result.stdout:
            log('redis_ready_after_restart')
            return
        time.sleep(2)
    raise RuntimeError('Redis did not become ready after restart.')


def run_command_allow_failure(command: list[str], timeout: int = 120):
    import subprocess
    from validation.common import REPO_ROOT

    log('command_start', command=' '.join(command))
    result = subprocess.run(command, cwd=REPO_ROOT, capture_output=True, text=True, timeout=timeout)
    log('command_finish', command=' '.join(command), returncode=result.returncode)
    return result


if __name__ == '__main__':
    main_exit(validate_compose)
