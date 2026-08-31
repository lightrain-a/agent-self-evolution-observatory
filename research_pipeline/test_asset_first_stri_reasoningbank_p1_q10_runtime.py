from __future__ import annotations

import copy
import json
import unittest
from unittest.mock import patch

from research_pipeline.asset_first_stri_reasoningbank_p1_q10_runtime import (
    DaemonReconciledDockerRun,
    Q10RuntimeHold,
)

BASE = "a" * 40
CONTAINER_ID = "b" * 64
IMAGE_ID = "sha256:" + "c" * 64
DIGEST = "sha256:" + "d" * 64
IMAGE = "swebench/sweb.eval.x86_64.demo:latest"


def result(
    returncode: int | None = 0,
    output: str = "",
    timed_out: bool = False,
) -> dict:
    return {
        "started_at_utc": "2026-08-31T00:00:00+00:00",
        "finished_at_utc": "2026-08-31T00:00:01+00:00",
        "returncode": returncode,
        "output": output,
        "timed_out": timed_out,
    }


class HostHarness:
    def __init__(
        self,
        run: DaemonReconciledDockerRun,
        *,
        start_result: dict | None = None,
        container_changes: dict | None = None,
        inspect_result: dict | None = None,
    ) -> None:
        self.run = run
        self.start_result = start_result or result(0, run.name + "\n")
        self.container_changes = container_changes or {}
        self.inspect_result = inspect_result
        self.commands: list[list[str]] = []

    def image_record(self) -> dict:
        return {
            "Id": IMAGE_ID,
            "Architecture": "amd64",
            "RepoDigests": [f"{IMAGE}@{DIGEST}"],
        }

    def container_record(self) -> dict:
        record = {
            "Id": CONTAINER_ID,
            "Name": f"/{self.run.name}",
            "Image": IMAGE_ID,
            "Config": {
                "Image": IMAGE,
                "Entrypoint": ["sleep"],
                "Cmd": ["infinity"],
            },
            "HostConfig": {"PidMode": "host"},
            "State": {
                "Status": "running",
                "Running": True,
                "Pid": 4242,
                "Dead": False,
                "Restarting": False,
            },
            "RestartCount": 0,
        }
        for dotted, value in self.container_changes.items():
            target = record
            parts = dotted.split(".")
            for part in parts[:-1]:
                target = target[part]
            target[parts[-1]] = value
        return record

    def __call__(self, command: list[str], *, timeout: int | float, docker: bool = False) -> dict:
        self.commands.append(command)
        if command[:3] == ["docker", "image", "inspect"]:
            return result(0, json.dumps([self.image_record()]))
        if command[:2] == ["docker", "create"]:
            return result(0, CONTAINER_ID + "\n")
        if command[:2] == ["docker", "start"]:
            return copy.deepcopy(self.start_result)
        if command[:2] == ["docker", "inspect"]:
            if self.inspect_result is not None:
                return copy.deepcopy(self.inspect_result)
            return result(0, json.dumps([self.container_record()]))
        if command[:2] == ["docker", "exec"]:
            return result(0, BASE + "\n")
        if command[:3] == ["docker", "rm", "-f"]:
            return result(0, self.run.name + "\n")
        raise AssertionError(f"unexpected command: {command}")

    @property
    def start_count(self) -> int:
        return sum(command[:2] == ["docker", "start"] for command in self.commands)

    @property
    def container_inspect_count(self) -> int:
        return sum(command[:2] == ["docker", "inspect"] for command in self.commands)


