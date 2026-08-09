#!/usr/bin/env bash
set -euo pipefail

BASE_PYTHON="${BASE_PYTHON:-/data/wyt/envs/vlm_test/bin/python}"
P0_SITE="${P0_SITE:-/data/wyt/envs/agent_evolution_p0_site}"
ALFWORLD_DATA="${ALFWORLD_DATA:-/data/wyt/agent-self-evolution-observatory/alfworld}"

mkdir -p "$P0_SITE" "$ALFWORLD_DATA"

# Keep the existing CUDA/PyTorch/Transformers environment untouched. Only the
# text-environment packages are installed into a separate import target.
"$BASE_PYTHON" -m pip install --target "$P0_SITE" \
  "textworld[pddl]==1.7.0" \
  "alfworld==0.4.2"

export P0_EXTRA_SITE="$P0_SITE"
export ALFWORLD_DATA

# Append the isolated target after the existing environment so its packages fill
# missing dependencies without shadowing the working CUDA/PyTorch stack. ALFWorld
# 0.4.2 ships the downloader as a generated bin script rather than alfworld.scripts.
"$BASE_PYTHON" -c "import runpy,site,sys; site.addsitedir('$P0_SITE'); sys.argv=['alfworld-download']; runpy.run_path('$P0_SITE/bin/alfworld-download', run_name='__main__')"

"$BASE_PYTHON" - <<'PY'
import importlib.util, os, site
site.addsitedir(os.environ["P0_EXTRA_SITE"])
for name in ("torch", "transformers", "alfworld", "textworld"):
    assert importlib.util.find_spec(name), f"missing {name}"
import torch, transformers, alfworld, textworld
print("torch", torch.__version__, "cuda", torch.cuda.is_available())
print("transformers", transformers.__version__)
print("alfworld", getattr(alfworld, "__version__", "unknown"))
print("textworld", getattr(textworld, "__version__", "unknown"))
PY
