#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import shutil
import tempfile
import zipfile
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
SRC = HERE / "source"
DOWNLOADS = REPO / "downloads"
ART = Path("/data/wyt/agent-self-evolution-observatory/paper-acceptance-artifacts/D2-PAPER-PROXY-REWARD-MEMORY-VARIANCE")
RUN_STAGE1_R1 = Path("/data/wyt/agent-self-evolution-observatory/runs/d2-proxy-reward-o6-cross-writer-glm53-stage1-r1-4096-20260824")
RUN_STAGE2 = Path("/data/wyt/agent-self-evolution-observatory/runs/d2-proxy-reward-o6-cross-writer-terminal-stage2-20260824")

PDF_OUT = DOWNLOADS / "D2-PAPER-PROXY-REWARD-MEMORY-VARIANCE-stanford-r3-20260824.pdf"
SOURCE_OUT = DOWNLOADS / "D2-PAPER-PROXY-REWARD-MEMORY-VARIANCE-stanford-r3-20260824-source.zip"
SUPP_OUT = DOWNLOADS / "D2-PAPER-PROXY-REWARD-MEMORY-VARIANCE-stanford-r3-20260824-supplement.zip"

FORBIDDEN_TEXT = ["/home/", "/data/", "wyt@", "222.20.", "202.69.", "10.42.", "ARK_API_KEY", "source_message_ref"]
PRIVATE_KEY_FRAGMENTS = ("path", "run_root", "artifact_path", "provider_env_file", "source_message_ref")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def sanitize(value: Any) -> Any:
    if isinstance(value, dict):
        out = {}
        for key, item in value.items():
            lk = str(key).lower()
            if any(fragment in lk for fragment in PRIVATE_KEY_FRAGMENTS) and not lk.endswith("sha256"):
                continue
            # The safe-summary boolean merely says no secret is emitted; it is not useful in the public supplement.
            if lk == "api_key_in_output":
                continue
            out[key] = sanitize(item)
        return out
    if isinstance(value, list):
        return [sanitize(x) for x in value]
    if isinstance(value, str):
        if any(token in value for token in FORBIDDEN_TEXT):
            return "<private-location-redacted>"
        return value
    return value


def public_projection(source: Path) -> dict[str, Any]:
    return {
        "schema_version": "1.0",
        "projection_type": "anonymous-public-projection",
        "source_artifact_sha256": sha(source),
        "payload": sanitize(load(source)),
    }


def copy_source_tree(dst: Path) -> None:
    dst.mkdir(parents=True, exist_ok=True)
    for name in ["main.tex", "references.bib", "iclr2027_conference.bst", "iclr2027_conference.sty", "natbib.sty", "fancyhdr.sty", "build_figures.py"]:
        shutil.copy2(SRC / name, dst / name)
    shutil.copytree(SRC / "figures", dst / "figures")
    shutil.copytree(SRC / "sections", dst / "sections")


