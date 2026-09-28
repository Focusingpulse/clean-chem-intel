#!/usr/bin/env python3
"""Station-2 revision, 2026-09-28 (Dolman).

Two citation corrections, no data-value changes except the Suavitel source text.

R1 — Suavitel Liquid Fabric Softener, Field Flowers (Linnea FAIL, rev1
2026-09-27). The record's `source` claimed the cited CVS page carried the
identical 10-line list including Polyquaternium-7 "verbatim". Re-derived this
fire: the served retailer pages carry NINE of the ten lines and drop
Polyquaternium-7 (verified 2026-09-28 against Hannaford item 168076, Stop & Shop
353698, GIANT 168076 and GIANT Food Stores 353698 — all HTTP 200, ingredient
field read from served HTML). No resolvable manufacturer or retailer-transcribed
page carrying Polyquaternium-7 was located. Per the verdict this is resolved by
option (c): the line is KEPT and flagged as pack-transcription-only, not
supported by any cited URL. `source_url` repointed to the Hannaford page the
9-line list was read from.

Also repoints the Rite Aid owner record off the ndclist mirror onto the DailyMed
SPL (the 2026-09-26 lesson: an NDC mirror is not a primary source).

Usage:  python3 tools/revise_station2_2026_09_28.py [--dry-run]
"""
from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data")

DRY = "--dry-run" in sys.argv
TODAY = "2026-09-28"

SUAVITEL = "Suavitel Liquid Fabric Softener, Field Flowers"
SUAVITEL_SRC_URL = "https://hannaford.com/groceries/product/suavitel-field-flowers-liquid-fabric-softener-46-oz-jug/168076"

SUAVITEL_SOURCE = (
    "Colgate-Palmolive's own liquid SmartLabel record was searched for and not "
    "located; the manufacturer's product pages return a bot wall to a plain fetch, "
    "and the SmartLabel record previously cited (35000472991) is the dryer-sheets "
    "variant, not this liquid. The list above is the PACK TRANSCRIPTION. The "
    "retailer-transcribed manufacturer label at Hannaford (item 168076) carries "
    "NINE of these ten lines - Water, Dihydrogenated Tallowamidoethyl "
    "Hydroxyethylmonium Methosulfate, Fragrances, Polyquaternium-32, Lactic Acid, "
    "Methylisothiazolinone, Methylchloroisothiazolinone, Octylisothiazolinone, "
    "Colorants - and does NOT carry Polyquaternium-7. The same 9-line list appears "
    "on the GIANT, GIANT Food Stores and Stop and Shop pages. Polyquaternium-7 is "
    "therefore recorded as pack-transcription-only: it is not supported by any "
    "cited URL, and no resolvable manufacturer or retailer-transcribed page "
    "carrying it was located on 2026-09-28. Colgate's own SDS for the regular "
    "variant states structure below the pack list (an acrylamide trace below 0.1 "
    "percent, and a quaternized triethanolamine diester at 1 to 5 percent) - that "
    "is an SDS composition section, not the consumer list, and is not merged in "
    "here."
)

SUAVITEL_NOTE = (
    "A fabric softener is a fragranced consumer product in the sense Sandra's "
    "Sep-24 expansion names, and this is the largest such brand the database did "
    "not carry. It carries two preservative allergens (methylisothiazolinone and "
    "methylchloroisothiazolinone) plus octylisothiazolinone, all three named on the "
    "pack rather than hidden behind 'preservative'. The pack's first line reads "
    "'Made With Love And Water'; recorded here as Water. CAVEAT ON SOURCE: the "
    "Polyquaternium-7 line comes from the pack transcription only and is not "
    "supported by any cited URL - see the source field. Entered ungraded: product "
    "grading is the Sifter lane."
)

RITEAID_SRC = "https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=20d8b8a8-9d15-ad76-e063-6294a90a0521"


def main() -> int:
    prod_path = os.path.join(DATA, "products.json")
    owners_path = os.path.join(DATA, "owners.json")

    products = json.loads(open(prod_path, encoding="utf-8").read())
    owners = json.loads(open(owners_path, encoding="utf-8").read())

    touched = []

    for p in products:
        if p.get("name") == SUAVITEL:
            p["source"] = SUAVITEL_SOURCE
            p["source_url"] = SUAVITEL_SRC_URL
            p["note"] = SUAVITEL_NOTE
            p["updated"] = TODAY
            touched.append(p["name"])

    ra = owners["owners"].get("Rite Aid Corporation")
    if ra and ra.get("src") != RITEAID_SRC:
        ra["src"] = RITEAID_SRC
        ra["detail"] = (
            "Owns the Rite Aid and Simplify house brands; labeler of record on the "
            "FDA OTC listings. Owner source repointed from an NDC mirror to the "
            "DailyMed SPL for NDC 11822-2003 on 2026-09-28."
        )
        touched.append("owners:Rite Aid Corporation")

    print("touched:", touched)
    if DRY:
        print("dry run — nothing written")
        return 0

    open(prod_path, "w", encoding="utf-8").write(json.dumps(products, indent=1, ensure_ascii=False) + "\n")
    open(owners_path, "w", encoding="utf-8").write(json.dumps(owners, indent=1, ensure_ascii=False) + "\n")
    print("written")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())