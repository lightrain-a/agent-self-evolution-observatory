from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from research_pipeline.config import SemanticScholarSettings
from research_pipeline.semantic_scholar import SemanticScholarClient


def main() -> None:
    parser = argparse.ArgumentParser(description="Run one minimal Semantic Scholar API request.")
    parser.add_argument("--query", default="self evolving visual agents")
    parser.add_argument("--limit", type=int, default=2)
    parser.add_argument("--cached", action="store_true", help="Allow a cached response instead of forcing the network request.")
    args = parser.parse_args()

    settings = SemanticScholarSettings.from_env(required=True)
    client = SemanticScholarClient(settings)
    rows = client.search_papers(
        args.query,
        limit=max(1, min(args.limit, 5)),
        force_refresh=not args.cached,
    )
    print(f"S2_SMOKE_OK {len(rows)}")
    for row in rows:
        print(f"{row.get('year') or 'n.d.'}\t{row.get('title') or '<untitled>'}")


if __name__ == "__main__":
    main()
