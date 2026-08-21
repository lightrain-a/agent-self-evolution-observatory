from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def save(fig, path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)


def box(ax, xy, w, h, text, fs=9):
    p = FancyBboxPatch(xy, w, h, boxstyle="round,pad=0.02", linewidth=1.2, facecolor="white")
    ax.add_patch(p)
    ax.text(xy[0] + w / 2, xy[1] + h / 2, text, ha="center", va="center", fontsize=fs)
    return p


def arrow(ax, a, b, text=""):
    patch = FancyArrowPatch(a, b, arrowstyle="->", mutation_scale=12, linewidth=1.2)
    ax.add_patch(patch)
    if text:
        ax.text((a[0] + b[0]) / 2, (a[1] + b[1]) / 2 + 0.025, text, ha="center", va="bottom", fontsize=8)


def fig1(out: Path):
    fig, ax = plt.subplots(figsize=(7.2, 3.25))
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
    box(ax, (0.03, 0.39), 0.16, 0.22, "Task order\n$\\pi$", 10)
    box(ax, (0.29, 0.66), 0.21, 0.20, "Agent memory\nhistory $M(\\pi)$", 9)
    box(ax, (0.29, 0.16), 0.21, 0.20, "Environment\nhistory $E(\\pi)$", 9)
    box(ax, (0.61, 0.52), 0.18, 0.20, "Agent\nbehavior", 9)
    box(ax, (0.61, 0.10), 0.18, 0.20, "Current website\nstate", 9)
    box(ax, (0.84, 0.34), 0.13, 0.22, "Observed\nscore", 9)
    arrow(ax, (0.19, 0.54), (0.29, 0.74))
    arrow(ax, (0.19, 0.46), (0.29, 0.26))
    arrow(ax, (0.50, 0.75), (0.61, 0.63))
    arrow(ax, (0.50, 0.26), (0.61, 0.20))
    arrow(ax, (0.79, 0.62), (0.84, 0.48))
    arrow(ax, (0.79, 0.20), (0.84, 0.40))
    ax.text(0.905, 0.71, "fixed gold\nfrom initial state", ha="center", va="center", fontsize=8)
    arrow(ax, (0.905, 0.65), (0.905, 0.56), "")
    ax.text(0.5, 0.965, "Task-order stress tests perturb two persistent states, not one", ha="center", va="top", fontsize=11, fontweight="bold")
    ax.text(0.5, 0.015, "Memory-only attribution requires holding environment history fixed, restoring state per task, or conditioning truth on the current state.", ha="center", va="bottom", fontsize=8)
    save(fig, out)


def fig2(out: Path):
    fig, ax = plt.subplots(figsize=(7.2, 3.0))
    ax.set_xlim(0, 10); ax.set_ylim(0, 4); ax.axis("off")
    ax.plot([0.7, 9.3], [2.15, 2.15], linewidth=1.4)
    events = [
        (1.2, "Task 509", "Checkout succeeds\nCole Haan order\n$469 total"),
        (3.7, "Benchmark scorer", "Task 509 = FAIL\nscore 0\nbackend write persists"),
        (6.2, "Task 96", "Reads latest order\n#000000197\nPending, $469"),
        (8.7, "Fixed evaluator", "Gold: last order\nwas canceled\nTask 96 = FAIL"),
    ]
    for x, title, body in events:
        ax.scatter([x], [2.15], s=45)
        ax.plot([x, x], [2.15, 2.85], linewidth=1.0)
        box(ax, (x - 0.85, 2.85), 1.7, 0.83, title + "\n" + body, 8.2)
    ax.annotate("same item + same $469 order", xy=(6.2, 1.7), xytext=(1.2, 1.7), arrowprops=dict(arrowstyle="<->", linewidth=1.0), ha="center", va="center", fontsize=8)
    ax.text(5.0, 0.55, "Released AWM shuffle1 / shopping / run1", ha="center", va="center", fontsize=10, fontweight="bold")
    ax.text(5.0, 0.15, "A task can be scored FAIL yet still mutate the shared website, making a later fixed reference answer stale.", ha="center", va="center", fontsize=8.5)
    save(fig, out)


