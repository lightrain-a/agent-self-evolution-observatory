from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PORT_PLAN = ROOT / "generated" / "paper-first-pre-f0-evidence-acquisition-plan.json"

EXPECTED = {
    "InstructScene": {
        "commit": "a9097a62c484c56ac7be5ec2928ef497cbbaaf24",
        "license_sha256": "a117b2768e88ff0aa0caa9b1c4e4c9a0d3191ccc512584248b8e1e332f540b8e",
    },
    "ATISS": {
        "commit": "0909ce0000e52bf1bf300a6a558109f7f8383fd9",
        "license_sha256": "5b9817b997f4a85f064f66762982d068571c9062ccc3a302b0c518dfd3484d28",
    },
    "DiffuScene": {
        "commit": "d78a2890c6b806b61279463b1dbe7701f286a024",
        "license_sha256": "a3c6a9205c84f9d94c43bbe79a78b40e48c9727f7beeb1288e6403fb5df664dc",
    },
}
EXPECTED_HF_REVISION = "c8cf0bd282699d56a7940ac588ea5e961b1260cb"


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_head(path: Path) -> str:
    return subprocess.check_output(
        ["git", "-C", str(path), "rev-parse", "HEAD"], text=True
    ).strip()


def verify_source(name: str, path: Path) -> None:
    expected = EXPECTED[name]
    actual_commit = git_head(path)
    if actual_commit != expected["commit"]:
        raise SystemExit(f"{name} commit drift: {actual_commit}")
    actual_license = sha256_file(path / "LICENSE")
    if actual_license != expected["license_sha256"]:
        raise SystemExit(f"{name} license drift: {actual_license}")


def port010_snapshot() -> dict[str, Any]:
    plan = json.loads(PORT_PLAN.read_text(encoding="utf-8"))
    rows = [
        row
        for row in plan.get("entries") or []
        if row.get("candidate_id") == "PORT-010"
        and row.get("title") == "Complex-description boundary in end-to-end 3D world construction"
    ]
    if len(rows) != 1:
        raise SystemExit("exact PORT-010 row not found")
    row = rows[0]
    adjudication = row["release_change_adjudication"]
    if row.get("status") != "HOLD_EVIDENCE_REVIEW_BLOCKED":
        raise SystemExit("PORT-010 HOLD drifted")
    if (row.get("evidence_review") or {}).get("verdict") != "BLOCK_BAKE_IN":
        raise SystemExit("PORT-010 evidence review drifted")
    if adjudication.get("remaining_reopen_components") != ["per_case_outcomes"]:
        raise SystemExit("PORT-010 reopen components drifted")
    for key in (
        "offline_replay_tier_authorized",
        "provider_authority",
        "gpu_authority",
        "scientific_execution_authority",
    ):
        if adjudication.get(key) is not False:
            raise SystemExit(f"PORT-010 authority drifted: {key}")
    return {
        "candidate_id": "PORT-010",
        "status": row["status"],
        "evidence_review": row["evidence_review"]["verdict"],
        "required_reopen_components": adjudication["required_reopen_components"],
        "materialized_reopen_components": adjudication["materialized_reopen_components"],
        "remaining_reopen_components": adjudication["remaining_reopen_components"],
        "offline_replay_tier_authorized": False,
        "provider_authority": False,
        "gpu_authority": False,
        "scientific_execution_authority": False,
        "changed_by_this_object": False,
    }


