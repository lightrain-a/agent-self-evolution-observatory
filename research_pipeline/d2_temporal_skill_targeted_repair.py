from __future__ import annotations

import argparse
import base64
import hashlib
import json
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PAPER_ID = "D2-PAPER-TEMPORAL-SKILL-CAUSAL-BOTTLENECK"
CONTRACT_SHA256 = "a3942d3f7bb384893faf3649ce966419b5729dd6108c7b7b8d5fe76d3ad3025c"
GITHUB_REPO = "TimeSage-Series/TimeSage-EV"
HF_REPO = "TimeSage-Series/TimeSage-EV"
ARXIV_ID = "2608.14270"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _canonical_sha(value: Any) -> str:
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _get_json(url: str, timeout: int = 15) -> tuple[dict[str, Any] | list[Any] | None, str]:
    req = urllib.request.Request(url, headers={"User-Agent": "agent-self-evolution-observatory-paper-repair/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8")), f"HTTP_{response.status}"
    except urllib.error.HTTPError as exc:
        return None, f"HTTP_{exc.code}"
    except Exception as exc:  # network support is not scientific evidence
        return None, f"{type(exc).__name__}:{exc}"


def _github_probe() -> dict[str, Any]:
    repo, repo_status = _get_json(f"https://api.github.com/repos/{GITHUB_REPO}")
    contents, contents_status = _get_json(f"https://api.github.com/repos/{GITHUB_REPO}/contents/")
    readme, readme_status = _get_json(f"https://api.github.com/repos/{GITHUB_REPO}/contents/README.md")
    commit, commit_status = _get_json(f"https://api.github.com/repos/{GITHUB_REPO}/commits/master")
    names = []
    if isinstance(contents, list):
        names = sorted(str(row.get("name") or "") for row in contents if isinstance(row, dict))
    readme_text = ""
    if isinstance(readme, dict) and readme.get("content"):
        try:
            readme_text = base64.b64decode(str(readme.get("content") or "")).decode("utf-8", "replace")
        except Exception:
            readme_text = ""
    row = {
        "canonical_url": f"https://github.com/{GITHUB_REPO}",
        "api_status": {"repo": repo_status, "contents": contents_status, "readme": readme_status, "commit": commit_status},
        "private": (repo or {}).get("private") if isinstance(repo, dict) else None,
        "default_branch": (repo or {}).get("default_branch") if isinstance(repo, dict) else None,
        "repo_size": (repo or {}).get("size") if isinstance(repo, dict) else None,
        "pushed_at": (repo or {}).get("pushed_at") if isinstance(repo, dict) else None,
        "head": (commit or {}).get("sha") if isinstance(commit, dict) else None,
        "root_paths": names,
        "readme_blob_sha": (readme or {}).get("sha") if isinstance(readme, dict) else None,
        "readme_size": (readme or {}).get("size") if isinstance(readme, dict) else None,
        "readme_text": readme_text,
    }
    row["code_assets_present"] = any(name not in {"README.md", ".gitattributes", "LICENSE", "LICENSE.md"} for name in names)
    return row


def _hf_probe() -> dict[str, Any]:
    canonical = f"https://huggingface.co/api/datasets/{HF_REPO}"
    mirror = f"https://hf-mirror.com/api/datasets/{HF_REPO}"
    payload, status = _get_json(canonical)
    used = canonical
    if not isinstance(payload, dict):
        payload, mirror_status = _get_json(mirror)
        status = f"canonical={status};mirror={mirror_status}"
        used = mirror if isinstance(payload, dict) else canonical
    siblings = []
    if isinstance(payload, dict):
        siblings = sorted(
            str(row.get("rfilename") or "")
            for row in (payload.get("siblings") or [])
            if isinstance(row, dict)
        )
    row = {
        "canonical_url": f"https://huggingface.co/datasets/{HF_REPO}",
        "probe_url_used": used,
        "api_status": status,
        "id": payload.get("id") if isinstance(payload, dict) else None,
        "sha": payload.get("sha") if isinstance(payload, dict) else None,
        "private": payload.get("private") if isinstance(payload, dict) else None,
        "disabled": payload.get("disabled") if isinstance(payload, dict) else None,
        "created_at": payload.get("createdAt") if isinstance(payload, dict) else None,
        "last_modified": payload.get("lastModified") if isinstance(payload, dict) else None,
        "root_paths": siblings,
    }
    row["dataset_assets_present"] = any(path not in {".gitattributes", "README.md", "README.md"} for path in siblings)
    return row


