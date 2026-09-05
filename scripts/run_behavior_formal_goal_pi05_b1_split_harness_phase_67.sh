#!/usr/bin/env bash
set -euo pipefail
PHASE=${1:?phase required: reference|save|verify}
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PY=/data/wyt/formal-goal-shared26-openpi-env-20260901/bin/python
CHILD=/data/wyt/formal-goal-portable-openpi-child-69-20260903
PARAMS=/data/wyt/formal-goal-pi05-base-params-v1
BASE="$ROOT/generated/behavior-formal-goal-coupling-pi05-base-transport-repair1-result-20260902.json"
NORM=/data/wyt/formal-goal-checkpoint-qualification-assets-20260905/norm_stats.json
AUTH="$ROOT/generated/behavior-formal-goal-coupling-shared26-pi05-b1-split-harness-checkpoint-qualification-repair1-authority-20260905.json"
PARENT="$ROOT/generated/behavior-formal-goal-coupling-shared26-pi05-b1-serial-item-checkpoint-fingerprint-lifetime-adjudication-20260905.json"
REVIEW="$ROOT/generated/behavior-formal-goal-coupling-shared26-pi05-b1-split-harness-independent-review-20260905.json"
SOURCE="$ROOT/generated/behavior-formal-goal-coupling-shared26-pi05-b1-serial-item-checkpoint-source-adjudication-20260905.json"
STAGE_RUNNER="$ROOT/research_pipeline/behavior_formal_goal_coupling_shared26_pi05_b1_split_harness_checkpoint_stage.py"
VERIFY_RUNNER="$ROOT/research_pipeline/behavior_formal_goal_coupling_shared26_pi05_b1_split_harness_checkpoint_verify.py"
OUT=/data/wyt/formal-goal-checkpoint-save-qualification-67-20260905/b1-split-repair1-8gb-96g
REF="$ROOT/generated/behavior-formal-goal-coupling-shared26-pi05-b1-split-reference-result-67-20260905.json"
SAVE="$ROOT/generated/behavior-formal-goal-coupling-shared26-pi05-b1-split-save-stage-result-67-20260905.json"
RESULT="$ROOT/generated/behavior-formal-goal-coupling-shared26-pi05-b1-split-harness-checkpoint-qualification-result-67-20260905.json"
LOG=/data/wyt/formal-goal-b1-split-harness-${PHASE}-67-20260905.log
exec >>"$LOG" 2>&1
for f in "$AUTH" "$PARENT" "$REVIEW" "$SOURCE" "$BASE" "$NORM" "$STAGE_RUNNER" "$VERIFY_RUNNER"; do [[ -f "$f" ]] || { echo "missing input: $f"; exit 3; }; done
case "$PHASE" in
  reference)
    [[ ! -e "$OUT" && ! -e "$REF" && ! -e "$SAVE" && ! -e "$RESULT" ]] || { echo "Refusing split reference replay/stale state"; exit 2; }
    exec /usr/bin/taskset -c 0-63 /usr/bin/env \
      OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 \
      TOKENIZERS_PARALLELISM=false JAX_PLATFORMS=cuda XLA_PYTHON_CLIENT_MEM_FRACTION=0.9 \
      HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 \
      "$PY" "$STAGE_RUNNER" --mode reference \
        --authority "$AUTH" --parent-failure-adjudication "$PARENT" --review "$REVIEW" --source-adjudication "$SOURCE" \
        --openpi-child-root "$CHILD" --params-root "$PARAMS" --base-receipt "$BASE" --norm-stats "$NORM" \
        --output-root "$OUT" --receipt "$REF" --reference-receipt "$REF"
    ;;
  save)
    [[ -f "$REF" && ! -e "$OUT" && ! -e "$SAVE" && ! -e "$RESULT" ]] || { echo "Split save admission failed"; exit 2; }
    exec /usr/bin/taskset -c 0-63 /usr/bin/env \
      OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 \
      TOKENIZERS_PARALLELISM=false JAX_PLATFORMS=cuda XLA_PYTHON_CLIENT_MEM_FRACTION=0.9 \
      HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 \
      "$PY" "$STAGE_RUNNER" --mode save \
        --authority "$AUTH" --parent-failure-adjudication "$PARENT" --review "$REVIEW" --source-adjudication "$SOURCE" \
        --openpi-child-root "$CHILD" --params-root "$PARAMS" --base-receipt "$BASE" --norm-stats "$NORM" \
        --output-root "$OUT" --receipt "$SAVE" --reference-receipt "$REF"
    ;;
  verify)
    [[ -f "$REF" && -f "$SAVE" && -d "$OUT" && ! -e "$RESULT" ]] || { echo "Split verify admission failed"; exit 2; }
    exec /usr/bin/taskset -c 0-63 /usr/bin/env \
      OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 \
      JAX_PLATFORMS=cpu HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 \
      "$PY" "$VERIFY_RUNNER" \
        --authority "$AUTH" --runner "$STAGE_RUNNER" --reference-receipt "$REF" --save-receipt "$SAVE" \
        --output-root "$OUT" --result "$RESULT"
    ;;
  *) echo "unknown phase: $PHASE"; exit 2 ;;
esac
