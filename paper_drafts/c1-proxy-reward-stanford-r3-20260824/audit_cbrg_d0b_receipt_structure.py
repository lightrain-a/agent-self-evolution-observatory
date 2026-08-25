#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
import re
from pathlib import Path
from typing import Any

import pandas as pd

PAPER_ID = "D2-PAPER-PROXY-REWARD-MEMORY-VARIANCE"
AUDIT_ID = "C1-CBRG-D0B-RECEIPT-STRUCTURE-V1"
EXTRACTOR_VERSION = "C1_D0B_RECEIPT_EXTRACTOR_V1"
ADJUDICATOR_VERSION = "NONE_STRUCTURAL_AUDIT_ONLY"

HERE = Path(__file__).resolve().parent
OUT = HERE / "cbrg-d0b-receipt-structural-audit-20260824.json"

SHOP_MANIFEST = Path("/data/wyt/agent-self-evolution-observatory/runs/d2-proxy-reward-b4-retrieval-matched-fixed-evidence-20260824/b4-memory-manifest.json")
SHOP_PARQUET = Path("/home/wyt/code/agent-self-evolution-observatory-discovery-benchmark-20260821/generated/research-data/paper-yield-d5-c01/parquet-cache/wa_awm_shuffle1-shopping_run1.parquet")
F0 = Path("/data/wyt/agent-self-evolution-observatory/paper-acceptance-artifacts/D2-PAPER-PROXY-REWARD-MEMORY-VARIANCE/f0-write-channel.json")
B2_CONTRACT = Path("/data/wyt/agent-self-evolution-observatory/runs/d2-proxy-reward-b2-source-expansion-r1-4096-20260824/b2-source-expansion-r1-contract.json")

REDDIT_ROOT = Path("/data/wyt/agent-self-evolution-observatory/runs/d2-proxy-reward-b12-crossdomain-qualification-20260824")
REDDIT_PARQUET = REDDIT_ROOT / "input/wa_awm_shuffle1-reddit_run1.parquet"
REDDIT_R1_CONTRACT = REDDIT_ROOT / "b12-reddit-r1-contract.json"
REDDIT_QUALIFICATION = REDDIT_ROOT / "b12-reddit-qualification-result.json"
REDDIT_WRITER_CSV = REDDIT_ROOT / "b12-r1-writer.csv"

EXPECTED_FILE_SHA = {
    "shopping_manifest": "2880b83c71745f049039c15edb02f731e4f87a44670977b61627143102bee0d1",
    "shopping_parquet": "fc9b0011d384403f21534529da0397ca2aabf29fcb30c2dbb5a3c01c30b1387e",
    "f0": "f2e4f3424faf1e3a9ec7aba7958e538eac457e89308552ef7a9c3d69c6a914f9",
    "b2_contract": "d9deadb844104b6a7ba8af6bae02ca2083fd1048e43d866c9658df8d8d190eac",
    "reddit_parquet": "dadaedf3e9661426e324bdb8804cd0e5748bb29919b6a755eb0ef41fcbd21a19",
    "reddit_r1_contract": "3e2975923b39d4e47974d568b07e064d7a7415632354d23b5be77044a865a88f",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def tsha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def jsha(value: Any) -> str:
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"JSON root is not object: {path}")
    return value


def require(ok: bool, message: str) -> None:
    if not ok:
        raise RuntimeError(message)


def norm(text: Any) -> str:
    return " ".join(str(text or "").split())


def action_summary(trajectory_json: str) -> str:
    data = json.loads(trajectory_json)
    lines: list[str] = []
    for step_id, step in sorted((data.get("steps") or {}).items(), key=lambda kv: int(kv[0])):
        output = (step or {}).get("output_messages") or {}
        calls = (output.get("tool_call_message") or {}).get("tool_calls") or []
        if calls:
            args = calls[0].get("args") or {}
            current = args.get("current_state") or {}
            if current.get("evaluation_previous_goal"):
                lines.append(f"Step {step_id} evaluation: {norm(current['evaluation_previous_goal'])[:500]}")
            if current.get("next_goal"):
                lines.append(f"Step {step_id} next goal: {norm(current['next_goal'])[:500]}")
            for action in args.get("action") or []:
                lines.append(f"Step {step_id} action: {json.dumps(action, ensure_ascii=False, sort_keys=True)[:900]}")
        controller = (step or {}).get("controller_messages") or {}
        for result in controller.get("action_result") or []:
            content = result.get("content") if isinstance(result, dict) else str(result)
            if content:
                lines.append(f"Step {step_id} result: {norm(content)[:900]}")
        if len(lines) >= 36:
            break
    return "\n".join(lines)