def fig3(panel: dict, out: Path):
    tasks = [str(r["task_id"]) for r in panel["sentinels"]]
    ordinal = [r["ordinal"]["pass_rate"] * 100 for r in panel["sentinels"]]
    s1 = [r["shuffle1"]["pass_rate"] * 100 for r in panel["sentinels"]]
    s2 = [r["shuffle2"]["pass_rate"] * 100 for r in panel["sentinels"]]
    x = list(range(len(tasks)))
    width = 0.23
    fig, ax = plt.subplots(figsize=(6.6, 3.4))
    ax.bar([v - width for v in x], ordinal, width, label="Ordinal")
    ax.bar(x, s1, width, label="Shuffle seed 42")
    ax.bar([v + width for v in x], s2, width, label="Shuffle seed 99")
    ax.set_xticks(x, [f"Task {t}" for t in tasks])
    ax.set_ylabel("Pass rate across AWM/RBank × 3 runs (%)")
    ax.set_ylim(0, 112)
    ax.legend(frameon=False, ncol=3, fontsize=8, loc="upper center")
    ax.set_title("Dynamic-reference sentinels are stable in ordinal order and fail after shuffling")
    for i, value in enumerate(ordinal):
        ax.text(i - width, value + 3, "6/6", ha="center", fontsize=8)
        ax.text(i, 3, "0/6", ha="center", fontsize=8)
        ax.text(i + width, 3, "0/6", ha="center", fontsize=8)
    ax.spines[["top", "right"]].set_visible(False)
    save(fig, out)


def fig4(retro: dict, out: Path):
    rows = retro["order_contrasts"]
    labels = []
    raw = []
    clean = []
    removed = []
    for r in rows:
        method = "AWM" if r["method"] == "wa_awm" else "ReasoningBank"
        seed = "42" if r["order"] == "shuffle1" else "99"
        labels.append(f"{method}\nseed {seed}")
        raw.append(r["observed_success_drop"] * 100)
        clean.append(r["non_sensitive_success_drop"] * 100)
        removed.append(r["fraction_observed_gap_removed_by_sensitive_reader_exclusion"] * 100)
    x = list(range(len(labels)))
    width = 0.34
    fig, ax = plt.subplots(figsize=(7.0, 3.55))
    ax.bar([v - width / 2 for v in x], raw, width, label="Observed gap")
    ax.bar([v + width / 2 for v in x], clean, width, label="After excluding state-sensitive readers")
    ax.set_xticks(x, labels)
    ax.set_ylabel("Ordinal - shuffle success gap (percentage points)")
    ax.set_title("A substantial residual remains after removing state-sensitive readers")
    ax.legend(frameon=False, fontsize=8, loc="upper left")
    ax.spines[["top", "right"]].set_visible(False)
    for i, pct in enumerate(removed):
        y = max(raw[i], clean[i]) + 0.35
        ax.text(i, y, f"{pct:.1f}% gap reduction", ha="center", va="bottom", fontsize=8)
    ax.set_ylim(0, max(raw) + 1.8)
    save(fig, out)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--panel", type=Path, required=True)
    p.add_argument("--retrospective", type=Path, required=True)
    p.add_argument("--out-dir", type=Path, required=True)
    a = p.parse_args()
    panel = load(a.panel); retro = load(a.retrospective)
    fig1(a.out_dir / "fig1_causal_decomposition.pdf")
    fig2(a.out_dir / "fig2_direct_witness.pdf")
    fig3(panel, a.out_dir / "fig3_sentinel_replication.pdf")
    fig4(retro, a.out_dir / "fig4_gap_sensitivity.pdf")
    print(json.dumps({"status":"FIGURES_COMPLETE","files":[str(p) for p in sorted(a.out_dir.glob('*.pdf'))]}, indent=2))


if __name__ == "__main__":
    main()
