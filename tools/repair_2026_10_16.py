#!/usr/bin/env python3
"""Repair 2026-10-16 (Dolman, dolman-research-pulse).

One record carries a DEAD citation in `tier_src`: `Lestoil Heavy Duty Multi-Purpose
Cleaner` cited `https://www.lestoil.com/`, a parked domain with no A record
(`www.lestoil.com` is NXDOMAIN; the apex zone's SOA contact is `parked.nsone.net`).
A citation that does not resolve evidences nothing, so it is repointed to the brand
owner's own live page for the same product.

A `tier_src` repoint is a URL swap on its own: it changes no `ings`, grade, evidence
level, `safe`, `tier`, ownership, substitute or exposure value, and `tier` renders
nowhere, so it does not feed `productGrade(p.ings)`. Same class as the 2026-10-13
`source_url` repoints, which were executed as mechanical edits rather than routed
as a ruling.

Idempotent: a second run reports SKIP for the record. `--dry-run` guards EVERY write.
"""
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
PRODUCTS = REPO / "data" / "products.json"

DRY = "--dry-run" in sys.argv[1:]

NAME = "Lestoil Heavy Duty Multi-Purpose Cleaner"
OLD_SRC = "https://www.lestoil.com/"
NEW_SRC = "https://www.clorox.com/learn/what-is-lestoil-where-can-i-buy-it/"
NOTE_ADD = (
    " Revised 2026-10-16: the previous tier_src (https://www.lestoil.com/) was a parked "
    "domain -- no A record on the apex and NXDOMAIN on www, so it evidenced nothing -- and "
    "was repointed to Clorox's own Lestoil page, which names the product and addresses where "
    "it is sold. That page describes the product as difficult to find and more likely at "
    "hardware and home-improvement stores than at grocery stores. Grocery-channel placement "
    "was separately confirmed live the same day at Publix and Hannaford (both HTTP 200)."
)


def main():
    raw = PRODUCTS.read_text()
    data = json.loads(raw)
    prods = data if isinstance(data, list) else data.get("products", data)

    hits = [p for p in prods if p.get("name") == NAME]
    if len(hits) != 1:
        print(f"ERROR: expected exactly 1 record named {NAME!r}, found {len(hits)}")
        return 2
    rec = hits[0]

    cur = rec.get("tier_src")
    if cur == NEW_SRC:
        print(f"SKIP: {NAME!r} already repointed (tier_src == {NEW_SRC})")
        return 0
    if cur != OLD_SRC:
        print(f"ERROR: {NAME!r} tier_src is {cur!r}, expected {OLD_SRC!r}; refusing to guess")
        return 2

    print(f"RECORD: {NAME}")
    print(f"  tier_src: {OLD_SRC}")
    print(f"        ->  {NEW_SRC}")
    old_note = rec.get("tier_note") or ""
    print(f"  tier_note: appending {len(NOTE_ADD)} chars")
    print(f"  updated: {rec.get('updated')} -> 2026-10-16")

    if DRY:
        print("DRY RUN: nothing written")
        return 0

    rec["tier_src"] = NEW_SRC
    rec["tier_note"] = old_note + NOTE_ADD
    rec["updated"] = "2026-10-16"

    out = json.dumps(data, ensure_ascii=False, indent=1, separators=(",", ": "))
    # products.json ends with `]` and NO trailing newline -- match it exactly.
    PRODUCTS.write_text(out)
    print("WROTE data/products.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
