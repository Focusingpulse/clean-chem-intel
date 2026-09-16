#!/usr/bin/env python3
"""update_counts.py — regenerate counts.md from the data files.

Run after ANY change to data/ (products, ingredients, recipes, reg).
Called by Dolman's clean-chem-grow cron after every fire, and by
Chris's daily lane if wired in (one line in chem_cron.sh:
    python3 update_counts.py
 before the commit step). The file it writes is meant to be committed
and pushed so BOTH lanes and Sandra can see the database grow.
"""
import json, datetime
from pathlib import Path

REPO = Path(__file__).resolve().parent
DATA = REPO / "data"

def load(name, default):
    f = DATA / name
    if not f.exists():
        return default
    return json.loads(f.read_text(encoding="utf-8"))

products = load("products.json", [])
ings = load("ingredients.json", {})
recipes = load("recipes.json", {})
reg = load("reg.json", [])

graded = [p for p in products if p.get("safe") is not None]
ungraded = [p for p in products if p.get("safe") is None]
heritage = [p for p in products if p.get("heritage")]
sources = {}
for p in products:
    s = (p.get("source") or "curated").lower()
    sources[s] = sources.get(s, 0) + 1
top_sources = ", ".join(f"{k}: {v}" for k, v in sorted(sources.items(), key=lambda x: -x[1])[:4])

now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

lines = [
    "---",
    "description: Live database counts for Clean Chem Intel — regenerated from data/ by update_counts.py after every growth run.",
    "---",
    "",
    "# Clean Chem Intel — Live Counts",
    "",
    f"_Updated: {now}_",
    "",
    "| Metric | Count |",
    "|---|---:|",
    f"| **Products** | {len(products)} |",
    f"| — Graded (safe set) | {len(graded)} |",
    f"| — Ungraded (safe null) | {len(ungraded)} |",
    f"| — Heritage | {len(heritage)} |",
    f"| **Ingredients** | {len(ings)} |",
    f"| **Regulatory entries** | {len(reg)} |",
    f"| **DIY recipes (backend)** | {len(recipes.get('recipes', []))} |",
    "",
    "## Sources of products",
    f"{top_sources}",
    "",
    "## Note",
    "- Raw product count grows mainly from **curated additions** (Dolman's lane, Mon/Wed/Fri).",
    "- Ingest lanes (EPA SCIL, CPID, PubChem sync) grow mostly the *ingredient* index.",
    "- Graded count grows as enrichment completes; verification is Linnea's lane.",
    "",
]

REPO.joinpath("counts.md").write_text("\n".join(lines), encoding="utf-8")
print(f"counts.md updated: {len(products)} products, {len(graded)} graded, {len(ings)} ingredients")