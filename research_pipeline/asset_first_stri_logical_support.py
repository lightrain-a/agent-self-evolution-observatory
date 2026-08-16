from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import time
from collections import Counter
from pathlib import Path
from typing import Any

from .asset_first_stri_certificate import certify

VALUE_SETS = {
    "Name": ["Ada", "Ben", "Cora", "Dion", "Eli", "Faye"],
    "Drink": ["Tea", "Coffee", "Juice", "Water", "Milk", "Cocoa"],
    "Project": ["Robot", "Garden", "Mural", "Archive", "Theater", "Orchard"],
    "Day": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"],
    "Color": ["Red", "Blue", "Green", "Yellow", "White", "Purple"],
    "Pet": ["Cat", "Dog", "Bird", "Fish", "Horse", "Rabbit"],
}


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def file_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def compiler_bundle_sha(package_root: Path) -> str:
    lines = []
    for path in sorted(package_root.glob("skill_*/compiler.json")):
        rel = path.relative_to(package_root).as_posix()
        lines.append(f"{file_sha(path)}  {rel}\n")
    return hashlib.sha256("".join(lines).encode("utf-8")).hexdigest()


def validate_asset(contract: dict[str, Any]) -> dict[str, Any]:
    author = contract["author_asset"]
    repo = Path(author["repo"])
    package_root = repo / "logical_reasoning" / "packages"
    commit = subprocess.check_output(["git", "-C", str(repo), "rev-parse", "HEAD"], text=True).strip()
    checks = {
        "repo_commit": commit == author["repo_commit"],
        "compiler_py_sha": file_sha(repo / "logical_reasoning/compiler.py") == author["compiler_py_sha256"],
        "compiler_resources_py_sha": file_sha(repo / "logical_reasoning/compiler_resources.py") == author["compiler_resources_py_sha256"],
        "contracts_py_sha": file_sha(repo / "logical_reasoning/contracts.py") == author["contracts_py_sha256"],
        "initial_skills_sha": file_sha(repo / "logical_reasoning/initial_skills.json") == author["initial_skills_sha256"],
        "compiler_bundle_sha": compiler_bundle_sha(package_root) == author["compiler_bundle_sha256"],
    }
    return {"pass": all(checks.values()), "checks": checks, "commit": commit, "package_root": str(package_root)}


def build_blueprint(house_count: int, attribute_count: int, skill_id: str) -> dict[str, Any]:
    attributes = [
        {"name": name, "values": values[:house_count]}
        for name, values in list(VALUE_SETS.items())[:attribute_count]
    ]
    return {
        "task_family": "zebra_grid",
        "house_count": house_count,
        "theme": "compiler validation",
        "attributes": attributes,
        "difficulty": "medium" if house_count * attribute_count <= 20 else "hard",
        "skill_id": skill_id,
    }


def classify_certificate(*, all_source_units_valid: bool, certificate: dict[str, Any]) -> str:
    if not all_source_units_valid:
        return "INVALID_FIRST_PARTY_SUBSTRATE"
    ratio = certificate.get("optimal_global_package_weighting", {}).get("ratio")
    multi = int(certificate.get("multi_membership_rows") or 0)
    if ratio is not None and float(ratio) > 1.0 + 1e-8 and multi > 0:
        return "CROSS_DOMAIN_PACKAGE_ONLY_RESIDUAL"
    if ratio is not None and float(ratio) <= 1.0 + 1e-8:
        return "DISJOINT_OR_EQUALIZABLE_NEGATIVE_CONTROL"
    return "UNRESOLVED_SUPPORT_TOPOLOGY"


