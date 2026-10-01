#!/usr/bin/env python3
"""Night-shift station 2 repairs, 2026-10-01 (Dolman).

Two revisions owed by Linnea's 2026-09-30 station-2 verdict
(`verdicts/SPX-spectrum-station2-verdict-2026-09-30.md`) and the ruling in
`gaps/great-value-apc-bleach-cites-mirror-not-manufacturer-2026-09-30.md`.

R1 — duplicate-substance pair. `Butoxydiglycol` was minted as a NEW key on
2026-09-30 while `Diethylene Glycol Monobutyl Ether` already existed with the
same CAS 112-34-5 and carries grades (derm C, repro C, work C). The label
wording is "Butoxydiglycol"; the canonical key is the graded one. Repoint the
two products that read the new key, drop the ungraded duplicate. The direction
of the alias in `tools/harvest_2026_09_30.py` was inverted (existing -> new);
it is corrected here so a re-run does not re-mint the duplicate.

R2 — mirror source. `Great Value All Purpose Cleaner With Bleach` cited a
msdsdigital.com mirror and carried a two-line list. Linnea's ruling resolved
the two documents to the same SKU (UPC 681131596633 on both) and named repair 1
governing: repoint `source_url` to the Walmart CDN SB-258 filing, add the three
missing ingredients, update `source`/`note`/`tier_src`, set
`strength_disclosure` to `full`. The mirror does not survive.

Idempotent: a second run reports 0 changes.

Usage:  python3 tools/repair_2026_10_01.py [--dry-run]
"""
from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data")
TODAY = "2026-10-01"

DRY = "--dry-run" in sys.argv

GV_APC = "Great Value All Purpose Cleaner With Bleach"
GV_APC_URL = ("https://i5.walmartimages.com/dfw/4ff9c6c9-10c4/"
              "k2-_c814c3b8-f3ec-47c0-989c-9cdcb783dedc.v1.pdf")
MIRROR = "msdsdigital.com"

DUP_KEY = "Butoxydiglycol"
KEEP_KEY = "Diethylene Glycol Monobutyl Ether"

# R1b — a second instance of the same class, found while resolving R1.
# "Sodium Xylene Sulfonate" (ungraded) and "Sodium Xylenesulfonate" (graded
# H319) are the same substance, CAS 1300-72-7. The ungraded duplicate is used
# by two products.
DUP_KEY_2 = "Sodium Xylene Sulfonate"
KEEP_KEY_2 = "Sodium Xylenesulfonate"

changed = []