def build_support_receipt() -> dict[str, Any]:
    github = _github_probe()
    hf = _hf_probe()
    evaluated_snapshot_present = bool(github["code_assets_present"] and hf["dataset_assets_present"])
    body = {
        "schema_version": "1.0",
        "receipt_type": "first-party-support-recheck",
        "paper_id": PAPER_ID,
        "contract_sha256": CONTRACT_SHA256,
        "generated_at": _now(),
        "scientific_object": {
            "arxiv": f"arXiv:{ARXIV_ID}",
            "title": "TimeSage-EV: A Live Benchmark for Agentic Time Series Analysis in Evolving Environments",
            "frozen_evaluated_horizon": "through 2026-05",
            "benchmark_substitution_allowed": False,
        },
        "first_party": {"github": github, "huggingface": hf},
        "support_gate": {
            "evaluated_snapshot_present": evaluated_snapshot_present,
            "required_for_execution": [
                "hashable first-party scenario-period inputs",
                "hashable first-party expected outcomes or evaluator contract",
                "hashable first-party skill interface / executable harness",
                "period/cutoff metadata sufficient to freeze failure-family labels before outcomes",
            ],
            "pass": evaluated_snapshot_present,
            "status": "READY_FIRST_PARTY_SUPPORT" if evaluated_snapshot_present else "HOLD_SUPPORT_FIRST_PARTY_EVALUATED_SNAPSHOT_UNAVAILABLE",
        },
        "interpretation": {
            "paper_release_statement_is_not_asset_presence": True,
            "support_failure_has_scientific_authority": False,
            "support_failure_refutes_c3_or_c4": False,
            "surrogate_benchmark_authorized": False,
        },
        "reopen_condition": "A hashable first-party TimeSage-EV evaluated snapshot exposes the frozen scenario inputs, outcomes/evaluator contract, cutoff metadata, and skill interface needed by the registered C3/C4 intervention.",
        "scientific_authority": False,
        "experiment_authority": False,
        "gpu_authority": False,
    }
    return {**body, "receipt_body_sha256": _canonical_sha(body)}


