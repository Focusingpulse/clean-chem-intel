#!/usr/bin/env python3
"""Repair the dead / non-governing citations on six product records (2026-10-13).

Six records cite a document that does not resolve or does not govern the record:

  * five records carry `https://cpid.calepa.ca.gov/` as their ONLY source_url.
    That host has no A/AAAA/CNAME record (measured 2026-10-06, re-measured
    2026-10-13) and is a bare portal root with no path, so it named no product
    even when it worked.
  * one record (Swiffer Sweeper Wet Mopping Cloth Refills, Lavender) cites
    `https://smartlabel.pg.com/en-ca/<gtin>.html`, a catch-all shell host that
    serves a byte-identical 2,317-byte body at EVERY path.

Every replacement below is the manufacturer's own product-specific disclosure,
fetched HTTP 200 from this sandbox on 2026-10-13 (browser user-agent).

This script changes ONLY `source_url`, `source` and `updated`. It does NOT touch
`ings`, any grade, any evidence level, `safe`, `tier` or ownership, so it is not
a grade-surface change. Where the record's pre-existing list diverges from the
newly cited filing, the divergence is written into the record's `source` prose
rather than silently smoothed -- the list itself is left for the product-level
duplicate ruling.

Idempotent: the write is guarded on whether `source_url` already carries the new
value. --dry-run guards EVERY write.

Run:  python3 tools/repair_2026_10_13.py [--dry-run]
"""
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
PRODUCTS = REPO / "data" / "products.json"
CHANGELOG = REPO / "data" / "changelog.json"

TODAY = "2026-10-13"

PG_API = ("https://az-na-smartlabel-prod-functionapp-api.pgcloud.com"
          "/api/getproductdetails?gtin={gtin}&locale={loc}")

