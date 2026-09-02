#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV=/data/wyt/formal-goal-shared26-openpi-env-20260901
OPENPI=/data/wyt/formal-goal-policy-contracts-20260828/openpi
RECEIPT="$ROOT/generated/behavior-formal-goal-coupling-shared26-pi05-portable-direct-device-no-update-model-load-result-232-20260903.json"
[[ ! -e "$RECEIPT" ]] || { echo "Refusing replay: $RECEIPT" >&2; exit 2; }
exec /usr/bin/taskset -c 0-63 /usr/bin/env \
  JAX_PLATFORMS=cuda \
  XLA_PYTHON_CLIENT_MEM_FRACTION=0.9 \
  OMP_NUM_THREADS=1 \
  MKL_NUM_THREADS=1 \
  OPENBLAS_NUM_THREADS=1 \
  NUMEXPR_NUM_THREADS=1 \
  TOKENIZERS_PARALLELISM=false \
  "$ENV/bin/python" "$ROOT/research_pipeline/behavior_formal_goal_coupling_pi05_portable_direct_device_no_update_model_load.py" \
    --openpi-child-root "$OPENPI" \
    --params-root /data/wyt/formal-goal-pi05-base-params-v1 \
    --base-receipt "$ROOT/generated/behavior-formal-goal-coupling-pi05-base-transport-repair1-result-20260902.json" \
    --authority "$ROOT/generated/behavior-formal-goal-coupling-shared26-pi05-portable-direct-device-no-update-model-load-authority-232-20260903.json" \
    --host-exit-adjudication "$ROOT/generated/behavior-formal-goal-coupling-shared26-pi05-accum8x8-attempt1-host-exit-adjudication-20260902.json" \
    --static-qualification "$ROOT/generated/behavior-formal-goal-coupling-shared26-pi05-direct-device-checkpoint-loader-static-qualification-20260902.json" \
    --portable-child-equivalence "$ROOT/generated/behavior-formal-goal-coupling-shared26-pi05-portable-openpi-child-equivalence-232-20260903.json" \
    --portable-env-qualification "$ROOT/generated/behavior-formal-goal-coupling-shared26-pi05-portable-openpi-environment-232-20260903.json" \
    --receipt "$RECEIPT"
