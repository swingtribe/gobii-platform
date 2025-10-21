#!/usr/bin/env bash
set -euo pipefail

# Ensure runtime env is generated once and sourced
CONFIG_DIR="${BOOTSTRAP_CONFIG_DIR:-/config}"
DJANGO_ENV_FILE="$CONFIG_DIR/django.env"

# Run bootstrap to create secrets/env if missing
python /app/docker/bootstrap/runtime_env.py >/dev/null 2>&1 || true

# Source env file if present
if [ -f "$DJANGO_ENV_FILE" ]; then
  set -a
  . "$DJANGO_ENV_FILE"
  set +a
fi

# Default to headless=false unless overridden (production anti-bot heuristics)
export BROWSER_HEADLESS="${BROWSER_HEADLESS:-false}"

exec "$@"