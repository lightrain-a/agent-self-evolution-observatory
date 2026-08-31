"""Q6 single-variable Docker create acknowledgement reconciliation."""

from __future__ import annotations

import json
from typing import Any

from research_pipeline.asset_first_stri_reasoningbank_p1_core import (
    PID_NAMESPACE, DockerRun, run_host,
)

Q6_CONTRACT_SHA256 = "3c3a368070869eb30585c435c47122c41932a41db07c8d53db1404cdfed3c155"


class ReconciledDockerRun(DockerRun):
    """Accept only an exact Created side effect after docker-create timeout."""

    def _finish_exact_base_start(
        self, image_inspect: dict[str, Any], reconciliation: dict[str, Any],
    ) -> dict[str, Any]:
        started = run_host(["docker", "start", self.name], timeout=60, docker=True)
        if started["returncode"] != 0:
            raise RuntimeError(f"docker start failed: {started['output'][-800:]}")
        if not self.exact_base:
            raise RuntimeError("Q6 reconciliation is scoped to exact-base containers")
        pre = self.exec(
            "git rev-parse HEAD && "
            f"git cat-file -e {self.base_commit}^{{commit}} && "
            f"git merge-base --is-ancestor {self.base_commit} HEAD && "
            "test -z \"$(git status --porcelain=v1 --untracked-files=all)\"",
            timeout=30,
        )
        if pre["returncode"] != 0:
            raise RuntimeError(
                "Q6 exact-base normalization precondition failed: "
                f"{pre['output'].strip()}"
            )
        normalization = self.exec(f"git reset --hard {self.base_commit}", timeout=30)
        if normalization["returncode"] != 0:
            raise RuntimeError(
                "Q6 exact-base normalization action failed: "
                f"{normalization['output'].strip()}"
            )
        base = self.exec(
            f'test "$(git rev-parse HEAD)" = "{self.base_commit}" && '
            "test -z \"$(git status --porcelain=v1 --untracked-files=all)\" && "
            "git rev-parse HEAD",
            timeout=30,
        )
        if base["returncode"] != 0:
            raise RuntimeError(
                "Q6 exact-base normalization postcondition failed: "
                f"{base['output'].strip()}"
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
        return {
            "image_inspect": image_inspect,
            "base_commit_receipt": base,
            "q6_create_acknowledgement": reconciliation,
        }

    def start(self) -> dict[str, Any]:
        try:
            result = super().start()
            result["q6_create_acknowledgement"] = {
                "repair_invoked": False,
                "normal_create_receipt_accepted": True,
                "contract_sha256": Q6_CONTRACT_SHA256,
            }
            return result
        except RuntimeError as error:
            if str(error) != "docker create failed: ":
                raise
        image_inspect = run_host(
            ["docker", "image", "inspect", self.image, "--format",
             "{{json .RepoDigests}} {{.Architecture}}"],
            timeout=30,
            docker=True,
        )
        inspected = run_host(["docker", "inspect", self.name], timeout=30, docker=True)
        if image_inspect["returncode"] != 0 or inspected["returncode"] != 0:
            raise RuntimeError("Q6 docker-create timeout had no inspectable side effect")
        record = json.loads(inspected["output"])[0]
        exact = (
            record["State"]["Status"] == "created"
            and record["State"]["Running"] is False
            and record["Config"]["Image"] == self.image
            and record["Config"]["Entrypoint"] == ["sleep"]
            and record["Config"]["Cmd"] == ["infinity"]
            and record["HostConfig"]["PidMode"] == PID_NAMESPACE
            and record["Name"] == f"/{self.name}"
        )
        if not exact:
            raise RuntimeError("Q6 docker-create side effect failed exact reconciliation")
        self.created = True
        reconciliation = {
            "repair_invoked": True,
            "normal_create_receipt_accepted": False,
            "trigger": "docker create failed with empty output after 60-second boundary",
            "container_id": record["Id"],
            "container_name": record["Name"],
            "state": record["State"]["Status"],
            "image": record["Config"]["Image"],
            "entrypoint": record["Config"]["Entrypoint"],
            "cmd": record["Config"]["Cmd"],
            "pid_mode": record["HostConfig"]["PidMode"],
            "exact_side_effect_verified": True,
            "contract_sha256": Q6_CONTRACT_SHA256,
        }
        return self._finish_exact_base_start(image_inspect, reconciliation)
