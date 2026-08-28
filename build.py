#!/usr/bin/env python3
"""Clean Chem Intel site builder — the living-system core.

Reads data/*.json, merges into a template, writes index.html with a
generated-at stamp. The cron workflow: edit data -> run build.py -> push.
Nothing in the site is hand-edited HTML anymore.

Usage:
    python3 build.py
"""
import json
import sys
from datetime import date, datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parent
DATA = REPO / "data"
TPL = REPO / "index.template.html"
OUT = REPO / "index.html"


def load(name):
    return json.loads((DATA / name).read_text(encoding="utf-8"))


def main():
    products = load("products.json")
    ings = load("ingredients.json")
    changelog = load("changelog.json")
    reg = load("reg.json")

    # Last-updated = newest changelog date (stable across day rebuilds)
    last_updated = max(e["date"] for e in changelog) if changelog else date.today().isoformat()

    # Live stats for the hero
    n_reclassified = sum(1 for v in ings.values() if v.get("reclassified"))
    n_heritage = sum(1 for p in products if p.get("heritage"))
    n_safe = sum(1 for p in products if p.get("safe"))

    # Regulatory scoreboard
    entries = reg.get("entries", {})
    n_restricted_anywhere = len(entries)
    # count by status per region (US explicit entries)
    by_region = {}
    us_flags = []
    for ing, lst in entries.items():
        for e in lst:
            r = e["region"]
            by_region.setdefault(r, {"banned": 0, "restricted": 0, "review": 0, "flagged": 0, "allowed": 0})
            st = e.get("status", "restricted")
            by_region[r][st] = by_region[r].get(st, 0) + 1
            if r == "us" and st in ("flagged", "restricted", "banned"):
                us_flags.append({"ing": ing, "status": st, "since": e.get("since"), "rule": e.get("rule", "")})
    scoreboard = {
        "n_restricted_anywhere": n_restricted_anywhere,
        "watchlist": len(reg.get("watchlist", [])),
        "by_region": by_region,
        "us_flags": us_flags,
        "us_flags_count": len(us_flags),
    }

    meta = {
        "products": len(products),
        "ingredients": len(ings),
        "reclassified": n_reclassified,
        "heritage": n_heritage,
        "safe": n_safe,
        "restricted_anywhere": n_restricted_anywhere,
        "last_updated": last_updated,
        "built_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "tagline": "A living database of cleaning products — graded ingredient by ingredient, updated regularly.",
    }

    tpl = TPL.read_text(encoding="utf-8")

    def inject(token, obj):
        return html.replace(token, json.dumps(obj, ensure_ascii=False))

    html = tpl
    html = inject("__PRODUCTS__", products)
    html = inject("__INGS__", ings)
    html = inject("__CHANGELOG__", changelog)
    html = inject("__META__", meta)
    html = inject("__REG__", reg)
    html = inject("__SCOREBOARD__", scoreboard)

    OUT.write_text(html, encoding="utf-8")

    print(f"built {OUT.name}: {len(products)} products, {len(ings)} ingredients")
    print(f"  last_updated={last_updated} | reclassified={n_reclassified} | heritage={n_heritage} | safe={n_safe} | restricted-elsewhere={n_restricted_anywhere}")
    print(f"  size: {OUT.stat().st_size/1024:.0f} KB")


if __name__ == "__main__":
    main()