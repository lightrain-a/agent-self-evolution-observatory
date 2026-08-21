from __future__ import annotations

import argparse
import hashlib
import json
import random
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DOMAINS = ("gitlab", "reddit", "shopping", "shopping_admin", "map", "multisite")
ORDERS = {"ordinal": None, "shuffle1": 42, "shuffle2": 99}


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def norm(x: Any) -> str:
    return " ".join(re.sub(r"[^a-z0-9]+", " ", str(x or "").lower()).split())


def val(row: dict[str, Any], *keys: str) -> str:
    inst = row.get("instantiation_dict") or {}
    for key in keys:
        x = inst.get(key)
        if isinstance(x, list):
            x = " ".join(map(str, x))
        if str(x or "").strip():
            return norm(x)
    return ""


def subreddit(row: dict[str, Any]) -> str:
    x = val(row, "subreddit", "forum")
    if x:
        return x.removeprefix("r ")
    m = re.search(r"(?:subreddit|forum)\s+[\"']?([a-z0-9_ ]+)", str(row.get("intent") or ""), re.I)
    return norm(m.group(1)) if m else ""


def add(keys: set[str], site: str, channel: str, entity: str = "") -> None:
    keys.add(f"{site}:{channel}" + (f":{entity}" if entity else ""))


def state_keys(row: dict[str, Any]) -> tuple[set[str], set[str], list[str]]:
    """Return (writes, sensitive_reads, reasons). Conservative, benchmark-specific rules."""
    sites = row.get("sites") or []
    intent = str(row.get("intent") or "")
    text = norm(intent)
    writes: set[str] = set()
    reads: set[str] = set()
    reasons: list[str] = []

    # Multi-site tasks are not used for the clean single-domain interference estimate.
    site = sites[0] if len(sites) == 1 else "multisite"
    repo = val(row, "repo", "gitlab_repo", "project_name", "name")
    product = val(row, "product")
    order = val(row, "order", "order_id", "id", "order_number")
    sub = subreddit(row)

    if site == "reddit":
        if re.match(r"^(change my reddit bio|upvote |thumbs down |reply |edit my post|post |re post |create a discussion post|create a new forum|open the thread .* subscribe)", text):
            if text.startswith("change my reddit bio"):
                add(writes, site, "profile:self"); reasons.append("reddit-profile-write")
            elif "subscribe" in text:
                add(writes, site, "subscription", sub or "unknown"); reasons.append("reddit-subscription-write")
            elif text.startswith("create a new forum"):
                add(writes, site, "forum-catalog"); reasons.append("reddit-forum-create")
            else:
                add(writes, site, "ranking", sub or "unknown")
                add(writes, site, "content", sub or "unknown")
                reasons.append("reddit-content-or-vote-write")
        if any(q in text for q in ("latest post", "newest post", "most recent post", "top 10 post", "top 1 post", "top 2 post", "top 3 post", "top 4 post", "top 5 post", "trending post", "most active")):
            add(reads, site, "ranking", sub or "unknown"); reasons.append("reddit-order-sensitive-ranking-read")

    elif site == "gitlab":
        if re.match(r"^(post |fork |set my gitlab status|update the project site|assign the issue|set the homepage|set up a new|create a (new )?(private |public )?(project|repository|repo)|start a (private |public )?project|invite |star |follow |add the following users|create a milestone|create an issue|submit a (request to merge|merge request))", text):
            if "issue" in text and ("assign" in text or "create" in text):
                add(writes, site, "issue-index", repo or "global"); reasons.append("gitlab-issue-write")
            elif "merge request" in text or "request to merge" in text or text.startswith("post "):
                add(writes, site, "merge-request-index", repo or "global"); reasons.append("gitlab-mr-write")
            elif any(x in text for x in ("set my gitlab status", "set the homepage", "follow ")):
                add(writes, site, "profile:self"); reasons.append("gitlab-profile-write")
            elif any(x in text for x in ("set up a new", "create a new", "create a private", "create a public", "create a repository", "create a repo", "start a private", "start a public", "fork ", "star ")):
                add(writes, site, "repo-catalog"); reasons.append("gitlab-repo-catalog-write")
            else:
                add(writes, site, "repo", repo or "global"); reasons.append("gitlab-repo-write")
        if any(q in text for q in ("most recent open issues", "latest updated issue", "latest created issue", "merge requests assigned", "merge requests requiring", "my todos")):
            if "issue" in text or "todos" in text:
                add(reads, site, "issue-index", repo or "global")
            if "merge requests" in text:
                add(reads, site, "merge-request-index", repo or "global")
            reasons.append("gitlab-dynamic-index-read")
        if any(q in text for q in ("most stars", "least stars", "more than 100 stars", "less than 5 stars", "no stars", "top five most stared", "top eight most stared", "top four most stared", "top three most stared", "top one most stared")):
            add(reads, site, "repo-catalog"); reasons.append("gitlab-ranking-read")

    elif site == "shopping":
        if re.match(r"^(buy |change the delivery address|i recently moved|rate my recent purchase|add .* wish list|add .* wishlist|add the product .* shopping cart|subscribe to the newsletter)", text):
            if text.startswith("buy "):
                add(writes, site, "order-history"); reasons.append("shopping-order-create")
            elif text.startswith("change the delivery address"):
                add(writes, site, "order-history"); reasons.append("shopping-order-update")
            elif text.startswith("i recently moved"):
                add(writes, site, "profile-address"); reasons.append("shopping-profile-write")
            elif "wish list" in text or "wishlist" in text:
                add(writes, site, "wishlist"); reasons.append("shopping-wishlist-write")
            elif "shopping cart" in text:
                add(writes, site, "cart"); reasons.append("shopping-cart-write")
            elif text.startswith("rate my recent purchase"):
                add(writes, site, "review", product or "global"); reasons.append("shopping-review-write")
            else:
                add(writes, site, "profile:self"); reasons.append("shopping-profile-write")
        if any(q in text for q in ("latest order", "most recent order", "first purchase", "how much i spent", "how many fulfilled orders", "total amount of money i spent", "most recent cancelled order", "most recent pending order", "most recent complete order", "most recent completed order", "most recent processing order", "most recent non cancelled order", "latest cancelled order", "latest pending order", "latest complete order", "latest processing order")):
            add(reads, site, "order-history"); reasons.append("shopping-order-history-read")

    elif site == "shopping_admin":
        if re.match(r"^(cancel order|notify |update order|modify the address of order|update the product description|update the description|add a new color|add a new size|add new size|add a simple product|[0-9]+ .* update the stock|we ve received .* update the inventory|approve the positive reviews|delete all .* reviews|change the page title)", text):
            if any(x in text for x in ("cancel order", "notify ", "update order", "modify the address of order")):
                add(writes, site, "order-history");
                if order: add(writes, site, "order", order)
                reasons.append("admin-order-write")
            elif text.startswith("update the product description") or text.startswith("update the description") or text.startswith("add a new color") or text.startswith("add a new size") or text.startswith("add new size") or text.startswith("add a simple product") or "update the stock" in text or "update the inventory" in text:
                add(writes, site, "product-catalog")
                if product: add(writes, site, "product", product)
                reasons.append("admin-product-write")
            elif text.startswith("approve the positive reviews") or text.startswith("delete all") and "review" in text:
                add(writes, site, "review-index"); reasons.append("admin-review-write")
            elif "page title" in text:
                add(writes, site, "cms-pages"); reasons.append("admin-cms-write")
        if any(q in text for q in ("most recent cancelled order", "newest pending order", "oldest complete order", "earliest fraud suspect order", "most recent canlled order", "most recent pending order", "most recent completed order", "monthly count of successful orders", "top 1 best selling", "top 2 best selling", "top 3 best selling", "top 5 best selling")):
            add(reads, site, "order-history"); reasons.append("admin-order-aggregate-read")
        if any(q in text for q in ("count of pending reviews", "count of approved reviews", "count of not approved reviews", "reviews that our store received")):
            add(reads, site, "review-index"); reasons.append("admin-review-index-read")

    return writes, reads, reasons


