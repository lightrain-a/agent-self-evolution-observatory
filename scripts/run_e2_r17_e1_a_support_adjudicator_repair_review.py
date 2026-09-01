#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import scripts.run_e2_r17_v3_1_review as base

REPAIR = ROOT / "generated/e2-r17-e1-a-support-adjudicator-zero-parse-repair-20260828.json"
IDENTITY = ROOT / "generated/e2-r17-e1-a-v2-1-model-identity-qualification-20260828.json"
OUT_ROOT = ROOT / "generated/e2-r17-e1-a-support-adjudicator-repair-review-20260828"


def schema() -> dict[str, Any]:
    return {
        "repair_sha256_acknowledged": "",
        "verdict": "PASS_TO_REPAIRED_SUPPORT_ADJUDICATION|REVISE_REPAIR|STOP",
        "zero_parse_bug_assessment": "",
        "delta_scope_assessment": "",
        "post_outcome_selection_risk_assessment": "",
        "support_logic_unchanged_assessment": "",
        "authority_boundary_assessment": "",
        "remaining_blockers": [
            {"priority": "P0|P1", "issue": "", "why_blocking": "", "exact_repair": ""}
        ],
        "nonblocking_notes": [""],
        "mechanical_pilot_recommendation": "HOLD|STOP",
        "provider_runtime_pilot_recommendation": "HOLD|STOP",
        "e1_a_recommendation": "ALLOW_REPAIRED_SUPPORT_ADJUDICATION_ONLY|HOLD|STOP",
        "e1_b_recommendation": "HOLD|STOP",
        "paper_claim_authority": False,
        "single_sentence_verdict": "",
    }


def prompt_for(model: str, bound: str, repair_sha: str) -> str:
    spec = json.dumps(schema(), ensure_ascii=False, indent=2)
    return f"""You are an independent adversarial reviewer for a post-run mechanical adjudicator repair in E2-R17 E1-A. You are blind to the other reviewer. You must NOT infer or request any mixed-pool/support result; those statistics have not been exposed to the operator before this repair. This review has zero E1-B, paper, frontend, or submission authority.

Reviewer endpoint: {model}
Exact repair artifact SHA-256: {repair_sha}

The frozen E1-A run has completed its predeclared 12 streams / 768 rollout refs with zero technical failures. The first invocation of the independently bound support adjudicator stopped before support computation because its precondition used `int(summary.get('updater_calls') or -1) == 0`. In Python, legitimate integer 0 is falsy, so this maps 0 to -1 and rejects a valid zero-updater summary. No mixed/exposed/family support value was read before deciding the repair.

A new versioned adjudicator is proposed. Its diff against the original must be exactly one semantic line: explicit `is not None` plus `int(summary['updater_calls']) == 0`. The original file remains untouched. Audit the bound repair JSON and both source files.

Questions:
1. Is the diagnosed Python falsy-zero bug real and sufficient to explain the precondition failure without consulting support outcomes?
2. Is the repaired file's only difference the zero-updater parsing line? Confirm that mixed-pool recomputation, per-stream exposure, family support, thresholds, trajectory SHA validation, PASS/STOP status, and authority logic are byte/semantically unchanged otherwise.
3. Because this repair occurs after pool generation, is it acceptably outcome-independent given that no support values were inspected and the repair cannot change any support statistic or threshold? Flag any plausible p-hacking path.
4. Does accepting explicit zero while rejecting missing/nonzero updater_calls preserve the intended E1-A no-updater invariant?
5. May this repaired adjudicator be run once on the already-frozen E1-A summary/pools solely to produce the predeclared support PASS/STOP decision? Even on PASS, E1-B must remain HOLD pending a separate immutable contract/review.

Return exactly one JSON object and no markdown using this schema:
{spec}

Set `repair_sha256_acknowledged` exactly to the SHA above. PASS only if there is no P0/P1 blocker. Use verdict `PASS_TO_REPAIRED_SUPPORT_ADJUDICATION` and e1_a_recommendation `ALLOW_REPAIRED_SUPPORT_ADJUDICATION_ONLY` for a PASS. Keep e1_b_recommendation=HOLD and paper_claim_authority=false.

INDEPENDENCE: independent=true; exposed_to_other_review=false.

BOUND DOSSIER START
{bound}
BOUND DOSSIER END
"""


