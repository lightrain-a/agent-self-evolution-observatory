from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--adjudication", required=True)
    parser.add_argument("--output-prefix", required=True)
    args = parser.parse_args()
    data = load(Path(args.adjudication))
    primary = data["primary_same_schedule_control"]
    fixed = data["secondary_fixed_probe_snapshots"]
    rows = primary["paired_rows"]

    plt.rcParams.update({
        "font.size": 8.5,
        "axes.titlesize": 9.5,
        "axes.labelsize": 8.5,
        "font.family": "DejaVu Sans",
        "pdf.fonttype": 42,
    })
    fig, axes = plt.subplots(1, 3, figsize=(10.5, 3.0), gridspec_kw={"width_ratios": [0.8, 1.7, 1.05]})

    ax = axes[0]
    treatment_events = primary["treatment_branch_events"]
    control_events = primary["control_branch_events"]
    ax.bar([0, 1], [treatment_events, control_events], color=["#D84A3A", "#3F7CAC"], width=0.62)
    ax.set_xticks([0, 1], ["Update", "No update"])
    ax.set_ylim(0, 12)
    ax.set_ylabel("Branches with first violation")
    for x, value in enumerate([treatment_events, control_events]):
        ax.text(x, value + 0.35, f"{value}/12", ha="center", fontweight="bold")
    ax.set_title("(a) Same-schedule control")
    ax.spines[["top", "right"]].set_visible(False)

    ax = axes[1]
    y_t = [row["treatment_first_violation_step"] or 4 for row in rows]
    y_c = [row["control_first_violation_step"] or 4 for row in rows]
    x = np.arange(len(rows))
    for i, (a, b) in enumerate(zip(y_t, y_c)):
        ax.plot([i - 0.13, i + 0.13], [a, b], color="#999999", lw=0.8, zorder=1)
    ax.scatter(x - 0.13, y_t, marker="o", s=27, color="#D84A3A", label="Update", zorder=2)
    ax.scatter(x + 0.13, y_c, marker="s", s=24, color="#3F7CAC", label="No update", zorder=2)
    ax.set_yticks([1, 2, 3, 4], ["1", "2", "3", ">3"])
    ax.set_xticks(x, [f"{row['state_id']}\nB{row['branch_seed']}" for row in rows], rotation=55, ha="right", fontsize=6.5)
    ax.set_ylabel("First-violation step")
    ax.set_title("(b) Paired branch event time")
    ax.legend(frameon=False, ncol=2, loc="upper left")
    ax.spines[["top", "right"]].set_visible(False)

    ax = axes[2]
    exposure = [0, 1, 2, 3]
    violations = [int(fixed["violations_by_exposure_step"][str(step)]) for step in exposure]
    ax.plot(exposure, violations, color="#6A4C93", marker="o", lw=2)
    ax.fill_between(exposure, violations, color="#6A4C93", alpha=0.12)
    ax.set_xticks(exposure)
    ax.set_ylim(0, 12)
    ax.set_xlabel("Persistent-state exposure step")
    ax.set_ylabel("Violating fixed-probe episodes / 12")
    ax.set_title("(c) Fixed qualification probes")
    ax.spines[["top", "right"]].set_visible(False)
    for x_value, y_value in zip(exposure, violations):
        ax.text(x_value, y_value + 0.35, str(y_value), ha="center")

    fig.tight_layout(w_pad=1.2)
    prefix = Path(args.output_prefix)
    prefix.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(prefix.with_suffix(".pdf"), bbox_inches="tight")
    fig.savefig(prefix.with_suffix(".png"), dpi=220, bbox_inches="tight")
    print(json.dumps({"pdf": str(prefix.with_suffix('.pdf')), "png": str(prefix.with_suffix('.png'))}))


if __name__ == "__main__":
    main()