def run(contract: dict[str, Any], output_dir: Path) -> dict[str, Any]:
    started = time.monotonic()
    preflight = validate_asset(contract)
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "preflight.json").write_text(json.dumps(preflight, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if not preflight["pass"]:
        result = {
            "schema_version": "1.0",
            "experiment_id": contract["experiment_id"],
            "candidate_id": contract["candidate_id"],
            "decision": "INVALID_FIRST_PARTY_SUBSTRATE",
            "scientific_result_available": False,
            "protocol_valid_for_scientific_update": False,
            "preflight": preflight,
            "scientific_authority": False,
        }
        (output_dir / "result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return result

    repo = Path(contract["author_asset"]["repo"])
    if str(repo) not in sys.path:
        sys.path.insert(0, str(repo))
    from logical_reasoning.compiler import compile_zebra_blueprint
    from logical_reasoning.compiler_resources import compiler_sample_alignment_errors, load_compiler_spec
    from logical_reasoning.contracts import check_zebra_sample_contract

    skill_ids = [str(x) for x in contract["units"]["skill_ids"]]
    sizes = [(int(x[0]), int(x[1])) for x in contract["units"]["grid_sizes"]]
    seeds = [int(x) for x in contract["units"]["seeds"]]
    package_root = str(repo / "logical_reasoning" / "packages")
    specs = {sid: load_compiler_spec(sid, package_root=package_root) for sid in skill_ids}

    rows: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []
    raw_path = output_dir / "support-matrix.jsonl"
    with raw_path.open("w", encoding="utf-8") as handle:
        index = 0
        for source_skill_id in skill_ids:
            source_spec = specs[source_skill_id]
            for house_count, attribute_count in sizes:
                for seed in seeds:
                    blueprint = build_blueprint(house_count, attribute_count, source_skill_id)
                    try:
                        sample = compile_zebra_blueprint(blueprint, compiler_spec=source_spec, seed=seed)
                    except Exception as exc:
                        sample = None
                        failures.append({"source_skill_id": source_skill_id, "house_count": house_count, "attribute_count": attribute_count, "seed": seed, "error": f"compile_exception:{type(exc).__name__}:{exc}"})
                    if sample is None:
                        if not failures or failures[-1].get("source_skill_id") != source_skill_id or failures[-1].get("seed") != seed:
                            failures.append({"source_skill_id": source_skill_id, "house_count": house_count, "attribute_count": attribute_count, "seed": seed, "error": "compile_returned_none"})
                        index += 1
                        continue
                    contract_check = check_zebra_sample_contract(sample)
                    if float(contract_check.get("contract_valid", 0.0) or 0.0) < 1.0:
                        failures.append({"source_skill_id": source_skill_id, "house_count": house_count, "attribute_count": attribute_count, "seed": seed, "error": "author_contract_invalid", "contract": contract_check})
                        index += 1
                        continue
                    accepted = [sid for sid in skill_ids if not compiler_sample_alignment_errors(specs[sid], sample)]
                    constraint_counts = Counter(str(item.get("type") or "") for item in sample.get("constraints") or [] if isinstance(item, dict))
                    row = {
                        "level": 0,
                        "index": index,
                        "tool": f"zebra_{house_count}x{attribute_count}",
                        "source_skill_id": source_skill_id,
                        "house_count": house_count,
                        "attribute_count": attribute_count,
                        "seed": seed,
                        "accepted_skill_ids": accepted,
                        "membership_cardinality": len(accepted),
                        "constraint_type_counts": dict(sorted(constraint_counts.items())),
                        "author_contract_valid": True,
                    }
                    rows.append(row)
                    handle.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
                    index += 1

    expected_units = int(contract["units"]["total_source_units"])
    all_valid = len(rows) == expected_units and not failures
    certificate = certify(rows, context_id="skill_sp_logical_author_compiler_validation") if rows else {
        "decision": "NO_VALID_ROWS",
        "covered_rows": 0,
        "multi_membership_rows": 0,
        "optimal_global_package_weighting": {"ratio": None},
        "structural_witness": {"witness_count": 0},
        "scientific_authority": False,
    }
    decision = classify_certificate(all_source_units_valid=all_valid, certificate=certificate)
    raw_sha = file_sha(raw_path)
    result = {
        "schema_version": "1.0",
        "experiment_id": contract["experiment_id"],
        "candidate_id": contract["candidate_id"],
        "decision": decision,
        "scientific_result_available": all_valid,
        "protocol_valid_for_scientific_update": all_valid,
        "source_units_expected": expected_units,
        "source_units_valid": len(rows),
        "source_failures": failures,
        "support_matrix_sha256": raw_sha,
        "certificate": certificate,
        "elapsed_seconds": time.monotonic() - started,
        "model_calls": 0,
        "gpu_hours": 0.0,
        "paper_claim_C3_authorized": False,
        "paper_claim_C4_authorized": False,
        "scientific_authority": False,
    }
    (output_dir / "result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return result


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--contract", type=Path, required=True)
    ap.add_argument("--output-dir", type=Path, required=True)
    args = ap.parse_args()
    result = run(load_json(args.contract), args.output_dir)
    cert = result.get("certificate") or {}
    print(json.dumps({
        "decision": result["decision"],
        "valid": result["source_units_valid"],
        "expected": result["source_units_expected"],
        "multi": cert.get("multi_membership_rows"),
        "witnesses": (cert.get("structural_witness") or {}).get("witness_count"),
        "lp_ratio": (cert.get("optimal_global_package_weighting") or {}).get("ratio"),
        "elapsed_seconds": result["elapsed_seconds"],
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
