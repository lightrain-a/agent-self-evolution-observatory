from __future__ import annotations

"""Run SkillRL's exact model_merger.py without importing the full verl runtime.

The upstream merger imports only two helpers from ``verl.utils`` for saving
processor/tokenizer files. Importing the full package pulls unrelated training
runtime dependencies (ray/tensordict). This shim provides only those two helpers
with standard Transformers APIs, then executes the pinned upstream merger file
unchanged via runpy. Weight loading/DTensor placement/merging/saving therefore
remain the author's implementation.
"""

import runpy
import sys
import types
from pathlib import Path

from transformers import AutoProcessor, AutoTokenizer

UPSTREAM = Path('/data/wyt/evidence-substrates/SkillRL-8e66726-runnable/scripts/model_merger.py')
UPSTREAM_SHA256 = 'ad50e027112ad9c5d067764e05a5eda6ef644041a099b68dee60670a7a6f2cff'


def hf_tokenizer(path: str):
    return AutoTokenizer.from_pretrained(path, trust_remote_code=True)


def hf_processor(path: str):
    try:
        return AutoProcessor.from_pretrained(path, trust_remote_code=True)
    except (ValueError, OSError, KeyError):
        return None


def main() -> None:
    verl = types.ModuleType('verl')
    utils = types.ModuleType('verl.utils')
    utils.hf_tokenizer = hf_tokenizer
    utils.hf_processor = hf_processor
    verl.utils = utils
    sys.modules['verl'] = verl
    sys.modules['verl.utils'] = utils
    sys.argv[0] = str(UPSTREAM)
    runpy.run_path(str(UPSTREAM), run_name='__main__')


if __name__ == '__main__':
    main()
