#!/usr/bin/env python3
"""Fresh3 source execution rebind from empty runtime-v1 to qualified runtime-v2.

No scientific treatment changes are introduced here.  All source semantics, Q0.2/Q0.3
provider conditions, frozen source schedule, probe specs, smoke requirement, and hard
10/10 no-replacement gate are inherited from the preregistered fresh3 source runner.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from research_pipeline import run_c1_pacta_msr_atomgit_qwen38_fresh3_source_20260903 as base

RUNTIME = Path(
    "/data/wyt/agent-self-evolution-observatory/runs/"
    "c1-pacta-msr-atomgit-qwen38-fresh3-runtime-20260903-v2/normalization-qualification.json"
)
DEFAULT = Path(
    "/data/wyt/agent-self-evolution-observatory/runs/"
    "c1-pacta-msr-atomgit-qwen38-fresh3-source-20260903-v2"
)


def bind() -> None:
    base.RUNTIME = RUNTIME
    base.DEFAULT = DEFAULT


def main() -> None:
    bind()
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=DEFAULT)
    parser.add_argument("--phase", choices=("prepare", "prelaunch", "smoke", "acquire"), required=True)
    parser.add_argument("--runtime-qualification-sha", required=True)
    args = parser.parse_args()
    fn = {
        "prepare": base.prepare,
        "prelaunch": base.prelaunch,
        "smoke": base.smoke,
        "acquire": base.acquire,
    }[args.phase]
    result = fn(args.root, args.runtime_qualification_sha)
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
