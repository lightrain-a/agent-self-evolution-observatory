#!/bin/bash
set -euo pipefail

# Run-local PostTrainBench adapter for a two-segment intervention protocol.
# This file is deliberately outcome-free: it only controls when an already-frozen
# continuation instruction is delivered. Scientific validity is decided from the
# resulting trace and evaluator outputs outside this adapter.

: "${PROMPT:?PROMPT is required}"
: "${AGENT_CONFIG:?AGENT_CONFIG is required}"
: "${PTB_INTERVENTION_ARM:?PTB_INTERVENTION_ARM is required}"

BOUNDARY_MARKER="PTB_INTERVENTION_BOUNDARY_READY"
ARM="$(printf '%s' "$PTB_INTERVENTION_ARM" | tr '[:lower:]' '[:upper:]')"
BACKEND="${PTB_SESSION_BACKEND:-claude}"
PHASE1_TRACE="${PTB_PHASE1_TRACE:-/home/ben/task/intervention_phase1.jsonl}"
PHASE2_TRACE="${PTB_PHASE2_TRACE:-/home/ben/task/intervention_phase2.jsonl}"

case "$ARM" in
  PRE_STRATEGY|POST_STRATEGY|POST_EXECUTION|POST_CONFLICT_FREE) ;;
  *) echo "unsupported PTB_INTERVENTION_ARM=$ARM" >&2; exit 64 ;;
esac

load_payload() {
  local file_name="$1"
  local b64_name="$2"
  local file_value=""
  local b64_value=""
  if declare -p "$file_name" >/dev/null 2>&1; then
    file_value="${!file_name}"
  fi
  if declare -p "$b64_name" >/dev/null 2>&1; then
    b64_value="${!b64_name}"
  fi
  if [ -n "$b64_value" ]; then
    printf '%s' "$b64_value" | base64 -d
    return
  fi
  if [ -n "$file_value" ] && [ -s "$file_value" ]; then
    cat "$file_value"
    return
  fi
  echo "required intervention payload missing/empty: $file_name or $b64_name" >&2
  return 65
}

STRATEGY_INSTRUCTION="$(load_payload PTB_STRATEGY_INSTRUCTION_FILE PTB_STRATEGY_INSTRUCTION_B64)"
EXECUTION_CONTROL="$(load_payload PTB_EXECUTION_CONTROL_FILE PTB_EXECUTION_CONTROL_B64)"
CONFLICT_FREE_STRATEGY="$(load_payload PTB_CONFLICT_FREE_STRATEGY_FILE PTB_CONFLICT_FREE_STRATEGY_B64)"

# The phase-1 agent must not inherit future-arm identity or payload locations/content.
# These values remain only as non-exported parent-shell variables after this point.
unset PTB_INTERVENTION_ARM PTB_SESSION_BACKEND \
  PTB_STRATEGY_INSTRUCTION_FILE PTB_EXECUTION_CONTROL_FILE PTB_CONFLICT_FREE_STRATEGY_FILE \
  PTB_STRATEGY_INSTRUCTION_B64 PTB_EXECUTION_CONTROL_B64 PTB_CONFLICT_FREE_STRATEGY_B64 \
  PTB_ADAPTER_B64

BOUNDARY_PROTOCOL=$(cat <<'EOF'
## Segmented intervention checkpoint protocol
Work normally and autonomously until the first training command that actually updates model parameters has completed successfully. Script writing, data preparation, package installation, evaluation-only commands, checkpoint copying, and failed launches do not count as the boundary. Immediately after that first successful parameter-update run returns, stop the current agent segment. Do not plan or execute a second training experiment. End the segment with the exact standalone marker:
PTB_INTERVENTION_BOUNDARY_READY
You may receive a continuation message after the checkpoint. Do not speculate about its contents before it arrives.
EOF
)

