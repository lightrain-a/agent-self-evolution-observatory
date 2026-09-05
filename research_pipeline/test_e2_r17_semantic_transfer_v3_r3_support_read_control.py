from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from .e2_r17_r3c_signed_support_capability import HARD_PROVIDER_NOT_BEFORE, OPENSSL, sign_document

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import authorize_e2_r17_semantic_transfer_v3_stage_a_r3_support_read as minter
import run_e2_r17_semantic_transfer_v3_stage_a_r3_support_adjudication_gate as gate


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


class R3PostTerminalSupportReadControlTests(unittest.TestCase):
    def make_fixture(self) -> dict[str, Path]:
        td = tempfile.TemporaryDirectory()
        self.addCleanup(td.cleanup)
        root = Path(td.name)
        run = root / "run"
        private_key_path = root / "test-signing-private.pem"
        public_key_path = root / "test-signing-public.pem"
        subprocess.run([OPENSSL, "genpkey", "-algorithm", "ED25519", "-out", str(private_key_path)], check=True, capture_output=True)
        with public_key_path.open("wb") as handle:
            subprocess.run([OPENSSL, "pkey", "-in", str(private_key_path), "-pubout"], check=True, stdout=handle, stderr=subprocess.PIPE)
        claims = run / "checkpoints/stage_a_task_claims"
        claims.mkdir(parents=True)
        completed = run / "checkpoints/completed_streams.jsonl"
        completed.parent.mkdir(parents=True, exist_ok=True)
        completed.write_text("{}\n", encoding="utf-8")

        streams: dict[str, list[str]] = {}
        task_ids: list[str] = []
        for idx in range(20):
            sid = "stv3-cgwb-00" if idx == 0 else "stv3-cgwp-00" if idx == 1 else f"stv3-test-{idx:02d}"
            count = 7 if idx < 2 else 8
            rows = [f"test-{idx:02d}-{j:02d}" for j in range(count)]
            streams[sid] = rows
            task_ids.extend(rows)
        self.assertEqual(len(task_ids), 158)

        manifest = root / "execution-units.json"
        write_json(manifest, {"ordered_task_ids": task_ids})
        opportunity = root / "opportunity.json"
        write_json(opportunity, {"provider_task_ids_by_stream": streams})

        lease = root / "r3-lease.json"
        contract = root / "contract.json"
        contract_payload = {
            "schema_version": "1.0",
            "status": minter.CONTRACT_STATUS,
            "control_plane_revision": minter.CONTROL_PLANE_REVISION,
            "run_root": str(run),
            "global_lease_path": str(lease),
            "exact_once_acquisition": {
                "unit_manifest_path": str(manifest),
                "unit_manifest_sha256": sha(manifest),
                "claim_root": str(claims),
            },
            "recovery_opportunity_manifest": {"path": str(opportunity), "sha256": sha(opportunity)},
            "bound_code": {
                "post_terminal_support_minter": {"path": str(Path(minter.__file__)), "sha256": sha(Path(minter.__file__))},
                "post_terminal_support_gate": {"path": str(Path(gate.__file__)), "sha256": sha(Path(gate.__file__))},
                "equal_dose_adjudicator": {"path": str(minter.EXPECTED_SUPPORT_ADJUDICATOR), "sha256": sha(minter.EXPECTED_SUPPORT_ADJUDICATOR)},
            },
            "post_terminal_support_read_control": {
                "trusted_external_signer": {
                    "algorithm": "Ed25519",
                    "public_key_path": str(public_key_path),
                    "public_key_sha256": sha(public_key_path),
                    "private_key_in_repository": False,
                    "signed_capability_required": True,
                }
            },
        }
        write_json(contract, contract_payload)
        csha = sha(contract)

        recovery_auth = root / "recovery-auth.json"
        recovery_auth_payload = {
            "schema_version": "1.0",
            "status": minter.RECOVERY_AUTH_STATUS,
            "contract_sha256": csha,
            "single_use": True,
            "exactly_once": True,
            "authority": {
                "stage_a_provider_execution": True,
                "stage_b_learning_execution": False,
                "updater": False,
                "heldout_evaluation": False,
                "analyzer": False,
                "second_backbone": False,
                "public_benchmark": False,
                "paper_promotion": False,
                "submission": False,
            },
        }
        write_json(recovery_auth, recovery_auth_payload)
        asha = sha(recovery_auth)

        for task in task_ids:
            task_dir = run / "cases" / task
            task_dir.mkdir(parents=True)
            pool = task_dir / "pool_k8.json"
            pool.write_text("{}\n", encoding="utf-8")
            attempt, sealed = minter.task_claim_paths(claims, task)
            write_json(
                attempt,
                {
                    "artifact_type": "e2-r17-semantic-transfer-v3-stage-a-task-attempt",
                    "status": "ATTEMPTED_IN_FLIGHT_DO_NOT_REPLAY",
                    "task_id": task,
                    "contract_sha256": csha,
                    "authorization_sha256": asha,
                },
            )
            write_json(
                sealed,
                {
                    "artifact_type": "e2-r17-semantic-transfer-v3-stage-a-task-seal",
                    "status": "SEALED_EXACT_ONCE",
                    "task_id": task,
                    "contract_sha256": csha,
                    "authorization_sha256": asha,
                    "attempt_sha256": sha(attempt),
                    "pool_k8_sha256": sha(pool),
                },
            )

        summary = run / "summary/stage_a_r3_recovery_pool_freeze_summary.json"
        summary_payload = {
            "schema_version": "1.0",
            "status": minter.SUMMARY_STATUS,
            "contract_sha256": csha,
            "authorization_sha256": asha,
            "planned_tasks": 160,
            "provider_executable_tasks": 158,
            "sealed_k8_pools": 158,
            "terminal_technical_missing": 1,
            "matched_no_provider_censor": 1,
            "actor_rollouts": 1264,
            "support_inspected": False,
            "updater_calls": 0,
            "heldout_evaluations": 0,
            "partial_effect_read": False,
            "scientific_scores_read": False,
            "stage_b_authority": False,
            "completed_stream_manifest_path": str(completed),
            "completed_stream_manifest_sha256": sha(completed),
        }
        write_json(summary, summary_payload)
        ssha = sha(summary)
        write_json(
            lease,
            {
                "schema_version": "1.0",
                "status": minter.LEASE_STATUS,
                "contract_sha256": csha,
                "authorization_sha256": asha,
                "summary_path": str(summary),
                "summary_sha256": ssha,
            },
        )

        control_review = root / "control-review.json"
        write_json(
            control_review,
            {
                "schema_version": "1.0",
                "status": "COMPLETED",
                "surface": "ChatGPT web",
                "model": "GPT-5.6 Sol",
                "verdict": minter.CONTROL_REVIEW_VERDICT,
                "control_plane_revision": minter.CONTROL_PLANE_REVISION,
                "minter_sha256_acknowledged": sha(Path(minter.__file__)),
                "gate_sha256_acknowledged": sha(Path(gate.__file__)),
                "support_adjudicator_sha256_acknowledged": sha(minter.EXPECTED_SUPPORT_ADJUDICATOR),
                "stage_b_authority": False,
                "scientific_authority": False,
            },
        )
        return {
            "root": root,
            "run": run,
            "contract": contract,
            "recovery_auth": recovery_auth,
            "summary": summary,
            "lease": lease,
            "control_review": control_review,
            "support_auth": root / "support-auth.json",
            "signed_capability": root / "signed-capability.json",
            "private_key": private_key_path,
            "public_key": public_key_path,
            "adjudication_output": root / "support-adjudication.json",
        }

    def build_auth(self, fixture: dict[str, Path]) -> dict:
        payload = minter.build_support_authorization(
            contract_path=fixture["contract"],
            recovery_authorization_path=fixture["recovery_auth"],
            summary_path=fixture["summary"],
            control_review_path=fixture["control_review"],
            output_path=fixture["support_auth"],
            adjudication_output_path=fixture["adjudication_output"],
            created_at_utc="2026-09-07T00:01:00+08:00",
        )
        write_json(fixture["support_auth"], payload)
        return payload

    def build_signed_capability(self, fixture: dict[str, Path]) -> dict:
        support_auth = json.loads(fixture["support_auth"].read_text())
        control = support_auth["bound_control_plane"]
        scope = support_auth["execution_scope"]
        payload = {
            "capability_id": "test-capability-r3c",
            "issued_at_utc": "2026-09-07T00:01:00+08:00",
            "control_plane_revision": minter.CONTROL_PLANE_REVISION,
            "hard_provider_not_before": HARD_PROVIDER_NOT_BEFORE,
            "contract_sha256": sha(fixture["contract"]),
            "recovery_authorization_sha256": sha(fixture["recovery_auth"]),
            "terminal_summary_sha256": sha(fixture["summary"]),
            "support_authorization_sha256": sha(fixture["support_auth"]),
            "control_review_sha256": sha(fixture["control_review"]),
            "minter_sha256": control["minter_sha256"],
            "gate_sha256": control["gate_sha256"],
            "support_adjudicator_sha256": control["support_adjudicator_sha256"],
            "required_adjudication_output": str(fixture["adjudication_output"].resolve()),
            "required_run_root": str(Path(scope["required_run_root"]).resolve()),
            "single_use": True,
            "stage_a_support_read": True,
            "stage_a_provider_execution": False,
            "stage_b_learning_execution": False,
            "updater": False,
            "heldout_evaluation": False,
            "analyzer": False,
            "second_backbone": False,
            "public_benchmark": False,
            "paper_promotion": False,
            "submission": False,
            "scientific_authority": False,
        }
        document = sign_document(payload=payload, private_key_path=fixture["private_key"], public_key_path=fixture["public_key"])
        write_json(fixture["signed_capability"], document)
        return document

    def test_minter_rejects_absent_or_nonterminal_summary(self) -> None:
        fixture = self.make_fixture()
        missing = fixture["root"] / "missing-summary.json"
        with self.assertRaises(FileNotFoundError):
            minter.build_support_authorization(
                contract_path=fixture["contract"],
                recovery_authorization_path=fixture["recovery_auth"],
                summary_path=missing,
                control_review_path=fixture["control_review"],
                output_path=fixture["support_auth"],
                adjudication_output_path=fixture["adjudication_output"],
            )
        summary = json.loads(fixture["summary"].read_text())
        summary["status"] = "RUNNING"
        write_json(fixture["summary"], summary)
        with self.assertRaisesRegex(RuntimeError, "terminal summary status drift"):
            self.build_auth(fixture)

    def test_minter_rejects_support_already_inspected(self) -> None:
        fixture = self.make_fixture()
        summary = json.loads(fixture["summary"].read_text())
        summary["support_inspected"] = True
        write_json(fixture["summary"], summary)
        with self.assertRaisesRegex(RuntimeError, "already inspected support"):
            self.build_auth(fixture)

    def test_minter_rejects_recovery_authorization_hash_drift(self) -> None:
        fixture = self.make_fixture()
        auth = json.loads(fixture["recovery_auth"].read_text())
        auth["tampered"] = True
        write_json(fixture["recovery_auth"], auth)
        with self.assertRaisesRegex(RuntimeError, "summary authorization SHA drift"):
            self.build_auth(fixture)

    def test_minter_grants_only_stage_a_support_read(self) -> None:
        fixture = self.make_fixture()
        payload = self.build_auth(fixture)
        self.assertTrue(payload["authority"]["stage_a_support_read"])
        self.assertFalse(payload["authority"]["stage_a_provider_execution"])
        self.assertFalse(payload["authority"]["stage_b_learning_execution"])
        self.assertFalse(payload["authority"]["heldout_evaluation"])
        self.assertEqual(payload["provider_calls"], 0)
        self.assertFalse(payload["scientific_execution"])

    def test_gate_refuses_invalid_support_authorization(self) -> None:
        fixture = self.make_fixture()
        payload = self.build_auth(fixture)
        payload["authority"]["stage_a_support_read"] = False
        write_json(fixture["support_auth"], payload)
        with self.assertRaisesRegex(RuntimeError, "support-read authority absent"):
            gate.run_gate(
                support_authorization_path=fixture["support_auth"],
                contract_path=fixture["contract"],
                recovery_authorization_path=fixture["recovery_auth"],
                summary_path=fixture["summary"],
                signed_capability_path=fixture["signed_capability"],
                output_path=fixture["adjudication_output"],
            )
        consumption = fixture["run"] / "checkpoints/post_terminal_support_read" / gate.CONSUMPTION_NAME
        self.assertFalse(consumption.exists())

    def test_gate_rejects_forged_permit_without_review_provenance(self) -> None:
        fixture = self.make_fixture()
        payload = self.build_auth(fixture)
        forged_review = fixture["root"] / "forged-review.json"
        write_json(forged_review, {"status": "COMPLETED", "surface": "ChatGPT web", "model": "GPT-5.6 Sol", "verdict": minter.CONTROL_REVIEW_VERDICT})
        payload["control_review"]["path"] = str(forged_review)
        payload["control_review"]["sha256"] = sha(forged_review)
        write_json(fixture["support_auth"], payload)
        with self.assertRaisesRegex(RuntimeError, "review/minter SHA drift|control-review revision drift|control-review receipt binding drift"):
            gate.run_gate(
                support_authorization_path=fixture["support_auth"],
                contract_path=fixture["contract"],
                recovery_authorization_path=fixture["recovery_auth"],
                summary_path=fixture["summary"],
                signed_capability_path=fixture["signed_capability"],
                output_path=fixture["adjudication_output"],
            )

    def test_guarded_adjudicator_rejects_direct_invocation_without_support_permit(self) -> None:
        fixture = self.make_fixture()
        command = [
            sys.executable,
            str(minter.EXPECTED_SUPPORT_ADJUDICATOR),
            "--contract",
            str(fixture["contract"]),
            "--authorization",
            str(fixture["recovery_auth"]),
            "--summary",
            str(fixture["summary"]),
            "--output",
            str(fixture["adjudication_output"]),
        ]
        result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("--support-authorization", result.stderr)
        self.assertFalse(fixture["adjudication_output"].exists())

    def test_full_forged_review_permit_and_capability_cannot_directly_invoke_adjudicator(self) -> None:
        fixture = self.make_fixture()
        support_auth = self.build_auth(fixture)

        # Construct the verdict-changing adversarial path from the R3B reviewer:
        # a field-complete forged review plus a field-complete forged permit.
        genuine_review = json.loads(fixture["control_review"].read_text())
        forged_review = fixture["root"] / "field-complete-forged-review.json"
        write_json(forged_review, genuine_review)
        support_auth["control_review"]["path"] = str(forged_review.resolve())
        support_auth["control_review"]["sha256"] = sha(forged_review)
        write_json(fixture["support_auth"], support_auth)

        control = support_auth["bound_control_plane"]
        scope = support_auth["execution_scope"]
        payload = {
            "capability_id": "attacker-fabricated-capability",
            "issued_at_utc": "2026-09-07T00:01:00+08:00",
            "control_plane_revision": minter.CONTROL_PLANE_REVISION,
            "hard_provider_not_before": HARD_PROVIDER_NOT_BEFORE,
            "contract_sha256": sha(fixture["contract"]),
            "recovery_authorization_sha256": sha(fixture["recovery_auth"]),
            "terminal_summary_sha256": sha(fixture["summary"]),
            "support_authorization_sha256": sha(fixture["support_auth"]),
            "control_review_sha256": sha(forged_review),
            "minter_sha256": control["minter_sha256"],
            "gate_sha256": control["gate_sha256"],
            "support_adjudicator_sha256": control["support_adjudicator_sha256"],
            "required_adjudication_output": str(fixture["adjudication_output"].resolve()),
            "required_run_root": str(Path(scope["required_run_root"]).resolve()),
            "single_use": True,
            "stage_a_support_read": True,
            "stage_a_provider_execution": False,
            "stage_b_learning_execution": False,
            "updater": False,
            "heldout_evaluation": False,
            "analyzer": False,
            "second_backbone": False,
            "public_benchmark": False,
            "paper_promotion": False,
            "submission": False,
            "scientific_authority": False,
        }
        wrong_private_path = fixture["root"] / "attacker-private.pem"
        wrong_public_path = fixture["root"] / "attacker-public.pem"
        subprocess.run([OPENSSL, "genpkey", "-algorithm", "ED25519", "-out", str(wrong_private_path)], check=True, capture_output=True)
        with wrong_public_path.open("wb") as handle:
            subprocess.run([OPENSSL, "pkey", "-in", str(wrong_private_path), "-pubout"], check=True, stdout=handle, stderr=subprocess.PIPE)
        forged_capability = sign_document(payload=payload, private_key_path=wrong_private_path, public_key_path=wrong_public_path)
        # The attacker can copy every public metadata field, including the trusted
        # public-key fingerprint, but cannot create a signature verifiable by it.
        forged_capability["signature"]["public_key_sha256"] = sha(fixture["public_key"])
        write_json(fixture["signed_capability"], forged_capability)

        command = [
            sys.executable,
            str(minter.EXPECTED_SUPPORT_ADJUDICATOR),
            "--contract", str(fixture["contract"]),
            "--authorization", str(fixture["recovery_auth"]),
            "--summary", str(fixture["summary"]),
            "--support-authorization", str(fixture["support_auth"]),
            "--signed-capability", str(fixture["signed_capability"]),
            "--output", str(fixture["adjudication_output"]),
        ]
        result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("signature verification failed", result.stderr)
        self.assertFalse(fixture["adjudication_output"].exists())
        consumption = fixture["run"] / "checkpoints/post_terminal_support_read" / gate.CONSUMPTION_NAME
        self.assertFalse(consumption.exists())

    def test_gate_consumes_once_and_fail_closes_on_unexpected_adjudicator_error(self) -> None:
        fixture = self.make_fixture()
        self.build_auth(fixture)
        self.build_signed_capability(fixture)

        def failed_invoke(command: list[str]) -> subprocess.CompletedProcess[str]:
            self.assertIn("--signed-capability", command)
            control = fixture["run"] / "checkpoints/post_terminal_support_read"
            write_json(
                control / gate.CONSUMPTION_NAME,
                {
                    "artifact_type": "e2-r17-v3-stage-a-r3c-signed-support-capability-consumption",
                    "status": "CONSUMED_IN_FLIGHT_DO_NOT_RETRY",
                    "signed_capability_sha256": sha(fixture["signed_capability"]),
                    "trusted_public_key_sha256": sha(fixture["public_key"]),
                    "stage_b_authority": False,
                    "scientific_authority": False,
                },
            )
            return subprocess.CompletedProcess(command, 2, stdout="", stderr="synthetic failure")

        with self.assertRaisesRegex(RuntimeError, "signed support capability remains consumed"):
            gate.run_gate(
                support_authorization_path=fixture["support_auth"],
                contract_path=fixture["contract"],
                recovery_authorization_path=fixture["recovery_auth"],
                summary_path=fixture["summary"],
                signed_capability_path=fixture["signed_capability"],
                output_path=fixture["adjudication_output"],
                invoke=failed_invoke,
            )
        control = fixture["run"] / "checkpoints/post_terminal_support_read"
        self.assertTrue((control / gate.CONSUMPTION_NAME).is_file())
        self.assertFalse((control / gate.COMPLETION_NAME).exists())
        with self.assertRaisesRegex(RuntimeError, "already consumed"):
            gate.run_gate(
                support_authorization_path=fixture["support_auth"],
                contract_path=fixture["contract"],
                recovery_authorization_path=fixture["recovery_auth"],
                summary_path=fixture["summary"],
                signed_capability_path=fixture["signed_capability"],
                output_path=fixture["adjudication_output"],
                invoke=failed_invoke,
            )

    def test_gate_accepts_terminal_pass_without_stage_b_authority(self) -> None:
        fixture = self.make_fixture()
        self.build_auth(fixture)
        self.build_signed_capability(fixture)

        def passed_invoke(command: list[str]) -> subprocess.CompletedProcess[str]:
            self.assertIn("--support-authorization", command)
            self.assertIn("--signed-capability", command)
            control = fixture["run"] / "checkpoints/post_terminal_support_read"
            write_json(
                control / gate.CONSUMPTION_NAME,
                {
                    "artifact_type": "e2-r17-v3-stage-a-r3c-signed-support-capability-consumption",
                    "status": "CONSUMED_IN_FLIGHT_DO_NOT_RETRY",
                    "signed_capability_sha256": sha(fixture["signed_capability"]),
                    "trusted_public_key_sha256": sha(fixture["public_key"]),
                    "stage_b_authority": False,
                    "scientific_authority": False,
                },
            )
            output = Path(command[command.index("--output") + 1])
            write_json(
                output,
                {
                    "status": "PASS_SEMANTIC_TRANSFER_V3_R3_MATCHED_CENSOR_EQUAL_DOSE_SUPPORT_READY_FOR_STAGE_B_DESIGN",
                    "authority": {
                        "prepare_stage_b_contract": True,
                        "execute_stage_b": False,
                        "heldout_evaluation": False,
                        "analyzer": False,
                        "paper_promotion": False,
                    },
                },
            )
            return subprocess.CompletedProcess(command, 0, stdout="synthetic pass", stderr="")

        result = gate.run_gate(
            support_authorization_path=fixture["support_auth"],
            contract_path=fixture["contract"],
            recovery_authorization_path=fixture["recovery_auth"],
            summary_path=fixture["summary"],
            signed_capability_path=fixture["signed_capability"],
            output_path=fixture["adjudication_output"],
            invoke=passed_invoke,
        )
        self.assertEqual(result["status"], "COMPLETED_POST_TERMINAL_SUPPORT_READ")
        self.assertFalse(result["stage_b_authority"])
        completion = fixture["run"] / "checkpoints/post_terminal_support_read" / gate.COMPLETION_NAME
        self.assertTrue(completion.is_file())
        self.assertFalse(json.loads(completion.read_text())["stage_b_authority"])


if __name__ == "__main__":
    unittest.main()
