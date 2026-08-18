from __future__ import annotations

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "generated" / "asset-first-stri-paper-analysis-suite-20260816.json"
REVIEWER_EXT = ROOT / "generated" / "asset-first-stri-reviewer-extensions-20260819.json"
OUT_DIR = Path(__file__).resolve().parent / "figures"
OUT_DIR.mkdir(parents=True, exist_ok=True)

payload = json.loads(DATA.read_text(encoding="utf-8"))
reviewer = json.loads(REVIEWER_EXT.read_text(encoding="utf-8"))
level1 = payload["taxonomy_perturbation_ablation"]["level1_all"]
clone = level1["clone_controls"]
sensitivity = payload["failure_and_sensitivity"]

fig, axes = plt.subplots(1, 3, figsize=(6.95, 2.08), gridspec_kw={"width_ratios": [1.25, 1.0, 1.15]})

# A — Representation perturbation: raw multiplicity changes while quotienting restores the witness layer.
ax = axes[0]
skills = [row["skill"].replace("skill_", "") for row in clone]
inflation = [100.0 * float(row["raw_membership_inflation"]) for row in clone]
raw_witness = [int(row["raw_witness_count"]) for row in clone]
bars = ax.bar(skills, inflation)
for bar, witness in zip(bars, raw_witness, strict=True):
    ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1.3, f"W={witness}", ha="center", va="bottom", fontsize=6.5)
ax.set_ylim(0, 69)
ax.set_xlabel("Cloned package")
ax.set_ylabel("Raw membership inflation (%)")
ax.set_title("A  Clone perturbation", loc="left", fontsize=9.5, fontweight="bold")
ax.text(0.02, 0.97, "Quotient: exact recovery + W=2 for 6/6", transform=ax.transAxes, ha="left", va="top", fontsize=6.6)
ax.grid(axis="y", linewidth=0.35, alpha=0.3)

# B — Robustness under deletions/resampling.
ax = axes[1]
robust_labels = ["LOO tool\nboth W", "LOO row\nboth W", "Bootstrap\n≥1 W", "Bootstrap\nboth W"]
robust_values = [
    100.0 * float(sensitivity["leave_one_tool_out"]["two_witness_fraction"]),
    100.0 * float(sensitivity["leave_one_row_out"]["two_witness_fraction"]),
    100.0 * float(sensitivity["tool_bootstrap"]["any_witness_fraction"]),
    100.0 * float(sensitivity["tool_bootstrap"]["two_witness_fraction"]),
]
y = list(range(len(robust_labels)))
ax.barh(y, robust_values)
ax.set_yticks(y, robust_labels)
ax.invert_yaxis()
ax.set_xlim(0, 103)
ax.set_xlabel("Witness retained (%)")
ax.set_title("B  Robustness", loc="left", fontsize=9.5, fontweight="bold")
for yi, value in zip(y, robust_values, strict=True):
    ax.text(min(value + 1.0, 100.5), yi, f"{value:.1f}", va="center", fontsize=6.5)
p05, p50, p95 = [100.0 * float(v) for v in sensitivity["tool_bootstrap"]["multi_fraction_p05_p50_p95"]]
ax.text(0.02, -0.29, f"Bootstrap overlap 5/50/95%: {p05:.1f}/{p50:.1f}/{p95:.1f}%", transform=ax.transAxes, fontsize=6.2)
ax.grid(axis="x", linewidth=0.35, alpha=0.3)

# C — Where the closed-form witness is and is not applicable.
ax = axes[2]
counts = sensitivity["regime_counts"]
regimes = [
    ("Singleton /\ndisjoint", int(counts.get("DISJOINT_OR_SINGLETON_ONLY", 0))),
    ("Overlap, no\nwitness", int(counts.get("OVERLAP_WITNESS_INCONCLUSIVE", 0))),
    ("No support", int(counts.get("NO_SUPPORT", 0))),
    ("Closed-form\nwitness", int(counts.get("CLOSED_FORM_WITNESS", 0))),
]
labels = [name for name, _ in regimes]
values = [value for _, value in regimes]
y = list(range(len(labels)))
ax.barh(y, values)
ax.set_yticks(y, labels)
ax.invert_yaxis()
ax.set_xlim(0, max(values) + 4)
ax.set_xlabel("Level-1 tools (count)")
ax.set_title("C  Failure / boundary map", loc="left", fontsize=9.5, fontweight="bold")
for yi, value in zip(y, values, strict=True):
    ax.text(value + 0.5, yi, str(value), va="center", fontsize=7)
per_tool = reviewer["per_tool_exact_lp"]["overlap_without_singleton_witness"]
ax.text(0.02, -0.29, f"Exact LP: {per_tool['equalizable_by_exact_lp']}/{per_tool['tools']} equalizable", transform=ax.transAxes, fontsize=6.2)
ax.grid(axis="x", linewidth=0.35, alpha=0.3)

for ax in axes:
    ax.tick_params(labelsize=6.8)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)

fig.subplots_adjust(left=0.08, right=0.99, top=0.86, bottom=0.34, wspace=0.55)
for ext in ("pdf", "png"):
    fig.savefig(OUT_DIR / f"stri-ablation-robustness.{ext}", dpi=240, bbox_inches="tight")

print(json.dumps({
    "clone_controls": len(clone),
    "leave_one_tool_both": robust_values[0],
    "leave_one_row_both": robust_values[1],
    "bootstrap_any": robust_values[2],
    "bootstrap_both": robust_values[3],
    "failure_regimes": counts,
    "pdf": str(OUT_DIR / "stri-ablation-robustness.pdf"),
    "png": str(OUT_DIR / "stri-ablation-robustness.png"),
}, ensure_ascii=False))
