#!/usr/bin/env python3
"""Persist T0.5/T0 summaries and Research OS lessons after the frozen run."""
from __future__ import annotations
import argparse,json,sys
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from research_pipeline.c1_pacta_rb_qwen397 import atomic_json,sha256_file

T05=Path("/data/wyt/agent-self-evolution-observatory/runs/c1-pacta-rb-qwen397-t05-images-20260901-v1")
T0=Path("/data/wyt/agent-self-evolution-observatory/runs/c1-pacta-rb-qwen397-t0-source-trajectory-20260901-v2")
PAPER=ROOT/"paper_drafts/c1-manuscript-strengthening-20260825"
OS=ROOT/"research_pipeline/c1_pacta_rb_qwen397_t05_t0_source_acquisition_20260901.json"

def now():return datetime.now(timezone.utc).replace(microsecond=0).isoformat()
def load(path:Path):return json.loads(path.read_text())
def stamped(path:Path):return {"path":str(path),"sha256":sha256_file(path)}

def main():
 ap=argparse.ArgumentParser();ap.add_argument("--execution-sha",required=True);args=ap.parse_args()
 manifest=load(T05/"manifest-resolution.json");plan=load(T05/"blob-plan.json")
 receipt=load(T05/"blob-receipt.json");imported=load(T05/"import-receipt.json")
 runtime=load(T05/"runtime-qualification.json")
 t05_ready=runtime["decision"]=="T0_5_FIXED_IMAGES_READY"
 if t05_ready:
  smoke=load(T05/"synthetic-smoke.json")
  bridge=load(T0/"bridge-qualification.json");schedule=load(T0/"acquisition-schedule.json")
  support=load(T0/"support-audit.json")
 else:
  smoke={"schema_version":1,"created_at_utc":now(),"status":"NOT_RUN_DUE_T05_GATE","pass":False,
   "provider_calls":0,"source_trajectory_calls":0}
  bridge={"schema_version":1,"created_at_utc":now(),"status":"NOT_RUN_DUE_T05_GATE","pass":False,"provider_calls":0}
  schedule={"schema_version":1,"created_at_utc":now(),"status":"NOT_CREATED_DUE_T05_GATE","logical_attempts":0,
   "source_trajectory_calls":0,"writer_calls":0,"binder_calls":0,"shadow_calls":0,"final_measurement_calls":0}
  support={"schema_version":1,"created_at_utc":now(),"decision":runtime["decision"],
   "N_valid_trajectory":0,"N_valid_repository":0,"full_6_plus_5_design_recovered":False,
   "source_logical_attempts":0,"writer_calls":0,"binder_calls":0,"shadow_calls":0,"final_measurement_calls":0}
 freeze={"schema_version":1,"created_at_utc":now(),"decision":manifest["decision"],
  "stable_twice":manifest["stable_twice"],"supplied_observations_match":manifest["supplied_observations_match"],
  "mirror":manifest["mirror"],"rows":manifest["rows"],"source_artifact":stamped(T05/"manifest-resolution.json"),
  "provider_calls":0,"source_trajectory_calls":0,"writer_calls":0,"binder_calls":0,"shadow_calls":0,"final_measurement_calls":0}
 inventory={"schema_version":1,"created_at_utc":now(),"unique_blob_count":plan["unique_blob_count"],
  "unique_blob_bytes":plan["unique_blob_bytes"],"reusable_blob_count":plan["reusable_blob_count"],
  "reusable_blob_bytes":plan["reusable_blob_bytes"],"missing_blob_count_at_freeze":plan["missing_blob_count"],
  "missing_blob_bytes_at_freeze":plan["missing_blob_bytes"],"all_blobs_verified":receipt["all_blobs_verified"],
  "downloaded_bytes":sum(r["size"] for r in receipt["rows"] if r["status"]=="downloaded-and-verified"),
  "rows":plan["rows"],"plan_artifact":stamped(T05/"blob-plan.json"),"receipt_artifact":stamped(T05/"blob-receipt.json")}
 acquisition={"schema_version":1,"created_at_utc":now(),"decision":runtime["decision"],
  "manifest":stamped(T05/"manifest-resolution.json"),"blobs":stamped(T05/"blob-receipt.json"),
  "import":stamped(T05/"import-receipt.json"),"all_blobs_verified":receipt["all_blobs_verified"],
  "oci_import_status":f"{sum(r['exact_digest_pass'] for r in imported['rows'])}/11",
  "docker":imported["docker"],"infrastructure_retries_only":True,"scientific_retries":0}
 closure={"schema_version":1,"created_at_utc":now(),"execution_git_sha":args.execution_sha,
  "t05_decision":runtime["decision"],"runtime_qualified":runtime["qualified_images"],
  "multistep_smoke_pass":smoke["pass"],"bridge_identity_pass":bridge["pass"],
  "source_support_decision":support["decision"],"N_valid_trajectory":support["N_valid_trajectory"],
  "N_valid_repository":support["N_valid_repository"],"full_6_plus_5_design_recovered":support["full_6_plus_5_design_recovered"],
  "writer_calls":0,"binder_calls":0,"shadow_calls":0,"final_measurement_calls":0,"future_task_executions":0,
  "claim_authority":"NO_NEW_PACTA_EFFECT_EVIDENCE","active_manuscript":"R9",
  "strongest_failure_differential":"The frozen mirror manifests were stable and every blob was SHA-verified, but the substrate failed before model use: one exact image could not unpack under the 65,536-ID rootless mapping, and all ten imported images had /testbed HEAD values different from the frozen source base commits. This is image/runtime provenance failure, not PACTA or Qwen397 evidence."}
 copies={
 "c1-pacta-rb-qwen397-t05-image-manifest-freeze-20260901.json":freeze,
 "c1-pacta-rb-qwen397-t05-blob-inventory-20260901.json":inventory,
 "c1-pacta-rb-qwen397-t05-image-acquisition-result-20260901.json":acquisition,
 "c1-pacta-rb-qwen397-t05-runtime-qualification-20260901.json":runtime,
 "c1-pacta-rb-qwen397-t05-multistep-smoke-20260901.json":smoke,
 "c1-pacta-rb-qwen397-t0-v2-acquisition-schedule-20260901.json":schedule,
 "c1-pacta-rb-qwen397-t0-v2-support-audit-20260901.json":support,
 "c1-pacta-rb-qwen397-t0-v2-closure-20260901.json":closure}
 for name,payload in copies.items():atomic_json(PAPER/name,payload)
 os_asset={"schema_version":1,"asset_id":"c1-pacta-rb-qwen397-t05-t0-source-acquisition-20260901",
  "created_at_utc":now(),"decision":support["decision"],"belief_update":"No PACTA mechanism update; T0.5/T0 establish carrier substrate and trajectory provenance only.",
  "lessons":[
   "Runtime image absence is an acquisition-layer blocker, not evidence against a carrier or method. For SWE-bench-backed scientific units, mutable tags must be resolved and frozen to content-addressed platform manifests before execution.",
   "Transport retries for immutable image blobs are infrastructure recovery and are distinct from forbidden scientific sample retries.",
   "A stable content-addressed image digest is not sufficient substrate provenance when the image's /testbed HEAD differs from the frozen task base commit; both digest binding and task-state qualification are required.",
   "A planned native source ID is not a native source trajectory. A writer-ready experience requires persisted trajectory bytes, an exact rendering contract, and content-addressed provenance.",
   "ReasoningBank exposes native SUCCESSFUL_SI and FAILED_SI induction instructions over the same Query + Trajectory input. PACTA may use them as a controlled writer-branch intervention, but this must not be described as ReasoningBank's natural branch selection or as pure reward-bit causality."],
  "artifacts":{k:stamped(PAPER/k) for k in copies},
  "call_counts":{"writer":0,"binder":0,"shadow":0,"final":0,"future_task":0},
  "claim_authority":"NO_NEW_PACTA_EFFECT_EVIDENCE","active_manuscript":"R9",
  "reopen_conditions":["New human authorization after trajectory-backed pool closure for outcome-blind 6+5 selection and controlled writer-branch intervention."]}
 atomic_json(OS,os_asset)
 print(json.dumps({"decision":support["decision"],"research_os":str(OS),"artifacts":len(copies)},sort_keys=True))

if __name__=="__main__":main()