REPAIRS = [
    {
        "name": "Dawn Ultra Dish Soap",
        "url": PG_API.format(gtin="00037000750598", loc="en-US"),
        "source": (
            "P&G's own SmartLabel product disclosure for Dawn Ultra Dishwashing "
            "Liquid Dish Soap, Original Scent, 21.6 fl oz (GTIN 00037000750598), "
            "read via the keyless P&G SmartLabel API 2026-10-13 (HTTP 200). "
            "Source repointed this date from the dead CPID host "
            "(cpid.calepa.ca.gov, no DNS record). The ingredient list on this "
            "record is its PRE-EXISTING list and was NOT re-derived against the "
            "filing: the filing discloses 12 intentionally added ingredients "
            "against the 5 here, and Cocamidopropyl Betaine does not appear on "
            "the filing at all. Where the two disagree the filing governs; "
            "reconciliation is pending the product-level duplicate ruling (this "
            "record duplicates the corpus records Dawn Ultra and Dawn Ultra "
            "Dishwashing Liquid)."
        ),
    },
    {
        "name": "Tide Original Liquid Laundry",
        "url": PG_API.format(gtin="00037000402176", loc="en-US"),
        "source": (
            "P&G's own SmartLabel product disclosure for Tide Liquid Laundry "
            "Detergent, Original, 64 loads, 92 fl oz (GTIN 00037000402176), read "
            "via the keyless P&G SmartLabel API 2026-10-13 (HTTP 200). Source "
            "repointed this date from the dead CPID host (cpid.calepa.ca.gov, no "
            "DNS record). The ingredient list on this record is its PRE-EXISTING "
            "list and was NOT re-derived against the filing: the filing discloses "
            "29 intentionally added ingredients against the 5 here. Where the two "
            "disagree the filing governs; reconciliation is pending the "
            "product-level duplicate ruling (this record duplicates the corpus "
            "record Tide)."
        ),
    },
    {
        "name": "Clorox Disinfecting Bleach",
        "url": "https://smartlabel.labelinsight.com/product/6190734/ingredients",
        "source": (
            "Clorox's own SmartLabel ingredient disclosure for Clorox Disinfecting "
            "Bleach, Concentrated Formula, Regular (24 fl oz, UPC 044600322513), "
            "information updated 2024-10-29 by Clorox, read 2026-10-13 (HTTP 200). "
            "Source repointed this date from the dead CPID host "
            "(cpid.calepa.ca.gov, no DNS record). The ingredient list on this "
            "record is its PRE-EXISTING list and was NOT re-derived against the "
            "filing: the filing discloses 8 intentionally added ingredients "
            "against the 3 here. Where the two disagree the filing governs; "
            "reconciliation is pending the product-level duplicate ruling (this "
            "record duplicates the corpus record Clorox Bleach)."
        ),
    },
    {
        "name": "Lysol Multi-Surface Cleaner",
        "url": "https://www.rbnainfo.com/product.php?productLineId=3354",
        "source": (
            "Reckitt's own ingredient disclosure (rbnainfo.com) for LYSOL Power "
            "Clean Multi-Surface Cleaner, Sparkling Lemon & Sunflower Essence, "
            "read 2026-10-13 (HTTP 200; the served HTML carries the full panel "
            "with a CAS line per ingredient). Source repointed this date from the "
            "dead CPID host (cpid.calepa.ca.gov, no DNS record). The ingredient "
            "list on this record is its PRE-EXISTING list and was NOT re-derived "
            "against the filing: the filing names Water, Benzalkonium Chloride, "
            "C10-16 Alketh, Tetrasodium EDTA, Sodium Tetraborate Decahydrate, "
            "Fragrance/Parfum and two dyes, plus a fragrance-component section; "
            "this record's Sodium Lauryl Sulfate does not appear on the filing. "
            "Where the two disagree the filing governs; reconciliation is pending "
            "the product-level duplicate ruling."
        ),
    },
    {
        "name": "Seventh Generation Free & Clear Dish",
        "url": "https://www.seventhgeneration.com/dish-liquid-free-clear-19-fl-oz",
        "source": (
            "Seventh Generation's own product page for Dish Soap - Free & Clear "
            "(19 fl oz), ingredient list read 2026-10-13 (HTTP 200). Source "
            "repointed this date from the dead CPID host (cpid.calepa.ca.gov, no "
            "DNS record). The ingredient list on this record is its PRE-EXISTING "
            "list and was NOT re-derived against the page: the manufacturer lists "
            "9 ingredients (water, sodium lauryl sulfate, lauramine oxide, "
            "glycerin, decyl glucoside, magnesium chloride, citric acid, "
            "benzisothiazolinone, methylisothiazolinone), this record carries the "
            "placeholder 'Plant-derived Surfactants', and this record's Sodium "
            "Gluconate does not appear on the manufacturer's list. Where the two "
            "disagree the manufacturer governs; reconciliation is pending the "
            "product-level duplicate ruling."
        ),
    },
    {
        "name": "Swiffer Sweeper Wet Mopping Cloth Refills, Lavender",
        "url": PG_API.format(gtin="00030772142271", loc="en-CA"),
        "source": (
            "P&G's own SmartLabel product disclosure for Swiffer Sweeper Wet "
            "Mopping Cloth Refills with Febreze Freshness, Lavender Scent, 24 "
            "count (GTIN 00030772142271), read via the keyless P&G SmartLabel API "
            "at locale en-CA 2026-10-13 (HTTP 200; the en-US locale 404s for this "
            "GTIN). Cited route corrected this date: the previously cited "
            "smartlabel.pg.com HTML path is a catch-all shell that returns a "
            "byte-identical 2,317-byte body at every path and is never a valid "
            "citation for an ingredient list. The record's 12 registry keys match "
            "the filing's 11 disclosed substances (the filing prints "
            "methylchloroisothiazolinone/methylisothiazolinone as one line)."
        ),
    },
]


def main():
    dry = "--dry-run" in sys.argv
    products = json.loads(PRODUCTS.read_text(encoding="utf-8"))
    by_name = {p.get("name"): p for p in products if isinstance(p, dict)}

    changed = []
    for r in REPAIRS:
        p = by_name.get(r["name"])
        if p is None:
            print(f"MISS  {r['name']}: record not found")
            continue
        if p.get("source_url") == r["url"]:
            print(f"SKIP  {r['name']}: already repointed (idempotent)")
            continue
        old = p.get("source_url")
        p["source_url"] = r["url"]
        p["source"] = r["source"]
        p["updated"] = TODAY
        changed.append((r["name"], old, r["url"]))
        print(f"FIX   {r['name']}\n      {old}\n   -> {r['url']}")

    if not changed:
        print("nothing to do")
        return 0

    if dry:
        print(f"--dry-run: no file written ({len(changed)} would change)")
        return 0

    PRODUCTS.write_text(
        json.dumps(products, ensure_ascii=False, indent=1), encoding="utf-8"
    )
    print(f"wrote {PRODUCTS} ({len(changed)} records)")
    print("NOTE: index.html must be regenerated (python3 build.py). "
          "No changelog entry written: the source/provenance layer renders "
          "nowhere, so a page-visible changelog line would be noise.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
