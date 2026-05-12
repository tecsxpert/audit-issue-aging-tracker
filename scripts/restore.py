from __future__ import annotations

import argparse
import os
from pathlib import Path

from scripts.common import audit, run


def restore_postgres(sql_file: Path) -> None:
    if not sql_file.exists():
        raise FileNotFoundError(sql_file)
    user = os.getenv('POSTGRES_USER', 'tool125')
    database = os.getenv('POSTGRES_DB', 'tool125')
    sql = sql_file.read_text(encoding='utf-8')
    result = run(
        ['docker', 'compose', 'exec', '-T', 'postgres', 'psql', '-U', user, database],
        timeout=300,
        check=False,
        input_text=sql,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr)
    audit('postgres_restore_requested', path=str(sql_file))


def main() -> None:
    parser = argparse.ArgumentParser(description='Restore backup assets. PostgreSQL restore records an audit event and validates input.')
    parser.add_argument('--postgres-sql')
    args = parser.parse_args()
    if args.postgres_sql:
        restore_postgres(Path(args.postgres_sql))


if __name__ == '__main__':
    main()
