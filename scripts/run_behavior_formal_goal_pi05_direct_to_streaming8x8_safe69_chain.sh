#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DIRECT="$ROOT/generated/behavior-formal-goal-coupling-shared26-pi05-portable-direct-device-no-update-model-load-result-232-20260903.json"
SYNTH="$ROOT/generated/behavior-formal-goal-coupling-shared26-pi05-accum8x8-synthetic-fused-direct-device-repair2-host67-result-20260903.json"
AUTH="$ROOT/generated/behavior-formal-goal-coupling-shared26-pi05-streaming-accum8x8-safe69-authority-20260903.json"
FINAL="$ROOT/generated/behavior-formal-goal-coupling-shared26-pi05-streaming-accum8x8-safe69-result-20260903.json"
LOG=/data/wyt/formal-goal-pi05-direct-to-streaming8x8-safe69-chain-20260903.log
exec >>"$LOG" 2>&1
printf '[%s] chain start\n' "$(date --iso-8601=seconds)"
while [[ ! -e "$DIRECT" ]]; do sleep 30; done
STATUS=$(python3 -c "import json; print(json.load(open('$DIRECT')).get('status',''))")
if [[ "$STATUS" != PI05_PORTABLE_DIRECT_DEVICE_NO_UPDATE_MODEL_LOAD_PASS ]]; then
  echo "portable direct-device gate failed/held: $STATUS; no streaming authority"; exit 4
fi
while [[ ! -e "$SYNTH" ]]; do sleep 30; done
SYNTH_STATUS=$(python3 -c "import json; print(json.load(open('$SYNTH')).get('status',''))")
if [[ "$SYNTH_STATUS" != PI05_SYNTHETIC_FUSED_ACCUM8X8_DIRECT_DEVICE_REPAIR2_PASS ]]; then
  echo "synthetic fused 8x8 gate failed/held: $SYNTH_STATUS; no streaming authority"; exit 5
fi
if [[ ! -e "$AUTH" ]]; then
  python3 "$ROOT/research_pipeline/compile_behavior_formal_goal_pi05_streaming_accum8x8_safe69_authority.py" \
    --direct-result "$DIRECT" \
    --synthetic-result "$SYNTH" \
    --runner "$ROOT/research_pipeline/behavior_formal_goal_coupling_shared26_pi05_accum8x8_streaming_direct_device_dry_gradient.py" \
    --worker "$ROOT/scripts/run_behavior_formal_goal_pi05_streaming_accum8x8_safe69_worker.sh" \
    --launcher "$ROOT/scripts/run_behavior_formal_goal_pi05_streaming_accum8x8_safe69.sh" \
    --design "$ROOT/generated/behavior-formal-goal-coupling-shared26-pi05-accum8x8-streaming-direct-device-repair2-design-20260903.json" \
    --output "$AUTH"
fi
[[ ! -e "$FINAL" ]] || { echo "streaming result already exists; no replay"; exit 0; }
exec "$ROOT/scripts/run_behavior_formal_goal_pi05_streaming_accum8x8_safe69.sh"
