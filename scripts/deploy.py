from __future__ import annotations

import argparse

from scripts.common import audit, compose_base, run
from scripts.health_verify import verify_health


def deploy(environment: str, version: str, skip_health: bool = False) -> None:
    audit('deployment_started', environment=environment, version=version)
    command = compose_base(environment) + ['up', '--build', '-d']
    run(command, timeout=300)
    if not skip_health:
        verify_health()
    audit('deployment_completed', environment=environment, version=version)


def main() -> None:
    parser = argparse.ArgumentParser(description='Deploy Tool-125 AI service with Docker Compose.')
    parser.add_argument('--environment', default='development', choices=['development', 'staging', 'production'])
    parser.add_argument('--version', default='local')
    parser.add_argument('--skip-health', action='store_true')
    args = parser.parse_args()
    deploy(args.environment, args.version, args.skip_health)


if __name__ == '__main__':
    main()