INITIAL_PROMPT="$PROMPT"
if [ "$ARM" = "PRE_STRATEGY" ]; then
  INITIAL_PROMPT+=$'\n\n## Binding strategy instruction\n'
  INITIAL_PROMPT+="$STRATEGY_INSTRUCTION"
fi
INITIAL_PROMPT+=$'\n\n'
INITIAL_PROMPT+="$BOUNDARY_PROTOCOL"

case "$ARM" in
  PRE_STRATEGY)
    CONTINUATION_PROMPT="The checkpoint boundary has been verified. Continue the assigned post-training task autonomously under the original objective. No new strategy-level guidance is supplied in this continuation."
    ;;
  POST_STRATEGY)
    CONTINUATION_PROMPT=$'## Binding strategy instruction\n'
    CONTINUATION_PROMPT+="$STRATEGY_INSTRUCTION"
    ;;
  POST_EXECUTION)
    CONTINUATION_PROMPT=$'## Binding execution-level correction\n'
    CONTINUATION_PROMPT+="$EXECUTION_CONTROL"
    ;;
  POST_CONFLICT_FREE)
    CONTINUATION_PROMPT=$'## Binding conflict-free strategy extension\n'
    CONTINUATION_PROMPT+="$CONFLICT_FREE_STRATEGY"
    ;;
esac

sha256_text() {
  printf '%s' "$1" | sha256sum | awk '{print $1}'
}

echo "PTB_INTERVENTION_PROTOCOL arm=$ARM backend=$BACKEND boundary=$BOUNDARY_MARKER strategy_sha256=$(sha256_text "$STRATEGY_INSTRUCTION")"

if [ "${PTB_SKIP_AGENT_UPDATE:-0}" != "1" ] && [ -x /home/ben/update_agent_cli.sh ]; then
  case "$BACKEND" in
    claude) bash /home/ben/update_agent_cli.sh claude ;;
    codex) bash /home/ben/update_agent_cli.sh codex ;;
  esac
fi

run_phase1() {
  case "$BACKEND" in
    claude)
      printf '%s' "$INITIAL_PROMPT" | claude --print --verbose --model "$AGENT_CONFIG" \
        --output-format stream-json --thinking-display summarized --dangerously-skip-permissions
      ;;
    codex)
      printf '%s' "$INITIAL_PROMPT" | codex --search exec --json \
        -c model_reasoning_summary=detailed --skip-git-repo-check --yolo --model "$AGENT_CONFIG"
      ;;
    *) echo "unsupported PTB_SESSION_BACKEND=$BACKEND" >&2; return 64 ;;
  esac
}

run_phase2() {
  case "$BACKEND" in
    claude)
      printf '%s' "$CONTINUATION_PROMPT" | claude --print --verbose --continue --model "$AGENT_CONFIG" \
        --output-format stream-json --thinking-display summarized --dangerously-skip-permissions
      ;;
    codex)
      printf '%s' "$CONTINUATION_PROMPT" | codex --search exec resume --last --json \
        -c model_reasoning_summary=detailed --skip-git-repo-check --yolo --model "$AGENT_CONFIG" -
      ;;
  esac
}

rm -f "$PHASE1_TRACE" "$PHASE2_TRACE"
run_phase1 | tee "$PHASE1_TRACE"

MARKER_COUNT=$(grep -Foc "$BOUNDARY_MARKER" "$PHASE1_TRACE" || true)
if [ "$MARKER_COUNT" -ne 1 ]; then
  echo "PTB_INTERVENTION_PROTOCOL_INVALID expected exactly one boundary marker, found $MARKER_COUNT" >&2
  exit 66
fi

# This is intentionally not treated as scientific verification. It only proves that the
# delivery boundary was reached. The post-run trace audit must still verify that a successful
# parameter update preceded this marker.
echo "PTB_INTERVENTION_BOUNDARY_ACCEPTED arm=$ARM continuation_sha256=$(sha256_text "$CONTINUATION_PROMPT")"
run_phase2 | tee "$PHASE2_TRACE"
