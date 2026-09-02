#!/usr/bin/env python3
from __future__ import annotations

import argparse, hashlib, json, shutil, sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research_pipeline.e2_r17_controlled_spreadsheet_suite import BUILDERS
from research_pipeline.e2_r17_controlled_suite_schema import (
    DISTRACTOR_COUNTS, FAMILIES, FAMILY_CODES, L9_PROFILES,
    add_distractors, answer_cells, canonical_sha, new_book, normalize_xlsx,
    seeded_rng, select_by_hash, sha256_file, write_json,
)

SUITE_ID = "E2-R17-PROSPECTIVE-HETEROGENEITY-SUITE-V2"
UPDATE_BLOCKS = tuple(range(7, 13))
HELDOUT_BLOCK = 13


def build_task(root: Path, *, block: int, family: str, profile_index: int, role: str) -> dict[str, Any]:
    depth, distractor_level, ambiguity = L9_PROFILES[profile_index]
    task_id = f"r17-b{block}-{FAMILY_CODES[family]}-p{profile_index}"
    rng = seeded_rng(task_id)
    wb = new_book(task_id)
    distractors = add_distractors(wb, DISTRACTOR_COUNTS[distractor_level], rng, ambiguity)
    instruction, answer_position, expected = BUILDERS[family](wb, rng, depth, ambiguity, task_id)
    task_dir = root / "spreadsheetbench_verified_400" / "spreadsheet" / task_id
    task_dir.mkdir(parents=True, exist_ok=True)
    init = task_dir / f"{task_id}_init.xlsx"
    golden = task_dir / f"{task_id}_golden.xlsx"
    expected_values = {f"{s}!{c}": wb[s][c].value for s,c in answer_cells(answer_position)}
    for s,c in answer_cells(answer_position): wb[s][c] = None
    wb.save(init); normalize_xlsx(init)
    for key,val in expected_values.items():
        s,c=key.split("!",1); wb[s][c]=val
    wb.save(golden); normalize_xlsx(golden); wb.close()
    return {
        "record": {"id":task_id,"instruction":instruction,"spreadsheet_path":f"spreadsheet/{task_id}","answer_position":answer_position,"answer_sheet":None,"instruction_type":family},
        "metadata": {"id":task_id,"suite_id":SUITE_ID,"block":block,"role":role,"primary_failure_family":family,"profile_index":profile_index,"procedure_depth_level":depth,"distractor_level":distractor_level,"distractor_count":DISTRACTOR_COUNTS[distractor_level],"schema_ambiguity_level":ambiguity,"distractor_sheets":distractors,"answer_position":answer_position,"expected":expected,"golden_answer_cells":expected_values},
        "init": init, "golden": golden,
    }


def rows_for_manifest(root: Path) -> list[dict[str, Any]]:
    out=[]
    for p in sorted(root.rglob("*")):
        if p.is_file() and p.name != "suite_manifest.json":
            out.append({"path":str(p.relative_to(root)),"size":p.stat().st_size,"sha256":sha256_file(p)})
    return out


