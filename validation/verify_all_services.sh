#!/usr/bin/env sh
set -eu

cd "$(dirname "$0")/.."

python -m validation.env_validator
python -m validation.startup_verification
python -m validation.container_health_check
python -m validation.e2e_test_runner
python -m validation.ai_monitoring
