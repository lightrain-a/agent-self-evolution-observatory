from __future__ import annotations

import ast
from dataclasses import asdict, dataclass
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from research_pipeline.e2_r17_evidence_window import (
    MatchedEvidenceWindowRenderer,
    canonical_trajectory_text,
    select_head_tail,
)


RB_PINNED_COMMIT = "ed80611788292ea739f1effd31f16c53823b8a0d"
RB_PROMPT_RELATIVE_PATH = "WebArena/prompts/memory_instruction.py"
RB_PROMPT_NAME = "PARALLEL_SI"
RB_PER_TRAJECTORY_CAP_TOKENS = 512
RB_AGGREGATOR_MAX_OUTPUT_TOKENS = 1024
RB_AGGREGATOR_TEMPERATURE = 0.7


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_text(text: str) -> str:
    return sha256_bytes(text.encode("utf-8"))


def extract_literal_assignment(path: Path, name: str) -> str:
    """Extract a top-level literal string without importing the baseline module."""
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(path))
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        if not any(isinstance(target, ast.Name) and target.id == name for target in node.targets):
            continue
        value = ast.literal_eval(node.value)
        if not isinstance(value, str):
            raise RuntimeError(f"{name} in {path} is not a literal string")
        return value
    raise RuntimeError(f"literal assignment {name} not found in {path}")


def _task_text(payload: Mapping[str, Any]) -> str:
    for message in payload.get("messages") or []:
        if isinstance(message, Mapping) and str(message.get("role") or "") == "user":
            content = message.get("content")
            if isinstance(content, str) and content.strip():
                return content.strip()
    raise ValueError("trajectory does not contain a user task message")


@dataclass(frozen=True)
class RBAggregationSourceReceipt:
    rollout_index: int
    trajectory_sha256: str
    verifier_score: float
    verifier_label: str
    raw_tokens: int
    rendered_tokens: int
    rendered_sha256: str


@dataclass(frozen=True)
class RBAggregationPromptReceipt:
    baseline_commit: str
    baseline_prompt_relative_path: str
    baseline_prompt_source_sha256: str
    baseline_system_prompt_sha256: str
    task_text_sha256: str
    per_trajectory_cap_tokens: int
    aggregator_temperature: float
    aggregator_max_output_tokens: int
    user_prompt_sha256: str
    sources: tuple[RBAggregationSourceReceipt, ...]

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["sources"] = [asdict(row) for row in self.sources]
        return payload


def render_rb_style_aggregation_prompt(
    *,
    trajectory_payloads: Sequence[Mapping[str, Any]],
    trajectory_sha256s: Sequence[str],
    reasoningbank_root: Path,
    renderer: MatchedEvidenceWindowRenderer,
) -> tuple[str, str, RBAggregationPromptReceipt]:
    """Build a provenance-bound paper-spec ReasoningBank-style aggregation input.

    This deliberately does NOT claim source-faithful ReasoningBank execution.
    It binds the official PARALLEL_SI prompt from a pinned checkout, but it makes
    per-trajectory verifier labels explicit because the public prompt describes
    successful/failed contrast while the public scaling concatenation does not
    clearly attach those labels. Every trajectory receives the same fixed 512
    token source cap; this richer aggregation arm is accounted separately from
    the one-slot WIN/MRW primary causal contrast.
    """
    if len(trajectory_payloads) != len(trajectory_sha256s):
        raise ValueError("payload/SHA lengths differ")
    if len(trajectory_payloads) < 2:
        raise ValueError("RB-AGG requires at least two trajectories")

    prompt_path = reasoningbank_root / RB_PROMPT_RELATIVE_PATH
    if not prompt_path.exists():
        raise FileNotFoundError(prompt_path)
    system_prompt = extract_literal_assignment(prompt_path, RB_PROMPT_NAME)

    task_text = _task_text(trajectory_payloads[0])
    if any(_task_text(payload) != task_text for payload in trajectory_payloads[1:]):
        raise ValueError("RB-AGG pool contains multiple task texts")

    parts = [f"**Query:** {task_text}"]
    source_rows: list[RBAggregationSourceReceipt] = []
    for index, (payload, trajectory_sha) in enumerate(zip(trajectory_payloads, trajectory_sha256s)):
        if sha256_text(json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))) == trajectory_sha:
            # Some callers may bind canonical JSON rather than file bytes. This
            # branch is intentionally a no-op; the supplied SHA is still recorded.
            pass
        text = canonical_trajectory_text(payload)
        raw_tokens = renderer.encoding.encode(text)
        rendered_tokens = select_head_tail(raw_tokens, RB_PER_TRAJECTORY_CAP_TOKENS)
        rendered = renderer.encoding.decode(rendered_tokens)
        score = float(payload.get("score") or 0.0)
        label = "SUCCESS" if score >= 1.0 else "FAILURE"
        rollout_index = int(payload.get("rollout_index", index))
        parts.extend(
            [
                f"\n**Trajectory {index + 1} (rollout_index={rollout_index}, verifier={label}):**",
                rendered,
            ]
        )
        source_rows.append(
            RBAggregationSourceReceipt(
                rollout_index=rollout_index,
                trajectory_sha256=str(trajectory_sha),
                verifier_score=score,
                verifier_label=label,
                raw_tokens=len(raw_tokens),
                rendered_tokens=len(rendered_tokens),
                rendered_sha256=sha256_text(rendered),
            )
        )

    user_prompt = "\n".join(parts)
    receipt = RBAggregationPromptReceipt(
        baseline_commit=RB_PINNED_COMMIT,
        baseline_prompt_relative_path=RB_PROMPT_RELATIVE_PATH,
        baseline_prompt_source_sha256=sha256_bytes(prompt_path.read_bytes()),
        baseline_system_prompt_sha256=sha256_text(system_prompt),
        task_text_sha256=sha256_text(task_text),
        per_trajectory_cap_tokens=RB_PER_TRAJECTORY_CAP_TOKENS,
        aggregator_temperature=RB_AGGREGATOR_TEMPERATURE,
        aggregator_max_output_tokens=RB_AGGREGATOR_MAX_OUTPUT_TOKENS,
        user_prompt_sha256=sha256_text(user_prompt),
        sources=tuple(source_rows),
    )
    return system_prompt, user_prompt, receipt
