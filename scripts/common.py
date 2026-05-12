from __future__ import annotations

import json
import os
import subprocess
import time
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
AUDIT_DIR = REPO_ROOT / 'deployment' / 'audit'
BACKUP_DIR = REPO_ROOT / 'deployment' / 'backups'


def compose_base(environment: str = 'development') -> list[str]:
    command = ['docker', 'compose', '-f', 'docker-compose.yml']
    if environment in {'staging', 'production'}:
        command.extend(['-f', 'docker-compose.prod.yml'])
    return command


def run(
    command: list[str],
    timeout: int = 180,
    check: bool = True,
    env: dict[str, str] | None = None,
    input_text: str | None = None,
) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        command,
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=timeout,
        env=env or os.environ.copy(),
        input=input_text,
    )
    if check and result.returncode != 0:
        raise RuntimeError(
            f'Command failed: {" ".join(command)}\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}'
        )
    return result


def audit(event: str, **fields: Any) -> Path:
    AUDIT_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        'event': event,
        'generated_at_epoch': time.time(),
        **fields,
    }
    path = AUDIT_DIR / 'deployment_audit.jsonl'
    with path.open('a', encoding='utf-8') as handle:
        handle.write(json.dumps(payload, sort_keys=True) + '\n')
    return path


def timestamp() -> str:
    return time.strftime('%Y%m%d-%H%M%S', time.gmtime())