class ReasoningBankP1Q10RuntimeTest(unittest.TestCase):
    def make_run(self) -> DaemonReconciledDockerRun:
        return DaemonReconciledDockerRun(
            IMAGE, BASE, "q10-fault-test", DIGEST, exact_base=True
        )

    def test_t1_normal_success(self) -> None:
        run = self.make_run()
        host = HostHarness(run)
        with patch(
            "research_pipeline.asset_first_stri_reasoningbank_p1_q10_runtime.run_host",
            side_effect=host,
        ):
            receipt = run.start()["q10_start_reconciliation"]
            cleanup = run.close()
        self.assertTrue(receipt["accepted"])
        self.assertFalse(receipt["reconciliation_invoked"])
        self.assertEqual(receipt["client_start_invocations"], 1)
        self.assertFalse(receipt["second_start_invoked"])
        self.assertEqual(host.start_count, 1)
        self.assertTrue(cleanup["accepted"])

    def test_t2_timeout_daemon_running(self) -> None:
        run = self.make_run()
        host = HostHarness(
            run,
            start_result=result(None, "", True),
        )
        with patch(
            "research_pipeline.asset_first_stri_reasoningbank_p1_q10_runtime.run_host",
            side_effect=host,
        ):
            receipt = run.start()["q10_start_reconciliation"]
            cleanup = run.close()
        self.assertTrue(receipt["reconciliation_invoked"])
        self.assertTrue(receipt["exact_running_state_verified"])
        self.assertEqual(
            receipt["acceptance_rule"],
            "exact_daemon_side_running_state_after_ambiguous_client_timeout",
        )
        self.assertEqual(host.start_count, 1)
        self.assertFalse(receipt["second_start_invoked"])
        self.assertTrue(cleanup["reconciliation_receipt_finalized_before_cleanup"])

    def assert_timeout_hold(self, changes: dict) -> tuple[dict, HostHarness]:
        run = self.make_run()
        host = HostHarness(
            run,
            start_result=result(None, "", True),
            container_changes=changes,
        )
        with patch(
            "research_pipeline.asset_first_stri_reasoningbank_p1_q10_runtime.run_host",
            side_effect=host,
        ):
            with self.assertRaises(Q10RuntimeHold) as caught:
                run.start()
            cleanup = run.close()
        receipt = caught.exception.receipt
        self.assertTrue(receipt["receipt_finalized"])
        self.assertFalse(receipt["accepted"])
        self.assertEqual(host.start_count, 1)
        self.assertFalse(receipt["second_start_invoked"])
        self.assertTrue(cleanup["reconciliation_receipt_finalized_before_cleanup"])
        return receipt, host

    def test_t3_timeout_daemon_created_holds(self) -> None:
        receipt, _ = self.assert_timeout_hold({
            "State.Status": "created",
            "State.Running": False,
            "State.Pid": 0,
        })
        self.assertEqual(receipt["daemon_status"], "created")

    def test_t4_timeout_daemon_exited_holds(self) -> None:
        receipt, _ = self.assert_timeout_hold({
            "State.Status": "exited",
            "State.Running": False,
            "State.Pid": 0,
        })
        self.assertEqual(receipt["daemon_status"], "exited")

    def test_t5_timeout_daemon_restarting_holds(self) -> None:
        receipt, _ = self.assert_timeout_hold({
            "State.Status": "restarting",
            "State.Running": True,
            "State.Restarting": True,
        })
        self.assertTrue(receipt["daemon_restarting"])

    def test_t6_wrong_container_identity_holds(self) -> None:
        receipt, _ = self.assert_timeout_hold({"Id": "e" * 64})
        self.assertFalse(receipt["exact_identity_verified"])

    def test_t7_wrong_image_pid_or_command_holds(self) -> None:
        cases = [
            {"Config.Image": "wrong:image"},
            {"HostConfig.PidMode": "private"},
            {"Config.Cmd": ["not-infinity"]},
        ]
        for changes in cases:
            with self.subTest(changes=changes):
                receipt, _ = self.assert_timeout_hold(changes)
                self.assertFalse(receipt["exact_identity_verified"])

    def test_t8_explicit_error_is_hard_failure_without_reconciliation(self) -> None:
        run = self.make_run()
        host = HostHarness(
            run,
            start_result=result(1, "permission denied", False),
        )
        with patch(
            "research_pipeline.asset_first_stri_reasoningbank_p1_q10_runtime.run_host",
            side_effect=host,
        ):
            with self.assertRaisesRegex(RuntimeError, "permission denied"):
                run.start()
            cleanup = run.close()
        receipt = run.start_reconciliation_receipt
        self.assertIsNotNone(receipt)
        assert receipt is not None
        self.assertFalse(receipt["reconciliation_invoked"])
        self.assertFalse(receipt["docker_inspect_invoked"])
        self.assertEqual(host.container_inspect_count, 0)
        self.assertEqual(host.start_count, 1)
        self.assertTrue(cleanup["reconciliation_receipt_finalized_before_cleanup"])

    def test_t9_reconciliation_inspect_timeout_holds_without_retry(self) -> None:
        run = self.make_run()
        host = HostHarness(
            run,
            start_result=result(None, "", True),
            inspect_result=result(None, "", True),
        )
        with patch(
            "research_pipeline.asset_first_stri_reasoningbank_p1_q10_runtime.run_host",
            side_effect=host,
        ):
            with self.assertRaises(Q10RuntimeHold) as caught:
                run.start()
            run.close()
        receipt = caught.exception.receipt
        self.assertTrue(receipt["docker_inspect_invoked"])
        self.assertFalse(receipt["accepted"])
        self.assertEqual(host.container_inspect_count, 1)
        self.assertEqual(host.start_count, 1)

    def test_t10_cleanup_after_receipt_finalization(self) -> None:
        run = self.make_run()
        host = HostHarness(run, start_result=result(None, "", True))
        with patch(
            "research_pipeline.asset_first_stri_reasoningbank_p1_q10_runtime.run_host",
            side_effect=host,
        ):
            receipt = run.start()["q10_start_reconciliation"]
            cleanup = run.close()
        self.assertTrue(receipt["receipt_finalized"])
        self.assertTrue(cleanup["reconciliation_receipt_finalized_before_cleanup"])
        start_index = next(
            i for i, command in enumerate(host.commands)
            if command[:2] == ["docker", "start"]
        )
        inspect_index = next(
            i for i, command in enumerate(host.commands)
            if command[:2] == ["docker", "inspect"]
        )
        cleanup_index = next(
            i for i, command in enumerate(host.commands)
            if command[:3] == ["docker", "rm", "-f"]
        )
        self.assertLess(start_index, inspect_index)
        self.assertLess(inspect_index, cleanup_index)


if __name__ == "__main__":
    unittest.main()
