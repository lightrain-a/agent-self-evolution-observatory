#!/usr/bin/env bash
set -euo pipefail

KEY_FILE="${C1_AA_KEY_FILE:-/dev/shm/c1_aa_api_key}"
RUN_ROOT="/data/wyt/agent-self-evolution-observatory/runs/c1-pacta-msr-qwen397-source-20260902-v1"
PYTHON="/data/wyt/r17-compute-shielding-venv/bin/python"

if [[ ! -f "$KEY_FILE" ]]; then
  echo "STOP_PROVIDER_CREDENTIAL_NOT_CONFIGURED: expected local credential file $KEY_FILE" >&2
  exit 10
fi
if [[ "$(stat -c '%U' "$KEY_FILE")" != "wyt" || "$(stat -c '%a' "$KEY_FILE")" != "600" ]]; then
  echo "STOP_PROVIDER_CREDENTIAL_FILE_PERMISSIONS" >&2
  exit 11
fi
if [[ ! -s "$KEY_FILE" ]]; then
  echo "STOP_PROVIDER_CREDENTIAL_FILE_EMPTY" >&2
  exit 12
fi
if find "$RUN_ROOT" -maxdepth 1 -type d -name 'source-*' -print -quit | grep -q .; then
  echo "STOP_SOURCE_ATTEMPT_ALREADY_EXISTS" >&2
  exit 13
fi
if [[ ! -f "$RUN_ROOT/contract.json" || ! -f "$RUN_ROOT/acquisition-schedule.json" || ! -f "$RUN_ROOT/prelaunch-qualification.json" ]]; then
  echo "STOP_SOURCE_FREEZE_ARTIFACT_MISSING" >&2
  exit 14
fi

export AA_API_KEY="$(cat "$KEY_FILE")"
exec "$PYTHON" -u -m research_pipeline.run_c1_pacta_msr_source_20260902 --root "$RUN_ROOT" --phase acquire
