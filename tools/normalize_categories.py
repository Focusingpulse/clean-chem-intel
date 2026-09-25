#!/usr/bin/env python3
"""Normalize the `cat` field in data/products.json to the canonical taxonomy.

Presentation lane (Dolman). Mechanical, idempotent, additive: it only rewrites
the `cat` value on existing records. No record is added, removed, or reordered,
and no other field is touched.

Spine is the CCI-006 Rev 1 taxonomy (three-agent-intelligence
findings/CCI-006-presentation-spec-2026-09-16.md, Linnea-verified). CCI-006
absorbed the whole tail into one "Specialty" bucket, which at 197 products
leaves ~47 items behind a single filter chip. Five clusters inside that tail
are 5+ items and are split out here, per the clean-chem-grow RUN B mandate
("extend only where a real cluster exists, 5+ products"). The deviation is
recorded in docs/presentation-categories.md and flagged to Trellis.

Rules enforced:
  * every existing cat value is in ALIASES or PRODUCT_OVERRIDES, else the run
    HALTS and prints the unmapped value. A silent passthrough would let a new
    ingest category quietly reintroduce fragmentation.
  * the run is idempotent: run twice, the second run reports 0 changes.

Usage:
    python3 tools/normalize_categories.py [--dry-run]
"""
from __future__ import annotations

import json
import os
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PRODUCTS = os.path.join(ROOT, "data", "products.json")

# --- canonical taxonomy -----------------------------------------------------
# Room/task categories first (the CCI-006 spine), then the split-out clusters,
# then Specialty as the honest remainder.
ALIASES: dict[str, str] = {
    # CCI-006 spine
    "All-Purpose": "All-Purpose",
    "All-Purpose (Commercial)": "All-Purpose",
    "Multi-Surface Cleaner": "All-Purpose",
    "Laundry": "Laundry",
    "Laundry Detergent": "Laundry",
    "Fabric": "Laundry",
    "Fabric Softener": "Laundry",
    "Dish Soap": "Dish Soap",
    "dish": "Dish Soap",
    "Dish": "Dish Soap",
    "Dishwasher": "Dishwasher",
    "Dishwasher Detergent": "Dishwasher",
    "Bathroom": "Bathroom",
    "Toilet": "Bathroom",
    "Toilet Cleaner": "Bathroom",
    "Toilet Bowl Cleaner": "Bathroom",
    "Glass": "Glass",
    "Glass Cleaner": "Glass",
    "Glass (Commercial)": "Glass",
    "Disinfectant": "Disinfectant",
    "Floor": "Floor & Carpet",
    "Floor (Commercial)": "Floor & Carpet",
    "Carpet": "Floor & Carpet",
    "Floor & Carpet": "Floor & Carpet",
    # split out of CCI-006's Specialty tail (each 5+ items)
    "Hand Soap": "Hand Soap",
    "Abrasive": "Abrasive Cleanser",
    "Abrasive Cleanser": "Abrasive Cleanser",
    "Stain Remover": "Stain & Odor",
    "Polish": "Wood & Stone Care",
    "Wood Cleaner": "Wood & Stone Care",
    "Stone & Granite": "Wood & Stone Care",
    "Surface Cleaner": "Wood & Stone Care",  # both records are BMVC granite/wood care
    "Wood & Stone Care": "Wood & Stone Care",
    "Physical": "Physical",
    # honest remainder
    "Specialty": "Specialty",
    "Essential Oil": "Specialty",
    "Drain": "Specialty",
    "Oven Cleaner": "Specialty",
    "Degreaser": "Specialty",
    # identity maps for the split-out clusters, so a second run is a no-op
    "Hand Soap": "Hand Soap",
    "Abrasive Cleanser": "Abrasive Cleanser",
    "Stain & Odor": "Stain & Odor",
}

# Per-product overrides where the old cat value was simply wrong for that item.
PRODUCT_OVERRIDES: dict[str, str] = {
    # a clear ammonia all-purpose cleaner filed under "Glass"
    "Great Value Clear Ammonia All Purpose Cleaner": "All-Purpose",
    # scouring cleansers filed under "Specialty"
    "Bar Keepers Friend": "Abrasive Cleanser",
    # laundry/stain products filed scattered
    "OxiClean Baby Stain Soaker": "Stain & Odor",
    "Biokleen Bac-Out Stain & Odor Eliminator": "Stain & Odor",
    # a melamine abrasive block filed under "Specialty"
    "Mr. Clean Magic Eraser": "Physical",
    # "Eco-Friendly" is a claim, not a room (CCI-006): remap each to its
    # functional category. The eco attribute lives in `tier` / `cert`, not `cat`.
    "Method All-Purpose": "All-Purpose",
    "Mrs. Meyer's Multi-Surface": "All-Purpose",
    "Seventh Gen All-Purpose": "All-Purpose",
    "Green Works": "All-Purpose",
    "Biokleen All-Purpose": "All-Purpose",
    "Dr. Bronner's Sal Suds": "All-Purpose",
    "Grove Co. Multi-Purpose": "All-Purpose",
    "Bon Ami": "Abrasive Cleanser",
    "ECOS Dishmate": "Dish Soap",
}


_CANONICAL = set(ALIASES.values()) | set(PRODUCT_OVERRIDES.values())
_MISSING = sorted(c for c in _CANONICAL if c not in ALIASES)
if _MISSING:
    # A canonical value with no identity map halts on the second run and makes this
    # script look idempotent when it is not. Fail loudly instead of shipping that.
    raise SystemExit(f"HALT: canonical value(s) missing an identity map: {_MISSING}")


def target(rec: dict) -> str:
    name = rec.get("name")
    if name in PRODUCT_OVERRIDES:
        return PRODUCT_OVERRIDES[name]
    cat = rec.get("cat")
    if cat not in ALIASES:
        raise SystemExit(
            f"HALT: unmapped cat {cat!r} on product {name!r}. "
            "Add it to ALIASES or PRODUCT_OVERRIDES before running."
        )
    return ALIASES[cat]


def main() -> int:
    dry = "--dry-run" in sys.argv
    with open(PRODUCTS, encoding="utf-8") as fh:
        products = json.load(fh)

    before = Counter(p.get("cat") for p in products)
    changed = 0
    for p in products:
        new = target(p)
        if p.get("cat") != new:
            p["cat"] = new
            changed += 1
    after = Counter(p.get("cat") for p in products)

    print(f"products: {len(products)}")
    print(f"distinct cats: {len(before)} -> {len(after)}   records changed: {changed}")
    print("\ncanonical distribution:")
    for k, v in after.most_common():
        print(f"  {v:4d}  {k}")

    if dry:
        print("\n--dry-run: nothing written")
        return 0

    with open(PRODUCTS, "w", encoding="utf-8") as fh:
        # no trailing newline: match the file's existing bytes so a no-change run
        # leaves the tree clean instead of showing a one-line diff every time.
        json.dump(products, fh, indent=1, ensure_ascii=False)
    print(f"\nwrote {PRODUCTS}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
