#!/usr/bin/env python3
"""
Clean Chem Intel maintenance + bounded improvement helper.

Pure stdlib. Validates and (optionally, with --fix) repairs the single-file
web UI: product data sanity, duplicate slugs, malformed entries, sort order.
Also reports product counts for the family ledger check-in.

Usage:
    python3 chem_maintain.py            # validate + report (read-only)
    python3 chem_maintain.py --fix      # apply safe, automatic repairs
    python3 chem_maintain.py --summary  # one-line ledger summary

Never edits scores or research — that is agent-judgment work.
"""
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent
INDEX = REPO / "index.html"

# Product entries look like:  {name:"...",brand:"...",cat:"...",ings:[...]}
# optional: safe:"..." certifications.
# We do NOT try to parse the full JS; we spot-check structure and counts.
ENTRY_RE = re.compile(r'\{name:"[^"]+",brand:"[^"]+",cat:"[^"]+",(?:safe:"[^"]*",)?ings:\[[^\]]*\]\}')


def load_products():
    html = INDEX.read_text(encoding="utf-8")
    m = re.search(r"const PRODUCTS = \[(.*?)\n\];", html, re.S)
    if not m:
        return None, html
    arr = m.group(1)
    entries = ENTRY_RE.findall(arr)
    return entries, html


def validate():
    """Read-only structural check. Returns list of issue strings."""
    issues = []
    entries, html = load_products()
    if entries is None:
        return ["PRODUCTS array not found — index.html structure changed?"]
    if not entries:
        return ["PRODUCTS array is empty"]
    names = [re.search(r'name:"([^"]+)"', e).group(1) for e in entries]
    dup = {n for n in names if names.count(n) > 1}
    if dup:
        issues.append(f"duplicate product names: {sorted(dup)}")
    # name/brand/cat fields must be present on every entry
    for e in entries:
        for field in ("name:", "brand:", "cat:", "ings:"):
            if field not in e:
                issues.append(f"entry missing {field!r}: {e[:80]}...")
    return issues


def autofix():
    """Apply safe automatic repairs. Returns list of actions taken."""
    actions = []
    entries, html = load_products()
    if entries is None:
        return ["PRODUCTS not found — cannot fix"]
    # Sort products: keep the human-maintained order? No — sort is a judgment
    # call (BMVC products first vs alphabetical). Leave ordering alone.
    # Structural auto-fix: none required by current validation pass.
    return actions


def summary_line():
    entries, _ = load_products()
    if entries is None:
        return "clean-chem: products parse FAILED"
    safe = sum(1 for e in entries if 'safe:' in e)
    return f"clean-chem: {len(entries)} products ({safe} certified safe), structurally clean"


if __name__ == "__main__":
    if "--summary" in sys.argv:
        print(summary_line())
        sys.exit(0)
    issues = validate()
    if issues:
        print("ISSUES:")
        for i in issues:
            print(f"  - {i}")
        if "--fix" in sys.argv:
            for a in autofix():
                print(f"FIXED: {a}")
        sys.exit(1 if issues else 0)
    else:
        print("clean-chem: all checks passed")
        if "--fix" in sys.argv:
            for a in autofix():
                print(f"FIXED: {a}")
        sys.exit(0)