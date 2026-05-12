from __future__ import annotations

import argparse
import json
import subprocess

from scripts.common import audit


def release_audit(version: str, git_sha: str | None = None, dry_run: bool = False) -> dict[str, str]:
    resolved_sha = git_sha or subprocess.run(['git', 'rev-parse', 'HEAD'], capture_output=True, text=True).stdout.strip()
    payload = {'version': version, 'git_sha': resolved_sha, 'dry_run': str(dry_run).lower()}
    if not dry_run:
        audit('release_tagged', **payload)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description='Record release metadata for deployment audit tracking.')
    parser.add_argument('--version', required=True)
    parser.add_argument('--git-sha')
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()
    print(json.dumps(release_audit(args.version, args.git_sha, args.dry_run), indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
