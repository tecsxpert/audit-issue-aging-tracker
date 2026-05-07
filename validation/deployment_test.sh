#!/usr/bin/env sh
set -eu

cd "$(dirname "$0")/.."

if docker compose version >/dev/null 2>&1; then
  COMPOSE="docker compose"
else
  COMPOSE="docker-compose"
fi

$COMPOSE config >/dev/null
$COMPOSE up --build -d
python -m validation.e2e_test_runner
python -m validation.compose_validation
$COMPOSE logs --tail 120 ai-service
