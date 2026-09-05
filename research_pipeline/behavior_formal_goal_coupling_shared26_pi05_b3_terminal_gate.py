from __future__ import annotations

import json
from pathlib import Path

WAIT_STATUSES = {
    "PI05_B3_CHECKPOINT_SAVE_QUALIFICATION_STARTED",
    "PI05_B3_CHECKPOINT_SAVE_QUALIFICATION_SAVE_STARTED",
}
PASS_STATUS = "PI05_B3_CHECKPOINT_SAVE_QUALIFICATION_PASS"
HOLD_STATUS = "PI05_B3_CHECKPOINT_SAVE_QUALIFICATION_HOLD"


def classify_save_result(path: str | Path) -> str:
    p = Path(path)
    if not p.exists():
        return "WAIT"
    try:
        payload = json.loads(p.read_text())
    except Exception:
        return "HOLD"
    status = payload.get("status")
    if status in WAIT_STATUSES:
        return "WAIT"
    if status == PASS_STATUS:
        return "PASS"
    if status == HOLD_STATUS:
        return "HOLD"
    return "HOLD"