def build_operationalization() -> dict[str, Any]:
    body = {
        "schema_version": "1.0",
        "receipt_type": "c3-c4-operationalization",
        "paper_id": PAPER_ID,
        "contract_sha256": CONTRACT_SHA256,
        "generated_at": _now(),
        "scope": {
            "claim_ids": ["C3", "C4"],
            "new_claims_allowed": False,
            "scientific_object": f"TimeSage-EV arXiv:{ARXIV_ID}, evaluated horizon through 2026-05",
            "alternative_benchmark_allowed": False,
            "synthetic_timesage_snapshot_allowed": False,
        },
        "pre_outcome_freeze": {
            "failure_family_labels_must_be_frozen_before_intervention_outcomes": True,
            "endpoint_identity_must_be_frozen_before_condition_assignment": True,
            "model_harness_and_evidence_package_must_be_identical_across_paired_conditions": True,
            "repeat_count_and_condition_order_must_be_frozen_before_outcomes": True,
        },
        "failure_families": {
            "temporal_cutoff": {
                "eligibility": "The first-party task contract exposes a target cutoff and timestamped candidate evidence, and the endpoint requires cutoff-valid reasoning.",
                "success": "The answer uses no evidence that becomes available after the target cutoff; any cited or traceable support is cutoff-valid.",
            },
            "release_alignment": {
                "eligibility": "The first-party task requires mapping a source release/publication date to the benchmark reporting period represented by the evidence.",
                "success": "The response selects the exact benchmark reporting period and the time-series row aligned to that period.",
            },
            "exogenous_grounding": {
                "eligibility": "The first-party task asks for attribution or contextual explanation that is scoreable against cutoff-valid documentary evidence.",
                "success": "Each scored exogenous attribution is supported by a cutoff-valid first-party document span tied to the evaluated period.",
            },
        },
        "conditions": {
            "no_skill": {
                "id": "N0",
                "contract": "Same source-faithful model, prompt, tools, evidence package, and harness; the experimental targeted/generic skill is absent and no scenario-specific answer artifact is injected.",
            },
            "generic_skill": {
                "id": "G0",
                "contract": "Frozen reusable helper under the same callable wrapper and tool-interface envelope as the targeted skill. It may perform generic validation or organization but may not inspect or act on the target mechanism variables.",
                "matching": {
                    "same_callable_signature": True,
                    "source_token_count_tolerance_fraction": 0.10,
                    "ast_node_count_tolerance_fraction": 0.05,
                    "same_max_external_tool_calls": True,
                    "same_persistent_registration_timing": True,
                },
                "forbidden_target_actions": [
                    "compare evidence timestamps to the evaluation cutoff",
                    "map release dates to reporting-period identifiers",
                    "select documentary events as explanations for numerical changes",
                    "encode scenario-specific facts, answers, dates, labels, or expected outputs",
                ],
                "family_matched_helpers": {
                    "temporal_cutoff": "Generic evidence-package schema/type validator; it cannot read cutoff timestamps or filter by time.",
                    "release_alignment": "Generic table/index consistency validator; it cannot read release dates or reporting-period fields.",
                    "exogenous_grounding": "Generic document-structure helper that can expose document inventory/format metadata; it cannot select events, align them to numerical changes, or use document timestamps for attribution.",
                },
            },
            "targeted_ablation": {
                "T1_temporal_cutoff_only": "Add only the cutoff-valid evidence filtering procedure.",
                "T2_plus_release_alignment": "Keep T1 unchanged and add release-date to reporting-period normalization/verification.",
                "T3_plus_exogenous_grounding": "Keep T2 unchanged and add cutoff-valid documentary grounding for scored attribution targets.",
                "ordered": True,
                "no_component_refit_after_outcome_inspection": True,
            },
        },
        "estimands": {
            "C3_primary": "Paired targeted-minus-generic change in the matched family success indicator on the identical endpoint; no-skill supplies an additional baseline anchor.",
            "C3_secondary": "Paired change in source-native TimeSage-EV metrics where the released evaluator supports immutable recomputation.",
            "C4_cross_period": "Apply the frozen acquired targeted skill without edits to later periods of the same scenario and compare against the same generic/no-skill controls.",
            "C4_cross_domain_compatible": "After the cross-period test, apply the unchanged skill only to a different-domain scenario whose first-party interface and registered failure-family criterion are compatible; no scenario-specific facts may be added.",
        },
        "immutable_result_row": [
            "dataset_repo_sha",
            "code_repo_sha",
            "scenario_id",
            "period_id",
            "cutoff_timestamp",
            "failure_family",
            "condition_id",
            "skill_source_sha256",
            "model_identifier",
            "model_config_sha256",
            "prompt_harness_sha256",
            "repeat_id",
            "raw_response_sha256",
            "family_success",
            "native_metric_payload",
            "cutoff_or_grounding_evidence_refs",
            "support_status",
        ],
        "activation_gate": {
            "first_party_support_receipt_pass_required": True,
            "scoped_human_authorization_required": True,
            "gpu_preflight_required_if_gpu_execution_is_used": True,
            "no_69_to_52_jump": True,
            "52_gpu_index_if_used": 5,
            "52_independent_run_root_required": True,
        },
        "forbidden": [
            "replace TimeSage-EV with TimeSage-MT or another benchmark",
            "construct a synthetic evaluated TimeSage-EV snapshot and count it as benchmark evidence",
            "choose endpoints or failure labels after seeing intervention outcomes",
            "let the generic control access target-category operations",
            "insert scenario-specific facts into any reusable skill",
            "interpret support/network failure as scientific counterevidence",
        ],
        "scientific_authority": False,
        "experiment_authority": False,
        "gpu_authority": False,
    }
    return {**body, "receipt_body_sha256": _canonical_sha(body)}


