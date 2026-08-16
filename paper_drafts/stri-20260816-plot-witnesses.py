from __future__ import annotations

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "generated" / "asset-first-stri-narrow-paper-table-data-20260816.json"
OUT_DIR = Path(__file__).resolve().parent / "figures"
OUT_DIR.mkdir(parents=True, exist_ok=True)

payload = json.loads(DATA.read_text(encoding="utf-8"))
witnesses = payload["figure_2_witnesses"]

fig, axes = plt.subplots(1, 2, figsize=(8.4, 3.1), sharey=True)
for ax, witness in zip(axes, witnesses, strict=True):
    left, right = witness["pair"]
    labels = [
        f"{{{left}}}\n{witness['left_singleton']}",
        f"{{{left}, {right}}}\n{witness['shared']}",
        f"{{{right}}}\n{witness['right_singleton']}",
    ]
    xs = [0, 1, 2]
    ys = [0, 0, 0]
    ax.scatter(xs, ys, s=[80, 115, 80])
    for x, label in zip(xs, labels, strict=True):
        ax.annotate(label, (x, 0), xytext=(0, 18), textcoords="offset points", ha="center", va="bottom", fontsize=8.4)
    ax.add_patch(FancyArrowPatch((0.12, 0), (0.88, 0), arrowstyle="->", mutation_scale=11, linewidth=1.0))
    ax.add_patch(FancyArrowPatch((1.88, 0), (1.12, 0), arrowstyle="->", mutation_scale=11, linewidth=1.0))
    ax.text(1, -0.19, r"singleton rows force $w_a,w_b\geq r$; shared row $\geq2r$", ha="center", fontsize=8.3)
    ax.set_title(f"{left} / {right}", fontsize=10)
    ax.set_xlim(-0.42, 2.42)
    ax.set_ylim(-0.32, 0.42)
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)

fig.suptitle(r"Two released global-singleton overlap witnesses imply $R^*(A)\geq2$", fontsize=11)
fig.tight_layout(rect=(0, 0, 1, 0.91))
for ext in ("pdf", "png"):
    fig.savefig(OUT_DIR / f"stri-factor2-witnesses.{ext}", dpi=220, bbox_inches="tight")
print(json.dumps({"witnesses": len(witnesses), "pdf": str(OUT_DIR / "stri-factor2-witnesses.pdf")}))
