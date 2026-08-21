from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import scripts.run_d2_active_paper_mock_pc as mock_pc


def main() -> int:
    mock_pc.OUTDIR = mock_pc.ROOT / "generated/d2-active-paper-mock-pc-20260821-r2-c02"
    ledger_root = Path("/data/wyt/agent-self-evolution-observatory/d2-paper-acceptance-round2-c02")
    state = mock_pc.states()["D2-PAPER-PROXY-REWARD-MEMORY-VARIANCE"]
    result = mock_pc.run_paper(ledger_root, state)
    payload = {
        "schema_version": "1.0",
        "round": "R2_AFTER_PROMPT_CONTROL",
        "paper": result,
        "ledger_index": mock_pc.build_paper_ledger_index(ledger_root),
        "scientific_authority": False,
        "experiment_authority": False,
        "submission_authority": False,
    }
    mock_pc.OUTDIR.mkdir(parents=True, exist_ok=True)
    (mock_pc.OUTDIR / "round-result.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if result.get("voting_reviews") == 2 else 2


if __name__ == "__main__":
    raise SystemExit(main())
