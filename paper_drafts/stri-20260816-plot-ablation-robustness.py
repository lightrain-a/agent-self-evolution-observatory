from __future__ import annotations

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "generated" / "asset-first-stri-paper-analysis-suite-20260816.json"
TARGET_NULL = ROOT / "generated" / "asset-first-stri-target-null-analysis-20260824.json"
WITNESS_PEELING = ROOT / "generated" / "asset-first-stri-witness-peeling-20260824.json"
SUPPORT_EDIT = ROOT / "generated" / "asset-first-stri-support-edit-radius-20260824.json"
OUT_DIR = Path(__file__).resolve().parent / "figures"
OUT_DIR.mkdir(parents=True, exist_ok=True)

payload = json.loads(DATA.read_text(encoding="utf-8"))
target_null = json.loads(TARGET_NULL.read_text(encoding="utf-8"))
witness_peeling = json.loads(WITNESS_PEELING.read_text(encoding="utf-8"))
support_edit = json.loads(SUPPORT_EDIT.read_text(encoding="utf-8"))
level1 = payload["taxonomy_perturbation_ablation"]["level1_all"]
clone = level1["clone_controls"]

fig, axes = plt.subplots(1, 4, figsize=(6.95, 2.05), gridspec_kw={"width_ratios": [1.15, 0.90, 1.0, 1.15]})

# A — Representation perturbation: raw multiplicity changes while quotienting restores the witness layer.
ax = axes[0]
skills = [row["skill"].replace("skill_", "") for row in clone]
inflation = [100.0 * float(row["raw_membership_inflation"]) for row in clone]
raw_witness = [int(row["raw_witness_count"]) for row in clone]
bars = ax.bar(skills, inflation)
for bar, witness in zip(bars, raw_witness, strict=True):
    ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1.2, f"W={witness}", ha="center", va="bottom", fontsize=5.5)
ax.set_ylim(0, 69)
ax.set_xlabel("Cloned package")
ax.set_ylabel("Raw membership inflation (%)")
ax.set_title("A  Representation", loc="left", fontsize=8.3, fontweight="bold")
ax.text(0.02, 0.98, "Quotient: exact recovery", transform=ax.transAxes, ha="left", va="top", fontsize=5.7)
ax.grid(axis="y", linewidth=0.35, alpha=0.3)

# B — Exact support-edit radius: globally minimum addition-only/deletion-only changes needed for R*=1.
ax = axes[1]
radius = support_edit["support_edit_radius"]
labels = ["Add", "Delete"]
values = [int(radius["minimum_additions_to_equalizable"]), int(radius["minimum_deletions_to_equalizable"])]
bars = ax.bar(labels, values)
for bar, value in zip(bars, values, strict=True):
    ax.text(bar.get_x() + bar.get_width() / 2, value + 2, str(value), ha="center", va="bottom", fontsize=6.5, fontweight="bold")
ax.set_ylim(0, max(values) * 1.22)
ax.set_ylabel("Minimum support-cell edits")
ax.set_title("B  Exact edit radius", loc="left", fontsize=8.3, fontweight="bold")
ax.text(0.03, 0.98, "MILP gap=0\nverified $R^*=1$", transform=ax.transAxes, ha="left", va="top", fontsize=5.5)
null_summary = target_null["degree_preserving_null_ensemble"]["summary"]
ax.text(0.5, -0.29, f"Degree-preserving rewires: {null_summary['residual_draws']}/200 keep $R^*=2$", transform=ax.transAxes, ha="center", fontsize=5.4)
ax.grid(axis="y", linewidth=0.35, alpha=0.3)

# C — Successive disjoint sparse witnesses: the residual persists through 22 peeled optima.
ax = axes[2]
peel = witness_peeling["witness_peeling"]
rounds = peel["rounds"]
removed_rows = [0]
rstars = [float(rounds[0]["R_star_before"])]
removed = 0
for record in rounds:
    removed += int(record["witness_row_count"])
    removed_rows.append(removed)
    if record is rounds[-1]:
        rstars.append(float(peel["summary"]["final_R_star"]))
    else:
        rstars.append(float(rounds[int(record["round"]) + 1]["R_star_before"]))
ax.step(removed_rows, rstars, where="post")
ax.scatter([removed_rows[-1]], [rstars[-1]], s=12, zorder=3)
ax.set_xlim(0, 70)
ax.set_ylim(0.9, 2.12)
ax.set_yticks([1.0, 1.5, 2.0])
ax.set_xlabel("Witness rows peeled")
ax.set_ylabel("$R^*$")
ax.set_title("C  Witness redundancy", loc="left", fontsize=8.3, fontweight="bold")
summary = peel["summary"]
ax.text(0.03, 0.97, f"22 disjoint triples\n66 rows / {summary['unique_tools_spanned']} tools", transform=ax.transAxes, ha="left", va="top", fontsize=5.5)
ax.grid(linewidth=0.35, alpha=0.3)

# D — Non-uniform target rays and package-mass concentration sensitivity.
ax = axes[3]
target_records = target_null["target_ray_sensitivity"]["records"]
alphas = [float(record["alpha"]) for record in target_records]
ratios = [float(record["R_star"]) for record in target_records]
ax.plot(alphas, ratios, marker="o", markersize=3.2, linewidth=1.0)
ax.axhline(2.0, linewidth=0.6, linestyle="--")
ax.set_yscale("log")
ax.set_ylim(1.7, 110)
ax.set_xticks([-1.0, -0.5, 0.0, 0.5, 1.0])
ax.set_yticks([2, 10, 100], labels=["2", "10", "100"])
ax.set_xlabel("Tool-frequency target exponent $\\alpha$")
ax.set_ylabel("$R^*(A;q)$")
ax.set_title("D  Target / weight", loc="left", fontsize=8.3, fontweight="bold")
share_summary = target_null["max_share_sensitivity"]["summary"]
ax.text(0.03, 0.97, f"7/7 targets residual\nmax-share: {share_summary['valid_constraints']}/9 keep $R^*=2$", transform=ax.transAxes, ha="left", va="top", fontsize=5.5)
ax.grid(axis="y", linewidth=0.35, alpha=0.3)

for ax in axes:
    ax.tick_params(labelsize=5.9, pad=1.5)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)

fig.subplots_adjust(left=0.075, right=0.995, top=0.84, bottom=0.34, wspace=0.55)
for ext in ("pdf", "png"):
    fig.savefig(OUT_DIR / f"stri-ablation-robustness.{ext}", dpi=260, bbox_inches="tight")

print(json.dumps({
    "clone_controls": len(clone),
    "minimum_additions_to_equalizable": radius["minimum_additions_to_equalizable"],
    "minimum_deletions_to_equalizable": radius["minimum_deletions_to_equalizable"],
    "degree_preserving_residual_draws": null_summary["residual_draws"],
    "witness_peeling_rounds": summary["peeling_rounds_before_equalizable"],
    "witness_rows_removed": summary["pairwise_disjoint_witness_rows_removed"],
    "witness_tools_spanned": summary["unique_tools_spanned"],
    "target_rays": len(target_records),
    "target_min_R_star": min(ratios),
    "target_max_R_star": max(ratios),
    "max_share_valid_constraints": share_summary["valid_constraints"],
    "pdf": str(OUT_DIR / "stri-ablation-robustness.pdf"),
    "png": str(OUT_DIR / "stri-ablation-robustness.png"),
}, ensure_ascii=False))
