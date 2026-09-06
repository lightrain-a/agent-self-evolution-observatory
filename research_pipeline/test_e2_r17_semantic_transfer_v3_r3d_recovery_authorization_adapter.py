from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import authorize_e2_r17_semantic_transfer_v3_stage_a_r3d_recovery as adapter
from research_pipeline.e2_r17_r3d_runtime_replay_attestation import OPENSSL, sign_document

CONTRACT = ROOT / "generated/e2-r17-semantic-transfer-v3-stage-a-contract-r3d-pinned-support-capability-20260906.json"
PREFLIGHT = ROOT / "generated/e2-r17-semantic-transfer-v3-stage-a-preflight-r3d-pinned-support-capability-20260906.json"
R3D_REVIEW = ROOT / "generated/e2-r17-v3-r3d-pinned-trust-root-gpt56-review-20260906.json"

def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")

class R3DRecoveryAuthorizationAdapterTests(unittest.TestCase):
    def fixture(self) -> dict[str, Path]:
        td = tempfile.TemporaryDirectory(prefix="e2-r17-r3d-auth-adapter-")
        self.addCleanup(td.cleanup)
        root = Path(td.name)
        private_key = root / "trusted-private.pem"
        public_key = root / "trusted-public.pem"
        subprocess.run([OPENSSL, "genpkey", "-algorithm", "ED25519", "-out", str(private_key)], check=True, capture_output=True)
        subprocess.run([OPENSSL, "pkey", "-in", str(private_key), "-pubout", "-out", str(public_key)], check=True, capture_output=True)
        r3d_review = root / "r3d-review.json"
        shutil.copyfile(R3D_REVIEW, r3d_review)
        identity = root / "fresh-identity.json"
        write_json(identity,{"schema_version":"1.0","status":"PASS_CURRENT_REVIEW_TRANCHE","created_at_utc":"2026-09-07T00:01:00+08:00","requested_and_resolved":{"deepseek-v4-pro":{"resolved":"deepseek-v4-pro-ga-260813","thinking":"disabled","provider_retry_limit":0}}})
        review = root / "adapter-review.json"
        write_json(review,{"schema_version":"1.0","status":"COMPLETED","surface":"ChatGPT web","model":"GPT-5.6 Sol","verdict":adapter.ADAPTER_REVIEW_VERDICT,"adapter_sha256_acknowledged":sha(Path(adapter.__file__)),"contract_sha256_acknowledged":sha(CONTRACT),"preflight_sha256_acknowledged":sha(PREFLIGHT),"r3d_review_sha256_acknowledged":sha(r3d_review),"runtime_replay_attestation_verifier_sha256_acknowledged":sha(adapter.RUNTIME_REPLAY_ATTESTATION_VERIFIER_PATH),"runtime_replay_public_key_sha256_acknowledged":sha(public_key),"provider_authority_only":True,"stage_b_authority":False,"scientific_authority":False,"remaining_blockers":[]})
        contract=json.loads(CONTRACT.read_text())
        runtime_replay=root/"runtime-replay-attestation.json"
        runtime_payload={"schema_version":"1.0","status":adapter.RUNTIME_REPLAY_STATUS,"execution_host_role":"HOST69_FROZEN_RUNTIME","execution_host_origin":"HOST69_LOCAL_ED25519_PRIVATE_KEY","hostname":adapter.EXPECTED_RUNTIME_REPLAY_HOSTNAME,"execution_host_ipv4":adapter.EXPECTED_RUNTIME_REPLAY_IPV4,"python_executable":contract["runtime"]["python_executable"],"python_freeze_sha256":contract["runtime"]["freeze_sha256"],"contract_sha256":sha(CONTRACT),"preflight_sha256":sha(PREFLIGHT),"r3d_review_sha256":sha(r3d_review),"adapter_sha256":sha(Path(adapter.__file__)),"adapter_tests_sha256":sha(Path(__file__)),"provider_runner_sha256":sha(adapter.PROVIDER_RUNNER_PATH),"runtime_replay_tool_sha256":sha(adapter.RUNTIME_REPLAY_TOOL_PATH),"host69_public_key_sha256":sha(public_key),"compile_pass":True,"unit_tests_pass":True,"unit_tests_failed":0,"provider_calls":0,"scientific_execution":False,"support_inspected":False,"stage_b_authority":False}
        write_json(runtime_replay,sign_document(payload=runtime_payload,private_key_path=private_key,public_key_path=public_key))
        return {"root":root,"private_key":private_key,"public_key":public_key,"r3d_review":r3d_review,"identity":identity,"adapter_review":review,"runtime_replay":runtime_replay,"output":root/"authorization.json"}
    def call(self,fixture:dict[str,Path],*,now:str="2026-09-07T00:02:00+08:00")->dict:
        with patch.object(adapter,"PRODUCTION_RUNTIME_REPLAY_PUBLIC_KEY_PATH",fixture["public_key"]),patch.object(adapter,"PRODUCTION_RUNTIME_REPLAY_PUBLIC_KEY_SHA256",sha(fixture["public_key"])):
            return adapter.build_authorization(contract_path=CONTRACT,preflight_path=PREFLIGHT,r3d_review_path=fixture["r3d_review"],adapter_review_path=fixture["adapter_review"],runtime_replay_path=fixture["runtime_replay"],fresh_identity_path=fixture["identity"],output_path=fixture["output"],now=datetime.fromisoformat(now))
    def resign_runtime_replay(self,fixture:dict[str,Path],payload:dict,*,private_key:Path|None=None,public_key:Path|None=None)->None:
        write_json(fixture["runtime_replay"],sign_document(payload=payload,private_key_path=private_key or fixture["private_key"],public_key_path=public_key or fixture["public_key"]))
    def test_pre_reset_is_rejected(self):
        f=self.fixture()
        with self.assertRaisesRegex(RuntimeError,"hard provider reset boundary not reached"): self.call(f,now="2026-09-06T23:59:59+08:00")
    def test_adapter_review_must_bind_exact_adapter_sha(self):
        f=self.fixture(); r=json.loads(f["adapter_review"].read_text()); r["adapter_sha256_acknowledged"]="0"*64; write_json(f["adapter_review"],r)
        with self.assertRaisesRegex(RuntimeError,"adapter review code SHA drift"): self.call(f)
    def test_r3d_review_exact_sha_is_pinned_even_if_adapter_review_agrees(self):
        f=self.fixture(); r=json.loads(f["r3d_review"].read_text()); r["attacker_extra_field"]="self-consistent-but-not-frozen"; write_json(f["r3d_review"],r); ar=json.loads(f["adapter_review"].read_text()); ar["r3d_review_sha256_acknowledged"]=sha(f["r3d_review"]); write_json(f["adapter_review"],ar); rr=json.loads(f["runtime_replay"].read_text())["payload"]; rr["r3d_review_sha256"]=sha(f["r3d_review"]); self.resign_runtime_replay(f,rr)
        with self.assertRaisesRegex(RuntimeError,"accepted review receipt SHA drift"): self.call(f)
    def test_runtime_replay_must_bind_exact_adapter_and_runner_state(self):
        f=self.fixture(); rr=json.loads(f["runtime_replay"].read_text())["payload"]; rr["provider_runner_sha256"]="0"*64; self.resign_runtime_replay(f,rr)
        with self.assertRaisesRegex(RuntimeError,"attestation binding drift: provider_runner_sha256"): self.call(f)
    def test_field_complete_runtime_replay_signed_by_attacker_key_is_rejected(self):
        f=self.fixture(); ap=f["root"]/"attacker-private.pem"; au=f["root"]/"attacker-public.pem"; subprocess.run([OPENSSL,"genpkey","-algorithm","ED25519","-out",str(ap)],check=True,capture_output=True); subprocess.run([OPENSSL,"pkey","-in",str(ap),"-pubout","-out",str(au)],check=True,capture_output=True); rr=json.loads(f["runtime_replay"].read_text())["payload"]; self.resign_runtime_replay(f,rr,private_key=ap,public_key=au)
        with self.assertRaisesRegex(RuntimeError,"signature public-key fingerprint drift|signature verification failed"): self.call(f)
    def test_runtime_replay_host69_origin_fields_are_bound(self):
        f=self.fixture(); rr=json.loads(f["runtime_replay"].read_text())["payload"]; rr["execution_host_ipv4"]="222.20.126.68"; self.resign_runtime_replay(f,rr)
        with self.assertRaisesRegex(RuntimeError,"attestation binding drift: execution_host_ipv4"): self.call(f)
    def test_fresh_identity_must_match_frozen_model_policy(self):
        f=self.fixture(); i=json.loads(f["identity"].read_text()); i["requested_and_resolved"]["deepseek-v4-pro"]["resolved"]="wrong-model"; write_json(f["identity"],i)
        with self.assertRaisesRegex(RuntimeError,"resolved model drift"): self.call(f)
    def test_valid_post_reset_adapter_mints_runner_compatible_narrow_authority(self):
        f=self.fixture(); p=self.call(f); self.assertEqual(p["status"],adapter.AUTH_STATUS); self.assertEqual(p["contract_sha256"],adapter.EXPECTED_CONTRACT_SHA256); self.assertTrue(p["authority"]["stage_a_provider_execution"])
        for k in ("stage_b_learning_execution","updater","heldout_evaluation","analyzer","second_backbone","public_benchmark","paper_promotion","submission"): self.assertFalse(p["authority"][k])
        s=p["execution_scope"]; self.assertEqual(s["recovery_mode"],"MATCHED_CENSOR_158"); self.assertEqual(len(s["allowed_task_ids"]),158); self.assertEqual(len(set(s["allowed_task_ids"])),158); self.assertNotIn(adapter.BURNED,s["allowed_task_ids"]); self.assertNotIn(adapter.CENSOR,s["allowed_task_ids"]); self.assertFalse(s["recovery_exceptions"]["replacement_allowed"]); self.assertEqual(s["recovery_exceptions"]["additional_attempted_but_unsealed_policy"],"STOP"); self.assertFalse(p["automatic_retry"])

if __name__=="__main__": unittest.main()
