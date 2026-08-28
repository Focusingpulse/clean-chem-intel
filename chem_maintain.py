#!/usr/bin/env python3
"""Clean Chem Intel data validator — the living-system checks.

Validates the SOURCE OF TRUTH (data/*.json) instead of the built HTML:
- products.json: required fields, duplicate names, unknown/missing ingredients
- ingredients.json: required fields, valid grades, valid impact tags
- reg.json: valid regions/statuses, no empty reasons
- changelog.json: sane entries

Usage:
    python3 chem_maintain.py            # validate (read-only), exit 1 on issues
    python3 chem_maintain.py --summary  # one-line ledger summary
"""
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent
DATA = REPO / "data"

VALID_GRADES = {"A", "B", "C", "D", "F"}
VALID_IMPACTS = {"resp", "repro", "endo", "derm", "aqua", "canc", "allerg"}
VALID_DIMS = {"resp", "derm", "endo", "repro", "organ", "env", "work", "canc"}
VALID_REGIONS = {"eu", "uk", "ca", "jp", "us"}
VALID_STATUS = {"banned", "restricted", "review", "flagged", "allowed"}


def load(name):
    try:
        return json.loads((DATA / name).read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None
    except json.JSONDecodeError as e:
        return f"JSON ERROR in {name}: {e}"


def validate():
    issues = []

    products = load("products.json")
    if isinstance(products, str):
        return [products]
    if products is None:
        return ["data/products.json missing"]
    seen = {}
    for i, p in enumerate(products):
        for f in ("name", "brand", "cat", "ings"):
            if f not in p:
                issues.append(f"product[{i}] missing {f}: {p.get('name','?')}")
        nm = p.get("name")
        if nm and nm in seen:
            issues.append(f"duplicate product name: {nm} (idx {seen[nm]} and {i})")
        seen[nm] = i
        for ing in p.get("ings", []):
            if not isinstance(ing, str) or not ing.strip():
                issues.append(f"product {nm}: bad ingredient entry {ing!r}")

    ings = load("ingredients.json")
    if isinstance(ings, str):
        return [ings]
    if ings is None:
        return ["data/ingredients.json missing"]
    for name, d in ings.items():
        if not isinstance(d, dict):
            issues.append(f"ingredient {name}: not a dict")
            continue
        for g in (d.get("gr") or {}).values():
            if g not in VALID_GRADES:
                issues.append(f"ingredient {name}: invalid grade {g!r}")
        for dim in (d.get("gr") or {}):
            if dim not in VALID_DIMS:
                issues.append(f"ingredient {name}: invalid dim {dim!r}")
        for imp in d.get("impacts", []):
            if imp not in VALID_IMPACTS:
                issues.append(f"ingredient {name}: invalid impact {imp!r}")
        ev = d.get("ev")
        if ev not in (None, "High", "Medium", "Low", "Extrapolated"):
            issues.append(f"ingredient {name}: odd evidence {ev!r}")

    # products must not reference unknown ingredients
    for p in products:
        for ing in p.get("ings", []):
            if ing not in ings:
                issues.append(f"product {p.get('name')}: unknown ingredient {ing!r} (add to data/ingredients.json)")

    reg = load("reg.json")
    if isinstance(reg, str):
        return [reg]
    if reg:
        for ing, lst in reg.get("entries", {}).items():
            if ing not in ings:
                issues.append(f"reg entry references ingredient missing from DB: {ing}")
            for e in lst:
                if e.get("region") not in VALID_REGIONS:
                    issues.append(f"reg {ing}: bad region {e.get('region')}")
                if e.get("status") not in VALID_STATUS:
                    issues.append(f"reg {ing}: bad status {e.get('status')}")
                if not e.get("reason"):
                    issues.append(f"reg {ing}: missing reason")
        for w in reg.get("watchlist", []):
            if not w.get("rule") or not w.get("reason"):
                issues.append(f"watchlist {w.get('name')}: missing rule/reason")

    cl = load("changelog.json")
    if isinstance(cl, str):
        return [cl]
    if cl:
        for e in cl:
            if not e.get("date") or not e.get("text"):
                issues.append(f"changelog entry missing date/text: {e}")

    return issues


def summary_line():
    counts = {}
    try:
        products = json.loads((DATA / "products.json").read_text())
        ings = json.loads((DATA / "ingredients.json").read_text())
        reg = json.loads((DATA / "reg.json").read_text())
        counts["products"] = len(products)
        counts["ings"] = len(ings)
        counts["rec"] = sum(1 for v in ings.values() if v.get("reclassified"))
        counts["her"] = sum(1 for p in products if p.get("heritage"))
        n_restricted = 0
        for lst in reg.get("entries", {}).values():
            if any(e.get("status") in ("banned", "restricted") and e.get("region") != "us" for e in lst):
                n_restricted += 1
        counts["restricted"] = n_restricted
        return (f"clean-chem: {counts['products']} products, {counts['ings']} ingredients, "
                f"{counts['rec']} reclassified, {counts['her']} heritage, {counts['restricted']} restricted-elsewhere")
    except Exception as e:
        return f"clean-chem: summary error ({e})"


if __name__ == "__main__":
    if "--summary" in sys.argv:
        print(summary_line())
        sys.exit(0)
    issues = validate()
    if issues:
        print("ISSUES:")
        for i in issues[:20]:
            print(f"  - {i}")
        if len(issues) > 20:
            print(f"  ... and {len(issues)-20} more")
        sys.exit(1)
    print("clean-chem: data checks passed")
    sys.exit(0)