def domain_of(row: dict[str, Any]) -> str:
    sites = row.get("sites") or []
    if len(sites) >= 2:
        return "multisite"
    return sites[0] if sites else "unknown"


def sequences(rows: list[dict[str, Any]], domain: str) -> dict[str, list[int]]:
    ids = sorted(int(r["task_id"]) for r in rows if domain_of(r) == domain)
    out = {"ordinal": ids}
    for name, seed in ORDERS.items():
        if seed is None:
            continue
        copy = list(ids)
        random.seed(seed)
        random.shuffle(copy)
        out[name] = copy
    return out


def audit(rows: list[dict[str, Any]]) -> dict[str, Any]:
    annotated: dict[int, dict[str, Any]] = {}
    for row in rows:
        writes, reads, reasons = state_keys(row)
        annotated[int(row["task_id"])] = {
            "task_id": int(row["task_id"]),
            "domain": domain_of(row),
            "intent": row.get("intent"),
            "writes": sorted(writes),
            "sensitive_reads": sorted(reads),
            "reasons": reasons,
        }

    domain_reports = []
    all_pairs = []
    for domain in DOMAINS:
        seqs = sequences(rows, domain)
        if not seqs["ordinal"]:
            continue
        positions = {name: {tid: i for i, tid in enumerate(seq)} for name, seq in seqs.items()}
        ids = seqs["ordinal"]
        mutators = [tid for tid in ids if annotated[tid]["writes"]]
        readers = [tid for tid in ids if annotated[tid]["sensitive_reads"]]
        pairs = []
        for w in mutators:
            wk = set(annotated[w]["writes"])
            for r in readers:
                if w == r:
                    continue
                overlap = sorted(wk & set(annotated[r]["sensitive_reads"]))
                if not overlap:
                    continue
                exposed = {name: positions[name][w] < positions[name][r] for name in seqs}
                switched = len(set(exposed.values())) > 1
                pair = {
                    "domain": domain,
                    "writer_task_id": w,
                    "reader_task_id": r,
                    "overlap_channels": overlap,
                    "writer_intent": annotated[w]["intent"],
                    "reader_intent": annotated[r]["intent"],
                    "positions": {name: {"writer": positions[name][w], "reader": positions[name][r]} for name in seqs},
                    "writer_precedes_reader": exposed,
                    "exposure_switches_across_orders": switched,
                }
                pairs.append(pair)
                all_pairs.append(pair)
        exposure_counts = {name: sum(p["writer_precedes_reader"][name] for p in pairs) for name in seqs}
        switched = [p for p in pairs if p["exposure_switches_across_orders"]]
        domain_reports.append({
            "domain": domain,
            "tasks": len(ids),
            "state_mutators": len(mutators),
            "state_sensitive_readers": len(readers),
            "direct_interference_pairs": len(pairs),
            "order_switched_interference_pairs": len(switched),
            "writer_before_sensitive_reader": exposure_counts,
            "state_mutator_task_ids": mutators,
            "state_sensitive_reader_task_ids": readers,
        })

    switched_all = [p for p in all_pairs if p["exposure_switches_across_orders"]]
    top_pairs = sorted(
        switched_all,
        key=lambda p: (len(p["overlap_channels"]), p["domain"], -p["writer_task_id"], -p["reader_task_id"]),
        reverse=True,
    )[:40]
    return {
        "schema_version": "1.0",
        "generated_at": now(),
        "status": "PROTOCOL_INTERFERENCE_AUDIT_COMPLETE",
        "scientific_authority": False,
        "policy": {
            "static_task_config_analysis_only": True,
            "does_not_establish_observed_environment_contamination": True,
            "high_confidence_channels_only": True,
            "runtime_or_environment_support_failure_is_not_scientific_failure": True,
            "live_no_memory_shuffle_control_required_for_causal_adjudication": True,
        },
        "summary": {
            "tasks": len(rows),
            "domains": len([r for r in domain_reports if r["tasks"]]),
            "state_mutators": sum(r["state_mutators"] for r in domain_reports),
            "state_sensitive_readers": sum(r["state_sensitive_readers"] for r in domain_reports),
            "direct_interference_pairs": len(all_pairs),
            "order_switched_interference_pairs": len(switched_all),
        },
        "domains": domain_reports,
        "top_order_switched_pairs": top_pairs,
        "task_annotations": [annotated[k] for k in sorted(annotated)],
    }


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--raw-config", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    rows = json.loads(args.raw_config.read_text(encoding="utf-8"))
    report = audit(rows)
    report["source"] = {"path": str(args.raw_config), "sha256": hashlib.sha256(args.raw_config.read_bytes()).hexdigest()}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "summary": report["summary"], "domains": report["domains"], "top_pairs": report["top_order_switched_pairs"][:8]}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
