#!/usr/bin/env python3
from pathlib import Path
import json
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "generated" / "d2-temporal-skill-independent-probes-20260822.json"
STRONG = ROOT / "generated" / "d2-temporal-skill-f9f10-strong-control-20260823.json"
OUT = ROOT / "paper_drafts" / "d2-temporal-skill-bottleneck-iclr2027" / "figures" / "fig3_independent_probes.pdf"

d = json.loads(DATA.read_text())
s = json.loads(STRONG.read_text())
rows = [
    ("Text", d["f0_text_skill_card"]["primary_targeted_vs_generic"]["paired_risk_difference"], d["f0_text_skill_card"]["primary_targeted_vs_generic"]["one_sided_exact_p"], False),
    ("Supplied\noutput", d["f2_downstream_finding_confirmatory"]["primary_targeted_vs_generic"]["paired_risk_difference"], d["f2_downstream_finding_confirmatory"]["primary_targeted_vs_generic"]["one_sided_exact_p"], False),
    ("Executable\nneutral ctrl.", d["f3_executable_skill_state"]["primary_targeted_vs_generic"]["paired_risk_difference"], d["f3_executable_skill_state"]["primary_targeted_vs_generic"]["one_sided_exact_p"], False),
    ("STL first-time\nmatched", d["f8_frozen_population_support_recovery_extension"]["primary_targeted_vs_generic"]["paired_risk_difference"], d["f8_frozen_population_support_recovery_extension"]["primary_targeted_vs_generic"]["one_sided_exact_p"], True),
    ("Non-STL Qwen\noff-target ctrl.", s["f9_qwen"]["primary"]["paired_risk_difference"], s["f9_qwen"]["primary"]["one_sided_exact_p"], False),
    ("Non-STL DeepSeek\noff-target ctrl.", s["f10_deepseek"]["primary"]["paired_risk_difference"], s["f10_deepseek"]["primary"]["one_sided_exact_p"], False),
]
labels = [r[0] for r in rows]
effects = [100 * r[1] for r in rows]
pvals = [r[2] for r in rows]

fig, ax = plt.subplots(figsize=(7.2, 3.2))
bars = ax.bar(range(len(rows)), effects)
bars[3].set_hatch("xx")
ax.axhline(0, linewidth=0.8)
ax.axhline(20, linewidth=1.0, linestyle="--")
ax.text(len(rows)-0.05, 20.8, "+20 pp magnitude criterion", ha="right", va="bottom", fontsize=8)
ax.set_ylabel("Targeted − matched control (percentage points)")
ax.set_xticks(range(len(rows)), labels)
ax.set_ylim(-12, 82)
for i, (effect, p) in enumerate(zip(effects, pvals)):
    y = effect + 1.4 if effect >= 0 else effect - 1.6
    va = "bottom" if effect >= 0 else "top"
    ax.text(i, y, f"{effect:+.1f}\np={p:.3g}", ha="center", va=va, fontsize=7.6)
ax.text(0.01, 0.025, "Cross-hatched STL tranche is the current independent matched-gate pass. Non-STL controls execute substantive task-local procedures.", transform=ax.transAxes, fontsize=6.7)
fig.tight_layout()
OUT.parent.mkdir(parents=True, exist_ok=True)
fig.savefig(OUT, bbox_inches="tight", metadata={"CreationDate": None, "ModDate": None})
print(OUT)
