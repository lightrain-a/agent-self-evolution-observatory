from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path("/data/wyt/agent-self-evolution-observatory/worktrees/e2-r17-deepseek-v2-repair2-m1-20260831")
RUN_ROOT = Path("/data/wyt/e2-r17-search-projection/runs/deepseek-v2-repair2-v3-20260831")
CONTRACT = ROOT / "generated/e2-r17-deepseek-v2-repair2-v3-contract-20260831.json"
AUTHORIZATION = ROOT / "generated/e2-r17-deepseek-v2-repair2-v3-authorization-20260831.json"
PREFLIGHT = ROOT / "generated/e2-r17-deepseek-v2-repair2-v3-frozen-preflight-adjudication-20260831.json"
PYTHON = Path("/data/wyt/e2-r17-search-projection/mindmemos-updater-venv/bin/python")
RUNNER = ROOT / "scripts/run_e2_r17_deepseek_v2_repair2_continuation_v3.py"
EXPECTED = {
    CONTRACT: "312e970520794c564b23a9717f4c40d4baeb0674619da334c8fcc20ee95fc045",
    AUTHORIZATION: "7aa826db915b40840fb54ca2c269a23c4f74807bae74fd99285eac6875ee5b74",
    PREFLIGHT: "fb1022bd6add1f5ea64237f81b0933331cfb6e263243deb33da5e0bc728ad66d",
    RUNNER: "a735c7cd15f10a4feb52cc171b5e906494ae53205e29f334ecd7e3afbf7efe30",
    ROOT / "scripts/run_e2_r17_actor_pool_repair2_v3.py": "a04f36ba6270d51eedf3d4fde31028f6aa3fc50852a6ce58736c45ff98eff0d0",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


for path, expected in EXPECTED.items():
    actual = sha(path)
    if actual != expected:
        raise RuntimeError(f"frozen SHA drift before V3 start: {path}: {actual}")
preflight = json.loads(PREFLIGHT.read_text())
if preflight.get("status") != "PREFLIGHT_PASS_REPAIR2_CONTINUATION_V3":
    raise RuntimeError("V3 frozen preflight not passing")
if preflight["actual_actor_authorization_path"].get("provider_calls") != 0:
    raise RuntimeError("V3 preflight provider-call drift")
RUN_ROOT.mkdir(parents=True, exist_ok=False)
receipt_path = RUN_ROOT / "run_start_receipt.json"
payload = {
    "schema_version": "1.0",
    "artifact_type": "e2-r17-deepseek-v2-repair2-continuation-v3-run-start-receipt",
    "status": "STARTED_EXACTLY_ONCE",
    "started_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    "pid": os.getpid(),
    "pgid": os.getpgrp(),
    "git_commit": "16a8cc6a",
    "contract_path": str(CONTRACT),
    "contract_sha256": EXPECTED[CONTRACT],
    "authorization_path": str(AUTHORIZATION),
    "authorization_sha256": EXPECTED[AUTHORIZATION],
    "preflight_path": str(PREFLIGHT),
    "preflight_sha256": EXPECTED[PREFLIGHT],
    "runner_path": str(RUNNER),
    "runner_sha256": EXPECTED[RUNNER],
    "actor_path": str(ROOT / "scripts/run_e2_r17_actor_pool_repair2_v3.py"),
    "actor_sha256": EXPECTED[ROOT / "scripts/run_e2_r17_actor_pool_repair2_v3.py"],
    "run_root": str(RUN_ROOT),
    "inherited_pairs": 15,
    "repair1_inherited_pairs": 14,
    "repair2_m1_recovered_pairs": 1,
    "fresh_pairs": 33,
    "expected_terminal": {
        "paired_units": 48,
        "learned_states": 96,
        "heldout_units": 1728,
    },
    "remaining_execution": {
        "new_learned_states": 66,
        "heldout_units": 1188,
    },
    "parent_repair2_updater_calls_sealed": 20,
    "inherited_provider_replay": False,
    "provider_claims_before_start": 0,
    "provider_calls_before_start": 0,
    "partial_effect_read": False,
    "analyzer_run": False,
    "exactly_once": True,
    "ambiguous_provider_response_retry": False,
}
temp = receipt_path.with_suffix(".json.tmp")
temp.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
with temp.open("rb") as handle:
    os.fsync(handle.fileno())
temp.replace(receipt_path)
directory_fd = os.open(RUN_ROOT, os.O_RDONLY)
try:
    os.fsync(directory_fd)
finally:
    os.close(directory_fd)
print(json.dumps({"status": payload["status"], "pid": payload["pid"], "pgid": payload["pgid"], "receipt_sha256": sha(receipt_path)}, sort_keys=True), flush=True)
os.chdir(ROOT)
os.execv(
    str(PYTHON),
    [
        str(PYTHON),
        str(RUNNER),
        "--contract",
        str(CONTRACT),
        "--authorization",
        str(AUTHORIZATION),
    ],
)
