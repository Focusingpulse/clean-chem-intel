#!/usr/bin/env python3
"""Complete Linnea's R2 on the station-2 spectrum build (Sep-26 pulse).

Verdict: three-agent-intelligence/verdicts/SPX-spectrum-station2-verdict-2026-09-25.md

R2 (required, before SPX-006) required the dish-soap household-penetration figure
be re-cited to a source that actually states it, and labelled a derivation.

The Sep-25 revision (tools/revise_station2_2026_09_25.py) fixed the records it
named -- Sprouts Free & Clear, Dish Liquid Unscented, Dish Liquid Free & Clear,
20 Mule Team Borax. It matched those bases by exact string, so it MISSED three
records carrying the same defect in different words, all still cited to
asinsight.com (an Amazon top-10 sales analysis that contains no household figure
at all -- re-fetched 2026-09-26, "household": 0 hits, "penetration": 0, "95": 0):

  Kirkland Signature Ultra Shine Plant-Based Dish Soap   "over 95 percent of households"
  Kirkland Signature Ultra Shine Premium Dish Soap (Citrus Scent)
                                                         relies on "dish-soap category penetration"
  Cascade                                                "dishwasher ownership above 70% of households"
  Cascade Complete ActionPacs                            "dishwasher ownership above 70% of households"

The asinsight page DOES state the Cascade channel share it is also used for
("Cascade follows with 110,000 units (17.5%)"), so that sentence stays -- named
inline as a channel figure, not a national share.

Replacement figures, both read live 2026-09-26:
  * indexbox, US Laundry & Home Products -- "household penetration above 98%",
    a category whose stated scope names dishwashing. (already the R2 remedy)
  * indexbox, US Dishwashing Market -- "over 130 million households in the US
    and dishwasher penetration at approximately 68-72%".

Idempotent: each replacement asserts it matched an expected state; a second run
is a no-op.
"""
import json
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data"

INDEXBOX_LAUNDRY = (
    "https://www.indexbox.io/store/"
    "united-states-laundry-home-products-market-analysis-forecast-size-trends-and-insights/"
)
INDEXBOX_DISHWASHING = (
    "https://www.indexbox.io/store/"
    "united-states-dishwashing-market-analysis-forecast-size-trends-and-insights/"
)

CATEGORY_98 = (
    "The category-penetration figure published for US laundry and home products is "
    "household penetration above 98% (indexbox), and dishwashing is named in that "
    "category's scope; no dish-soap-specific penetration figure is published."
)

OLD_KIRKLAND_PB = (
    "Liquid dish soap is owned by over 95 percent of households; the estimate is "
    "discounted"
)
NEW_KIRKLAND_PB = CATEGORY_98 + " The estimate is discounted"

OLD_KIRKLAND_CITRUS = (
    "Same derivation as the plant-based Kirkland dish soap: dish-soap category "
    "penetration discounted for Costco's household share and for this line within "
    "the Kirkland dish range."
)
NEW_KIRKLAND_CITRUS = (
    "Same derivation as the plant-based Kirkland dish soap: " + CATEGORY_98 +
    " The estimate is discounted for Costco's household share and for this line "
    "within the Kirkland dish range."
)

OLD_CASCADE_TAIL = (
    "Cascade was 17.5% of Amazon top-10 dish-soap volume, July 2026; automatic dish "
    "care is growing with dishwasher ownership above 70% of households."
)
NEW_CASCADE_TAIL = (
    "Indexbox reports US dishwasher penetration at approximately 68-72% of "
    "households (indexbox, US dishwashing market); Cascade was 17.5% of Amazon "
    "top-10 dish-soap volume in July 2026 (asinsight, channel figure, not a "
    "national share)."
)


def replace_basis(p, old, new, applied):
    basis = p["exposure_basis"]
    if old in basis:
        # rejoin: for Kirkland PB the replacement keeps the original sentence tail
        p["exposure_basis"] = basis.replace(old, new)
        applied.append("basis: " + p["name"])
    elif new in basis or (new[:40] in basis):
        applied.append("basis: " + p["name"] + " (already revised)")
    else:
        raise SystemExit(
            "no match on " + p["name"] + "\n  tail: ..." + basis[-200:]
        )


def main():
    prods = json.loads((DATA / "products.json").read_text(encoding="utf-8"))
    by_name = {p["name"]: p for p in prods}
    applied = []

    # Kirkland Plant-Based: replace the "over 95 percent" sentence in place.
    pb = by_name["Kirkland Signature Ultra Shine Plant-Based Dish Soap"]
    replace_basis(pb, OLD_KIRKLAND_PB, NEW_KIRKLAND_PB, applied)
    if pb["exposure_src"] != INDEXBOX_LAUNDRY:
        pb["exposure_src"] = INDEXBOX_LAUNDRY
        applied.append("exposure_src: Kirkland Plant-Based -> indexbox laundry/home")

    # Kirkland Citrus.
    ct = by_name["Kirkland Signature Ultra Shine Premium Dish Soap (Citrus Scent)"]
    replace_basis(ct, OLD_KIRKLAND_CITRUS, NEW_KIRKLAND_CITRUS, applied)
    if ct["exposure_src"] != INDEXBOX_LAUNDRY:
        ct["exposure_src"] = INDEXBOX_LAUNDRY
        applied.append("exposure_src: Kirkland Citrus -> indexbox laundry/home")

    # Cascade + Cascade Complete ActionPacs.
    for name in ("Cascade", "Cascade Complete ActionPacs"):
        p = by_name[name]
        replace_basis(p, OLD_CASCADE_TAIL, NEW_CASCADE_TAIL, applied)
        if p["exposure_src"] != INDEXBOX_DISHWASHING:
            p["exposure_src"] = INDEXBOX_DISHWASHING
            applied.append("exposure_src: " + name + " -> indexbox dishwashing")

    (DATA / "products.json").write_text(
        json.dumps(prods, indent=1, ensure_ascii=False), encoding="utf-8")

    print("edits applied: %d" % len(applied))
    for a in applied:
        print("  -", a)


if __name__ == "__main__":
    main()
