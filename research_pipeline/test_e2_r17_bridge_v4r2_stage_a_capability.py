from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from research_pipeline.e2_r17_bridge_v4r2_stage_a_capability import (
    CONTROL_PLANE_REVISION,
    PRODUCTION_PUBLIC_KEY_PATH,
    PRODUCTION_PUBLIC_KEY_SHA256,
    SIGNATURE_CONTEXT,
    sha256_file,
    sign_document,
    verify_document,
)
from research_pipeline.e2_r17_bridge_v4r2_stage_a_runtime import consume_capability

ROOT = Path(__file__).resolve().parents[1]


def exact_authority() -> dict[str, bool]:
    return {
        "scientific_experiment": True,
        "provider_io": True,
        "search_pool_acquisition": True,
        "support_inspection": True,
        "free_updater": False,
        "deterministic_state_materialization": False,
        "actor_evaluation": False,
        "screen_outcome_opening": False,
        "validation_opening": False,
        "analysis": False,
        "paper_promotion": False,
    }


def payload() -> dict:
    return {
        "capability_id": "cap-test",
        "issued_at_utc": "2026-09-07T00:00:00+00:00",
        "control_plane_revision": CONTROL_PLANE_REVISION,
        "contract_sha256": "a" * 64,
        "preflight_sha256": "b" * 64,
        "review_receipt_sha256": "c" * 64,
        "structural_authorization_sha256": "d" * 64,
        "runner_sha256": "e" * 64,
        "runtime_sha256": "f" * 64,
        "support_sha256": "1" * 64,
        "identity_sha256": "2" * 64,
        "run_root": "/tmp/run",
        "lineage_lease_path": "/tmp/lease.json",
        "consumption_marker_path": "/tmp/consume.json",
        "single_use": True,
        "authority": exact_authority(),
    }


class BridgeV4R2StageACapabilityTests(unittest.TestCase):
    def test_production_public_key_is_hard_pinned(self) -> None:
        self.assertTrue(PRODUCTION_PUBLIC_KEY_PATH.is_file())
        self.assertEqual(sha256_file(PRODUCTION_PUBLIC_KEY_PATH), PRODUCTION_PUBLIC_KEY_SHA256)
        self.assertEqual(SIGNATURE_CONTEXT, "E2-R17-BRIDGE-V4R2-STAGE-A-EXECUTION-CAPABILITY-V1")

    def test_attacker_signed_field_complete_capability_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            private = root / "attacker-private.pem"
            public = root / "attacker-public.pem"
            subprocess.run(["/usr/bin/openssl", "genpkey", "-algorithm", "Ed25519", "-out", str(private)], check=True, capture_output=True)
            subprocess.run(["/usr/bin/openssl", "pkey", "-in", str(private), "-pubout", "-out", str(public)], check=True, capture_output=True)
            document = sign_document(payload=payload(), private_key_path=private, public_key_path=public)
            expected = {key: value for key, value in payload().items() if key not in {"capability_id", "issued_at_utc", "control_plane_revision", "single_use", "authority"}}
            with self.assertRaisesRegex(RuntimeError, "signature verification failed"):
                verify_document(document, expected_payload_fields=expected)

    def test_tampered_payload_is_rejected(self) -> None:
        # An attacker-signed document already fails at production signature verification;
        # mutating a signed field must not create an alternate accepted path.
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            private = root / "attacker-private.pem"
            public = root / "attacker-public.pem"
            subprocess.run(["/usr/bin/openssl", "genpkey", "-algorithm", "Ed25519", "-out", str(private)], check=True, capture_output=True)
            subprocess.run(["/usr/bin/openssl", "pkey", "-in", str(private), "-pubout", "-out", str(public)], check=True, capture_output=True)
            document = sign_document(payload=payload(), private_key_path=private, public_key_path=public)
            document["payload"]["run_root"] = "/tmp/attacker-run"
            with self.assertRaises(RuntimeError):
                verify_document(document, expected_payload_fields={"run_root": "/tmp/run"})

    def test_consumption_marker_is_atomic_and_single_use(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            marker = Path(td) / "consume.json"
            consume_capability(
                marker_path=marker,
                capability_sha256="a" * 64,
                capability_id="cap-test",
                contract_sha256="b" * 64,
                authorization_sha256="c" * 64,
            )
            row = json.loads(marker.read_text(encoding="utf-8"))
            self.assertTrue(row["consumed_before_provider_io"])
            self.assertEqual(row["capability_id"], "cap-test")
            with self.assertRaises(FileExistsError):
                consume_capability(
                    marker_path=marker,
                    capability_sha256="a" * 64,
                    capability_id="cap-test",
                    contract_sha256="b" * 64,
                    authorization_sha256="c" * 64,
                )

    def test_cli_requires_signed_capability(self) -> None:
        source = (ROOT / "scripts/run_e2_r17_bridge_v4r2_stage_a.py").read_text(encoding="utf-8")
        self.assertIn('parser.add_argument("--signed-capability", type=Path, required=True)', source)
        self.assertIn("signed_capability_path=args.signed_capability", source)

    def test_runtime_consumes_capability_before_run_root_creation(self) -> None:
        source = (ROOT / "research_pipeline/e2_r17_bridge_v4r2_stage_a_runtime.py").read_text(encoding="utf-8")
        consume = source.index("consume_capability(marker_path=markerp")
        make_root = source.index("rr.mkdir(parents=True)")
        self.assertLess(consume, make_root)
        self.assertIn("os.O_CREAT|os.O_EXCL|os.O_WRONLY", source)


if __name__ == "__main__":
    unittest.main()
