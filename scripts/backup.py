from __future__ import annotations

import argparse
import os
from pathlib import Path

from scripts.common import BACKUP_DIR, audit, run, timestamp


def backup_postgres(output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    target = output_dir / f'postgres-{timestamp()}.sql'
    user = os.getenv('POSTGRES_USER', 'tool125')
    database = os.getenv('POSTGRES_DB', 'tool125')
    result = run(['docker', 'compose', 'exec', '-T', 'postgres', 'pg_dump', '-U', user, database], timeout=300)
    target.write_text(result.stdout, encoding='utf-8')
    audit('postgres_backup_created', path=str(target))
    return target


def backup_redis(output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    run(['docker', 'compose', 'exec', '-T', 'redis', 'redis-cli', 'BGSAVE'], timeout=120, check=False)
    target = output_dir / f'redis-dump-{timestamp()}.rdb'
    run(['docker', 'compose', 'cp', 'redis:/data/dump.rdb', str(target)], timeout=120)
    audit('redis_backup_created', path=str(target))
    return target


def main() -> None:
    parser = argparse.ArgumentParser(description='Create Redis and PostgreSQL backups for Tool-125 AI service.')
    parser.add_argument('--target-dir', default=str(BACKUP_DIR))
    parser.add_argument('--postgres', action='store_true')
    parser.add_argument('--redis', action='store_true')
    args = parser.parse_args()
    output_dir = Path(args.target_dir)
    run_all = not args.postgres and not args.redis
    if args.postgres or run_all:
        backup_postgres(output_dir)
    if args.redis or run_all:
        backup_redis(output_dir)


if __name__ == '__main__':
    main()
