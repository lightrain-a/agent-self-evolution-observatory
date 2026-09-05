#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PY=/data/wyt/formal-goal-shared26-openpi-env-20260901/bin/python
CHILD=/data/wyt/formal-goal-portable-openpi-child-69-20260903
PARAMS=/data/wyt/formal-goal-pi05-base-params-v1
BASE="$ROOT/generated/behavior-formal-goal-coupling-pi05-base-transport-repair1-result-20260902.json"
NORM=/data/wyt/formal-goal-checkpoint-qualification-assets-20260905/norm_stats.json
AUTH="$ROOT/generated/behavior-formal-goal-coupling-shared26-pi05-b1-serial-item-checkpoint-qualification-authority-20260905.json"
PARENT="$ROOT/generated/behavior-formal-goal-coupling-shared26-pi05-checkpoint-save-96g-resource-failure-adjudication-20260905.json"
REVIEW="$ROOT/generated/behavior-formal-goal-coupling-shared26-pi05-b1-serial-item-checkpoint-independent-review-20260905.json"
SOURCE="$ROOT/generated/behavior-formal-goal-coupling-shared26-pi05-b1-serial-item-checkpoint-source-adjudication-20260905.json"
SAVE_RUNNER="$ROOT/research_pipeline/behavior_formal_goal_coupling_shared26_pi05_b1_serial_item_checkpoint_save.py"
VERIFY_RUNNER="$ROOT/research_pipeline/behavior_formal_goal_coupling_shared26_pi05_b1_serial_item_checkpoint_verify.py"
OUT=/data/wyt/formal-goal-checkpoint-save-qualification-67-20260905/b1-serial-item-8gb-96g
STAGE="$ROOT/generated/behavior-formal-goal-coupling-shared26-pi05-b1-serial-item-checkpoint-save-stage-result-67-20260905.json"
RESULT="$ROOT/generated/behavior-formal-goal-coupling-shared26-pi05-b1-serial-item-checkpoint-qualification-result-67-20260905.json"
LOG=/data/wyt/formal-goal-b1-serial-item-checkpoint-qualification-67-20260905.log
exec >>"$LOG" 2>&1
for f in "$AUTH" "$PARENT" "$REVIEW" "$SOURCE" "$BASE" "$NORM" "$SAVE_RUNNER" "$VERIFY_RUNNER"; do [[ -f "$f" ]] || { echo "missing input: $f"; exit 3; }; done
[[ ! -e "$OUT" && ! -e "$STAGE" && ! -e "$RESULT" ]] || { echo "Refusing B1 replay: output/stage/result already exists"; exit 2; }
/usr/bin/taskset -c 0-63 /usr/bin/env \
  OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 \
  TOKENIZERS_PARALLELISM=false JAX_PLATFORMS=cuda XLA_PYTHON_CLIENT_MEM_FRACTION=0.9 \
  HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 \
  "$PY" "$SAVE_RUNNER" \
    --authority "$AUTH" --parent-failure-adjudication "$PARENT" --review "$REVIEW" --source-adjudication "$SOURCE" \
    --openpi-child-root "$CHILD" --params-root "$PARAMS" --base-receipt "$BASE" --norm-stats "$NORM" \
    --output-root "$OUT" --receipt "$STAGE"
/usr/bin/taskset -c 0-63 /usr/bin/env \
  OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 \
  JAX_PLATFORMS=cpu HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 \
  "$PY" "$VERIFY_RUNNER" \
    --authority "$AUTH" --runner "$SAVE_RUNNER" --save-receipt "$STAGE" --output-root "$OUT" --result "$RESULT"
