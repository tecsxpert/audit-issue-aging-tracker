from __future__ import annotations

import argparse
import os

from scripts.common import audit, compose_base, run
from scripts.health_verify import verify_health


def rollback(environment: str, image_tag: str) -> None:
    audit('rollback_started', environment=environment, image_tag=image_tag)
    env = os.environ.copy()
    env['AI_SERVICE_IMAGE'] = f'tool-125-ai-service:{image_tag}'
    env['AI_WORKER_IMAGE'] = f'tool-125-ai-service:{image_tag}'
    command = compose_base(environment) + ['up', '-d', '--no-build']
    result = run(command, timeout=180, check=False, env=env)
    if result.returncode != 0:
        audit('rollback_failed', environment=environment, image_tag=image_tag, stderr=result.stderr[-500:])
        raise RuntimeError(result.stderr)
    verify_health()
    audit('rollback_completed', environment=environment, image_tag=image_tag)


def main() -> None:
    parser = argparse.ArgumentParser(description='Rollback Tool-125 AI service to a previous image tag.')
    parser.add_argument('--environment', default='production', choices=['development', 'staging', 'production'])
    parser.add_argument('--image-tag', required=True)
    args = parser.parse_args()
    rollback(args.environment, args.image_tag)


if __name__ == '__main__':
    main()
