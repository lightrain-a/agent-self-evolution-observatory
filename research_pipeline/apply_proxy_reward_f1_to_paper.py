from __future__ import annotations

import json
from pathlib import Path


def _esc(text: str) -> str:
    return str(text).replace("_", "\\_").replace("%", "\\%")


def main() -> None:
    result_path = Path("generated/d2-proxy-reward-memory-f1.json")
    section_path = Path("paper_drafts/d2-proxy-reward-memory-variance-iclr2027/sections/03b_f1.tex")
    main_path = Path("paper_drafts/d2-proxy-reward-memory-variance-iclr2027/main.tex")
    ledger_path = Path("generated/d2-proxy-reward-memory-variance-claim-ledger.json")
    qa_contract_path = Path("generated/d2-active-paper-qa-contracts-20260821.json")

    r = json.loads(result_path.read_text(encoding="utf-8"))
    s = r["summary"]
    paired = int(s.get("aligned_success_failure_rollouts") or 0)
    raw_rate = s.get("paired_action_signature_divergence_rate")
    falsifier_result = str(r.get("falsifier_result") or "")
    if paired <= 0 or raw_rate is None or falsifier_result not in {"SURVIVES_F1", "FALSIFIED_F1"}:
        print(json.dumps({
            "status": "SUPPORT_FAILURE_NO_MANUSCRIPT_UPDATE",
            "f1_status": r.get("status"),
            "falsifier_result": falsifier_result,
            "aligned_rollouts": paired,
            "paired_action_signature_divergence_rate": raw_rate,
            "scientific_authority": False,
        }, ensure_ascii=False, indent=2))
        return

    rate = float(raw_rate)
    raw_modal_rate = s.get("modal_action_signature_difference_rate")
    raw_shift_rate = s.get("memory_condition_shift_from_no_memory")
    modal_rate = float(raw_modal_rate) if raw_modal_rate is not None else None
    shift_rate = float(raw_shift_rate) if raw_shift_rate is not None else None

    rows = []
    for task in r.get("task_results") or []:
        modes = task.get("modal_signatures") or {}
        rows.append(
            f"{_esc(task.get('future_task'))} & {_esc(modes.get('success_label_memory',''))} & "
            f"{_esc(modes.get('failure_label_memory',''))} & "
            f"{int(task.get('aligned_divergent_count') or 0)}/{int(task.get('aligned_pair_count') or 0)} \\\\"
        )

    if falsifier_result == "FALSIFIED_F1":
        interpretation = (
            f"Across {paired} aligned success-memory versus failure-memory rollouts, the structured next-action signature never diverges. "
            f"The paired divergence rate is {rate:.3f}. The frozen falsifier is evaluable across every required aligned rollout. "
            "This directly falsifies the narrow hypothesis that reward-induced memory divergence changes the immediate next structured action at these review-state intervention points. "
            "The experiment observes one decision point. Later within-trajectory divergence remains an active hypothesis. Terminal success variance also remains active experiment debt."
        )
        first_action_verdict = "REFUTED"
        first_action_retain = False
        deeper_state = "IMMEDIATE_FIRST_ACTION_REFUTED_DEEPER_TRAJECTORY_PENDING"
    else:
        modal_sentence = (
            f"The modal action differs on {modal_rate:.3f} of comparable held-out observations. "
            if modal_rate is not None
            else "The paired action witness is sufficient for the frozen falsifier; modal comparison is unavailable. "
        )
        interpretation = (
            f"Across {paired} aligned success-memory versus failure-memory rollouts, the structured next-action signature diverges at rate {rate:.3f}. "
            + modal_sentence
            + "This provides direct support that reward-induced memory divergence can reach a future action decision under fixed browser state. "
            + "Terminal success variance remains active experiment debt."
        )
        first_action_verdict = "SUPPORTED"
        first_action_retain = True
        deeper_state = "FIRST_ACTION_SUPPORTED_TERMINAL_VARIANCE_PENDING"

    shift_sentence = (
        f"The no-memory comparison provides a separate state-sensitivity check. At least one memory condition changes the modal action relative to the no-memory condition on {shift_rate:.3f} of comparable held-out observations."
        if shift_rate is not None
        else "The no-memory comparison is unavailable because no comparable no-memory policy output was recovered."
    )

    section = f"""\\section{{F1: Does Memory Divergence Reach a Future Action?}}
\\label{{sec:f1}}
F0 establishes that the reward label changes the memory written from an identical trajectory. F1 tests whether those paired memories change a held-out policy decision. Four complete F0 memory pairs are mapped to four held-out Shopping tasks from the same released trajectory set. The intervention point is the first strategic decision after the Reviews section is open. The future task and browser observation stay fixed. The policy model is Doubao Seed 2.0 Mini. Each memory condition receives three rollouts at temperature 0.2. A no-memory condition supplies an additional reference.

{interpretation}

{shift_sentence}

\\begin{{table}}[t]
\\centering
\\caption{{Held-out first-action signatures under paired reward-conditioned memories.}}
\\label{{tab:f1}}
\\small
\\begin{{tabular}}{{lccc}}
\\toprule
Future task & Success-memory mode & Failure-memory mode & Divergent paired rollouts \\\\
\\midrule
{chr(10).join(rows)}
\\bottomrule
\\end{{tabular}}
\\end{{table}}

This experiment separates memory-content change from immediate behavioral change. The result updates only the action scope that F1 observes. The run-level variance protocol in Section~\\ref{{sec:variance}} continues through later decisions and terminal outcomes.
"""
    section_path.write_text(section, encoding="utf-8")

    main = main_path.read_text(encoding="utf-8")
    if "\\input{sections/03b_f1}" not in main:
        main = main.replace("\\input{sections/03_f0}\n", "\\input{sections/03_f0}\n\\input{sections/03b_f1}\n")
        main_path.write_text(main, encoding="utf-8")

    ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
    claims = [c for c in ledger["claims"] if c.get("claim_id") not in {"C4a"}]
    for c in claims:
        if c.get("claim_id") == "C4":
            c["claim"] = "Reward-induced memory perturbations can amplify later within-trajectory behavior and terminal success variance when the memories are reused on matched future tasks."
            c["verdict"] = "ACTIVE_UNREFUTED_HYPOTHESIS"
            c["evidence_state"] = deeper_state
            c["closure_authority"] = ""
            c["retain_in_manuscript"] = True
            c["claim_narrowing_required"] = False
            c["experiment_debt"] = ["multi-step paired policy continuation", "terminal environment outcome execution", "controlled reward-corruption-rate variance experiment"]
    claims.insert(4, {
        "claim_id": "C4a",
        "claim": "Reward-induced memory divergence changes the immediate next structured browser action at the held-out review-state intervention points used by F1.",
        "verdict": first_action_verdict,
        "evidence_refs": ["generated/d2-proxy-reward-memory-f1.json"],
        "retain_in_manuscript": first_action_retain,
        "closure_authority": "direct_counterevidence" if first_action_verdict == "REFUTED" else "",
        "observed_paired_action_signature_divergence_rate": rate,
        "observed_modal_action_signature_difference_rate": modal_rate,
    })
    ledger["claims"] = claims
    ledger["f1_artifact"] = {
        "path": str(result_path),
        "status": r.get("status"),
        "falsifier_result": falsifier_result,
        "paired_action_signature_divergence_rate": rate,
        "modal_action_signature_difference_rate": modal_rate,
        "memory_condition_shift_from_no_memory": shift_rate,
        "aligned_rollouts": paired,
    }
    ledger_path.write_text(json.dumps(ledger, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    qa = json.loads(qa_contract_path.read_text(encoding="utf-8"))
    for paper in qa["papers"]:
        if paper.get("paper_id") != "D2-PAPER-PROXY-REWARD-MEMORY-VARIANCE":
            continue
        paper["required_pdf_fragments"] = list(dict.fromkeys((paper.get("required_pdf_fragments") or []) + [f"paired divergence rate is {rate:.3f}", "held-out first-action signatures"]))
        checks = [x for x in paper.get("artifact_checks") or [] if x.get("path") != str(result_path)]
        checks.extend([
            {"path": str(result_path), "key": "summary.paired_action_signature_divergence_rate", "equals": rate},
            {"path": str(result_path), "key": "summary.modal_action_signature_difference_rate", "equals": modal_rate},
            {"path": str(result_path), "key": "falsifier_result", "equals": falsifier_result},
        ])
        paper["artifact_checks"] = checks
    qa_contract_path.write_text(json.dumps(qa, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(json.dumps({"paired_action_signature_divergence_rate": rate, "modal_action_signature_difference_rate": modal_rate, "memory_condition_shift_from_no_memory": shift_rate, "claim_C4a": first_action_verdict, "deeper_claim_state": deeper_state}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