def main() -> int:
    prods = json.load(open(os.path.join(DATA, "products.json")))
    ings = json.load(open(os.path.join(DATA, "ingredients.json")))

    # ---------------------------------------------------------------- R1 ----
    repointed = []
    for p in prods:
        il = p.get("ings") or []
        if DUP_KEY in il:
            p["ings"] = [KEEP_KEY if x == DUP_KEY else x for x in il]
            p["updated"] = TODAY
            repointed.append(p["name"])
    if DUP_KEY in ings:
        del ings[DUP_KEY]
        changed.append(f"R1: dropped duplicate key {DUP_KEY!r}")
    for n in repointed:
        changed.append(f"R1: repointed {n!r} {DUP_KEY!r} -> {KEEP_KEY!r}")
    if not repointed and DUP_KEY not in ings:
        changed.append("R1: already applied")

    # --------------------------------------------------------------- R1b ----
    repointed2 = []
    for p in prods:
        il = p.get("ings") or []
        if DUP_KEY_2 in il:
            p["ings"] = [KEEP_KEY_2 if x == DUP_KEY_2 else x for x in il]
            p["updated"] = TODAY
            repointed2.append(p["name"])
    if DUP_KEY_2 in ings:
        del ings[DUP_KEY_2]
        changed.append(f"R1b: dropped duplicate key {DUP_KEY_2!r}")
    for n in repointed2:
        changed.append(f"R1b: repointed {n!r} {DUP_KEY_2!r} -> {KEEP_KEY_2!r}")
    if not repointed2 and DUP_KEY_2 not in ings:
        changed.append("R1b: already applied")

    # ---------------------------------------------------------------- R2 ----
    hit = [p for p in prods if p.get("name") == GV_APC]
    if len(hit) != 1:
        print(f"HALT: expected exactly one {GV_APC!r}, found {len(hit)}")
        return 1
    rec = hit[0]
    if rec.get("source_url") != GV_APC_URL:
        rec["ings"] = ["Water", "Sodium Hypochlorite", "Sodium Hydroxide",
                       "Lauramine Oxide", "Fragrance"]
        rec["source"] = (
            "Walmart-published California Cleaning Product Right to Know "
            "(SB-258) ingredient disclosure for this product, served from "
            "Walmart's own CDN (i5.walmartimages.com). Filing states UPC "
            "6 81131 59663 3, GS1 10000746 Cleaners Other, manufacturer of "
            "record KIK Custom Products, distributor Walmart, Inc., date of "
            "disclosure 7/3/2019. Five intentionally added ingredients with "
            "CAS numbers; the filing marks sodium hydroxide as present on the "
            "California non-cancer hazards list. The product is also an "
            "EPA-registered disinfectant (EPA Reg. No. 70271-15-41348 on the "
            "manufacturer's SDS for the same UPC), so the label carries an "
            "active while the SB-258 filing carries the full list."
        )
        rec["source_url"] = GV_APC_URL
        rec["note"] = (
            "FOURTH COPY OF ONE FORMULA IN THIS DATABASE, and the record that "
            "used to under-report it. Water, sodium hypochlorite, sodium "
            "hydroxide, lauramine oxide and fragrance is the complete "
            "disclosed list here and on Comet Ultra All Purpose Cleaner with "
            "Bleach, Comet Classic All Purpose Cleaner with Bleach and Great "
            "Value Bathroom Cleaner with Bleach. This record previously "
            "carried two lines (water, hypochlorite) because it cited a "
            "third-party SDS mirror rather than the manufacturer's own "
            "disclosure; the mirror did not carry the surfactant, the pH "
            "adjuster or the fragrance. A two-line list is not a shorter "
            "formula, it is a shorter disclosure, and the difference matters "
            "to anyone reading this as the whole truth about a household "
            "bleach cleaner. Repointed to the Walmart CDN SB-258 filing "
            "2026-10-01 under Linnea's ruling (same UPC 681131596633 on both "
            "documents)."
        )
        rec["strength_disclosure"] = "full"
        rec["tier_src"] = GV_APC_URL
        rec["tier_note"] = (
            "Walmart house brand; the SB-258 filing names KIK Custom "
            "Products as manufacturer of record and Walmart, Inc. as "
            "distributor."
        )
        rec["updated"] = TODAY
        cc = rec.get("claim_conflict")
        if isinstance(cc, dict) and cc.get("toxicology_src", "").find(MIRROR) >= 0:
            cc["toxicology_src"] = GV_APC_URL
        changed.append(f"R2: repointed {GV_APC!r} to the Walmart CDN filing; "
                       "ings 2 -> 5; strength_disclosure full")
    else:
        changed.append("R2: already applied")

    for c in changed:
        print(" -", c)
    if DRY:
        print("(dry run — nothing written)")
        return 0

    json.dump(prods, open(os.path.join(DATA, "products.json"), "w"),
              indent=1, ensure_ascii=False)
    json.dump(ings, open(os.path.join(DATA, "ingredients.json"), "w"),
              indent=1, ensure_ascii=False)

    # Append a changelog entry (drives the rendered last_updated date).
    cl_path = os.path.join(DATA, "changelog.json")
    cl = json.load(open(cl_path))
    entries = cl if isinstance(cl, list) else cl.get("entries", cl)
    if isinstance(entries, list):
        if not any(e.get("date") == TODAY for e in entries if isinstance(e, dict)):
            entries.append({"date": TODAY,
                            "note": "Night shift station 2: two revisions owed "
                                    "by the 2026-09-30 verdict (diglycol "
                                    "duplicate key merged; Great Value APC with "
                                    "Bleach repointed off a mirror to the "
                                    "manufacturer SB-258 filing) plus the "
                                    "exposure-ordered value-brand harvest."})
            if isinstance(cl, list):
                json.dump(cl, open(cl_path, "w"), indent=1, ensure_ascii=False)
            else:
                json.dump(cl, open(cl_path, "w"), indent=1, ensure_ascii=False)
            print("changelog: entry appended for", TODAY)
        else:
            print("changelog: entry for", TODAY, "already present")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
