#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PY=/data/wyt/formal-goal-shared26-openpi-env-20260901/bin/python
CHILD=/data/wyt/formal-goal-portable-openpi-child-69-20260903
PARAMS=/data/wyt/formal-goal-pi05-base-params-v1
BASE_RECEIPT="$ROOT/generated/behavior-formal-goal-coupling-pi05-base-transport-repair1-result-20260902.json"
AUTH="$ROOT/generated/behavior-formal-goal-coupling-shared26-pi05-step0-checkpoint-save-40g-qualification-authority-20260905.json"
ADJ="$ROOT/generated/behavior-formal-goal-coupling-shared26-pi05-formal-run2-checkpoint10000-failure-adjudication-20260905.json"
OUT=/data/wyt/formal-goal-checkpoint-save-qualification-67-20260905/stage-a-save-only-40g
RECEIPT="$ROOT/generated/behavior-formal-goal-coupling-shared26-pi05-step0-checkpoint-save-40g-qualification-result-67-20260905.json"
LOG=/data/wyt/formal-goal-step0-checkpoint-save-40g-qualification-67-20260905.log
exec >>"$LOG" 2>&1
[[ -f "$AUTH" && -f "$ADJ" && -f "$BASE_RECEIPT" ]] || { echo "checkpoint qualification authority/input missing"; exit 3; }
[[ ! -e "$OUT" && ! -e "$RECEIPT" ]] || { echo "Refusing qualification replay: output/receipt already exists"; exit 2; }
exec /usr/bin/taskset -c 0-63 /usr/bin/env \
  OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 \
  TOKENIZERS_PARALLELISM=false JAX_PLATFORMS=cuda XLA_PYTHON_CLIENT_MEM_FRACTION=0.9 \
  HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 \
  "$PY" "$ROOT/research_pipeline/behavior_formal_goal_coupling_shared26_pi05_step0_checkpoint_save_qualification.py" \
    --authority "$AUTH" --adjudication "$ADJ" \
    --openpi-child-root "$CHILD" --params-root "$PARAMS" --base-receipt "$BASE_RECEIPT" \
    --output-root "$OUT" --receipt "$RECEIPT"
