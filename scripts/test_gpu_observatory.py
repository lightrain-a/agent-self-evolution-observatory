#!/usr/bin/env python3
"""Dependency-free unit and localhost integration checks for GPU telemetry."""
import hashlib
import hmac
from http.server import ThreadingHTTPServer
import io
import json
from pathlib import Path
import subprocess
import sys
import threading
import time
from unittest import TestCase, main
from unittest.mock import patch
from urllib import request, error

sys.path.insert(0, str(Path(__file__).resolve().parent))
from gpu_observatory import Storage, make_handler, probe, safe_gpu

SAMPLE_GPU = {
    "index": 0,
    "model": "NVIDIA Test GPU",
    "util": 54.0,
    "used_mib": 8192.0,
    "total_mib": 24576.0,
    "temp_c": 51.0,
    "power_w": 150.0,
    "power_limit_w": 350.0,
}


class ProbeTests(TestCase):
    def test_parse_probe(self):
        fake = subprocess.CompletedProcess(
            [], 0,
            "0, NVIDIA RTX Test, 84, 20011, 24576, 63, 210, 350\n"
            "1, NVIDIA RTX Test, 1, 14, 24576, 36, 45, 350\n", "")
        with patch("gpu_observatory.subprocess.run", return_value=fake):
            result = probe()
        self.assertEqual([x["index"] for x in result], [0, 1])
        self.assertEqual(result[0]["used_mib"], 20011.0)
        self.assertEqual(result[1]["util"], 1.0)

    def test_reject_malicious_field(self):
        with self.assertRaises(ValueError):
            safe_gpu({**SAMPLE_GPU, "util": -1})

    def test_offline_marking(self):
        storage = Storage()
        self.assertFalse(storage.snapshot()["hosts"][0]["online"])
        storage.accept("69", {"sampled_at": time.time(), "gpus": [SAMPLE_GPU]})
        self.assertTrue(storage.snapshot()["hosts"][0]["online"])
        with storage.lock:
            storage.latest["69"]["sampled_at"] -= 100
        self.assertFalse(storage.snapshot()["hosts"][0]["online"])


class HttpTests(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.secret = "test-secret-" * 4
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(
            {host: cls.secret for host in ("69", "42", "52")}, Storage()))
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.url = "http://127.0.0.1:" + str(cls.server.server_port)

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=2)

    def test_authenticated_ingest_and_public_snapshot(self):
        now = str(int(time.time()))
        body = json.dumps({"host": "42", "sampled_at": time.time(),
                           "gpus": [SAMPLE_GPU]}).encode()
        bad = request.Request(self.url + "/api/v1/ingest/42", data=body,
                              headers={"X-Monitor-Timestamp": now,
                                       "X-Monitor-Signature": "bad"})
        with self.assertRaises(error.HTTPError) as result:
            request.urlopen(bad, timeout=3)
        self.assertEqual(result.exception.code, 403)

        signature = hmac.new(self.secret.encode(), now.encode() + b"." + body,
                             hashlib.sha256).hexdigest()
        good = request.Request(self.url + "/api/v1/ingest/42", data=body,
                               headers={"X-Monitor-Timestamp": now,
                                        "X-Monitor-Signature": signature})
        with request.urlopen(good, timeout=3) as res:
            self.assertEqual(res.status, 200)
        with request.urlopen(self.url + "/api/v1/gpus", timeout=3) as res:
            self.assertEqual(res.headers["Access-Control-Allow-Origin"],
                             "https://agent-evolution.lightrain.asia")
            result = json.load(res)
        target = next(row for row in result["hosts"] if row["id"] == "42")
        self.assertTrue(target["online"])
        self.assertEqual(target["gpus"][0]["used_mib"], 8192)
        self.assertNotIn("test-secret", json.dumps(result))
        self.assertNotIn("process_name", json.dumps(result))
        with request.urlopen(self.url + "/api/v1/history", timeout=3) as res:
            history = json.load(res)
        self.assertEqual(len(history["hosts"]["42"]), 1)


if __name__ == "__main__":
    main(verbosity=2)
