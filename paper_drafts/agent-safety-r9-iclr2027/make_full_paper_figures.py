#!/usr/bin/env python3
"""Build the full-paper R9 overview and descriptive analysis figures."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch
import numpy as np


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
ANALYSIS = REPO / "generated" / "agent-safety-r9-paper-analysis-suite-20260821.json"
OUT = HERE / "figures"


def box(ax, xy, width, height, title, body, face, edge="#344054"):
    x, y = xy
    patch = FancyBboxPatch(
        (x, y),
        width,
        height,
        boxstyle="round,pad=0.015,rounding_size=0.02",
        linewidth=1.2,
        edgecolor=edge,
        facecolor=face,
    )
    ax.add_patch(patch)
    ax.text(x + width / 2, y + height * 0.68, title, ha="center", va="center", fontsize=10, weight="bold")
    ax.text(x + width / 2, y + height * 0.32, body, ha="center", va="center", fontsize=8.5, color="#344054")
    return patch


def arrow(ax, start, end):
    ax.add_patch(
        FancyArrowPatch(
            start,
            end,
            arrowstyle="-|>",
            mutation_scale=13,
            linewidth=1.3,
            color="#667085",
        )
    )


def protocol_figure():
    fig, ax = plt.subplots(figsize=(7.2, 4.0))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    box(ax, (0.03, 0.64), 0.21, 0.24, "Current qualification", "4 states × 3 fixed probes\n0/12 violations", "#EAF2FF")
    box(ax, (0.30, 0.64), 0.18, 0.24, "Frozen split", "same states, seeds,\nschedule, and runtime", "#E8F7EF")
    arrow(ax, (0.24, 0.76), (0.30, 0.76))

    box(ax, (0.56, 0.72), 0.19, 0.20, "Update", "workflow snapshot\nevolves by step", "#FDECEC")
    box(ax, (0.56, 0.43), 0.19, 0.20, "No update", "step-0 workflow\nheld fixed", "#EAF2FF")
    arrow(ax, (0.48, 0.76), (0.56, 0.82))
    arrow(ax, (0.48, 0.72), (0.56, 0.53))

    box(ax, (0.80, 0.57), 0.17, 0.24, "Paired outcome", "first violation time\nor censoring at step 3", "#FFF4E5")
    arrow(ax, (0.75, 0.82), (0.80, 0.73))
    arrow(ax, (0.75, 0.53), (0.80, 0.64))

    box(ax, (0.17, 0.10), 0.29, 0.22, "Fixed-probe snapshots", "same 12 qualification probes\nat exposure steps 0, 1, 2, 3", "#F2F4F7")
    box(ax, (0.57, 0.10), 0.27, 0.22, "Read-only probe outcome", "first exposure with violation;\nprobe output never writes back", "#F2F4F7")
    arrow(ax, (0.46, 0.21), (0.57, 0.21))
    ax.text(
        0.5,
        0.02,
        "The matched arm separates workflow-update condition from held-out schedule in this frozen finite design.",
        ha="center",
        va="bottom",
        fontsize=8.5,
        color="#344054",
    )
    fig.tight_layout()
    fig.savefig(OUT / "evaluation_protocol.pdf", bbox_inches="tight")
    fig.savefig(OUT / "evaluation_protocol.png", dpi=220, bbox_inches="tight")
    plt.close(fig)


def analysis_figure(data):
    profile = data["temporal_detection_profile"]
    horizons = [row["future_horizon"] for row in profile]
    detected = [row["event_branches_detected"] for row in profile]
    incremental = [row["incremental_event_branches"] for row in profile]

    states = data["state_rows"]
    names = [row["state_id"] for row in states]
    state_events = [row["event_branches"] for row in states]

    fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.2), gridspec_kw={"width_ratios": [1.05, 1.15]})

    ax = axes[0]
    bars = ax.bar(horizons, detected, color=["#98A2B3", "#F79009", "#D92D20"], width=0.62)
    ax.axhline(12, color="#D0D5DD", linestyle="--", linewidth=1)
    for bar, total, inc in zip(bars, detected, incremental):
        ax.text(bar.get_x() + bar.get_width() / 2, total + 0.25, f"{total}/12", ha="center", fontsize=9, weight="bold")
        ax.text(bar.get_x() + bar.get_width() / 2, max(0.45, total * 0.55), f"+{inc}", ha="center", fontsize=8, color="white", weight="bold")
    ax.set_xticks(horizons, ["Step 1", "Through 2", "Through 3"])
    ax.set_ylim(0, 13)
    ax.set_ylabel("Branches with a first event detected")
    ax.set_title("Detection grows with future depth", fontsize=10, weight="bold")
    ax.spines[["top", "right"]].set_visible(False)

    ax = axes[1]
    colors = ["#F79009", "#98A2B3", "#D92D20", "#D92D20"]
    bars = ax.barh(np.arange(len(names)), state_events, color=colors, height=0.62)
    for bar, value in zip(bars, state_events):
        ax.text(value + 0.05, bar.get_y() + bar.get_height() / 2, f"{value}/3", va="center", fontsize=9, weight="bold")
    ax.set_yticks(np.arange(len(names)), names)
    ax.invert_yaxis()
    ax.set_xlim(0, 3.45)
    ax.set_xlabel("Event branches")
    ax.set_title("Events are state-heterogeneous", fontsize=10, weight="bold")
    ax.spines[["top", "right"]].set_visible(False)

    fig.tight_layout(w_pad=2.2)
    fig.savefig(OUT / "temporal_depth_and_state_profile.pdf", bbox_inches="tight")
    fig.savefig(OUT / "temporal_depth_and_state_profile.png", dpi=220, bbox_inches="tight")
    plt.close(fig)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    data = json.loads(ANALYSIS.read_text())
    protocol_figure()
    analysis_figure(data)


if __name__ == "__main__":
    main()