def build_scoped_authorization(support: dict[str, Any], operationalization: dict[str, Any]) -> dict[str, Any]:
    support_pass = bool((support.get("support_gate") or {}).get("pass"))
    body = {
        "schema_version": "1.0",
        "receipt_type": "external-human-scoped-experiment-authorization",
        "paper_id": PAPER_ID,
        "contract_sha256": CONTRACT_SHA256,
        "generated_at": _now(),
        "source_instruction_ref": "chat-instruction-2026-08-22-temporal-skill-targeted-repair",
        "scope_authorized": True,
        "authorized_claim_ids": ["C3", "C4"],
        "authorized_debt": [
            "targeted temporal cutoff skill intervention",
            "release-alignment skill intervention",
            "exogenous-grounding skill intervention",
            "matched generic-skill control",
            "same-endpoint no-skill control",
            "cross-period transfer test",
            "cross-domain compatible-scenario transfer test",
        ],
        "execution_priority": [
            "ordered C3 ablation: temporal-cutoff -> +release-alignment -> +exogenous-grounding",
            "matched frozen generic-skill and no-skill controls",
            "C4 cross-period transfer",
            "C4 cross-domain compatible-scenario transfer only if the same frozen first-party support object permits it",
        ],
        "authority_limits": {
            "new_claim_authority": False,
            "idea_search_authority": False,
            "benchmark_substitution_authority": False,
            "scientific_object_change_authority": False,
            "unregistered_experiment_authority": False,
            "69_to_52_jump_authority": False,
        },
        "compute_scope": {
            "preferred_execution_host": "root@10.42.8.52",
            "gpu_index": 5,
            "direct_local_mcp_connection_required": True,
            "gpu_must_be_rechecked_idle_immediately_before_execution": True,
            "independent_paper_run_root_required": True,
            "shared_dirty_repo_overwrite_allowed": False,
            "canonical_scientific_authority_host": "wyt@222.20.126.69",
        },
        "activation": {
            "support_receipt_body_sha256": support.get("receipt_body_sha256"),
            "operationalization_receipt_body_sha256": operationalization.get("receipt_body_sha256"),
            "first_party_support_gate_pass": support_pass,
            "current_execution_authorized": support_pass,
            "blocked_reason": "" if support_pass else "TIMESAGE_EVALUATED_FIRST_PARTY_ASSETS_NOT_PUBLIC",
        },
        "scientific_authority": False,
        "paper_workflow_authority": False,
        "gpu_authority": False,
    }
    return {**body, "receipt_body_sha256": _canonical_sha(body)}


def write_receipts(output_dir: Path) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    support = build_support_receipt()
    operationalization = build_operationalization()
    authorization = build_scoped_authorization(support, operationalization)
    rows = {
        "support-recheck": support,
        "operationalization": operationalization,
        "scoped-authorization": authorization,
    }
    paths = {}
    for name, payload in rows.items():
        path = output_dir / f"d2-temporal-skill-bottleneck-{name}-20260822.json"
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        paths[name] = str(path)
    return {
        "paper_id": PAPER_ID,
        "status": "READY_TO_EXECUTE_C3_C4" if authorization["activation"]["current_execution_authorized"] else "HOLD_SUPPORT_OPERATIONS_REPAIRED",
        "paths": paths,
        "support_pass": support["support_gate"]["pass"],
        "current_execution_authorized": authorization["activation"]["current_execution_authorized"],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Recheck TimeSage-EV support and freeze the C3/C4 targeted-repair execution contract.")
    parser.add_argument("--output-dir", type=Path, default=Path("generated"))
    args = parser.parse_args()
    print(json.dumps(write_receipts(args.output_dir), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