def zip_tree(root: Path, out: Path) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(out, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for path in sorted(root.rglob("*")):
            if path.is_file():
                zf.write(path, path.relative_to(root.parent))


def privacy_scan(root: Path) -> list[str]:
    hits = []
    binary_ext = {".pdf", ".png", ".jpg", ".jpeg", ".zip"}
    for path in root.rglob("*"):
        if not path.is_file() or path.suffix.lower() in binary_ext:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for token in FORBIDDEN_TEXT:
            if token in text:
                hits.append(f"{path.relative_to(root)}::{token}")
    return hits


def build_supplement(tree: Path, *, source_sha: str, pdf_sha: str) -> None:
    evidence = tree / "evidence"
    code = tree / "code"
    evidence.mkdir(parents=True, exist_ok=True)
    code.mkdir(parents=True, exist_ok=True)

    frozen = {
        "f0-write-channel.json": ART / "f0-write-channel.json",
        "f0c-prompt-control.json": ART / "f0c-prompt-control.json",
        "f1d-distributional-audit.json": ART / "f1d-distributional-audit.json",
        "f2-initial-terminal.json": ART / "f2-initial-terminal.json",
        "f2r1-confirmatory.json": ART / "f2r1-confirmatory.json",
        "f2r1-derived-corruption-variance.json": ART / "f2r1-derived-corruption-variance.json",
        "f2r1-heterogeneity-bootstrap.json": ART / "f2r1-heterogeneity-bootstrap.json",
        "strategy-slot-audit.json": ART / "revisions/20260822-stanford-paperonly-r2/strategy-slot-audit.json",
        "provider-failure-forensic.json": ART / "revisions/20260822-stanford-paperonly-r2/provider-failure-forensic.json",
    }
    for name, src in frozen.items():
        if name == "f2r1-derived-corruption-variance.json":
            projected = sanitize(load(src))
            if isinstance(projected, dict):
                projected["public_projection_source_sha256"] = sha(src)
            write_json(evidence / name, projected)
        else:
            shutil.copy2(src, evidence / name)

    branch_files = {
        "existing-evidence-diagnostics.json": HERE / "existing-evidence-diagnostics.json",
        "manuscript-qa.json": HERE / "manuscript-qa.json",
        "o6-stage1-failure-asset.json": HERE / "o6-stage1-failure-asset.json",
        "o6-final-evidence.json": HERE / "o6-final-evidence.json",
        "stanford-r3-o6-revision-receipt.json": HERE / "stanford-r3-o6-revision-receipt.json",
    }
    for name, src in branch_files.items():
        shutil.copy2(src, evidence / name)

    public_sources = {
        "o5-manuscript-evidence-public.json": HERE / "o5-manuscript-evidence.json",
        "o6-design-public.json": HERE / "o6-cross-writer-design.json",
        "o6-stage1-r1-result-public.json": RUN_STAGE1_R1 / "o6-stage1-r1-result.json",
        "o6-stage2-contract-public.json": RUN_STAGE2 / "o6-stage2-contract.json",
        "o6-stage2-result-public.json": RUN_STAGE2 / "o6-stage2-result.json",
    }
    for name, src in public_sources.items():
        write_json(evidence / name, public_projection(src))

    shutil.copy2(HERE / "build_o6_final_evidence.py", code / "build_o6_final_evidence.py")

    qa = load(HERE / "manuscript-qa.json")
    o6 = load(HERE / "o6-final-evidence.json")
    receipt = load(HERE / "stanford-r3-o6-revision-receipt.json")
    projection = {
        "schema_version": "1.0",
        "receipt_type": "supplement-current-projection",
        "paper_id": "D2-PAPER-PROXY-REWARD-MEMORY-VARIANCE",
        "revision": "stanford-r3-o6-cross-writer-20260824",
        "current_pdf_sha256": pdf_sha,
        "current_source_zip_sha256": source_sha,
        "new_experiment": True,
        "scientific_values_changed": True,
        "claim_expansion": False,
        "new_provider_calls_exact": None,
        "new_provider_calls_observable_lower_bound": qa["new_provider_calls_observable_lower_bound"],
        "new_scientifically_usable_provider_calls": qa["new_scientifically_usable_provider_calls"],
        "main_text_pages": qa["main_text_pages"],
        "references_begin_page": qa["references_begin_page"],
        "o6_write_channel_cross_writer_supported": o6["claim_boundary"]["write_channel_cross_writer_supported_on_four_sources"],
        "o6_terminal_cross_writer_generalization_supported": o6["claim_boundary"]["terminal_cross_writer_generalization_supported"],
        "o6_provider_posts_observable_lower_bound": o6["execution_accounting"]["o6_provider_posts_observable_lower_bound"],
        "known_provider_posts_observable_lower_bound_full_paper": receipt["system_paper_requirements"]["experiment_program_E1_E6"]["E6_efficiency_cost_scale"]["evidence"]["known_provider_posts_observable_lower_bound"],
        "scientific_authority": False,
        "experiment_authority": False,
        "submission_authority": False,
    }
    write_json(tree / "CURRENT-PROJECTION.json", projection)

    readme = """# Proxy Reward Memory Variance - Stanford R3 O5/O6 supplement\n\nThis anonymous supplement binds the frozen evidence used by the current manuscript. O5 adds a fresh 32-call no-memory branch-location control after a separately recorded execution-validator failure; only the frozen recovery outcomes enter science. O6 adds a sequential GLM-5.3 cross-writer test. The repaired writer stage changes all four paired memories and title sets (mean token-set Jaccard distance 0.737482), but the 256-call terminal replication yields mean absolute success-rate difference 0.140625 with permutation p=0.00012, below the preregistered 0.15 minimum-effect floor. The manuscript therefore does not claim writer-invariant terminal generalization.\n\nThe failed parent GLM writer attempt remains execution/operationalization debt with zero scientific authority. Its exact provider POST count is unreconstructible after a concurrency race; the observable lower bound is nine. Including O5 and O6, the paper has at least 841 observable provider POSTs, excluding the unresolved low-level count of the early 12-unit action witness. No training or local GPU fine-tuning is used.\n\nPrivate raw model text, provider response identifiers, human-authorization artifacts, host paths, and credentials are intentionally excluded. Public projections preserve source artifact SHA-256 bindings while removing private locations. Run `python verify_current_supplement.py` from this directory to validate the numerical and claim-boundary contract.\n"""
    (tree / "README.md").write_text(readme, encoding="utf-8")

    verifier = r'''from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parent
E=ROOT/'evidence'
def L(n): return json.load(open(E/n))
f0=L('f0-write-channel.json'); f2=L('f2r1-confirmatory.json'); q=L('manuscript-qa.json')
o6=L('o6-final-evidence.json'); r=L('stanford-r3-o6-revision-receipt.json'); fail=L('o6-stage1-failure-asset.json')
o5=L('o5-manuscript-evidence-public.json')['payload']; s1=L('o6-stage1-r1-result-public.json')['payload']; s2=L('o6-stage2-result-public.json')['payload']; proj=json.load(open(ROOT/'CURRENT-PROJECTION.json'))
checks=[
 f0['summary']['paired_trajectories_complete']==4,
 abs(f2['summary']['observed_mean_absolute_success_rate_difference']-0.15625)<1e-12,
 abs(f2['summary']['permutation_p_ge_observed']-0.00074)<1e-12,
 o5['status']=='O5_FRESH_NO_MEMORY_CONTROL_COMPLETE', o5['execution_accounting']['recovery_scientifically_usable_units']==32,
 o5['execution_accounting']['old_exploratory_no_memory_calls_reused']==0,
 s1['status']=='O6_STAGE1_COMPLETE', s1['summary']['complete_provider_calls']==8, s1['summary']['stage1_gate_pass'] is True,
 abs(s1['summary']['mean_token_jaccard_distance']-0.737482)<1e-12,
 s2['status']=='O6_STAGE2_COMPLETE', s2['summary']['complete_primary_calls']==256, s2['summary']['provider_failures']==0,
 abs(s2['summary']['observed_mean_absolute_success_rate_difference']-0.140625)<1e-12,
 abs(s2['summary']['permutation_p_ge_observed']-0.00012)<1e-12, s2['summary']['gate_pass'] is False,
 o6['writer_stage']['complete_pairs']==4, o6['terminal_stage']['joint_gate_pass'] is False,
 o6['cross_writer_comparison']['same_direction_among_nonzero_both']==4, o6['cross_writer_comparison']['opposite_direction_among_nonzero_both']==2,
 o6['execution_accounting']['o6_provider_posts_observable_lower_bound']==273,
 fail['execution_concurrency_failure']['provider_post_count_observable_lower_bound']==9,
 q['status']=='PASS', q['main_text_pages']==9, q['references_begin_page']==10,
 q['checks']['o5_fresh_no_memory_control'] is True, q['checks']['o6_cross_writer_boundary'] is True,
 q['checks']['system_E4_robustness_boundary'] is True, q['checks']['system_E5_negative_failure'] is True, q['checks']['system_E6_efficiency_cost_scale'] is True,
 r['objections']['PROXY-O6']['revision_status']=='PARTIALLY_ADDRESSED_WITH_FRESH_CROSS_WRITER_EXECUTION',
 r['system_paper_requirements']['experiment_program_E1_E6']['E6_efficiency_cost_scale']['evidence']['known_provider_posts_observable_lower_bound']==841,
 proj['claim_expansion'] is False, proj['o6_terminal_cross_writer_generalization_supported'] is False,
]
print({'checks':len(checks),'passed':sum(checks),'pass':all(checks)})
sys.exit(0 if all(checks) else 1)
'''
    (tree / "verify_current_supplement.py").write_text(verifier, encoding="utf-8")


def main() -> int:
    DOWNLOADS.mkdir(parents=True, exist_ok=True)
    shutil.copy2(HERE / "paper.pdf", PDF_OUT)
    with tempfile.TemporaryDirectory(prefix="c1-o6-package-") as td:
        tmp = Path(td)
        source_root = tmp / "source"
        copy_source_tree(source_root)
        zip_tree(source_root, SOURCE_OUT)
        source_sha = sha(SOURCE_OUT)
        pdf_sha = sha(PDF_OUT)

        supp_root = tmp / "supplement"
        build_supplement(supp_root, source_sha=source_sha, pdf_sha=pdf_sha)
        hits = privacy_scan(supp_root)
        if hits:
            raise RuntimeError("supplement privacy scan failed: " + "; ".join(hits[:20]))
        zip_tree(supp_root, SUPP_OUT)

    print(json.dumps({
        "pdf": {"path": str(PDF_OUT), "sha256": sha(PDF_OUT)},
        "source_zip": {"path": str(SOURCE_OUT), "sha256": sha(SOURCE_OUT)},
        "supplement_zip": {"path": str(SUPP_OUT), "sha256": sha(SUPP_OUT)},
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