base.REPAIR = REPAIR
base.IDENTITY = IDENTITY
base.OUT_ROOT = OUT_ROOT
base.DOSSIER = (
    ("repair_artifact", REPAIR),
    ("original_adjudicator", ROOT / "scripts/adjudicate_e2_r17_e1_a_pool_support.py"),
    ("repaired_adjudicator", ROOT / "scripts/adjudicate_e2_r17_e1_a_pool_support_v2.py"),
    ("frozen_contract", ROOT / "generated/e2-r17-e1-a-pool-support-v2-1-contract-20260828.json"),
    ("frozen_authorization", ROOT / "generated/e2-r17-e1-a-pool-support-v2-1-authorization-20260828.json"),
    ("prior_runtime_repair_review", ROOT / "generated/e2-r17-e1-a-runtime-repair-review-v21-20260828/summary.json"),
    ("review_identity", IDENTITY),
)
base.schema = schema
base.prompt_for = prompt_for


def main() -> int:
    # Reuse base transport and parsing, but custom summary semantics.
    import argparse
    from datetime import datetime, timezone

    parser = argparse.ArgumentParser()
    parser.add_argument("--env-file", type=Path, required=True)
    parser.add_argument("--max-output-tokens", type=int, default=4000)
    args = parser.parse_args()

    expected = base.identity_map()
    bound, hashes = base.dossier()
    repair_sha = base.sha_file(REPAIR)
    base.load_env_file(args.env_file)
    source = base.ArkSettings.from_env(required=True)
    if source.base_url.rstrip("/") != base.PLAN_BASE_URL:
        raise RuntimeError("repair review refuses non-Ark-Plan route")
    settings = base.ArkSettings(
        api_key=source.api_key,
        base_url=source.base_url,
        default_model=source.default_model,
        timeout_seconds=300.0,
        max_retries=0,
    )
    client = base.ArkResponsesClient(settings)
    OUT_ROOT.mkdir(parents=True, exist_ok=True)
    rows = []
    for model in base.MODELS:
        row = base.call(
            client,
            model=model,
            expected_resolved=expected[model],
            bound=bound,
            hashes=hashes,
            repair_sha=repair_sha,
            max_output_tokens=args.max_output_tokens,
        )
        base.atomic_json(OUT_ROOT / f"{base.slug(model)}.json", row)
        rows.append(row)
    completed = [row for row in rows if row.get("status") == "COMPLETED"]
    allow = (
        len(completed) == len(rows)
        and all(
            row.get("review", {}).get("verdict") == "PASS_TO_REPAIRED_SUPPORT_ADJUDICATION"
            and row.get("review", {}).get("e1_a_recommendation") == "ALLOW_REPAIRED_SUPPORT_ADJUDICATION_ONLY"
            and row.get("review", {}).get("e1_b_recommendation") == "HOLD"
            and row.get("review", {}).get("paper_claim_authority") is False
            and not row.get("review", {}).get("remaining_blockers")
            for row in completed
        )
    )
    summary = {
        "schema_version": "1.0",
        "artifact_type": "e2-r17-e1-a-support-adjudicator-repair-dual-review",
        "created_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "repair_sha256": repair_sha,
        "statuses": {row["requested_model"]: row.get("status") for row in rows},
        "resolved_models": {row["requested_model"]: row.get("resolved_model") for row in rows},
        "verdicts": {row["requested_model"]: row.get("review", {}).get("verdict") for row in completed},
        "all_allow_repaired_support_adjudication": allow,
        "independent": True,
        "exposed_to_other_review": False,
        "scientific_authority": False,
        "e1_b_authority": False,
        "paper_claim_authority": False,
    }
    base.atomic_json(OUT_ROOT / "summary.json", summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if len(completed) == len(rows) else 2


if __name__ == "__main__":
    raise SystemExit(main())
