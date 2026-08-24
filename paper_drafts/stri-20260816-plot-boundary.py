from __future__ import annotations

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "generated" / "asset-first-stri-narrow-paper-table-data-20260816.json"
SKILLRL = ROOT / "generated" / "asset-first-stri-skillrl-budget-baselines-20260824.json"
SKILLROUTER = ROOT / "generated" / "asset-first-stri-skillrouter-relevance-analogue-20260824.json"
OUT_DIR = Path(__file__).resolve().parent / "figures"
OUT_DIR.mkdir(parents=True, exist_ok=True)

payload = json.loads(DATA.read_text(encoding="utf-8"))
points = payload["figure_3_boundary_points"]
skillrl = json.loads(SKILLRL.read_text(encoding="utf-8"))
skillrouter = json.loads(SKILLROUTER.read_text(encoding="utf-8"))

fig, axes = plt.subplots(1, 2, figsize=(9.0, 3.45))
ax = axes[0]
xs = [100.0 * float(p["overlap_fraction"]) for p in points]
ys = [float(p["R_star"]) for p in points]
ax.scatter(xs, ys, s=44)

label_offsets = {
    "L1 full": (4, 7),
    "calibration": (4, -11),
    "heldout": (4, 7),
    "Level-3": (4, 7),
    "logical compiler": (-74, 7),
}
for x, y, point in zip(xs, ys, points, strict=True):
    dx, dy = label_offsets.get(point["regime"], (4, 6))
    ax.annotate(point["regime"], (x, y), xytext=(dx, dy), textcoords="offset points", fontsize=7.5)

router_x = 100.0 * float(skillrouter["headline"]["core_multi"]) / float(skillrouter["headline"]["core_rows"])
router_y = float(skillrouter["headline"]["core_R_star"])
ax.scatter([router_x], [router_y], s=58, marker="^")
ax.annotate("SkillRouter relevance†", (router_x, router_y), xytext=(-18, 10), textcoords="offset points", fontsize=7.5)
ax.axhline(1.0, linestyle="--", linewidth=1.0)
ax.set_xlim(-3, 103)
ax.set_ylim(0.88, 2.12)
ax.set_xlabel("Multi-membership (%)", fontsize=8)
ax.set_ylabel(r"Distortion $R^*$", fontsize=8)
ax.set_title("A  Geometry, not overlap count", fontsize=9)
ax.tick_params(labelsize=7.5)
ax.grid(True, linewidth=0.4, alpha=0.35)

ax = axes[1]
budgets = skillrl["budgets"]
ks = [int(row["top_k"]) for row in budgets]
official_changed = [int(row["controls"]["official_dynamic_priority"]["targets_with_semantic_set_change"]) for row in budgets]
official_reduced = [int(row["controls"]["official_dynamic_priority"]["targets_with_unique_count_reduction"]) for row in budgets]
capacity_changed = [int(row["controls"]["capacity_plus_one"]["targets_with_semantic_set_change"]) for row in budgets]
ax.plot(ks, official_changed, marker="o", label="dyn clone: set changed")
ax.plot(ks, official_reduced, marker="s", label="dyn clone: unique reduced")
ax.plot(ks, capacity_changed, marker="^", label="dyn clone + 1 slot")
ax.axhline(0, linestyle="--", linewidth=1.0)
ax.annotate("non-dynamic clone = quotient = 0", (3.0, 0.0), xytext=(0, 8), textcoords="offset points", fontsize=7.2)
ax.set_xticks(ks)
ax.set_ylim(-0.6, 12.4)
ax.set_xlabel(r"SkillRL general-skill budget $k$", fontsize=8)
ax.set_ylabel("Clone targets (of 12)", fontsize=8)
ax.set_title("B  Provenance priority × finite budget", fontsize=9)
ax.tick_params(labelsize=7.5)
ax.legend(fontsize=6.8, frameon=False, loc="upper left")
ax.grid(True, linewidth=0.4, alpha=0.35)

fig.tight_layout(w_pad=1.8)
for ext in ("pdf", "png"):
    fig.savefig(OUT_DIR / f"stri-rstar-boundary.{ext}", dpi=220, bbox_inches="tight")

print(json.dumps({
    "support_points": len(points),
    "external_relevance_point": {"multi_fraction": router_x / 100.0, "R_star": router_y},
    "skillrl_budgets": ks,
    "pdf": str(OUT_DIR / "stri-rstar-boundary.pdf"),
    "png": str(OUT_DIR / "stri-rstar-boundary.png"),
}))
