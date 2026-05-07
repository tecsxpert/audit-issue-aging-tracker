#!/usr/bin/env sh
set -eu

cd "$(dirname "$0")"

python -m validation.env_validator
python -m validation.final_system_check
