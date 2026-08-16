from __future__ import annotations

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "generated" / "asset-first-stri-narrow-paper-table-data-20260816.json"
OUT_DIR = Path(__file__).resolve().parent / "figures"
OUT_DIR.mkdir(parents=True, exist_ok=True)

payload = json.loads(DATA.read_text(encoding="utf-8"))
points = payload["figure_3_boundary_points"]

fig, ax = plt.subplots(figsize=(6.2, 3.8))
xs = [100.0 * float(p["overlap_fraction"]) for p in points]
ys = [float(p["R_star"]) for p in points]
ax.scatter(xs, ys, s=55)

label_offsets = {
    "L1 full": (4, 8),
    "calibration": (4, -13),
    "heldout": (4, 8),
    "Level-3": (4, 8),
    "logical compiler": (-91, 8),
}
for x, y, point in zip(xs, ys, points, strict=True):
    dx, dy = label_offsets.get(point["regime"], (4, 6))
    ax.annotate(point["regime"], (x, y), xytext=(dx, dy), textcoords="offset points", fontsize=9)

ax.axhline(1.0, linestyle="--", linewidth=1.0)
ax.set_xlim(-3, 103)
ax.set_ylim(0.88, 2.12)
ax.set_xlabel("Multi-membership among covered contexts (%)")
ax.set_ylabel(r"Exact package-only distortion $R^*(A)$")
ax.set_title("Overlap prevalence does not determine STRI residual")
ax.grid(True, linewidth=0.4, alpha=0.35)
fig.tight_layout()

for ext in ("pdf", "png"):
    fig.savefig(OUT_DIR / f"stri-rstar-boundary.{ext}", dpi=220, bbox_inches="tight")

print(json.dumps({"points": len(points), "pdf": str(OUT_DIR / "stri-rstar-boundary.pdf"), "png": str(OUT_DIR / "stri-rstar-boundary.png")}))