def main() -> int:
    ap=argparse.ArgumentParser(); ap.add_argument("--output-root",type=Path,required=True); ap.add_argument("--old-suite-root",type=Path,required=True); ap.add_argument("--overwrite",action="store_true"); a=ap.parse_args()
    root=a.output_root
    if root.exists():
        if not a.overwrite: raise FileExistsError(root)
        shutil.rmtree(root)
    (root/"spreadsheetbench_verified_400").mkdir(parents=True)
    records=[]; meta=[]; built=[]
    for b in UPDATE_BLOCKS:
        for fam in FAMILIES:
            for p in range(len(L9_PROFILES)):
                x=build_task(root,block=b,family=fam,profile_index=p,role="prospective_update_candidate")
                records.append(x["record"]); meta.append(x["metadata"]); built.append(x)
    for fam in FAMILIES:
        for p in range(len(L9_PROFILES)):
            x=build_task(root,block=HELDOUT_BLOCK,family=fam,profile_index=p,role="prospective_heldout_candidate")
            records.append(x["record"]); meta.append(x["metadata"]); built.append(x)
    records.sort(key=lambda x:x["id"]); meta.sort(key=lambda x:x["id"])
    write_json(root/"spreadsheetbench_verified_400"/"dataset.json",records)
    write_json(root/"r17_controlled_metadata.json",meta)

    cal={}; test={}; reserve={}
    by_id={m["id"]:m for m in meta}
    for fam in FAMILIES:
        code=FAMILY_CODES[fam]
        for depth in (0,1,2):
            ids=sorted(m["id"] for m in meta if m["role"]=="prospective_update_candidate" and m["primary_failure_family"]==fam and m["procedure_depth_level"]==depth)
            if len(ids)!=18: raise RuntimeError(f"candidate shape {fam} d{depth}: {len(ids)}")
            profiles=sorted({by_id[i]["profile_index"] for i in ids})
            if len(profiles)!=3: raise RuntimeError(f"profile shape {fam} d{depth}: {profiles}")
            low_order=sorted(profiles,key=lambda p:hashlib.sha256(f"ph-v2-low|{fam}|d{depth}|p{p}".encode()).hexdigest())
            cal_low=low_order[0]; test_low=low_order[1]
            cal_ids=[]; test_ids=[]; reserve_ids=[]
            for profile in profiles:
                pids=sorted((i for i in ids if by_id[i]["profile_index"]==profile),key=lambda v:hashlib.sha256(f"ph-v2-cell|{fam}|d{depth}|p{profile}|{v}".encode()).hexdigest())
                ccount=2 if profile==cal_low else 3
                tcount=2 if profile==test_low else 3
                cal_ids.extend(pids[:ccount]); test_ids.extend(pids[ccount:ccount+tcount]); reserve_ids.extend(pids[ccount+tcount:])
            cal[f"ph-cal-{code}-d{depth}"]=sorted(cal_ids)
            test[f"ph-test-{code}-d{depth}"]=sorted(test_ids)
            reserve[f"{code}-d{depth}"]=sorted(reserve_ids)
    heldout=[]; heldout_reserve=[]
    import itertools
    for fam in FAMILIES:
        ids=sorted(m["id"] for m in meta if m["role"]=="prospective_heldout_candidate" and m["primary_failure_family"]==fam)
        combos=[]
        for combo in itertools.combinations(ids,3):
            rows=[by_id[i] for i in combo]
            if len({r["procedure_depth_level"] for r in rows})==3 and len({r["distractor_level"] for r in rows})==3 and len({r["schema_ambiguity_level"] for r in rows})==3:
                combos.append(combo)
        if not combos: raise RuntimeError(f"no heldout orthogonal triple for {fam}")
        chosen=min(combos,key=lambda c:hashlib.sha256((f"ph-v2-heldout|{fam}|"+"|".join(c)).encode()).hexdigest())
        heldout.extend(chosen); heldout_reserve.extend(sorted(set(ids)-set(chosen)))
    heldout=sorted(heldout)
    split={"schema_version":"1.0","suite_id":SUITE_ID,"selection_is_outcome_blind":True,"selection_algorithm":"SHA256 fixed salts over pre-outcome task IDs","prediction_unit":"primary_failure_family x procedure_depth_level","cal_streams":cal,"test_streams":test,"update_reserve_integrity_only":reserve,"common_heldout_probe":heldout,"heldout_reserve_integrity_only":sorted(heldout_reserve),"rules":{"all_scientific_tasks_disjoint_from_closed_b0_b6":True,"cal_and_test_disjoint":True,"heldout_never_fed_to_updater":True,"test_outcomes_forbidden_before_cal_prediction_freeze":True,"reserve_never_replaces_model_failure_or_bad_outcome":True}}
    write_json(root/"r17_prospective_split_manifest.json",split)

    old_meta=json.loads((a.old_suite_root/"r17_controlled_metadata.json").read_text())
    old_ids={x["id"] for x in old_meta}; new_ids={x["id"] for x in meta}
    id_overlap=sorted(old_ids & new_ids)
    old_hashes=set()
    for p in (a.old_suite_root/"spreadsheetbench_verified_400"/"spreadsheet").rglob("*.xlsx"): old_hashes.add(sha256_file(p))
    new_hashes={sha256_file(x[k]) for x in built for k in ("init","golden")}
    content_overlap=sorted(old_hashes & new_hashes)
    if id_overlap or content_overlap: raise RuntimeError(f"old overlap ids={len(id_overlap)} content={len(content_overlap)}")
    cal_ids={x for xs in cal.values() for x in xs}; test_ids={x for xs in test.values() for x in xs}; h=set(heldout)
    if cal_ids & test_ids or cal_ids & h or test_ids & h: raise RuntimeError("new split overlap")
    if len(cal)!=18 or len(test)!=18 or any(len(x)!=8 for x in cal.values()) or any(len(x)!=8 for x in test.values()) or len(heldout)!=18: raise RuntimeError("shape mismatch")

    files=rows_for_manifest(root)
    manifest={"schema_version":"1.0","suite_id":SUITE_ID,"task_count":len(records),"families":list(FAMILIES),"update_blocks":list(UPDATE_BLOCKS),"heldout_block":HELDOUT_BLOCK,"prediction_cells":18,"cal_streams":18,"test_streams":18,"tasks_per_stream":8,"heldout_tasks":18,"dataset_sha256":canonical_sha(files),"files":files,"split_manifest_sha256":sha256_file(root/"r17_prospective_split_manifest.json"),"metadata_sha256":sha256_file(root/"r17_controlled_metadata.json"),"old_suite_disjointness":{"old_task_id_overlap":0,"old_xlsx_sha256_overlap":0},"provider_calls":0,"scientific_outcomes_accessed":False,"status":"PASS_ZERO_PROVIDER_STATIC_MATERIALIZATION"}
    write_json(root/"suite_manifest.json",manifest)
    print(json.dumps({k:manifest[k] for k in ["status","task_count","prediction_cells","cal_streams","test_streams","heldout_tasks","split_manifest_sha256","metadata_sha256","old_suite_disjointness"]},indent=2))
    return 0
if __name__=="__main__": raise SystemExit(main())