def build(args: argparse.Namespace) -> dict[str, Any]:
    verify_source("InstructScene", args.instructscene_repo)
    verify_source("ATISS", args.atiss_repo)
    verify_source("DiffuScene", args.diffuscene_repo)
    if args.hf_revision != EXPECTED_HF_REVISION:
        raise SystemExit(f"InstructScene HF revision drift: {args.hf_revision}")

    authority = {
        "canonical_generator": False,
        "problem_gate": False,
        "paper_design": False,
        "method": False,
        "experiment": False,
        "local_validation": False,
        "p0": False,
        "provider": False,
        "gpu": False,
        "scientific_execution": False,
        "scientific": False,
    }
    return {
        "schema_version": "relational-constraint-capacity-pre-f0-v1",
        "generated_at": "2026-08-30T15:30:00+00:00",
        "object_id": "RELATIONAL-CONSTRAINT-CAPACITY-20260830",
        "canonical_candidate_id": None,
        "status": "PRE_F0_HOLD_ASSET_AND_CONSTRUCT_QUALIFICATION",
        "scientific_object": {
            "title": "Relational constraint capacity in instruction-driven 3D scene generation",
            "question": (
                "Does increasing relational constraint load induce a reproducible "
                "constraint-capacity boundary in instruction-driven 3D scene generation, "
                "and can explicit structural representation shift that boundary?"
            ),
            "primary_prediction": (
                "With the base scene, object universe, room type, asset vocabulary, "
                "generation configuration, and seed policy held fixed, official iRecall "
                "declines as nested relation load |R| increases."
            ),
            "boundary_prediction": (
                "A stable breakpoint C* is supported only if segmented/change-point models "
                "outperform smooth alternatives out of sample and bootstrap C* is stable."
            ),
            "intervention_prediction": (
                "A same-information explicit structural representation shifts C* rightward, "
                "or yields gains concentrated in the high-|R| regime."
            ),
            "scope_boundary": (
                "This is an independent scientific object. It is not VWE reproduction, "
                "PORT-010 replacement evidence, author-outcome reconstruction, or evidence "
                "that can reopen PORT-010."
            ),
        },
        "relation_to_port010": {
            "policy": [
                "release change != scientific reopen",
                "new dataset result != VWE author outcome",
                "local rollout != author-released outcome",
                "cross-substrate confirmation requires a new scientific object",
            ],
            "snapshot": port010_snapshot(),
        },
        "source_and_publication_audit": {
            "dataset": {
                "name": "3D-FRONT / 3D-FUTURE",
                "paper": "3D-FRONT: 3D Furnished Rooms With layOuts and semaNTics",
                "venue": "ICCV 2021",
                "paper_url": (
                    "https://openaccess.thecvf.com/content/ICCV2021/html/"
                    "Fu_3D-FRONT_3D_Furnished_Rooms_With_layOuts_and_semaNTics_ICCV_2021_paper.html"
                ),
                "access_contract": (
                    "Original assets require acceptance of the official research-use terms; "
                    "a mirror or derivative archive is not evidence that those terms were accepted."
                ),
                "materialized_on_checked_69_paths": False,
                "license_acknowledgement_verified": False,
                "qualified_for_p0_now": False,
            },
            "methods": [
                {
                    "name": "ATISS",
                    "paper": "ATISS: Autoregressive Transformers for Indoor Scene Synthesis",
                    "authors": [
                        "Despoina Paschalidou",
                        "Amlan Kar",
                        "Maria Shugrina",
                        "Karsten Kreis",
                        "Andreas Geiger",
                        "Sanja Fidler",
                    ],
                    "venue": "NeurIPS 2021",
                    "paper_url": "https://openreview.net/forum?id=MtvKv_BDVV",
                    "repository_url": "https://github.com/nv-tlabs/ATISS",
                    "repository_commit": EXPECTED["ATISS"]["commit"],
                    "license": "NVIDIA Source Code License for ATISS",
                    "license_sha256": EXPECTED["ATISS"]["license_sha256"],
                    "publication_qualified": True,
                    "free_form_relational_instruction_same_access": False,
                    "role": "input-mismatched contextual baseline, not a same-access primary row",
                },
                {
                    "name": "DiffuScene",
                    "paper": "DiffuScene: Denoising Diffusion Models for Generative Indoor Scene Synthesis",
                    "authors": [
                        "Jiapeng Tang",
                        "Yinyu Nie",
                        "Lev Markhasin",
                        "Angela Dai",
                        "Justus Thies",
                        "Matthias Niessner",
                    ],
                    "venue": "CVPR 2024",
                    "paper_url": (
                        "https://openaccess.thecvf.com/content/CVPR2024/html/"
                        "Tang_DiffuScene_Denoising_Diffusion_Models_for_Generative_Indoor_Scene_Synthesis_CVPR_2024_paper.html"
                    ),
                    "repository_url": "https://github.com/tangjiapeng/DiffuScene",
                    "repository_commit": EXPECTED["DiffuScene"]["commit"],
                    "license": "custom noncommercial/restricted-use license",
                    "license_sha256": EXPECTED["DiffuScene"]["license_sha256"],
                    "publication_qualified": True,
                    "free_form_relational_instruction_same_access": False,
                    "role": "input-protocol-separated baseline unless an exact bridge is preregistered",
                },
                {
                    "name": "InstructScene",
                    "paper": (
                        "InstructScene: Instruction-Driven 3D Indoor Scene Synthesis "
                        "with Semantic Graph Prior"
                    ),
                    "authors": ["Chenguo Lin", "Yadong Mu"],
                    "venue": "ICLR 2024 Spotlight",
                    "paper_url": "https://openreview.net/forum?id=LtuRgL03pI",
                    "repository_url": "https://github.com/chenguolin/InstructScene",
                    "repository_commit": EXPECTED["InstructScene"]["commit"],
                    "license": "MIT",
                    "license_sha256": EXPECTED["InstructScene"]["license_sha256"],
                    "publication_qualified": True,
                    "official_irecall_evaluator_present": True,
                    "role": "primary instruction-driven substrate candidate",
                },
            ],
            "instructscene_release": {
                "huggingface_dataset": "chenguolin/InstructScene_dataset",
                "huggingface_revision": args.hf_revision,
                "revision_observed_via": "hf-mirror git ls-remote",
                "preprocessed_dataset_materialized_on_checked_69_paths": False,
                "official_fvqvae_weights_declared": True,
                "official_fvqvae_weights_materialized_on_checked_69_paths": False,
                "official_end_to_end_two_stage_checkpoint_declared": False,
                "third_party_unofficial_two_stage_checkpoints_declared": True,
                "third_party_checkpoint_is_official_reproduction_evidence": False,
                "training_cost_declared_by_repository": (
                    "1-3 days per semantic graph prior or layout decoder on one NVIDIA A40, "
                    "depending on room type"
                ),
            },
        },
        "construct_contract": {
            "primary_dose": "relation_count = |R|",
            "nested_relation_sets": "R1 subset R2 subset ... subset RK",
            "paired_invariants": [
                "same base scene",
                "same object universe",
                "same room type",
                "same asset vocabulary",
                "same downstream generation settings",
                "same seed policy",
            ],
            "primary_endpoint": (
                "official iRecall = satisfied instructed relation triplets / "
                "total instructed relation triplets"
            ),
            "secondary_endpoints": [
                "exact-all-relations success",
                "object coverage",
                "collision/physical validity",
                "generation failure",
                "runtime failure",
            ],
            "complexity_diagnostics": [
                "object_count",
                "scene_graph_degree",
                "max_relation_depth",
                "connected_components",
                "global_relation_fraction",
                "local_relation_fraction",
                "relation_type_entropy",
            ],
            "model_comparison": [
                "linear",
                "piecewise linear",
                "logistic",
                "segmented/change-point",
            ],
            "boundary_reporting": [
                "C* point estimate",
                "bootstrap confidence interval",
                "slope before C*",
                "slope after C*",
                "system heterogeneity",
            ],
            "smooth_decline_policy": (
                "If no stable breakpoint exists, adjudicate smooth capacity degradation "
                "and do not claim a boundary law."
            ),
        },
        "known_identifiability_risks": [
            {
                "risk": "COUNT_LENGTH_AND_AUTHORED_DIFFICULTY_CONFOUND",
                "evidence": (
                    "The canonical SceneEval outcome-blind audit already found total explicit "
                    "specification count nearly collinear with instruction length "
                    "(Spearman rho=0.939932) and strongly associated with authored difficulty "
                    "(rho=0.861922)."
                ),
                "required_resolution": (
                    "The nested construction must demonstrate that the |R| effect survives "
                    "paired scene/object controls and a prompt-length/content control; raw "
                    "cross-sectional count degradation is not a contribution."
                ),
            },
            {
                "risk": "SAME_ACCESS_BASELINE_GAP",
                "evidence": (
                    "ATISS and DiffuScene do not natively expose the same free-form relational "
                    "instruction interface as InstructScene."
                ),
                "required_resolution": (
                    "Separate same-access, structured-access, and oracle/upper-bound rows; "
                    "do not place input-mismatched systems in one undifferentiated main table."
                ),
            },
            {
                "risk": "INTERVENTION_NOT_IDENTIFIED",
                "evidence": (
                    "InstructScene already contains a semantic graph prior. Directly feeding "
                    "ground-truth relation graphs bypasses instruction interpretation and is "
                    "an oracle structured-access intervention, not automatically a "
                    "same-information text-vs-structure ablation."
                ),
                "required_resolution": (
                    "Freeze a deterministic, outcome-independent text-to-structure transform "
                    "or a matched architecture ablation before outcomes; otherwise report the "
                    "graph path only as an upper bound/operational localization."
                ),
            },
            {
                "risk": "NOVELTY_COLLISION",
                "evidence": (
                    "Generic count-based complexity degradation and graph-structured scene "
                    "generation priors are already represented in the current-source audit."
                ),
                "required_resolution": (
                    "The paper-level contribution must be the reproducible paired regime law "
                    "and falsifiable boundary shift, not merely lower iRecall at longer prompts "
                    "or a graph prompt improvement."
                ),
            },
        ],
        "gates": {
            "P0": {
                "purpose": "environment and official-stack qualification",
                "planned_units": "3-10 cases, one representative baseline, one fixed seed",
                "requirements": [
                    "licensed dataset access verified",
                    "dataset revision and file hashes pinned",
                    "official code revision pinned",
                    "checkpoint provenance classified",
                    "official inference succeeds",
                    "official iRecall evaluation succeeds",
                    "per-case append-only artifact writer verified",
                ],
                "status": "HOLD_ASSET_AND_CHECKPOINT_QUALIFICATION",
                "executed_cases": 0,
                "verdict": "NOT_RUN_NO_SCIENTIFIC_RESULT",
            },
            "P1": {
                "purpose": "complexity signal observability",
                "planned_units": "20-50 paired scenes, 3-5 relation doses",
                "status": "NOT_AUTHORIZED_DEPENDS_ON_P0_AND_CONSTRUCT_REVIEW",
                "executed_cases": 0,
            },
            "P2": {
                "purpose": "baseline qualification pilot",
                "status": "NOT_AUTHORIZED",
                "executed_cases": 0,
            },
            "P3": {
                "purpose": "confirmatory experiment",
                "status": "NOT_AUTHORIZED",
                "executed_cases": 0,
            },
        },
        "failure_differential": {
            "current_classification": [
                "EXECUTION_FAILURE_ASSET_NOT_MATERIALIZED",
                "SUBSTRATE_QUALIFICATION_HOLD_CHECKPOINT_PROVENANCE",
                "FORMULATION_HOLD_RELATION_COUNT_IDENTIFIABILITY",
                "BASELINE_HOLD_SAME_ACCESS_SUITE_INCOMPLETE",
            ],
            "scientific_belief_update": (
                "No model outcome was observed, so the mechanism hypothesis is neither "
                "supported nor falsified."
            ),
            "not_a_mechanism_failure": True,
        },
        "next_single_action": {
            "action": "P0_ASSET_AND_CONSTRUCT_DECISION",
            "requires_human_or_operator_input": True,
            "options": [
                (
                    "obtain verified acceptance of the 3D-FRONT/3D-FUTURE research terms "
                    "and train the official two-stage InstructScene stack under a separately "
                    "authorized budget"
                ),
                (
                    "use third-party checkpoints only as a separately labeled execution smoke, "
                    "never as official checkpoint reproduction evidence"
                ),
            ],
            "before_any_gpu_or_outcome_access": [
                "freeze prompt-length/content control for nested |R| doses",
                "freeze same-access baseline grouping",
                "freeze text-vs-structure intervention semantics",
            ],
        },
        "artifact_policy": {
            "append_only_per_case": True,
            "atomic_writes": True,
            "resume_support": True,
            "idempotent_case_ids": True,
            "required_hashes": [
                "git SHA",
                "dataset revision",
                "model revision",
                "config hash",
                "input hash",
                "output hash",
                "evaluator hash",
            ],
            "no_outcomes_read_in_this_pre_f0": True,
            "provider_calls_executed": 0,
            "gpu_calls_executed": 0,
        },
        "authority": authority,
        "scientific_authority": False,
        "execution_authority": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--instructscene-repo",
        type=Path,
        default=Path(
            "/data/wyt/constraint-capacity-source-audit-20260829/"
            "InstructScene-a9097a62c484c56ac7be5ec2928ef497cbbaaf24"
        ),
    )
    parser.add_argument(
        "--atiss-repo",
        type=Path,
        default=Path("/data/wyt/port010-alt-substrate-source-audit-20260828/ATISS"),
    )
    parser.add_argument(
        "--diffuscene-repo",
        type=Path,
        default=Path("/data/wyt/port010-alt-substrate-source-audit-20260828/DiffuScene"),
    )
    parser.add_argument("--hf-revision", default=EXPECTED_HF_REVISION)
    args = parser.parse_args()
    artifact = build(args)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(artifact, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
