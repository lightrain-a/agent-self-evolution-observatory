from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from research_pipeline.agent_safety_g1_qwen397_model_binding import BindingError, run_binding

ROOT = Path(__file__).resolve().parents[1]
PREREG = ROOT / "generated" / "agent-safety-g1-qwen397-capability-requalification-prereg-20260902.json"
MODEL = "qwen3.5-397b-a17b"


class FakeResponse:
    def __init__(self, payload: dict, status: int = 200):
        self._raw = json.dumps(payload).encode()
        self.status = status
        self.headers = {"Content-Type": "application/json", "X-Request-Id": "test-request"}

    def read(self) -> bytes:
        return self._raw

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


class FakeOpener:
    def __init__(self, *, catalog_has_model: bool = True, returned_model: str = MODEL):
        self.catalog_has_model = catalog_has_model
        self.returned_model = returned_model
        self.calls = []

    def __call__(self, request, timeout=0):
        self.calls.append((request.full_url, request.method))
        if request.full_url.endswith("/models"):
            ids = [MODEL] if self.catalog_has_model else ["qwen3.5-122b-a10b"]
            return FakeResponse({"object": "list", "data": [{"id": x} for x in ids]})
        if request.full_url.endswith("/chat/completions"):
            return FakeResponse({"id": "x", "model": self.returned_model, "system_fingerprint": "fp-test", "choices": []})
        raise AssertionError(request.full_url)


class ModelBindingTest(unittest.TestCase):
    def test_pass_persists_raw_before_safe_receipt(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            opener = FakeOpener()
            out = Path(td)
            receipt = run_binding(prereg_path=PREREG, output_dir=out, api_key="test-secret", opener=opener)
            self.assertEqual(receipt["status"], "MODEL_BINDING_PASS")
            self.assertEqual(receipt["returned_model"], MODEL)
            self.assertTrue((out / "provider-models-response.raw.json").is_file())
            self.assertTrue((out / "provider-binding-response.raw.json").is_file())
            saved = (out / "model-binding-receipt.json").read_text()
            self.assertNotIn("test-secret", saved)
            self.assertEqual(len(opener.calls), 2)

    def test_catalog_absence_stops_without_chat(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            opener = FakeOpener(catalog_has_model=False)
            receipt = run_binding(prereg_path=PREREG, output_dir=Path(td), api_key="test-secret", opener=opener)
            self.assertEqual(receipt["status"], "STOP_MODEL_BINDING")
            self.assertFalse(receipt["binding_request_executed"])
            self.assertEqual(len(opener.calls), 1)

    def test_returned_model_mismatch_stops(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            opener = FakeOpener(returned_model="qwen3.5-122b-a10b")
            receipt = run_binding(prereg_path=PREREG, output_dir=Path(td), api_key="test-secret", opener=opener)
            self.assertEqual(receipt["status"], "STOP_MODEL_BINDING")
            self.assertEqual(len(opener.calls), 2)

    def test_existing_attempt_is_never_overwritten(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            out = Path(td)
            (out / "provider-models-response.raw.json").write_text("already")
            with self.assertRaises(BindingError):
                run_binding(prereg_path=PREREG, output_dir=out, api_key="test-secret", opener=FakeOpener())

    def test_missing_key_fails_before_provider(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            opener = FakeOpener()
            with self.assertRaises(BindingError):
                run_binding(prereg_path=PREREG, output_dir=Path(td), api_key="", opener=opener)
            self.assertEqual(opener.calls, [])


if __name__ == "__main__":
    unittest.main()
