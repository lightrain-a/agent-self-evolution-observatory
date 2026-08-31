"""Q10 exactly-once Docker-start acknowledgement reconciliation."""

from __future__ import annotations

import json
import re
from typing import Any

from research_pipeline.asset_first_stri_reasoningbank_p1_core import (
    COMMAND_TIMEOUT_SECONDS, PID_NAMESPACE, run_host,
)
from research_pipeline.asset_first_stri_reasoningbank_p1_q9_runtime import (
    ExtendedStartGraceDockerRun, Q9_CONTRACT_SHA256,
)

Q10_CONTRACT_SHA256 = "bc4781ce0188d899af3b1a491b51f30467e6c655c7f8d3074b919a043b2878bd"


class Q10RuntimeHold(RuntimeError):
    """Fail-closed start ambiguity with a finalized reconciliation receipt."""

    def __init__(self, message: str, receipt: dict[str, Any]):
        super().__init__(message)
        self.receipt = receipt


class DaemonReconciledDockerRun(ExtendedStartGraceDockerRun):
    """Start once; reconcile only a timeout-ambiguous acknowledgement."""

    ACK_CONTRACT_SHA256 = Q10_CONTRACT_SHA256
    CREATE_INSPECT_TIMEOUT_SECONDS = 180
    START_INSPECT_TIMEOUT_SECONDS = 180
    START_TIMEOUT_SECONDS = 600

    def __init__(
        self,
        image: str,
        base_commit: str,
        run_id: str,
        expected_image_digest: str,
        exact_base: bool = False,
    ) -> None:
        super().__init__(image, base_commit, run_id, exact_base)
        self.expected_image_digest = expected_image_digest
        self.container_id: str | None = None
        self.start_reconciliation_receipt: dict[str, Any] | None = None
        self.cleanup_receipt: dict[str, Any] | None = None

    @staticmethod
    def _is_ambiguous_start(receipt: dict[str, Any]) -> bool:
        return bool(
            receipt.get("timed_out") is True
            and receipt.get("returncode") is None
        )

    def _image_record(self, image_inspect: dict[str, Any]) -> dict[str, Any]:
        try:
            records = json.loads(image_inspect["output"])
            record = records[0]
        except (KeyError, IndexError, TypeError, json.JSONDecodeError) as error:
            raise RuntimeError("Q10 frozen image inspection is not exact JSON") from error
        if (
            image_inspect["returncode"] != 0
            or image_inspect["timed_out"]
            or record.get("Architecture") != "amd64"
            or self.expected_image_digest not in " ".join(record.get("RepoDigests") or [])
        ):
            raise RuntimeError("Q10 frozen image/digest/architecture verification failed")
        return record

    def _create_once(self) -> tuple[dict[str, Any], dict[str, Any]]:
        image_inspect = run_host(
            ["docker", "image", "inspect", self.image],
            timeout=30,
            docker=True,
        )
        image_record = self._image_record(image_inspect)
        created = run_host(
            [
                "docker", "create", "--platform", "linux/amd64",
                "--pid", PID_NAMESPACE, "--name", self.name,
                "--entrypoint", "sleep", self.image, "infinity",
            ],
            timeout=60,
            docker=True,
        )
        create_ack: dict[str, Any] = {
            "client_create_invocations": 1,
            "client_returncode": created["returncode"],
            "client_timed_out": created["timed_out"],
            "client_output": created["output"][-800:],
            "repair_invoked": False,
            "normal_create_receipt_accepted": False,
            "second_create_invoked": False,
            "contract_sha256": Q9_CONTRACT_SHA256,
        }
        if created["returncode"] == 0 and not created["timed_out"]:
            container_id = created["output"].strip()
            if not container_id:
                raise RuntimeError("docker create returned an empty successful receipt")
            self.container_id = container_id
            self.created = True
            create_ack.update({
                "normal_create_receipt_accepted": True,
                "container_id": container_id,
                "accepted": True,
            })
            return image_inspect, create_ack
        if not (created["timed_out"] and created["returncode"] is None):
            raise RuntimeError(f"docker create failed: {created['output'][-800:]}")
        inspected = run_host(
            ["docker", "inspect", self.name],
            timeout=self.CREATE_INSPECT_TIMEOUT_SECONDS,
            docker=True,
        )
        if inspected["returncode"] != 0 or inspected["timed_out"]:
            raise RuntimeError("Q10 inherited create reconciliation found no inspectable side effect")
        try:
            record = json.loads(inspected["output"])[0]
        except (IndexError, TypeError, json.JSONDecodeError) as error:
            raise RuntimeError("Q10 inherited create reconciliation received invalid inspect JSON") from error
        exact = bool(
            record["State"]["Status"] == "created"
            and record["State"]["Running"] is False
            and record["Config"]["Image"] == self.image
            and record["Image"] == image_record["Id"]
            and record["Config"]["Entrypoint"] == ["sleep"]
            and record["Config"]["Cmd"] == ["infinity"]
            and record["HostConfig"]["PidMode"] == PID_NAMESPACE
            and record["Name"] == f"/{self.name}"
        )
        if not exact:
            raise RuntimeError("Q10 inherited create side effect failed exact reconciliation")
        self.container_id = record["Id"]
        self.created = True
        create_ack.update({
            "repair_invoked": True,
            "trigger": "docker create acknowledgement timeout",
            "container_id": record["Id"],
            "container_name": record["Name"],
            "state": record["State"]["Status"],
            "image": record["Config"]["Image"],
            "entrypoint": record["Config"]["Entrypoint"],
            "cmd": record["Config"]["Cmd"],
            "pid_mode": record["HostConfig"]["PidMode"],
            "exact_side_effect_verified": True,
            "accepted": True,
        })
        return image_inspect, create_ack

    def _receipt_base(self, started: dict[str, Any]) -> dict[str, Any]:
        return {
            "client_start_invocations": 1,
            "client_returncode": started["returncode"],
            "client_timed_out": started["timed_out"],
            "client_output": started["output"][-800:],
            "reconciliation_invoked": False,
            "docker_inspect_invoked": False,
            "container_id": self.container_id,
            "container_name": f"/{self.name}",
            "expected_image": self.image,
            "observed_image": None,
            "expected_image_digest": self.expected_image_digest,
            "observed_image_digests": None,
            "expected_pid_mode": PID_NAMESPACE,
            "observed_pid_mode": None,
            "daemon_status": None,
            "daemon_running": None,
            "daemon_pid": None,
            "daemon_dead": None,
            "daemon_restarting": None,
            "restart_count": None,
            "exact_identity_verified": False,
            "exact_running_state_verified": False,
            "second_start_invoked": False,
            "accepted": False,
            "acceptance_rule": None,
            "receipt_finalized": False,
            "contract_sha256": self.ACK_CONTRACT_SHA256,
        }

    def _inspect_running(
        self,
        receipt: dict[str, Any],
        image_record: dict[str, Any],
    ) -> bool:
        receipt["docker_inspect_invoked"] = True
        inspected = run_host(
            ["docker", "inspect", self.name],
            timeout=self.START_INSPECT_TIMEOUT_SECONDS,
            docker=True,
        )
        receipt["docker_inspect_receipt"] = {
            "returncode": inspected["returncode"],
            "timed_out": inspected["timed_out"],
            "output_sha256_recorded_elsewhere": False,
        }
        if inspected["returncode"] != 0 or inspected["timed_out"]:
            return False
        try:
            record = json.loads(inspected["output"])[0]
        except (IndexError, TypeError, json.JSONDecodeError):
            return False
        state = record.get("State") or {}
        config = record.get("Config") or {}
        host = record.get("HostConfig") or {}
        observed_digests = image_record.get("RepoDigests") or []
        identity = bool(
            self.container_id
            and record.get("Id") == self.container_id
            and record.get("Name") == f"/{self.name}"
            and record.get("Image") == image_record.get("Id")
            and config.get("Image") == self.image
            and self.expected_image_digest in " ".join(observed_digests)
            and config.get("Entrypoint") == ["sleep"]
            and config.get("Cmd") == ["infinity"]
            and host.get("PidMode") == PID_NAMESPACE
        )
        running = bool(
            state.get("Status") == "running"
            and state.get("Running") is True
            and isinstance(state.get("Pid"), int)
            and state["Pid"] > 0
            and state.get("Dead") is False
            and state.get("Restarting") is False
            and record.get("RestartCount", 0) == 0
        )
        receipt.update({
            "container_id": record.get("Id"),
            "container_name": record.get("Name"),
            "observed_image": config.get("Image"),
            "observed_image_digests": observed_digests,
            "observed_pid_mode": host.get("PidMode"),
            "observed_entrypoint": config.get("Entrypoint"),
            "observed_cmd": config.get("Cmd"),
            "daemon_status": state.get("Status"),
            "daemon_running": state.get("Running"),
            "daemon_pid": state.get("Pid"),
            "daemon_dead": state.get("Dead"),
            "daemon_restarting": state.get("Restarting"),
            "restart_count": record.get("RestartCount"),
            "exact_identity_verified": identity,
            "exact_running_state_verified": bool(identity and running),
        })
        return bool(identity and running)

    def _start_once(
        self,
        image_inspect: dict[str, Any],
    ) -> dict[str, Any]:
        image_record = self._image_record(image_inspect)
        started = run_host(
            ["docker", "start", self.name],
            timeout=self.START_TIMEOUT_SECONDS,
            docker=True,
        )
        receipt = self._receipt_base(started)
        self.start_reconciliation_receipt = receipt
        if started["returncode"] == 0 and not started["timed_out"]:
            exact = self._inspect_running(receipt, image_record)
            receipt.update({
                "accepted": exact,
                "acceptance_rule": (
                    "normal_client_acknowledgement_with_exact_post_start_state"
                    if exact else "normal_acknowledgement_but_exact_state_not_proven"
                ),
                "receipt_finalized": True,
            })
            if not exact:
                raise Q10RuntimeHold(
                    "Q10 normal start acknowledgement lacked exact running-state proof",
                    receipt,
                )
            return receipt
        if not self._is_ambiguous_start(started):
            receipt.update({
                "acceptance_rule": "explicit_non_timeout_error_hard_failure",
                "receipt_finalized": True,
            })
            raise RuntimeError(f"docker start failed: {started['output'][-800:]}")
        receipt["reconciliation_invoked"] = True
        exact = self._inspect_running(receipt, image_record)
        receipt.update({
            "accepted": exact,
            "acceptance_rule": (
                "exact_daemon_side_running_state_after_ambiguous_client_timeout"
                if exact else "HOLD_exact_daemon_side_running_state_not_proven"
            ),
            "receipt_finalized": True,
        })
        if not exact:
            raise Q10RuntimeHold(
                "Q10 docker-start acknowledgement reconciliation HOLD",
                receipt,
            )
        return receipt

    def _normalize_exact_base(self) -> dict[str, Any]:
        if not re.fullmatch(r"[0-9a-f]{40}", self.base_commit):
            raise RuntimeError("invalid frozen base commit")
        if not self.exact_base:
            raise RuntimeError("Q10 reconciliation is scoped to exact-base containers")
        pre = self.exec(
            "git rev-parse HEAD && "
            f"git cat-file -e {self.base_commit}^{{commit}} && "
            f"git merge-base --is-ancestor {self.base_commit} HEAD && "
            "test -z \"$(git status --porcelain=v1 --untracked-files=all)\"",
            timeout=30,
        )
        if pre["returncode"] != 0 or pre["timed_out"]:
            raise RuntimeError(
                f"Q10 exact-base normalization precondition failed: {pre['output'].strip()}"
            )
        normalization = self.exec(f"git reset --hard {self.base_commit}", timeout=30)
        if normalization["returncode"] != 0 or normalization["timed_out"]:
            raise RuntimeError(
                f"Q10 exact-base normalization action failed: {normalization['output'].strip()}"
            )
        base = self.exec(
            f'test "$(git rev-parse HEAD)" = "{self.base_commit}" && '
            "test -z \"$(git status --porcelain=v1 --untracked-files=all)\" && "
            "git rev-parse HEAD",
            timeout=30,
        )
        if base["returncode"] != 0 or base["timed_out"]:
            raise RuntimeError(
                f"Q10 exact-base normalization postcondition failed: {base['output'].strip()}"
            )
        base.update({
            "pre_normalization": pre,
            "normalization": normalization,
            "normalization_action": "git reset --hard <frozen expected base commit>",
            "git_clean_invoked": False,
            "expected_base_commit": self.base_commit,
            "observed_head": base["output"].strip(),
            "rule": "exact_base_after_preregistered_hard_reset",
        })
        return base

    def exec(
        self,
        action: str,
        *,
        timeout: int | float = COMMAND_TIMEOUT_SECONDS,
    ) -> dict[str, Any]:
        return run_host(
            [
                "docker", "exec", "--workdir", "/testbed",
                "--env", "PAGER=cat", "--env", "MANPAGER=cat",
                "--env", "LESS=-R", "--env", "PIP_PROGRESS_BAR=off",
                "--env", "TQDM_DISABLE=1", self.name, "bash", "-lc", action,
            ],
            timeout=timeout,
            docker=True,
        )

    def start(self) -> dict[str, Any]:
        image_inspect, create_ack = self._create_once()
        start_ack = self._start_once(image_inspect)
        base = self._normalize_exact_base()
        return {
            "image_inspect": image_inspect,
            "base_commit_receipt": base,
            "q6_create_acknowledgement": create_ack,
            "q10_start_reconciliation": start_ack,
        }

    def close(self) -> dict[str, Any]:
        finalized = bool(
            self.start_reconciliation_receipt
            and self.start_reconciliation_receipt.get("receipt_finalized") is True
        )
        cleanup = {
            "cleanup_invoked": self.created,
            "container_name": self.name,
            "reconciliation_receipt_finalized_before_cleanup": finalized,
            "returncode": None,
            "timed_out": False,
            "accepted": not self.created,
        }
        if self.created:
            removed = run_host(
                ["docker", "rm", "-f", self.name],
                timeout=60,
                docker=True,
            )
            cleanup.update({
                "returncode": removed["returncode"],
                "timed_out": removed["timed_out"],
                "accepted": removed["returncode"] == 0 and not removed["timed_out"],
            })
            self.created = False
        self.cleanup_receipt = cleanup
        return cleanup
