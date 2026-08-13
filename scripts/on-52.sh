#!/usr/bin/env bash
set -euo pipefail

EXPECTED_HOST="${EXPECTED_RESEARCH_HOST:-admin01-NF5468M5}"
ACTUAL_HOST="$(hostname)"
if [[ "${ACTUAL_HOST}" != "${EXPECTED_HOST}" ]]; then
  echo "Refusing to run: expected host ${EXPECTED_HOST}, got ${ACTUAL_HOST}." >&2
  exit 2
fi

PROJECT_ROOT="${PROJECT_ROOT:-/home/wyt/code/agent-self-evolution-observatory}"
ENV_FILE="${RESEARCH_ENV_FILE:-${PROJECT_ROOT}/.env}"
if [[ ! -f "${ENV_FILE}" ]]; then
  echo "Missing server environment file: ${ENV_FILE}" >&2
  exit 3
fi

set -a
# Accept either Unix LF or Windows CRLF without rewriting the secret file.
# shellcheck disable=SC1090
source <(tr -d '\r' < "${ENV_FILE}")
set +a

python3 -m research_pipeline --init-storage >/dev/null

if [[ "$#" -eq 0 ]]; then
  exec "${SHELL:-/bin/bash}"
fi

exec "$@"