def released_evidence(trajectory_json: str) -> tuple[str, list[str]]:
    data = json.loads(trajectory_json)
    states: list[str] = []
    hashes: list[str] = []
    seen: set[str] = set()
    for _, step in sorted((data.get("steps") or {}).items(), key=lambda kv: int(kv[0])):
        contents = ((step or {}).get("input_messages") or {}).get("contents") or []
        if not contents:
            continue
        text = str(contents[-1].get("content") or "")
        if "[Current state starts here]" not in text:
            continue
        current = text.split("[Current state starts here]", 1)[1].strip()
        digest = tsha(current)
        if digest in seen:
            continue
        seen.add(digest)
        states.append(current)
        hashes.append(digest)
    return "\n\n--- RELEASED BROWSER STATE ---\n\n".join(states), hashes


def outcome_excluded_projection(trajectory_json: str) -> dict[str, Any]:
    data = json.loads(trajectory_json)
    return {
        "task_prompt": data.get("task_prompt"),
        "steps": data.get("steps") or {},
    }


def parse_memory_fields(text: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line in text.splitlines():
        match = re.match(r"^##\s+(Title|Description|Content):\s*(.+?)\s*$", line.strip())
        if match and match.group(2):
            rows.append({"field": match.group(1).lower(), "text": match.group(2).strip()})
    if not rows:
        for match in re.finditer(r"(?:Title|Description|Content):\s*([^\n#]+)", text):
            rows.append({"field": "unknown", "text": match.group(1).strip()})
    require(bool(rows), "memory schema parsing produced zero fields")
    return rows


def claim_rows(domain: str, source_task: int, condition: str, text: str) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for index, unit in enumerate(parse_memory_fields(text)):
        text_digest = tsha(unit["text"])
        identity = {
            "paper_id": PAPER_ID,
            "domain": domain,
            "source_task": source_task,
            "condition": condition,
            "field": unit["field"],
            "field_index": index,
            "text_sha256": text_digest,
        }
        out.append(
            {
                "residual_claim_id": f"C1R-{jsha(identity)[:24]}",
                "field": unit["field"],
                "field_index": index,
                "text_sha256": text_digest,
            }
        )
    return out


def csv_index(path: Path) -> dict[tuple[int, str], dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    return {(int(row["source_task"]), row["condition"]): row for row in rows}


def dataframe_index(path: Path) -> dict[int, dict[str, Any]]:
    frame = pd.read_parquet(path)
    out: dict[int, dict[str, Any]] = {}
    for _, row in frame.iterrows():
        task_id = int(row["task_id"])
        require(task_id not in out, f"duplicate trajectory row: {path}:{task_id}")
        out[task_id] = row.to_dict()
    return out


def verify_file_bindings() -> dict[str, dict[str, str]]:
    paths = {
        "shopping_manifest": SHOP_MANIFEST,
        "shopping_parquet": SHOP_PARQUET,
        "f0": F0,
        "b2_contract": B2_CONTRACT,
        "reddit_parquet": REDDIT_PARQUET,
        "reddit_r1_contract": REDDIT_R1_CONTRACT,
    }
    bindings: dict[str, dict[str, str]] = {}
    for key, path in paths.items():
        require(path.is_file(), f"missing bound artifact: {path}")
        digest = sha(path)
        require(digest == EXPECTED_FILE_SHA[key], f"artifact SHA drift: {key}: {digest}")
        bindings[key] = {"path": str(path), "sha256": digest}
    return bindings


def main() -> None:
    bindings = verify_file_bindings()
    shop_manifest = load(SHOP_MANIFEST)
    f0 = load(F0)
    b2 = load(B2_CONTRACT)
    reddit_contract = load(REDDIT_R1_CONTRACT)
    reddit_qualification = load(REDDIT_QUALIFICATION)

    shop_rows = dataframe_index(SHOP_PARQUET)
    reddit_rows = dataframe_index(REDDIT_PARQUET)

    f0_summary = {int(row["task_id"]): row["trajectory_summary_sha256"] for row in f0["pairs"] if row.get("trajectory_summary_sha256")}
    b2_summary = {int(task): row["trajectory_summary_sha256"] for task, row in b2["source_metadata"].items()}
    reddit_summary = {int(row["source_task"]): row["action_summary_sha256"] for row in reddit_contract["writer_stage"]["source_units"]}
    reddit_writer = csv_index(REDDIT_WRITER_CSV)
    reddit_qualification_rows = {int(row["task_id"]): row for row in reddit_qualification["all_reddit_retrieval_rows"]}

    shopping_memory: dict[int, dict[str, dict[str, Any]]] = {}
    source_kind: dict[int, str] = {}
    for obj in shop_manifest["objects"]:
        task = int(obj["source_task"])
        condition = str(obj["condition"])
        path = Path(obj["raw_path"])
        require(path.is_file(), f"missing Shopping branch memory: {path}")
        text = path.read_text(encoding="utf-8")
        require(tsha(text) == obj["raw_sha256"], f"Shopping branch-memory SHA drift: {task}/{condition}")
        shopping_memory.setdefault(task, {})[condition] = {
            "path": str(path),
            "sha256": obj["raw_sha256"],
            "text": text,
        }
        source_kind[task] = obj["source_kind"]

    require(len(shopping_memory) == 20, f"expected 20 Shopping pairs, found {len(shopping_memory)}")
    require(all(set(value) == {"success", "failure"} for value in shopping_memory.values()), "incomplete Shopping branch pair")

    reddit_memory: dict[int, dict[str, dict[str, Any]]] = {}
    for task in sorted(reddit_summary):
        for condition in ("success", "failure"):
            path = REDDIT_ROOT / f"private/execution-r1/writer/provider-responses/reddit-r1-writer-{task}-{condition}.json"
            payload = load(path)
            text = str(payload.get("text") or "")
            require(text, f"missing Reddit response text: {task}/{condition}")
            writer_row = reddit_writer[(task, condition)]
            require(writer_row["status"] == "complete", f"Reddit writer row incomplete: {task}/{condition}")
            require(tsha(text) == writer_row["raw_sha256"], f"Reddit branch-memory SHA drift: {task}/{condition}")
            reddit_memory.setdefault(task, {})[condition] = {
                "path": str(path),
                "sha256": writer_row["raw_sha256"],
                "text": text,
            }
    require(len(reddit_memory) == 4, f"expected 4 Reddit pairs, found {len(reddit_memory)}")

    receipts: list[dict[str, Any]] = []
    total_claim_ids = 0

    def make_receipt(domain: str, task: int, row: dict[str, Any], memories: dict[str, dict[str, Any]], expected_summary_sha: str, summary_hash_mode: str) -> dict[str, Any]:
        nonlocal total_claim_ids
        trajectory_json = str(row["trajectory_json"])
        summary = action_summary(trajectory_json)
        observed_summary_sha = jsha(summary) if summary_hash_mode == "canonical-json-string" else tsha(summary)
        require(observed_summary_sha == expected_summary_sha, f"writer-input action-summary drift: {domain}/{task}")

        evidence_text, state_hashes = released_evidence(trajectory_json)
        require(bool(evidence_text.strip()) and bool(state_hashes), f"no released pre-writer browser evidence: {domain}/{task}")
        evidence_sha = tsha(evidence_text)

        if domain == "reddit":
            qrow = reddit_qualification_rows[task]
            require(qrow["trajectory_available"] is True, f"Reddit trajectory availability drift: {task}")
            require(qrow["released_evidence_sha256"] == evidence_sha, f"Reddit released-evidence SHA drift: {task}")
            require(qrow["released_state_sha256"] == state_hashes, f"Reddit released-state SHA drift: {task}")

        branch_claims: dict[str, list[dict[str, Any]]] = {}
        branch_hashes: dict[str, str] = {}
        branch_paths: dict[str, str] = {}
        for condition in ("success", "failure"):
            memory = memories[condition]
            branch_hashes[condition] = memory["sha256"]
            branch_paths[condition] = memory["path"]
            branch_claims[condition] = claim_rows(domain, task, condition, memory["text"])
            total_claim_ids += len(branch_claims[condition])

        projection = outcome_excluded_projection(trajectory_json)
        receipt_core = {
            "paper_id": PAPER_ID,
            "domain": domain,
            "source_task": task,
            "pre_writer_trajectory_projection_sha256": jsha(projection),
            "writer_input_action_summary_sha256": expected_summary_sha,
            "branch_memory_sha256": branch_hashes,
            "released_evidence_sha256": evidence_sha,
            "residual_claim_ids": {
                condition: [row["residual_claim_id"] for row in branch_claims[condition]]
                for condition in ("success", "failure")
            },
        }
        return {
            "receipt_prototype_id": f"C1-D0B-{jsha(receipt_core)[:24]}",
            "domain": domain,
            "source_task": task,
            "task_prompt_sha256": tsha(str(row["task_prompt"])),
            "trajectory_lineage": {
                "full_trajectory_json_sha256": tsha(trajectory_json),
                "pre_writer_trajectory_projection_sha256": jsha(projection),
                "terminal_outcome_fields_excluded_from_projection": ["is_successful", "rubric_results"],
                "projection_is_identical_for_success_and_failure_writers": True,
            },
            "writer_input": {
                "action_summary_sha256": expected_summary_sha,
                "hash_mode": summary_hash_mode,
                "recomputed_match": True,
                "branch_label_not_part_of_action_summary": True,
            },
            "branch_memories": {
                condition: {"path": branch_paths[condition], "sha256": branch_hashes[condition]}
                for condition in ("success", "failure")
            },
            "residual_claim_identity": {
                "parser": "deterministic Title/Description/Content field parser",
                "claims": branch_claims,
                "claim_ids_bindable": True,
                "semantic_residual_status_not_inferred": True,
            },
            "outcome_independent_evidence": {
                "source": "released pre-writer browser-state projection from frozen trajectory",
                "released_evidence_sha256": evidence_sha,
                "released_state_sha256": state_hashes,
                "state_count": len(state_hashes),
                "treatment_label_used_as_evidence": False,
                "terminal_reward_or_rubric_used_as_evidence": False,
            },
            "validity": {
                "state": "UNADJUDICATED_STRUCTURAL_ONLY",
                "allowed_authority_states_after_future_adjudication": ["SUPPORTED", "CONTRADICTED", "UNVERIFIABLE"],
                "extractor_version": EXTRACTOR_VERSION,
                "adjudicator_version": ADJUDICATOR_VERSION,
            },
            "authority_decision": "WITHHOLD_ALL_BRANCH_AUTHORITY",
            "scientific_authority": False,
            "provider_call_authority": False,
        }

    for task in sorted(shopping_memory):
        require(task in shop_rows, f"Shopping source trajectory missing: {task}")
        kind = source_kind[task]
        if kind == "original_f0":
            expected = f0_summary[task]
        elif kind == "b2_r1":
            expected = b2_summary[task]
        else:
            raise RuntimeError(f"unknown Shopping source kind: {task}:{kind}")
        receipt = make_receipt("shopping", task, shop_rows[task], shopping_memory[task], expected, "canonical-json-string")
        receipt["source_kind"] = kind
        receipts.append(receipt)

    for task in sorted(reddit_memory):
        require(task in reddit_rows, f"Reddit source trajectory missing: {task}")
        receipts.append(make_receipt("reddit", task, reddit_rows[task], reddit_memory[task], reddit_summary[task], "utf8-text"))

    structural_complete = (
        len(receipts) == 24
        and all(row["trajectory_lineage"]["projection_is_identical_for_success_and_failure_writers"] for row in receipts)
        and all(row["writer_input"]["recomputed_match"] for row in receipts)
        and all(row["residual_claim_identity"]["claim_ids_bindable"] for row in receipts)
        and all(row["outcome_independent_evidence"]["state_count"] > 0 for row in receipts)
        and all(row["authority_decision"] == "WITHHOLD_ALL_BRANCH_AUTHORITY" for row in receipts)
    )

    payload = {
        "schema_version": "1.0",
        "artifact_type": "c1-d0b-evidence-receipt-structural-audit",
        "audit_id": AUDIT_ID,
        "paper_id": PAPER_ID,
        "status": "D0B_RECEIPT_STRUCTURE_FEASIBLE_SEMANTIC_VALIDITY_UNADJUDICATED_AUTHORITY_HOLD" if structural_complete else "D0B_RECEIPT_STRUCTURE_INCOMPLETE_AUTHORITY_HOLD",
        "provider_calls": 0,
        "gpu_runs": 0,
        "source_bindings": bindings,
        "receipt_contract": {
            "content_addressed": True,
            "binds_exact_trajectory_sha256": True,
            "binds_branch_memory_sha256": True,
            "binds_residual_claim_id": True,
            "binds_evidence_refs_and_sha256": True,
            "records_validity_state": True,
            "records_extractor_and_adjudicator_version": True,
            "records_authority_decision": True,
            "receipt_is_required_before_nonzero_branch_authority": True,
            "receipt_cannot_grant_provider_or_scientific_authority": True,
        },
        "summary": {
            "paired_sources_expected": 24,
            "paired_sources_structurally_bound": len(receipts),
            "shopping_pairs_bound": sum(row["domain"] == "shopping" for row in receipts),
            "reddit_pairs_bound": sum(row["domain"] == "reddit" for row in receipts),
            "pre_writer_trajectory_projections_bound": sum(bool(row["trajectory_lineage"]["pre_writer_trajectory_projection_sha256"]) for row in receipts),
            "writer_input_action_summaries_recomputed_and_matched": sum(row["writer_input"]["recomputed_match"] for row in receipts),
            "paired_branch_memories_hash_bound": sum(set(row["branch_memories"]) == {"success", "failure"} for row in receipts),
            "released_evidence_packets_hash_bound": sum(row["outcome_independent_evidence"]["state_count"] > 0 for row in receipts),
            "residual_claim_ids_bound": total_claim_ids,
            "semantic_validity_adjudicated_claims": 0,
            "supported_claims": 0,
            "contradicted_claims": 0,
            "unverifiable_claims": 0,
            "nonzero_branch_authority_receipts": 0,
            "structural_complete": structural_complete,
        },
        "decision": "D0B_STRUCTURAL_GO_SEMANTIC_AUTHORITY_HOLD" if structural_complete else "D0B_STRUCTURAL_HOLD",
        "interpretation": "The frozen 24 same-trajectory source pairs can be bound into content-addressed receipt prototypes that identify exact pre-writer trajectory projections, exact branch memories, deterministic residual-claim identities, and outcome-independent released browser-state evidence. No claim-evidence validity judgment is made here, so no prototype is an authority-bearing evidence receipt.",
        "next_required_gate": "A separately versioned outcome-independent claim-evidence adjudicator must assign SUPPORTED, CONTRADICTED, or UNVERIFIABLE from the bound pre-writer evidence. Semantic similarity, the injected success/failure label, terminal reward, and downstream outcome are forbidden as validity evidence.",
        "claim_boundary": "Zero-call structural feasibility only. This does not establish CBRG effectiveness, branch validity, novelty, mediation, or provider-execution authority.",
        "receipts": receipts,
        "scientific_authority": False,
        "experiment_authority": False,
        "provider_call_authority": False,
        "gpu_authority": False,
        "claim_expansion_authority": False,
        "submission_authority": False,
    }

    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": payload["status"], "summary": payload["summary"], "output": str(OUT)}, indent=2))


if __name__ == "__main__":
    main()
