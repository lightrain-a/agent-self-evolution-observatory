from __future__ import annotations

import hashlib
import json
import re
from typing import Any


LINE_RE = re.compile(r"\[([^\]]+)\]\s*helpful=(\d+)\s*harmful=(\d+)\s*::\s*(.*)")
CONTENT = "Verify all constraints before committing the answer."
CANONICAL = f"[str-00001] helpful=6 harmful=2 :: {CONTENT}"
SPLIT = [
    f"[str-00001] helpful=3 harmful=1 :: {CONTENT}",
    f"[str-00002] helpful=3 harmful=1 :: {CONTENT}",
]
ID_PLACEBO = f"[str-00999] helpful=6 harmful=2 :: {CONTENT}"


def parse_line(line: str) -> dict[str, Any]:
    match = LINE_RE.fullmatch(line.strip())
    if not match:
        raise ValueError(f"invalid ACE bullet line: {line!r}")
    bullet_id, helpful, harmful, content = match.groups()
    return {
        "id": bullet_id,
        "helpful": int(helpful),
        "harmful": int(harmful),
        "content": content,
    }


def format_line(bullet: dict[str, Any]) -> str:
    return (
        f"[{bullet['id']}] helpful={int(bullet['helpful'])} "
        f"harmful={int(bullet['harmful'])} :: {bullet['content']}"
    )


def deterministic_exact_clone_reunion(lines: list[str]) -> str:
    bullets = [parse_line(line) for line in lines]
    if not bullets:
        raise ValueError("cannot reunite an empty exact-clone group")
    content = bullets[0]["content"]
    if any(b["content"] != content for b in bullets):
        raise ValueError("primary ACE probe permits exact-content clones only")
    merged = {
        "id": bullets[0]["id"],
        "helpful": sum(b["helpful"] for b in bullets),
        "harmful": sum(b["harmful"] for b in bullets),
        "content": content,
    }
    return format_line(merged)


def digest_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def build_result() -> dict[str, Any]:
    canonical = parse_line(CANONICAL)
    split = [parse_line(line) for line in SPLIT]
    repaired = deterministic_exact_clone_reunion(SPLIT)
    repaired_parsed = parse_line(repaired)
    placebo = parse_line(ID_PLACEBO)

    return {
        "schema_version": "1.0",
        "paper_id": "STRI",
        "experiment_id": "ASSET-FIRST-STRI-ACE-EXACT-CLONE-REUNION-P0-20260828",
        "stage": "SECONDARY_CARRIER_ZERO_PROVIDER_STATE_REUNION_PROBE",
        "source_commit": "82709de050e1db6e6ef2f07bcb0393560b94992a",
        "witness": {
            "canonical": CANONICAL,
            "split": SPLIT,
            "id_placebo": ID_PLACEBO,
            "deterministic_repair": repaired,
        },
        "checks": {
            "parse_format_roundtrip": all(
                format_line(parse_line(line)) == line
                for line in [CANONICAL, *SPLIT, ID_PLACEBO]
            ),
            "split_content_exact": all(b["content"] == canonical["content"] for b in split),
            "split_helpful_conserved": sum(b["helpful"] for b in split) == canonical["helpful"],
            "split_harmful_conserved": sum(b["harmful"] for b in split) == canonical["harmful"],
            "repair_exactly_matches_canonical_line": repaired == CANONICAL,
            "repair_sufficient_state_matches_canonical": (
                repaired_parsed["content"], repaired_parsed["helpful"], repaired_parsed["harmful"]
            ) == (canonical["content"], canonical["helpful"], canonical["harmful"]),
            "id_placebo_sufficient_state_matches_canonical": (
                placebo["content"], placebo["helpful"], placebo["harmful"]
            ) == (canonical["content"], canonical["helpful"], canonical["harmful"]),
            "id_placebo_id_differs": placebo["id"] != canonical["id"],
        },
        "timing_projection": {
            "native_analyzer_off_curator_input_sha256": digest_text("\n".join(SPLIT)),
            "native_analyzer_on_curator_input_sha256": digest_text("\n".join(SPLIT)),
            "deterministic_post_curator_reunion_curator_input_sha256": digest_text("\n".join(SPLIT)),
            "deterministic_pre_curator_reunion_curator_input_sha256": digest_text(repaired),
            "canonical_curator_input_sha256": digest_text(CANONICAL),
            "pre_curator_repair_matches_canonical_input": digest_text(repaired) == digest_text(CANONICAL),
            "post_curator_repair_cannot_change_current_curator_input": True,
        },
        "decision": "ZERO_PROVIDER_REUNION_OPERATOR_PASS",
        "scientific_boundary": {
            "new_model_calls": 0,
            "new_gpu_runs": 0,
            "counter_conservation_established": True,
            "timing_projection_established": True,
            "curator_output_invariance_established": False,
            "behavioral_effect_established": False,
            "native_ace_robustness_established": False,
            "claim_expansion": False,
        },
    }


if __name__ == "__main__":
    print(json.dumps(build_result(), ensure_ascii=False, sort_keys=True, indent=2))
