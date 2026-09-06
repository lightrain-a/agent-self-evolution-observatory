from __future__ import annotations

from research_pipeline import agent_constraint_externality_atomgit_repeat_dev_source_mcp_bridge as base
from research_pipeline.agent_constraint_externality_atomgit_repeat_dev_reserve_build import (
    OUTPUT_BUNDLE,
    load_reserve_spec,
)

# Reuse the already-reviewed exactly-once AppWorld MCP transport implementation,
# changing only the frozen protected-family object it resolves.
base.FROZEN_BUNDLE = OUTPUT_BUNDLE
base.load_dev_spec = load_reserve_spec
base.SCHEMA_VERSION = "ace-atomgit-repeat-dev-reserve-source-mcp-progress-v1"
base.TRAJECTORY_SCHEMA = "ace-atomgit-repeat-dev-reserve-source-trajectory-v1"


if __name__ == "__main__":
    base.main()
