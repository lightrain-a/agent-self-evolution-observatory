#!/usr/bin/env python3
"""Render the descriptive first-violation event-time matrix from the frozen receipt."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import BoundaryNorm, ListedColormap


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
RECEIPT = REPO / "generated" / "agent-safety-r9-future-evidence-adjudication-20260820.json"
OUTDIR = HERE / "figures"

STATE_ORDER = ["map-P2-A", "map-V4-C1", "reddit-A", "reddit-B"]


def _extract_steps(payload: dict) -> dict[str, list[int | None]]:
    states = payload.get("future_first_violation", {}).get("states")
    if not isinstance(states, dict):
        raise ValueError("The frozen receipt is missing future_first_violation.states")

    result: dict[str, list[int | None]] = {}
    for state in STATE_ORDER:
        row = states.get(state)
        if not isinstance(row, dict):
            raise ValueError(f"The frozen receipt is missing state {state}")
        steps = row.get("first_violation_steps")
        if not isinstance(steps, list) or len(steps) != 3:
            raise ValueError(f"State {state} does not contain three branch event times")
        if any(value not in {None, 1, 2, 3} for value in steps):
            raise ValueError(f"State {state} contains an out-of-horizon event time")
        result[state] = steps
    return result


def main() -> None:
    payload = json.loads(RECEIPT.read_text())
    steps = _extract_steps(payload)
    matrix = np.array(
        [[4 if value is None else value for value in steps[state]] for state in STATE_ORDER],
        dtype=int,
    )

    cmap = ListedColormap(["#d73027", "#fc8d59", "#fee08b", "#e6e8eb"])
    norm = BoundaryNorm([0.5, 1.5, 2.5, 3.5, 4.5], cmap.N)

    fig, ax = plt.subplots(figsize=(6.7, 3.4))
    ax.imshow(matrix, cmap=cmap, norm=norm, aspect="auto")

    for row in range(matrix.shape[0]):
        for col in range(matrix.shape[1]):
            value = matrix[row, col]
            label = ">3" if value == 4 else str(value)
            color = "white" if value == 1 else "#1f2933"
            ax.text(col, row, label, ha="center", va="center", fontsize=11, color=color)

    ax.set_xticks(range(3), ["Branch 1", "Branch 2", "Branch 3"])
    ax.set_yticks(range(4), STATE_ORDER)
    ax.set_xlabel("Common future branch")
    ax.set_ylabel("Persistent state")
    ax.set_title("First-violation event time within the three-step horizon", pad=10)
    ax.set_xticks(np.arange(-0.5, 3, 1), minor=True)
    ax.set_yticks(np.arange(-0.5, 4, 1), minor=True)
    ax.grid(which="minor", color="white", linewidth=2)
    ax.tick_params(which="minor", bottom=False, left=False)
    for spine in ax.spines.values():
        spine.set_visible(False)

    fig.tight_layout()
    OUTDIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUTDIR / "first_violation_by_state_branch.pdf", bbox_inches="tight")
    fig.savefig(OUTDIR / "first_violation_by_state_branch.png", dpi=220, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    main()
