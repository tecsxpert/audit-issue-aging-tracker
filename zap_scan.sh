#!/usr/bin/env bash
set -euo pipefail

TARGET_URL=${1:-http://host.docker.internal:8000}
REPORT_DIR=${2:-zap-reports}

mkdir -p "$REPORT_DIR"

echo "Running OWASP ZAP baseline scan against $TARGET_URL"
docker run --rm -v "$PWD":"$PWD" -w "$PWD" owasp/zap2docker-stable \
  zap-baseline.py \
  -t "$TARGET_URL" \
  -r "$REPORT_DIR/zap_baseline_report.html" \
  -j "$REPORT_DIR/zap_baseline_report.json" \
  -I

echo "Running OWASP ZAP full active scan against $TARGET_URL"
docker run --rm -v "$PWD":"$PWD" -w "$PWD" owasp/zap2docker-stable \
  zap-full-scan.py \
  -t "$TARGET_URL" \
  -r "$REPORT_DIR/zap_full_scan_report.html" \
  -j "$REPORT_DIR/zap_full_scan_report.json" \
  -I

echo "Completed ZAP scans. Reports are available in $REPORT_DIR."
